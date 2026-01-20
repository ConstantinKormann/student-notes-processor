"""
Configuration management for Student Notes Processor.
Handles storing and retrieving user settings including API keys, folder paths, and preferences.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any


def get_config_dir() -> Path:
    """
    Get the configuration directory for the application based on OS.
    
    Returns:
        Path to the config directory
    """
    if os.name == 'nt':  # Windows
        config_dir = Path(os.getenv('APPDATA', '~')) / 'StudentNotesProcessor'
    else:  # macOS and Linux
        config_dir = Path.home() / 'Library' / 'Application Support' / 'StudentNotesProcessor'
    
    # Create directory if it doesn't exist
    config_dir = config_dir.expanduser()
    config_dir.mkdir(parents=True, exist_ok=True)
    
    return config_dir


def get_config_file() -> Path:
    """
    Get the path to the config.json file.
    
    Returns:
        Path to config.json
    """
    return get_config_dir() / 'config.json'


def load_config() -> Dict[str, Any]:
    """
    Load configuration from the config file.
    
    Returns:
        Dictionary containing configuration settings
    """
    config_file = get_config_file()
    
    if not config_file.exists():
        return {}
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_config(config: Dict[str, Any]):
    """
    Save configuration to the config file.
    
    Args:
        config: Dictionary containing configuration settings
    """
    config_file = get_config_file()
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    except IOError as e:
        print(f"Error saving config: {e}")


def get_api_key() -> Optional[str]:
    """
    Get the saved API key if it exists.
    
    Returns:
        API key string or None if not saved
    """
    config = load_config()
    return config.get('api_key')


def save_api_key(api_key: str):
    """
    Save the API key to the config file.
    
    Args:
        api_key: OpenAI API key to save
    """
    config = load_config()
    config['api_key'] = api_key
    save_config(config)


def clear_api_key():
    """
    Remove the saved API key from the config file.
    """
    config = load_config()
    if 'api_key' in config:
        del config['api_key']
        save_config(config)


def get_last_input_folder() -> Optional[str]:
    """
    Get the last used INPUT folder path.
    
    Returns:
        Folder path string or None if not saved
    """
    config = load_config()
    return config.get('last_input_folder')


def save_last_input_folder(folder_path: str):
    """
    Save the last used INPUT folder path.
    
    Args:
        folder_path: Path to the INPUT folder
    """
    config = load_config()
    config['last_input_folder'] = folder_path
    save_config(config)


def get_last_output_folder() -> Optional[str]:
    """
    Get the last used OUTPUT folder path.
    
    Returns:
        Folder path string or None if not saved
    """
    config = load_config()
    return config.get('last_output_folder')


def save_last_output_folder(folder_path: str):
    """
    Save the last used OUTPUT folder path.
    
    Args:
        folder_path: Path to the OUTPUT folder
    """
    config = load_config()
    config['last_output_folder'] = folder_path
    save_config(config)


def get_output_formats() -> Dict[str, bool]:
    """
    Get the saved output format preferences.
    
    Returns:
        Dictionary with 'pdf' and 'word' keys (default both True)
    """
    config = load_config()
    formats = config.get('output_formats', {'pdf': True, 'word': True})
    # Ensure both keys exist
    if 'pdf' not in formats:
        formats['pdf'] = True
    if 'word' not in formats:
        formats['word'] = True
    return formats


def save_output_formats(pdf: bool, word: bool):
    """
    Save the output format preferences.
    
    Args:
        pdf: Whether to generate PDF
        word: Whether to generate Word document
    """
    config = load_config()
    config['output_formats'] = {'pdf': pdf, 'word': word}
    save_config(config)


def save_all_settings(api_key: Optional[str], input_folder: str, output_folder: str, 
                     pdf: bool, word: bool, remember_api_key: bool):
    """
    Save all settings at once.
    
    Args:
        api_key: API key to save (or None to not save)
        input_folder: Last used INPUT folder
        output_folder: Last used OUTPUT folder
        pdf: Generate PDF option
        word: Generate Word document option
        remember_api_key: Whether to remember the API key
    """
    config = {
        'last_input_folder': input_folder,
        'last_output_folder': output_folder,
        'output_formats': {'pdf': pdf, 'word': word}
    }
    
    if remember_api_key and api_key:
        config['api_key'] = api_key
    elif not remember_api_key:
        # Remove API key if user unchecked remember option
        pass  # Don't include it in config
    
    save_config(config)
