"""
Help utilities for Budgy
"""
import os
import sys
from pathlib import Path


def get_user_guide_path():
    """Get the path to the USER_GUIDE.md file"""
    # Try different locations where the guide might be installed
    possible_paths = [
        # In development environment
        Path(__file__).parent.parent.parent.parent / "USER_GUIDE.md",
        # In installed package
        Path(__file__).parent.parent.parent / "USER_GUIDE.md",
        # In site-packages
        Path(sys.prefix) / "share" / "budgy" / "USER_GUIDE.md",
        # Current working directory
        Path.cwd() / "USER_GUIDE.md"
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None


def show_user_guide():
    """Display the user guide"""
    guide_path = get_user_guide_path()
    
    if not guide_path:
        print("User guide not found. Please check your installation.")
        print("You can view the guide online at:")
        print("https://github.com/PapaMarky/budgy/blob/main/USER_GUIDE.md")
        return
    
    try:
        with open(guide_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to use a pager if available
        if sys.platform != 'win32':
            try:
                import subprocess
                subprocess.run(['less'], input=content, text=True, check=True)
                return
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        
        # Fallback: print to stdout
        print(content)
        
    except Exception as e:
        print(f"Error reading user guide: {e}")
        print("You can view the guide online at:")
        print("https://github.com/PapaMarky/budgy/blob/main/USER_GUIDE.md")


def get_help_text():
    """Get brief help text with pointer to full guide"""
    return """
For complete usage instructions, see the User Guide:
  
  Command: budgy-help
  Online: https://github.com/PapaMarky/budgy/blob/main/USER_GUIDE.md

Quick Start:
  1. Download OFX files from your bank
  2. Run: budgy-viewer
  3. Click "Import Data" and select your OFX file
  4. Categorize transactions and generate reports
"""