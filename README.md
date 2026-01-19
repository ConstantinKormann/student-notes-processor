# Student Notes Processor

A Python tool that batch processes scanned student notes (handwritten) using OpenAI's GPT-4o Vision API and generates compiled PDF and Word documents.

## Features

- **Batch Processing**: Process multiple scanned images automatically
- **AI-Powered OCR**: Uses OpenAI's GPT-4o Vision API to extract handwritten text
- **Dual Output Formats**: Generates both PDF and Word documents
- **Smart Structuring**: Automatically structures questions and answers (Q1:, Q2:, Q3:, etc.)
- **Page Tracking**: Includes page numbers and source filenames in output
- **Multiple Formats**: Supports JPG, JPEG, PNG, TIFF, BMP, and GIF images

## Installation

### Prerequisites

- Python 3.7 or higher
- OpenAI API key with access to GPT-4o Vision

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/ConstantinKormann/student-notes-processor.git
   cd student-notes-processor
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

## Usage

### Basic Workflow

1. **Place scanned images in the INPUT folder**
   - Supported formats: JPG, JPEG, PNG, TIFF, BMP, GIF
   - Images will be processed in alphabetical/numerical order

2. **Run the processor**
   ```bash
   python processor.py
   ```

3. **Find your output in the OUTPUT folder**
   - `student_notes_YYYYMMDD_HHMMSS.docx` - Word document
   - `student_notes_YYYYMMDD_HHMMSS.pdf` - PDF document

### Example

```bash
# Add your scanned images
cp ~/Downloads/scan_page*.jpg INPUT/

# Run the processor
python processor.py

# Check the output
ls OUTPUT/
```

### Output

The generated documents include:

- **Title page** with "Extracted Student Notes" and generation timestamp
- **Individual sections** for each scanned page with:
  - Page number
  - Original filename
  - Extracted and structured text
- **Page breaks** between sections for easy reading

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |

Set this in a `.env` file (see `.env.example`) or export it in your shell:

```bash
export OPENAI_API_KEY=your_key_here
```

### Supported Image Formats

- `.jpg` / `.jpeg` - JPEG images
- `.png` - PNG images
- `.tiff` / `.tif` - TIFF images
- `.bmp` - Bitmap images
- `.gif` - GIF images

Images are processed in sorted order (alphabetical/numerical filename).

## How It Works

### Processing Pipeline

1. **Image Loading**: Scans the `INPUT/` folder for supported image files
2. **Image Encoding**: Converts each image to base64 for API transmission
3. **AI Extraction**: Sends images to GPT-4o Vision API with specialized prompt
4. **Text Structuring**: AI formats the extracted text with question numbers (Q1:, Q2:, etc.)
5. **Document Generation**: Creates both PDF and Word documents with formatted content

### AI Prompt

The tool uses a specialized system prompt that instructs GPT-4o to:
- Act as an expert at reading handwritten student notes
- Extract all text accurately
- Preserve the structure of questions and answers
- Format questions clearly with Q1:, Q2:, Q3: etc.

## Error Handling

The processor includes robust error handling:

- ✅ Checks if INPUT folder exists
- ✅ Validates presence of image files
- ✅ Handles API errors gracefully
- ✅ Displays progress during processing
- ✅ Provides clear error messages

## Dependencies

- `openai>=1.0.0` - OpenAI API client
- `python-docx>=0.8.11` - Word document generation
- `fpdf2>=2.7.0` - PDF document generation
- `python-dotenv>=1.0.0` - Environment variable management

## Project Structure

```
student-notes-processor/
├── INPUT/              # Place scanned images here
│   └── .gitkeep
├── OUTPUT/             # Generated documents appear here
│   └── .gitkeep
├── processor.py        # Main processing script
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Troubleshooting

### "OPENAI_API_KEY environment variable not set"
Make sure you've created a `.env` file with your API key or exported it in your shell.

### "No image files found in INPUT"
Ensure your images are in the `INPUT/` folder and have supported extensions.

### API Errors
- Check your OpenAI API key is valid
- Ensure you have sufficient API credits
- Verify you have access to GPT-4o Vision API

## Cost Considerations

This tool uses OpenAI's GPT-4o Vision API, which has associated costs:
- Pricing varies based on image resolution and API usage
- Process ~40 pages per batch as per design
- Monitor your OpenAI usage dashboard

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Version

Current version: **v1.0.0**

Initial release with core features:
- Basic INPUT → OpenAI API → OUTPUT workflow
- PDF and Word document generation
- Batch processing of multiple images