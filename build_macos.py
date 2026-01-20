"""
Build script for creating macOS application bundle.
Packages the Student Notes Processor GUI into a .app bundle.
"""

import PyInstaller.__main__
import os
from pathlib import Path

def build_macos_app():
    """Build macOS application bundle using PyInstaller."""
    
    # Get the script directory
    script_dir = Path(__file__).parent
    
    # Define paths
    gui_script = str(script_dir / 'gui_processor.py')
    icon_file = str(script_dir / 'assets' / 'icon.icns')
    
    # PyInstaller arguments
    args = [
        gui_script,
        '--name=StudentNotesProcessor',
        '--onefile',
        '--windowed',  # Create .app bundle
        '--clean',
        f'--distpath={script_dir / "dist"}',
        f'--workpath={script_dir / "build"}',
        f'--specpath={script_dir}',
    ]
    
    # Add icon if it exists (macOS uses .icns format)
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
    
    # macOS specific options
    args.extend([
        '--osx-bundle-identifier=com.studentnotesprocessor.app',
    ])
    
    print("Building macOS application bundle...")
    print("This may take a few minutes...")
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print("\n" + "=" * 60)
    print("Build complete!")
    print("=" * 60)
    print(f"Application location: {script_dir / 'dist' / 'StudentNotesProcessor.app'}")
    print("\nYou can now distribute the .app bundle to users.")
    print("Note: Users may need to allow the app in System Preferences > Security & Privacy")


if __name__ == '__main__':
    build_macos_app()
