#!/usr/bin/env python3
"""
Glasir Login System - Main Component

This module provides the main interface for the Glasir login system,
managing profiles, credentials, and sessions.

Author: Claude AI Assistant
"""

import asyncio
import json
import logging
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Import the other components
from glasir_browser import GlasirBrowser
from glasir_http import GlasirHTTP

# Define script directory and ensure it's used for relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define paths relative to script directory
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
LOGS_DIR = os.path.join(SCRIPT_DIR, "logs")
SCREENSHOTS_DIR = os.path.join(SCRIPT_DIR, "screenshots")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
PROFILES_DIR = os.path.join(DATA_DIR, "profiles")

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PROFILES_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "schedules"), exist_ok=True)

# Setup debug levels
DEBUG_LEVELS = {
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'TRACE': 5,  # Custom level between DEBUG and NOTSET
    'VERBOSE': 1  # Most detailed level
}

# Register custom log levels
logging.addLevelName(5, "TRACE")
logging.addLevelName(1, "VERBOSE")

# Define how to log at custom levels
def trace(self, message, *args, **kws):
    if self.isEnabledFor(5):
        self._log(5, message, args, **kws)

def verbose(self, message, *args, **kws):
    if self.isEnabledFor(1):
        self._log(1, message, args, **kws)

# Add custom log levels to logger class
logging.Logger.trace = trace
logging.Logger.verbose = verbose

# Configure logging with default settings (can be overridden)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(LOGS_DIR, "glasir_login.log"))
    ]
)
logger = logging.getLogger(__name__)

# Debug configuration defaults
DEFAULT_DEBUG_CONFIG = {
    "debug_level": "INFO",
    "log_format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    "log_to_file": True,
    "log_file_path": os.path.join(LOGS_DIR, "glasir_login.log"),
    "console_output": True,
    "visualize_flow": False,
    "timing_metrics": False,
    "screenshot_frequency": "ERROR_ONLY"  # NONE, ERROR_ONLY, STATE_CHANGE, ALL
}

class GlasirSession:
    """
    Main class for managing Glasir login sessions.
    
    This class handles profile management, session storage, and orchestrates
    the login process using either browser automation or direct HTTP requests.
    """
    
    def __init__(self, profile_name="default", headless=True, debug_config=None):
        """
        Initialize a Glasir session manager.
        
        Args:
            profile_name (str): The name of the profile to use
            headless (bool): Whether to use headless browsing mode
            debug_config (dict): Debug configuration options
        """
        self.profile_name = profile_name
        self.headless = headless
        
        # Initialize debug configuration
        self.debug_config = DEFAULT_DEBUG_CONFIG.copy()
        if debug_config:
            self.debug_config.update(debug_config)
        
        # Configure logging for this instance
        self._configure_logging()
        
        # Log initialization
        logger.debug(f"Initializing GlasirSession with profile: {profile_name}, headless: {headless}")
        
        # Load credentials and session data for this profile
        self.credentials = self._load_credentials()
        self.session_data = self._load_session_data()
        
        # Initialize path variables
        self.profile_path = self._get_profile_path()
        self.credentials_path = self._get_credentials_path()
        self.session_path = self._get_session_path()
        
        # Initialize HTTP handler
        self.http = GlasirHTTP(output_dir=OUTPUT_DIR, 
                          debug_level=self.debug_config.get("debug_level", "INFO"))

    def _configure_logging(self):
        """Configure logging based on debug_config"""
        # Set log level
        level = self.debug_config.get("debug_level", "INFO")
        if level in DEBUG_LEVELS:
            logger.setLevel(DEBUG_LEVELS[level])
        else:
            logger.setLevel(logging.INFO)
        
        # Build handlers list
        handlers = []
        
        # Add console handler if enabled
        if self.debug_config.get("console_output", True):
            handlers.append(logging.StreamHandler())
        
        # Add file handler if enabled
        if self.debug_config.get("log_to_file", True):
            log_file = self.debug_config.get("log_file_path", 
                                             os.path.join(LOGS_DIR, "glasir_login.log"))
            handlers.append(logging.FileHandler(log_file))
        
        # Configure log format
        log_format = self.debug_config.get("log_format", 
                                           '%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        formatter = logging.Formatter(log_format)
        
        # Apply formatter to handlers
        for handler in handlers:
            handler.setFormatter(formatter)
        
        # Remove existing handlers and add new ones
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        for handler in handlers:
            logger.addHandler(handler)
        
        logger.debug(f"Logging configured at level {level}")
        
    def _get_profile_path(self):
        """Get the path to the profile directory."""
        return os.path.join(PROFILES_DIR, f"{self.profile_name}")
    
    def _get_credentials_path(self):
        """Get the path to the credentials file for this profile."""
        profile_dir = self._get_profile_path()
        os.makedirs(profile_dir, exist_ok=True)
        return os.path.join(profile_dir, "credentials.json")
    
    def _get_session_path(self):
        """Get the path to the session data file for this profile."""
        profile_dir = self._get_profile_path()
        os.makedirs(profile_dir, exist_ok=True)
        return os.path.join(profile_dir, "session_data.json")
    
    def _load_credentials(self):
        """Load credentials from JSON file."""
        credentials_path = self._get_credentials_path()
        
        # If profile doesn't exist, check for legacy credentials
        if not os.path.exists(credentials_path):
            legacy_path = os.path.join(DATA_DIR, "credentials.json")
            if os.path.exists(legacy_path):
                logger.info(f"Profile {self.profile_name} not found, using legacy credentials")
                try:
                    with open(legacy_path, 'r') as f:
                        credentials = json.load(f)
                    
                    # Save to profile location
                    os.makedirs(os.path.dirname(credentials_path), exist_ok=True)
                    with open(credentials_path, 'w') as f:
                        json.dump(credentials, f, indent=4)
                    
                    return credentials
                except Exception as e:
                    logger.error(f"Failed to load legacy credentials: {str(e)}")
        
        # Try to load profile credentials
        try:
            with open(credentials_path, 'r') as f:
                credentials = json.load(f)
            logger.info(f"Successfully loaded credentials for profile: {self.profile_name}")
            return credentials
        except FileNotFoundError:
            logger.warning(f"No credentials found for profile: {self.profile_name}")
            return self._create_new_credentials()
        except Exception as e:
            logger.error(f"Error loading credentials: {str(e)}")
            return self._create_new_credentials()
    
    def _create_new_credentials(self):
        """Create new credentials by asking the user."""
        print(f"\nNo credentials found for profile: {self.profile_name}")
        print("Please enter your Glasir login credentials:")
        email = input("Email: ")
        password = input("Password: ")
        
        credentials = {
            "email": email,
            "password": password
        }
        
        # Save the credentials
        credentials_path = self._get_credentials_path()
        os.makedirs(os.path.dirname(credentials_path), exist_ok=True)
        
        try:
            with open(credentials_path, 'w') as f:
                json.dump(credentials, f, indent=4)
            logger.info(f"Created new credentials for profile: {self.profile_name}")
        except Exception as e:
            logger.error(f"Failed to save new credentials: {str(e)}")
        
        return credentials
    
    def _load_session_data(self):
        """Load session data if it exists."""
        session_path = self._get_session_path()
        
        # If profile session doesn't exist, check for legacy session
        if not os.path.exists(session_path):
            legacy_path = os.path.join(DATA_DIR, "session_data.json")
            if os.path.exists(legacy_path):
                logger.info(f"Profile session not found, using legacy session data")
                try:
                    with open(legacy_path, 'r') as f:
                        session_data = json.load(f)
                    
                    # Save to profile location
                    os.makedirs(os.path.dirname(session_path), exist_ok=True)
                    with open(session_path, 'w') as f:
                        json.dump(session_data, f, indent=4)
                    
                    return session_data
                except Exception as e:
                    logger.error(f"Failed to load legacy session data: {str(e)}")
                    return None
        
        # Try to load profile session data
        try:
            with open(session_path, 'r') as f:
                session_data = json.load(f)
            logger.info(f"Successfully loaded session data for profile: {self.profile_name}")
            return session_data
        except FileNotFoundError:
            logger.info(f"No session data found for profile: {self.profile_name}")
            return None
        except Exception as e:
            logger.error(f"Error loading session data: {str(e)}")
            return None
    
    def save_session_data(self, session_data):
        """Save session data to file."""
        # Add timestamp
        session_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session_data["last_access_success"] = datetime.now().timestamp()
        
        session_path = self._get_session_path()
        try:
            with open(session_path, 'w') as f:
                json.dump(session_data, f, indent=4)
            logger.info(f"Saved session data for profile: {self.profile_name}")
            self.session_data = session_data
            return True
        except Exception as e:
            logger.error(f"Failed to save session data: {str(e)}")
            return False
    
    def delete_session(self):
        """Delete current session data."""
        session_path = self._get_session_path()
        try:
            if os.path.exists(session_path):
                os.remove(session_path)
                logger.info(f"Deleted session data for profile: {self.profile_name}")
                self.session_data = None
                return True
            else:
                logger.info(f"No session data to delete for profile: {self.profile_name}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete session data: {str(e)}")
            return False
    
    def check_session_validity(self):
        """
        Check if the session data is valid and not expired.
        Returns (is_valid, reason) tuple.
        """
        if not self.session_data:
            return False, "No session data found"
            
        return self.http.check_session_validity(self.session_data)
    
    async def login(self):
        """
        Perform login using the appropriate method based on session validity.
        
        Returns:
            bool: True if login was successful, False otherwise
        """
        logger.info(f"Starting login process for profile: {self.profile_name}")
        
        # Metrics tracking
        start_time = datetime.now()
        
        # Validate current session if it exists
        if self.session_data:
            logger.debug("Session data exists, checking validity")
            is_valid, reason = self.check_session_validity()
            
            if is_valid:
                logger.info("Using existing valid session")
                # Use HTTP-based login with existing session
                result = self.http.login(self.session_data, self.profile_name)
                
                if result:
                    logger.info("HTTP login successful with existing session")
                    # Update session data with latest
                    cookies, headers = result
                    self.session_data = {
                        "cookies": cookies,
                        "headers": headers,
                        "timestamp": datetime.now().isoformat(),
                        "last_access_success": datetime.now().timestamp()
                    }
                    self.save_session_data(self.session_data)
                    
                    # Log timing metrics if enabled
                    if self.debug_config.get("timing_metrics", False):
                        end_time = datetime.now()
                        logger.info(f"Login completed in {(end_time - start_time).total_seconds():.2f} seconds")
                    
                    return True
                else:
                    logger.warning("HTTP login failed despite valid session, falling back to browser")
            else:
                logger.info(f"Session invalid: {reason}, using browser login")
        else:
            logger.info("No session data, using browser login")
        
        # If HTTP login failed or no valid session, use browser
        browser_handler = GlasirBrowser(
            credentials=self.credentials,
            profile_name=self.profile_name,
            headless=self.headless,
            screenshots_dir=SCREENSHOTS_DIR,
            debug_level=self.debug_config.get("debug_level", "INFO")
        )
        
        browser_result = await browser_handler.login()
        
        if browser_result:
            logger.info("Browser login successful")
            # Save the new session data
            cookies, headers = browser_result
            self.session_data = {
                "cookies": cookies, 
                "headers": headers,
                "timestamp": datetime.now().isoformat()
            }
            self.save_session_data(self.session_data)
            
            # Log timing metrics if enabled
            if self.debug_config.get("timing_metrics", False):
                end_time = datetime.now()
                logger.info(f"Login completed in {(end_time - start_time).total_seconds():.2f} seconds")
            
            return True
        else:
            logger.error("Browser login failed")
            
            # Log timing metrics if enabled
            if self.debug_config.get("timing_metrics", False):
                end_time = datetime.now()
                logger.info(f"Login failed after {(end_time - start_time).total_seconds():.2f} seconds")
            
            return False


def get_profile_list():
    """Get list of available profiles."""
    profiles = []
    
    # Check profiles directory
    if os.path.exists(PROFILES_DIR):
        for item in os.listdir(PROFILES_DIR):
            profile_path = os.path.join(PROFILES_DIR, item)
            if os.path.isdir(profile_path):
                cred_file = os.path.join(profile_path, "credentials.json")
                if os.path.exists(cred_file):
                    profiles.append(item)
    
    # If no profiles found, check for legacy credentials
    if not profiles:
        legacy_path = os.path.join(DATA_DIR, "credentials.json")
        if os.path.exists(legacy_path):
            profiles.append("default")
    
    return profiles


def create_new_profile():
    """Create a new profile."""
    print("\n=== Create New Profile ===")
    profile_name = input("Enter profile name (e.g., work, personal): ").strip()
    
    if not profile_name:
        print("Profile name cannot be empty")
        return create_new_profile()
    
    # Check if profile already exists
    profile_dir = os.path.join(PROFILES_DIR, profile_name)
    if os.path.exists(profile_dir):
        overwrite = input(f"Profile '{profile_name}' already exists. Overwrite? (y/n): ").lower().strip()
        if overwrite != 'y':
            return create_new_profile()
    
    # Create profile directories
    os.makedirs(profile_dir, exist_ok=True)
    
    # Create new credentials
    print("\nEnter your Glasir login credentials:")
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    
    credentials = {
        "email": email,
        "password": password
    }
    
    # Save credentials
    credentials_path = os.path.join(profile_dir, "credentials.json")
    try:
        with open(credentials_path, 'w') as f:
            json.dump(credentials, f, indent=4)
        print(f"\nCreated new profile: {profile_name}")
        return profile_name
    except Exception as e:
        print(f"Error creating profile: {str(e)}")
        return None


async def main(args=None):
    """Main function to run the script with optional command-line arguments."""
    # Parse command-line arguments if provided
    if args is None:
        parser = argparse.ArgumentParser(description='Glasir Login System - Main Module')
        parser.add_argument('--profile', type=str, default=None, help='Profile name to use')
        parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
        parser.add_argument('--visible', dest='headless', action='store_false', help='Run browser in visible mode')
        parser.add_argument('--debug-level', type=str, choices=DEBUG_LEVELS.keys(), default='INFO',
                           help='Debug level (INFO, DEBUG, TRACE, VERBOSE)')
        parser.add_argument('--create-profile', action='store_true', help='Create a new profile')
        parser.add_argument('--delete-session', action='store_true', help='Delete session for profile')
        parser.add_argument('--timing', action='store_true', help='Enable timing metrics')
        parser.add_argument('--visualize', action='store_true', help='Enable flow visualization')
        parser.add_argument('--log-file', type=str, help='Custom log file path')
        parser.add_argument('--non-interactive', action='store_true', 
                           help='Run in non-interactive mode (requires --profile)')
        parser.set_defaults(headless=True)
        
        args = parser.parse_args(args)
    
    # Configure debug settings
    debug_config = {
        "debug_level": args.debug_level,
        "timing_metrics": args.timing,
        "visualize_flow": args.visualize
    }
    
    if args.log_file:
        debug_config["log_file_path"] = args.log_file
    
    # Configure root logger with these settings
    log_level = DEBUG_LEVELS.get(args.debug_level, logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(args.log_file if args.log_file else os.path.join(LOGS_DIR, "glasir_login.log"))
        ],
        force=True
    )
    
    # Non-interactive mode
    if args.non_interactive:
        if not args.profile:
            logger.error("Non-interactive mode requires a profile to be specified")
            return False
        
        # Create a profile if requested
        if args.create_profile:
            create_new_profile(args.profile)
        
        # Create session manager
        glasir = GlasirSession(profile_name=args.profile, headless=args.headless, debug_config=debug_config)
        
        # Delete session if requested
        if args.delete_session:
            glasir.delete_session()
            return True
        
        # Perform login
        result = await glasir.login()
        if result:
            logger.info("Login successful")
            return True
        else:
            logger.error("Login failed")
            return False
    
    # Interactive mode (original functionality)
    # Clear screen and show welcome message
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("=" * 60)
    print("               GLASIR LOGIN SYSTEM")
    print("=" * 60)
    
    # Get available profiles
    profiles = get_profile_list()
    
    if not profiles:
        print("No profiles found. Let's create one.")
        profile_name = create_new_profile()
        if not profile_name:
            print("Failed to create profile. Exiting.")
            return False
    else:
        print(f"Found {len(profiles)} profile(s): {', '.join(profiles)}")
    
    # Default to using the first profile or 'default'
    current_profile = args.profile if args.profile else (profiles[0] if profiles else "default")
    headless_mode = args.headless
    
    # Main menu loop
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 60)
        print("               GLASIR LOGIN SYSTEM")
        print("=" * 60)
        
        # Create session manager with current profile
        glasir = GlasirSession(profile_name=current_profile, headless=headless_mode, debug_config=debug_config)
        
        # Check session status
        session_status = "No session"
        if glasir.session_data:
            is_valid, reason = glasir.check_session_validity()
            if is_valid:
                session_status = "Valid session"
            else:
                session_status = f"Invalid session: {reason}"
        
        # Show current status
        print(f"\nCurrent profile: {current_profile}")
        print(f"Browser mode: {'Headless' if headless_mode else 'Visible'}")
        print(f"Session status: {session_status}")
        print(f"Debug level: {args.debug_level}")
        
        # Show menu options
        print("\nOptions:")
        print("1. Login with current profile")
        print("2. Switch profile")
        print("3. Create new profile")
        print("4. Delete session for current profile")
        print(f"5. Toggle browser visibility (currently {'hidden' if headless_mode else 'visible'})")
        print("6. Export class schedule")
        print(f"7. Change debug level (currently {args.debug_level})")
        print("8. Exit")
        
        choice = input("\nSelect option (1-8): ").strip()
        
        if choice == "1":
            # Login with current profile
            print(f"\nLogging in with profile '{current_profile}'...")
            result = await glasir.login()
            
            if result:
                print("\nLogin successful!")
                input("\nPress Enter to continue...")
            else:
                print("\nLogin failed.")
                input("\nPress Enter to continue...")
        
        elif choice == "2":
            # Switch profile
            profiles = get_profile_list()
            
            if not profiles:
                print("\nNo profiles found.")
                input("\nPress Enter to continue...")
                continue
            
            print("\nAvailable profiles:")
            for i, profile in enumerate(profiles, 1):
                print(f"{i}. {profile}")
            
            try:
                profile_choice = int(input("\nSelect profile number: ").strip())
                if 1 <= profile_choice <= len(profiles):
                    current_profile = profiles[profile_choice - 1]
                    print(f"\nSwitched to profile: {current_profile}")
                else:
                    print("\nInvalid choice.")
            except ValueError:
                print("\nPlease enter a number.")
            
            input("\nPress Enter to continue...")
        
        elif choice == "3":
            # Create new profile
            new_profile = create_new_profile()
            if new_profile:
                current_profile = new_profile
            input("\nPress Enter to continue...")
        
        elif choice == "4":
            # Delete session for current profile
            confirm = input(f"\nAre you sure you want to delete the session for '{current_profile}'? (y/n): ").lower().strip()
            if confirm == 'y':
                result = glasir.delete_session()
                if result:
                    print("\nSession deleted successfully.")
                else:
                    print("\nNo session to delete or deletion failed.")
            else:
                print("\nDeletion cancelled.")
            
            input("\nPress Enter to continue...")
        
        elif choice == "5":
            # Toggle browser visibility
            headless_mode = not headless_mode
            print(f"\nBrowser will now be {'hidden' if headless_mode else 'visible'} during login.")
            input("\nPress Enter to continue...")
        
        elif choice == "6":
            # Export class schedule
            if not glasir.session_data:
                print("\nYou need to have a session. Logging in first...")
                result = await glasir.login()
                if not result:
                    print("\nLogin failed. Cannot export schedule.")
                    input("\nPress Enter to continue...")
                    continue
            
            try:
                # Check if session is valid
                is_valid, reason = glasir.check_session_validity()
                if not is_valid:
                    print(f"\nSession is not valid: {reason}. Logging in again...")
                    result = await glasir.login()
                    if not result:
                        print("\nLogin failed. Cannot export schedule.")
                        input("\nPress Enter to continue...")
                        continue
            except Exception as e:
                print(f"\nError checking session: {str(e)}. Trying to log in...")
                result = await glasir.login()
                if not result:
                    print("\nLogin failed. Cannot export schedule.")
                    input("\nPress Enter to continue...")
                    continue
            
            # Import schedule module dynamically to avoid circular imports
            try:
                # Try to import the schedule module
                from glasir_schedule import GlasirSchedule
                
                print("\n=== Export Class Schedule ===")
                print("1. Export to JSON")
                print("2. Export to CSV")
                print("3. Export to Excel")
                print("4. Export to iCalendar")
                print("5. Export to all formats")
                print("6. Back to main menu")
                
                format_choice = input("\nSelect export format (1-6): ").strip()
                if format_choice == "6":
                    continue
                    
                format_map = {
                    "1": "json",
                    "2": "csv",
                    "3": "excel",
                    "4": "ical",
                    "5": "all"
                }
                
                if format_choice not in format_map:
                    print("\nInvalid choice.")
                    input("\nPress Enter to continue...")
                    continue
                    
                format_type = format_map[format_choice]
                
                print("\nExporting schedule...")
                # Initialize GlasirSchedule with the session
                schedules_dir = os.path.join(OUTPUT_DIR, "schedules")
                os.makedirs(schedules_dir, exist_ok=True)
                
                schedule = GlasirSchedule(
                    glasir,
                    output_dir=schedules_dir,
                    debug_level=args.debug_level
                )
                
                # Export the schedule
                export_paths = await schedule.export_schedule(format=format_type)
                
                if export_paths:
                    print("\nSchedule exported successfully to:")
                    for format_name, path in export_paths.items():
                        print(f"  - {format_name.upper()}: {os.path.basename(path)}")
                else:
                    print("\nNo schedule data was exported.")
                
            except ImportError as e:
                print(f"\nError: Missing required dependencies for schedule export. {str(e)}")
                print("Run 'pip install pandas icalendar' to install required packages")
            except Exception as e:
                print(f"\nError exporting schedule: {str(e)}")
            
            input("\nPress Enter to continue...")
        
        elif choice == "7":
            # Change debug level
            print("\nAvailable debug levels:")
            for i, level in enumerate(DEBUG_LEVELS.keys(), 1):
                print(f"{i}. {level}")
            
            try:
                level_choice = int(input("\nSelect debug level: ").strip())
                if 1 <= level_choice <= len(DEBUG_LEVELS):
                    args.debug_level = list(DEBUG_LEVELS.keys())[level_choice - 1]
                    debug_config["debug_level"] = args.debug_level
                    print(f"\nDebug level set to: {args.debug_level}")
                else:
                    print("\nInvalid choice.")
            except ValueError:
                print("\nPlease enter a number.")
            
            input("\nPress Enter to continue...")
        
        elif choice == "8":
            # Exit
            print("\nExiting. Goodbye!")
            break
        
        else:
            print("\nInvalid choice. Please try again.")
            input("\nPress Enter to continue...")
    
    return True


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main()) 