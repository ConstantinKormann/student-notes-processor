"""
Build script for creating Windows executable.
Packages the Student Notes Processor GUI into a single .exe file.
"""

import PyInstaller.__main__
import os
from pathlib import Path

def build_windows_exe():
    """Build Windows executable using PyInstaller."""
    
    # Get the script directory
    script_dir = Path(__file__).parent
    
    # Define paths
    gui_script = str(script_dir / 'gui_processor.py')
    icon_file = str(script_dir / 'assets' / 'icon.ico')
    
    # PyInstaller arguments
    args = [
        gui_script,
        '--name=StudentNotesProcessor',
        '--onefile',
        '--windowed',  # No console window
        '--clean',
        f'--distpath={script_dir / "dist"}',
        f'--workpath={script_dir / "build"}',
        f'--specpath={script_dir}',
    ]
    
    # Add icon if it exists
    if os.path.exists(icon_file):
        args.append(f'--icon={icon_file}')
    
    # Add hidden imports
    args.extend([
        '--hidden-import=openai',
        '--hidden-import=docx',
        '--hidden-import=fpdf',
        '--hidden-import=config',
        '--hidden-import=processor',
    ])
    
    print("Building Windows executable...")
    print("This may take a few minutes...")
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print("\n" + "=" * 60)
    print("Build complete!")
    print("=" * 60)
    print(f"Executable location: {script_dir / 'dist' / 'StudentNotesProcessor.exe'}")
    print("\nYou can now distribute the .exe file to users.")


if __name__ == '__main__':
    build_windows_exe()
