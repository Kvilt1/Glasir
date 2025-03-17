#!/usr/bin/env python3
"""
Glasir Login System - Integrated Solution

This script provides a unified login solution for the Glasir system, intelligently
managing sessions and using either fast HTTP requests or full browser automation
depending on session validity.

Author: Claude AI Assistant
Date: Created based on existing code from tg_glasir_login.py and tg_glasir_login_requests.py
"""

import asyncio
import sys
import os
import argparse

# Import from our modular components
from glasir_main import main as cli_main

def main():
    """Parse command-line arguments and run the appropriate interface"""
    parser = argparse.ArgumentParser(description='Glasir Login System')
    parser.add_argument('--gui', action='store_true', help='Launch with graphical user interface')
    parser.add_argument('--cli', action='store_true', help='Launch with command-line interface')
    
    # Pass through other arguments to the CLI interface
    args, remaining_args = parser.parse_known_args()
    
    # Default to GUI if no interface specified
    use_gui = args.gui or (not args.cli and not args.gui)
    
    if use_gui:
        try:
            # Import GUI only when needed
            from glasir_gui import main as gui_main
            return gui_main()
        except ImportError as e:
            print(f"Error loading GUI: {e}")
            print("Falling back to CLI mode")
            return 0 if asyncio.run(cli_main(remaining_args)) else 1
    else:
        # CLI mode
        return 0 if asyncio.run(cli_main(remaining_args)) else 1

if __name__ == "__main__":
    # Run the main function with system arguments
    sys.exit(main()) 