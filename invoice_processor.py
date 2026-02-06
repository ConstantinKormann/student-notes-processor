"""
Invoice Processor
Processes scanned invoices (JPG images and PDF files) into structured Excel spreadsheet.
"""

import os
import base64
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from io import BytesIO

from openai import OpenAI
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
import fitz  # PyMuPDF

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Supported formats for invoices
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif', '.pdf'}

# System prompt for invoice extraction
INVOICE_SYSTEM_PROMPT = """You are an expert at extracting structured data from invoice documents.
Your task is to carefully analyze invoice images and extract the following information:

- Invoice Number
- Invoice Date
- Vendor/Supplier Name
- Total Amount
- Currency
- Tax Amount (if present)
- Due Date (if present)
- Line Items (if readable): each with description, quantity, unit price, and total

Return the data in JSON format with these exact keys:
{
  "invoice_number": "string or null",
  "invoice_date": "string or null",
  "vendor_name": "string or null",
  "total_amount": "string or null",
  "currency": "string or null",
  "tax_amount": "string or null",
  "due_date": "string or null",
  "line_items": [
    {
      "description": "string",
      "quantity": "string",
      "unit_price": "string",
      "total": "string"
    }
  ] or null
}

If you cannot confidently extract a field, return null for that field.
Always return valid JSON."""


def encode_image_to_base64(image_path: str) -> str:
    """
    Convert an image file to base64 encoding for API transmission.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Base64 encoded string of the image
    """
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def pdf_to_images(pdf_path: str) -> List[bytes]:
    """
    Convert PDF pages to images using PyMuPDF.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List of image bytes (PNG format) for each page
    """
    images = []
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            # Render page to image with good quality (2x zoom)
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            # Convert to PNG bytes
            img_bytes = pix.tobytes("png")
            images.append(img_bytes)
        doc.close()
    except Exception as e:
        raise Exception(f"Failed to convert PDF to images: {str(e)}")
    
    return images


def extract_invoice_data(image_source: str, api_key: str, is_pdf: bool = False, 
                        status_callback=None) -> Dict[str, Any]:
    """
    Call OpenAI Vision API to extract structured invoice data from an image or PDF.
    
    Args:
        image_source: Path to the image file or PDF file
        api_key: OpenAI API key
        is_pdf: Whether the source is a PDF file
        status_callback: Optional callback function for status updates
        
    Returns:
        Dictionary containing extracted invoice data and processing status
    """
    result = {
        'source_file': Path(image_source).name,
        'invoice_data': None,
        'status': 'OK',
        'notes': '',
        'error': None
    }
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Handle PDF files
        if is_pdf:
            if status_callback:
                status_callback(f"Converting PDF to images: {Path(image_source).name}")
            
            try:
                images = pdf_to_images(image_source)
                if not images:
                    raise ValueError("PDF contains no pages")
                
                # For multi-page PDFs, process only the first page
                # (invoices are typically single page or most data is on first page)
                image_bytes = images[0]
                base64_image = base64.b64encode(image_bytes).decode('utf-8')
                media_type = 'image/png'
                
            except Exception as e:
                result['status'] = '⚠️ PROCESSING ERROR'
                result['notes'] = f"PDF conversion failed: {str(e)}"
                result['error'] = str(e)
                return result
        else:
            # Handle image files
            base64_image = encode_image_to_base64(image_source)
            ext = Path(image_source).suffix.lower()
            media_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
                '.tiff': 'image/tiff',
                '.tif': 'image/tiff'
            }
            media_type = media_type_map.get(ext, 'image/jpeg')
        
        # Call OpenAI API
        if status_callback:
            status_callback(f"Extracting invoice data: {Path(image_source).name}")
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": INVOICE_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{base64_image}"
                            }
                        },
                        {
                            "type": "text",
                            "text": "Please extract all invoice information from this image and return it as JSON."
                        }
                    ]
                }
            ],
            max_tokens=4096
        )
        
        # Parse the JSON response
        content = response.choices[0].message.content
        
        # Try to extract JSON from the response (handle markdown code blocks)
        try:
            # Remove markdown code blocks if present
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            invoice_data = json.loads(content)
            result['invoice_data'] = invoice_data
            
            # Check if critical fields are missing
            critical_fields = ['invoice_number', 'total_amount']
            missing_critical = [f for f in critical_fields if not invoice_data.get(f)]
            
            if missing_critical:
                result['status'] = '⚠️ PARTIAL DATA'
                result['notes'] = f"Missing critical fields: {', '.join(missing_critical)}"
            else:
                result['status'] = '✅ OK'
                
        except json.JSONDecodeError as e:
            result['status'] = '⚠️ PROCESSING ERROR'
            result['notes'] = f"Failed to parse JSON response: {str(e)}"
            result['error'] = str(e)
            result['invoice_data'] = {}
            
    except Exception as e:
        result['status'] = '⚠️ PROCESSING ERROR'
        result['notes'] = f"API error: {str(e)}"
        result['error'] = str(e)
    
    return result


def process_all_invoices(input_folder: str, api_key: str, progress_callback=None,
                        status_callback=None, cancel_event=None) -> List[Dict[str, Any]]:
    """
    Batch process all invoice files in the INPUT folder.
    
    Args:
        input_folder: Path to the INPUT folder
        api_key: OpenAI API key
        progress_callback: Optional callback(current, total) for progress updates
        status_callback: Optional callback(message) for status updates
        cancel_event: Optional threading.Event to check for cancellation
        
    Returns:
        List of dictionaries containing invoice data and processing results
    """
    input_path = Path(input_folder)
    
    if not input_path.exists():
        raise FileNotFoundError(f"INPUT folder not found: {input_folder}")
    
    # Get all supported files (images and PDFs)
    invoice_files = []
    for ext in SUPPORTED_FORMATS:
        invoice_files.extend(input_path.glob(f"*{ext}"))
        invoice_files.extend(input_path.glob(f"*{ext.upper()}"))
    
    invoice_files = sorted(set(invoice_files))
    
    if not invoice_files:
        raise ValueError(f"No invoice files found in {input_folder}")
    
    if status_callback:
        status_callback(f"Found {len(invoice_files)} invoice files to process")
    else:
        logger.info(f"Found {len(invoice_files)} invoice files to process")
    
    results = []
    for idx, invoice_file in enumerate(invoice_files, 1):
        # Check for cancellation
        if cancel_event and cancel_event.is_set():
            if status_callback:
                status_callback("Processing cancelled by user")
            raise InterruptedError("Processing cancelled by user")
        
        if status_callback:
            status_callback(f"Processing {idx}/{len(invoice_files)}: {invoice_file.name}")
        else:
            logger.info(f"Processing {idx}/{len(invoice_files)}: {invoice_file.name}")
        
        if progress_callback:
            progress_callback(idx, len(invoice_files))
        
        # Determine if file is PDF
        is_pdf = invoice_file.suffix.lower() == '.pdf'
        
        # Extract invoice data
        result = extract_invoice_data(
            str(invoice_file),
            api_key,
            is_pdf=is_pdf,
            status_callback=status_callback
        )
        
        results.append(result)
    
    return results


def create_excel_output(results: List[Dict[str, Any]], output_path: str, 
                       status_callback=None) -> List[str]:
    """
    Generate an Excel spreadsheet from invoice processing results.
    
    Args:
        results: List of dictionaries with invoice data and processing status
        output_path: Path to save the Excel file
        status_callback: Optional callback(message) for status updates
        
    Returns:
        List of filenames that had processing errors
    """
    if status_callback:
        status_callback("Generating Excel spreadsheet...")
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Invoices"
    
    # Define column headers
    headers = [
        'Source File',
        'Invoice Number',
        'Invoice Date',
        'Vendor',
        'Total Amount',
        'Currency',
        'Tax Amount',
        'Due Date',
        'Processing Status',
        'Notes'
    ]
    
    # Write headers with styling
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = Font(bold=True, size=12)
        cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        cell.font = Font(bold=True, color="FFFFFF", size=12)
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # Track failed invoices
    failed_invoices = []
    
    # Write data rows
    for row_idx, result in enumerate(results, 2):
        invoice_data = result.get('invoice_data', {}) or {}
        
        # Extract data from invoice_data
        row_data = [
            result['source_file'],
            invoice_data.get('invoice_number', ''),
            invoice_data.get('invoice_date', ''),
            invoice_data.get('vendor_name', ''),
            invoice_data.get('total_amount', ''),
            invoice_data.get('currency', ''),
            invoice_data.get('tax_amount', ''),
            invoice_data.get('due_date', ''),
            result['status'],
            result['notes']
        ]
        
        # Write row data
        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        
        # Highlight error rows
        if result['status'] != '✅ OK':
            failed_invoices.append(result['source_file'])
            
            # Determine fill color based on status
            if 'ERROR' in result['status']:
                fill_color = "FFC7CE"  # Light red for errors
            else:
                fill_color = "FFEB9C"  # Light yellow for partial data
            
            for col_idx in range(1, len(headers) + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.fill = PatternFill(start_color=fill_color, end_color=fill_color, 
                                       fill_type="solid")
    
    # Auto-adjust column widths
    column_widths = {
        1: 25,  # Source File
        2: 20,  # Invoice Number
        3: 15,  # Invoice Date
        4: 30,  # Vendor
        5: 15,  # Total Amount
        6: 10,  # Currency
        7: 15,  # Tax Amount
        8: 15,  # Due Date
        9: 20,  # Processing Status
        10: 40  # Notes
    }
    
    for col_idx, width in column_widths.items():
        ws.column_dimensions[ws.cell(row=1, column=col_idx).column_letter].width = width
    
    # Save the workbook
    wb.save(output_path)
    
    if status_callback:
        status_callback(f"Excel file saved to: {output_path}")
    else:
        logger.info(f"Excel file saved to: {output_path}")
    
    return failed_invoices


def log_failed_invoices(failed_invoices: List[str]):
    """
    Log warning messages for failed invoices.
    
    Args:
        failed_invoices: List of invoice filenames that failed processing
    """
    if failed_invoices:
        warning_msg = f"Could not fully process the following invoices: {', '.join(failed_invoices)}"
        logger.warning(warning_msg)
    else:
        logger.info("All invoices processed successfully!")


def main():
    """
    Main function to orchestrate the invoice processing workflow.
    """
    print("=" * 60)
    print("Invoice Processor v1")
    print("=" * 60)
    print()
    
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it in a .env file or export it in your shell")
        return
    
    # Define paths
    script_dir = Path(__file__).parent
    input_folder = script_dir / 'INPUT'
    output_folder = script_dir / 'OUTPUT'
    
    # Create OUTPUT folder if it doesn't exist
    output_folder.mkdir(exist_ok=True)
    
    try:
        # Process all invoices
        print("Step 1: Processing invoices from INPUT folder...")
        results = process_all_invoices(str(input_folder), api_key)
        print(f"\nProcessed {len(results)} invoice files")
        print()
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create Excel spreadsheet
        print("Step 2: Generating Excel spreadsheet...")
        excel_path = output_folder / f'invoices_{timestamp}.xlsx'
        failed_invoices = create_excel_output(results, str(excel_path))
        print()
        
        # Log failed invoices
        log_failed_invoices(failed_invoices)
        print()
        
        print("=" * 60)
        print("Processing complete!")
        print("=" * 60)
        print(f"Output file created: {excel_path}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        logger.error(str(e))


if __name__ == "__main__":
    # Load environment variables from .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    main()
