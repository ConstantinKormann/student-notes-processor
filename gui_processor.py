"""
GUI for Student Notes Processor
Provides a user-friendly interface for processing student notes.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
from pathlib import Path
from datetime import datetime

# Import our modules
import config
from processor import (
    process_all_images, 
    create_word_document, 
    create_pdf_document
)


class StudentNotesProcessorGUI:
    """Main GUI application for Student Notes Processor."""
    
    def __init__(self, root):
        """
        Initialize the GUI application.
        
        Args:
            root: The root Tkinter window
        """
        self.root = root
        self.root.title("📝 Student Notes Processor")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        # Processing state
        self.processing = False
        self.cancel_event = threading.Event()
        
        # Load saved settings
        self.load_settings()
        
        # Create GUI
        self.create_widgets()
        
        # Set window icon if available
        try:
            icon_path = Path(__file__).parent / 'assets' / 'icon.ico'
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass  # Icon loading is optional
    
    def load_settings(self):
        """Load saved settings from config."""
        self.saved_api_key = config.get_api_key() or ""
        self.last_input_folder = config.get_last_input_folder() or ""
        self.last_output_folder = config.get_last_output_folder() or ""
        formats = config.get_output_formats()
        self.generate_pdf = formats.get('pdf', True)
        self.generate_word = formats.get('word', True)
    
    def create_widgets(self):
        """Create all GUI widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        row = 0
        
        # API Key section
        ttk.Label(main_frame, text="API Key:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5)
        )
        row += 1
        
        api_key_frame = ttk.Frame(main_frame)
        api_key_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.api_key_var = tk.StringVar(value=self.saved_api_key)
        self.api_key_entry = ttk.Entry(
            api_key_frame, 
            textvariable=self.api_key_var, 
            width=40,
            show="•"
        )
        self.api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Show/Hide API key button
        self.show_api_key = False
        self.toggle_btn = ttk.Button(
            api_key_frame, 
            text="👁", 
            width=3,
            command=self.toggle_api_key_visibility
        )
        self.toggle_btn.pack(side=tk.LEFT, padx=(5, 5))
        
        # Remember API key checkbox
        self.remember_api_key_var = tk.BooleanVar(value=bool(self.saved_api_key))
        ttk.Checkbutton(
            api_key_frame, 
            text="Remember", 
            variable=self.remember_api_key_var
        ).pack(side=tk.LEFT)
        
        row += 1
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15
        )
        row += 1
        
        # INPUT folder section
        ttk.Label(main_frame, text="INPUT Folder:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5)
        )
        row += 1
        
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.input_folder_var = tk.StringVar(value=self.last_input_folder)
        ttk.Entry(
            input_frame, 
            textvariable=self.input_folder_var, 
            width=50
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(
            input_frame, 
            text="Browse...", 
            command=self.browse_input_folder
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        row += 1
        
        # OUTPUT folder section
        ttk.Label(main_frame, text="OUTPUT Folder:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5)
        )
        row += 1
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.output_folder_var = tk.StringVar(value=self.last_output_folder)
        ttk.Entry(
            output_frame, 
            textvariable=self.output_folder_var, 
            width=50
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(
            output_frame, 
            text="Browse...", 
            command=self.browse_output_folder
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        row += 1
        
        # Output format section
        format_frame = ttk.Frame(main_frame)
        format_frame.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(format_frame, text="Output Format:", font=('Arial', 10, 'bold')).pack(
            side=tk.LEFT, padx=(0, 10)
        )
        
        self.pdf_var = tk.BooleanVar(value=self.generate_pdf)
        ttk.Checkbutton(format_frame, text="PDF", variable=self.pdf_var).pack(side=tk.LEFT, padx=(0, 10))
        
        self.word_var = tk.BooleanVar(value=self.generate_word)
        ttk.Checkbutton(format_frame, text="Word Document", variable=self.word_var).pack(side=tk.LEFT)
        
        row += 1
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15
        )
        row += 1
        
        # Progress section
        ttk.Label(main_frame, text="Progress:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5)
        )
        row += 1
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame, 
            variable=self.progress_var, 
            maximum=100,
            length=400
        )
        self.progress_bar.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Progress label
        self.progress_label_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(
            main_frame, 
            textvariable=self.progress_label_var,
            font=('Arial', 9)
        )
        self.progress_label.grid(row=row, column=2, sticky=tk.E, padx=(5, 0))
        
        row += 1
        
        # Status text area
        ttk.Label(main_frame, text="Status:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(10, 5)
        )
        row += 1
        
        # Text widget with scrollbar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
        self.status_text = tk.Text(status_frame, height=8, width=60, wrap=tk.WORD)
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(status_frame, command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=scrollbar.set)
        
        row += 1
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=(10, 0))
        
        self.process_btn = ttk.Button(
            button_frame, 
            text="🚀 Process Notes", 
            command=self.start_processing,
            width=20
        )
        self.process_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_btn = ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self.cancel_processing,
            state=tk.DISABLED,
            width=15
        )
        self.cancel_btn.pack(side=tk.LEFT)
    
    def toggle_api_key_visibility(self):
        """Toggle the visibility of the API key."""
        self.show_api_key = not self.show_api_key
        if self.show_api_key:
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="•")
    
    def browse_input_folder(self):
        """Open folder browser for INPUT folder."""
        folder = filedialog.askdirectory(
            title="Select INPUT Folder",
            initialdir=self.input_folder_var.get() or os.path.expanduser("~")
        )
        if folder:
            self.input_folder_var.set(folder)
    
    def browse_output_folder(self):
        """Open folder browser for OUTPUT folder."""
        folder = filedialog.askdirectory(
            title="Select OUTPUT Folder",
            initialdir=self.output_folder_var.get() or os.path.expanduser("~")
        )
        if folder:
            self.output_folder_var.set(folder)
    
    def log_status(self, message):
        """
        Add a message to the status text area.
        
        Args:
            message: Status message to display
        """
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_progress(self, current, total):
        """
        Update the progress bar.
        
        Args:
            current: Current page number
            total: Total number of pages
        """
        percentage = (current / total) * 100 if total > 0 else 0
        self.progress_var.set(percentage)
        self.progress_label_var.set(f"{current} / {total} pages")
        self.root.update_idletasks()
    
    def validate_inputs(self):
        """
        Validate user inputs before processing.
        
        Returns:
            True if valid, False otherwise
        """
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showerror("Error", "Please enter your OpenAI API key.")
            return False
        
        input_folder = self.input_folder_var.get().strip()
        if not input_folder:
            messagebox.showerror("Error", "Please select an INPUT folder.")
            return False
        
        if not os.path.exists(input_folder):
            messagebox.showerror("Error", f"INPUT folder does not exist:\n{input_folder}")
            return False
        
        output_folder = self.output_folder_var.get().strip()
        if not output_folder:
            messagebox.showerror("Error", "Please select an OUTPUT folder.")
            return False
        
        if not self.pdf_var.get() and not self.word_var.get():
            messagebox.showerror("Error", "Please select at least one output format (PDF or Word).")
            return False
        
        return True
    
    def start_processing(self):
        """Start the processing in a background thread."""
        if not self.validate_inputs():
            return
        
        # Save settings
        api_key = self.api_key_var.get().strip()
        input_folder = self.input_folder_var.get().strip()
        output_folder = self.output_folder_var.get().strip()
        remember_api_key = self.remember_api_key_var.get()
        
        config.save_all_settings(
            api_key if remember_api_key else None,
            input_folder,
            output_folder,
            self.pdf_var.get(),
            self.word_var.get(),
            remember_api_key
        )
        
        # Clear API key if user doesn't want to remember
        if not remember_api_key:
            config.clear_api_key()
        
        # Create output folder if it doesn't exist
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        
        # Clear status
        self.status_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.progress_label_var.set("0 / 0 pages")
        
        # Update UI state
        self.processing = True
        self.cancel_event.clear()
        self.process_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        
        # Start processing thread
        thread = threading.Thread(target=self.process_notes, daemon=True)
        thread.start()
    
    def cancel_processing(self):
        """Cancel the current processing."""
        self.cancel_event.set()
        self.log_status("Cancelling... Please wait.")
        self.cancel_btn.config(state=tk.DISABLED)
    
    def process_notes(self):
        """Process notes in background thread."""
        try:
            api_key = self.api_key_var.get().strip()
            input_folder = self.input_folder_var.get().strip()
            output_folder = self.output_folder_var.get().strip()
            
            self.log_status("=" * 60)
            self.log_status("Starting Student Notes Processing...")
            self.log_status("=" * 60)
            
            # Process all images
            self.log_status("\nStep 1: Processing images from INPUT folder...")
            results = process_all_images(
                input_folder, 
                api_key,
                progress_callback=self.update_progress,
                status_callback=self.log_status,
                cancel_event=self.cancel_event
            )
            
            self.log_status(f"\nSuccessfully processed {len(results)} images")
            
            # Generate timestamp for filenames
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            output_files = []
            
            # Create Word document if selected
            if self.word_var.get():
                self.log_status("\nStep 2: Generating Word document...")
                word_path = Path(output_folder) / f'student_notes_{timestamp}.docx'
                create_word_document(results, str(word_path), status_callback=self.log_status)
                output_files.append(str(word_path))
            
            # Create PDF document if selected
            if self.pdf_var.get():
                self.log_status("\nStep 3: Generating PDF document...")
                pdf_path = Path(output_folder) / f'student_notes_{timestamp}.pdf'
                create_pdf_document(results, str(pdf_path), status_callback=self.log_status)
                output_files.append(str(pdf_path))
            
            self.log_status("\n" + "=" * 60)
            self.log_status("Processing complete!")
            self.log_status("=" * 60)
            
            # Show success dialog
            self.root.after(0, self.show_success_dialog, output_folder, output_files)
            
        except InterruptedError as e:
            self.log_status(f"\n{str(e)}")
            self.root.after(0, messagebox.showwarning, "Cancelled", "Processing was cancelled.")
            
        except FileNotFoundError as e:
            self.log_status(f"\nError: {str(e)}")
            self.root.after(0, messagebox.showerror, "Error", str(e))
            
        except ValueError as e:
            self.log_status(f"\nError: {str(e)}")
            self.root.after(0, messagebox.showerror, "Error", str(e))
            
        except Exception as e:
            error_msg = f"An error occurred:\n{str(e)}"
            self.log_status(f"\nError: {str(e)}")
            self.root.after(0, messagebox.showerror, "Error", error_msg)
            
        finally:
            # Reset UI state
            self.processing = False
            self.root.after(0, self.reset_ui_after_processing)
    
    def reset_ui_after_processing(self):
        """Reset UI controls after processing completes."""
        self.process_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
    
    def show_success_dialog(self, output_folder, output_files):
        """
        Show success dialog with option to open output folder.
        
        Args:
            output_folder: Path to the output folder
            output_files: List of generated file paths
        """
        file_list = "\n".join([f"  - {Path(f).name}" for f in output_files])
        message = f"Processing completed successfully!\n\nGenerated files:\n{file_list}\n\nWould you like to open the output folder?"
        
        if messagebox.askyesno("Success", message):
            self.open_folder(output_folder)
    
    def open_folder(self, folder_path):
        """
        Open a folder in the system file explorer.
        
        Args:
            folder_path: Path to the folder to open
        """
        try:
            if sys.platform == 'win32':
                os.startfile(folder_path)
            elif sys.platform == 'darwin':
                os.system(f'open "{folder_path}"')
            else:
                os.system(f'xdg-open "{folder_path}"')
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{str(e)}")


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    app = StudentNotesProcessorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
