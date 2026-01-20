# Student Notes Processor

A Python tool that batch processes scanned student notes (handwritten) using OpenAI's GPT-4o Vision API and generates compiled PDF and Word documents.

**Now with a user-friendly GUI!** 🎨

## Features

- **Graphical User Interface**: Easy-to-use GUI for non-technical users
- **Batch Processing**: Process multiple scanned images automatically
- **AI-Powered OCR**: Uses OpenAI's GPT-4o Vision API to extract handwritten text
- **Dual Output Formats**: Generates both PDF and Word documents (choose one or both)
- **Smart Structuring**: Automatically structures questions and answers (Q1:, Q2:, Q3:, etc.)
- **Page Tracking**: Includes page numbers and source filenames in output
- **Multiple Formats**: Supports JPG, JPEG, PNG, TIFF, BMP, and GIF images
- **Settings Memory**: Remembers your folders and preferences between sessions
- **Secure API Key Storage**: Optional API key saving with local encryption
- **Progress Tracking**: Real-time progress bar and status updates
- **Executable Packages**: Available as standalone .exe (Windows) and .app (macOS)

## Installation

### For End Users (Pre-built Executables)

**Windows:**
1. Download `StudentNotesProcessor.exe` from the releases page
2. Double-click to run (no installation needed!)
3. Enter your OpenAI API key in the GUI

**macOS:**
1. Download `StudentNotesProcessor.app` from the releases page
2. Double-click to run
3. If blocked, go to System Preferences > Security & Privacy and allow the app
4. Enter your OpenAI API key in the GUI

### For Developers (From Source)

#### Prerequisites

- Python 3.7 or higher
- OpenAI API key with access to GPT-4o Vision

#### Setup Steps

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

## Usage

### GUI Application (Recommended)

Run the graphical interface:
```bash
python gui_processor.py
```

**GUI Features:**
1. **API Key**: Enter your OpenAI API key
   - Click the 👁 button to show/hide the key
   - Check "Remember" to save it for next time (stored locally)
2. **INPUT Folder**: Select the folder containing your scanned images
3. **OUTPUT Folder**: Select where to save the processed documents
4. **Output Format**: Choose PDF, Word, or both
5. **Progress**: Watch real-time progress with page count
6. **Status**: See detailed logs of what's happening
7. **Cancel**: Stop processing at any time

The GUI will remember your last used folders and preferences between sessions!

### Command Line Interface (Classic)

For users who prefer command line or automation:

1. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

2. **Place scanned images in the INPUT folder**
   - Supported formats: JPG, JPEG, PNG, TIFF, BMP, GIF
   - Images will be processed in alphabetical/numerical order

3. **Run the processor**
   ```bash
   python processor.py
   ```

4. **Find your output in the OUTPUT folder**
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

## Building Executables

Create standalone executables for distribution to non-technical users.

### Building for Windows

**Requirements:**
- Windows machine or Windows VM
- Python 3.7+ installed

**Build Steps:**
```bash
# Install dependencies
pip install -r requirements.txt

# Run the build script
python build_windows.py

# Output will be in: dist/StudentNotesProcessor.exe
```

The resulting `.exe` file is a single, standalone executable that includes Python and all dependencies. Users can run it without installing anything.

### Building for macOS

**Requirements:**
- macOS machine
- Python 3.7+ installed

**Build Steps:**
```bash
# Install dependencies
pip install -r requirements.txt

# Run the build script
python build_macos.py

# Output will be in: dist/StudentNotesProcessor.app
```

The resulting `.app` bundle can be distributed to macOS users. They may need to allow it in System Preferences > Security & Privacy on first run.

**Note:** For both platforms, the build process may take a few minutes as PyInstaller bundles Python and all dependencies into the executable.

## Configuration & Settings

### GUI Settings Storage

When using the GUI, settings are automatically saved to:

- **Windows**: `%APPDATA%/StudentNotesProcessor/config.json`
- **macOS**: `~/Library/Application Support/StudentNotesProcessor/config.json`
- **Linux**: `~/.config/StudentNotesProcessor/config.json` (or `$XDG_CONFIG_HOME/StudentNotesProcessor/config.json`)

**Saved Settings:**
- Last used INPUT folder path
- Last used OUTPUT folder path
- Output format preferences (PDF/Word)
- API key (only if "Remember" is checked)

**Security Note:** API keys are stored in plain text in the local config file. Only enable "Remember API Key" on trusted, personal computers.

### Environment Variables (CLI Only)

For command-line usage:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes (CLI only) |

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

**GUI Mode:**
- ✅ User-friendly error dialogs (no technical jargon)
- ✅ Clear messages for invalid API keys
- ✅ Warnings for missing images in INPUT folder
- ✅ Network error retry suggestions
- ✅ Processing cancellation support
- ✅ All errors shown in popup dialogs

**CLI Mode:**
- ✅ Checks if INPUT folder exists
- ✅ Validates presence of image files
- ✅ Handles API errors gracefully
- ✅ Displays progress during processing
- ✅ Provides clear error messages in terminal

## Dependencies

- `openai>=1.0.0` - OpenAI API client
- `python-docx>=0.8.11` - Word document generation
- `fpdf2>=2.7.0` - PDF document generation
- `python-dotenv>=1.0.0` - Environment variable management
- `pyinstaller>=6.0.0` - Executable packaging (for building distributable apps)

**Note:** Tkinter is included with Python, so no separate installation is needed for the GUI.

## Project Structure

```
student-notes-processor/
├── gui_processor.py    # GUI application (main entry point)
├── processor.py        # Core processing logic
├── config.py           # Settings and configuration management
├── build_windows.py    # Windows .exe build script
├── build_macos.py      # macOS .app build script
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore rules
├── README.md           # This file
├── INPUT/              # Place scanned images here
│   └── .gitkeep
├── OUTPUT/             # Generated documents appear here
│   └── .gitkeep
└── assets/             # Application assets
    ├── README.md       # Icon generation instructions
    ├── icon.ico        # Windows application icon
    └── icon.icns       # macOS application icon (optional)
```

## Troubleshooting

### GUI Issues

**"Please enter your OpenAI API key"**
- Enter your API key in the API Key field at the top of the GUI
- Optionally check "Remember" to save it for future sessions

**"INPUT folder does not exist"**
- Click "Browse..." next to INPUT Folder and select a valid folder
- Make sure the folder exists and is accessible

**"No image files found in INPUT"**
- Ensure your images are in the selected INPUT folder
- Supported formats: JPG, JPEG, PNG, TIFF, BMP, GIF
- Check that files have the correct extensions

**Progress bar stuck / Not responding**
- The GUI runs processing in a background thread
- For large batches, processing may take time
- Use the Cancel button if needed

### CLI Issues

**"OPENAI_API_KEY environment variable not set"**
- Make sure you've created a `.env` file with your API key
- Or export it in your shell: `export OPENAI_API_KEY=your_key`

**"No image files found in INPUT"**
- Ensure your images are in the `INPUT/` folder and have supported extensions

### API Errors

- Check your OpenAI API key is valid
- Ensure you have sufficient API credits
- Verify you have access to GPT-4o Vision API
- Check your internet connection

### Build Issues

**PyInstaller errors during build**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Try cleaning build artifacts: Remove `build/` and `dist/` folders
- On macOS, you may need to install Xcode Command Line Tools

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

Current version: **v2.0.0**

**v2.0.0 - GUI Release**
- ✨ Added graphical user interface (GUI) using Tkinter
- ✨ Settings persistence (remembers folders, API key, preferences)
- ✨ Real-time progress tracking with progress bar
- ✨ Selectable output formats (PDF and/or Word)
- ✨ API key management with show/hide toggle
- ✨ Executable packaging for Windows (.exe) and macOS (.app)
- ✨ Background processing with cancellation support
- ✨ User-friendly error dialogs
- ✨ Option to open output folder on completion
- 🔧 Refactored core processing logic to support GUI callbacks
- 📝 Comprehensive documentation updates

**v1.0.0 - Initial Release**
- Basic INPUT → OpenAI API → OUTPUT workflow
- PDF and Word document generation
- Batch processing of multiple images