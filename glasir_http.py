#!/usr/bin/env python3
"""
Glasir HTTP Module - Requests-based HTTP interactions

This module handles direct HTTP requests for the Glasir system login using the requests library.

Author: Claude AI Assistant
"""

import json
import logging
import os
import argparse
from datetime import datetime

import requests

# Configure logging
logger = logging.getLogger(__name__)

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

class GlasirHTTP:
    """
    Class for handling HTTP request-based interactions with Glasir.
    """
    
    def __init__(self, target_url="https://tg.glasir.fo", 
                 final_url="https://tg.glasir.fo/132n/",
                 output_dir="output",
                 debug_level="INFO"):
        """
        Initialize the Glasir HTTP request handler.
        
        Args:
            target_url (str): The initial URL to navigate to
            final_url (str): The expected final URL after successful login
            output_dir (str): Directory to save output files
            debug_level (str): Debug level (INFO, DEBUG, TRACE, VERBOSE)
        """
        self.target_url = target_url
        self.final_url = final_url
        self.output_dir = output_dir
        
        # Make sure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Configure debug level
        self._configure_debug_level(debug_level)
        
        # Log initialization
        logger.debug(f"Initialized GlasirHTTP with target: {target_url}, final: {final_url}")
    
    def _configure_debug_level(self, level):
        """Configure logging level based on debug level string."""
        if level in DEBUG_LEVELS:
            logger.setLevel(DEBUG_LEVELS[level])
            logger.debug(f"Set debug level to {level}")
        else:
            logger.warning(f"Unknown debug level: {level}. Using INFO.")
            logger.setLevel(logging.INFO)
    
    def check_session_validity(self, session_data):
        """
        Check if the session data is valid and not expired.
        
        Args:
            session_data (dict): The session data containing cookies
            
        Returns:
            tuple: (is_valid, reason) where is_valid is a boolean and reason is a string
        """
        # Check if session data exists
        if not session_data:
            return False, "No session data found"
        
        # Check if ESTSAUTHPERSISTENT cookie exists and not expired
        auth_cookie_found = False
        for cookie in session_data.get("cookies", []):
            if cookie["name"] == "ESTSAUTHPERSISTENT":
                auth_cookie_found = True
                if cookie["expires"] != -1:
                    current_timestamp = datetime.now().timestamp()
                    if cookie["expires"] < current_timestamp:
                        return False, "Authentication cookie expired"
                break
        
        if not auth_cookie_found:
            return False, "Authentication cookie not found"
        
        # Check if we've successfully accessed the target URL in the last hour
        last_access = session_data.get("last_access_success", 0)
        if last_access > 0:
            current_time = datetime.now().timestamp()
            if current_time - last_access < 3600:  # Less than one hour
                logger.info("Session was successfully used in the last hour, skipping validation")
                return True, "Recent successful access"
        
        # Perform preflight request to check session validity
        try:
            session = requests.Session()
            # Set cookies from session data
            for cookie in session_data.get("cookies", []):
                session.cookies.set(
                    name=cookie["name"],
                    value=cookie["value"],
                    domain=cookie["domain"],
                    path=cookie["path"]
                )
            
            # Set headers
            session.headers.update(session_data.get("requestHeaders", {}))
            
            # Try accessing the target URL without following redirects
            logger.info("Performing preflight request to validate session")
            response = session.get(self.final_url, allow_redirects=False)
            
            # Check if we're still authenticated
            if response.status_code == 200:
                return True, "Session is valid"
            elif response.status_code == 302:
                redirect_url = response.headers.get("Location", "")
                if "/login" in redirect_url:
                    return False, "Session redirected to login page"
                else:
                    logger.warning(f"Unexpected redirect to: {redirect_url}")
                    return False, f"Unexpected redirect to: {redirect_url}"
            else:
                return False, f"Unexpected status code: {response.status_code}"
        
        except Exception as e:
            return False, f"Error checking session: {str(e)}"
    
    def login(self, session_data, profile_name="default"):
        """
        Attempt to login using stored session data and HTTP requests.
        
        Args:
            session_data (dict): The session data containing cookies and headers
            profile_name (str): Name of the profile, used for saving output files
        
        Returns:
            tuple or bool: Either (cookies_list, headers_dict) on success, or False on failure
        """
        if not session_data:
            logger.error("Cannot login with requests: No session data available")
            return False
        
        try:
            # Create a session with cookies from session data
            session = requests.Session()
            
            # Add cookies to the session
            for cookie in session_data["cookies"]:
                cookie_dict = {
                    'name': cookie['name'],
                    'value': cookie['value'],
                    'domain': cookie['domain'],
                    'path': cookie['path']
                }
                session.cookies.set(**cookie_dict)
            
            # Set common headers if they exist
            if "requestHeaders" in session_data:
                session.headers.update(session_data["requestHeaders"])
            
            # Try to access the target URL
            logger.info(f"Attempting to access target URL with requests: {self.final_url}")
            response = session.get(self.final_url, allow_redirects=True)
            
            # Log information about the response
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Final URL: {response.url}")
            
            # Check if we got a successful response
            if response.status_code == 200 and self.final_url in response.url:
                logger.info("Successfully accessed the target page")
                
                # Save the response details
                self._save_response_details(response, profile_name)
                
                # Extract cookies from the response in a serializable format
                cookies_list = []
                for cookie in session.cookies:
                    cookies_list.append({
                        'name': cookie.name,
                        'value': cookie.value,
                        'domain': cookie.domain,
                        'path': cookie.path,
                        'expires': cookie.expires,
                        'secure': cookie.secure
                    })
                
                # Extract headers in a serializable format
                headers_dict = dict(response.headers)
                
                return cookies_list, headers_dict
            else:
                logger.warning(f"Request login failed. Status: {response.status_code}, URL: {response.url}")
                return False
                
        except Exception as e:
            logger.error(f"Error during request login: {str(e)}")
            return False
    
    def _save_response_details(self, response, profile_name="default"):
        """
        Save response details to a file for inspection.
        
        Args:
            response (Response): The requests Response object
            profile_name (str): The profile name (for file naming)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{profile_name}_{timestamp}_response.json"
        filepath = os.path.join(self.output_dir, filename)
        
        # Prepare response data for saving
        data = {
            "url": response.url,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "cookies": {k: v for k, v in response.cookies.items()},
            "content_length": len(response.content),
            "content_type": response.headers.get('Content-Type', 'unknown'),
            "elapsed": str(response.elapsed),
            "encoding": response.encoding,
            "timestamp": timestamp
        }
        
        # For text responses, include a preview (limited to avoid huge files)
        if 'text/html' in response.headers.get('Content-Type', ''):
            # Save content preview (first 1000 chars)
            data["content_preview"] = response.text[:1000] + ("..." if len(response.text) > 1000 else "")
            
            # If in VERBOSE or TRACE mode, save full content
            if logger.level <= 5:  # TRACE or VERBOSE
                content_filename = f"{profile_name}_{timestamp}_content.html"
                content_filepath = os.path.join(self.output_dir, content_filename)
                with open(content_filepath, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                logger.trace(f"Saved full content to {content_filepath}")
        
        # Save response details
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.debug(f"Saved response details to {filepath}")
        return filepath


def main():
    """
    Main function for standalone execution of the HTTP module.
    """
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Glasir HTTP Module - Standalone Execution')
    parser.add_argument('--session-file', type=str, help='Path to the session data file')
    parser.add_argument('--profile', type=str, default='default', help='Profile name to use')
    parser.add_argument('--target-url', type=str, default='https://tg.glasir.fo', help='Target URL')
    parser.add_argument('--final-url', type=str, default='https://tg.glasir.fo/132n/', help='Expected final URL')
    parser.add_argument('--output-dir', type=str, default='output', help='Directory for output files')
    parser.add_argument('--debug-level', type=str, choices=DEBUG_LEVELS.keys(), default='INFO', help='Debug level')
    parser.add_argument('--check-only', action='store_true', help='Only check session validity, don\'t login')
    parser.add_argument('--no-save', action='store_true', help='Don\'t save response details')
    
    args = parser.parse_args()
    
    # Configure logging
    log_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    handlers = [
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', 'glasir_http.log'))
    ]
    
    logging.basicConfig(
        level=DEBUG_LEVELS[args.debug_level],
        format=log_format,
        handlers=handlers
    )
    
    # Create directories if they don't exist
    os.makedirs('logs', exist_ok=True)
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load session data
    session_data = None
    session_file = args.session_file
    
    if not session_file and args.profile:
        # Try to load session data from default location
        profile_dir = os.path.join('data', 'profiles', args.profile)
        default_session_file = os.path.join(profile_dir, 'session.json')
        if os.path.exists(default_session_file):
            session_file = default_session_file
    
    if session_file:
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            logger.info(f"Loaded session data from: {session_file}")
        except Exception as e:
            logger.error(f"Failed to load session data: {e}")
            return
    else:
        logger.error("No session file specified and couldn't find default session file")
        return
    
    # Initialize HTTP handler
    http_handler = GlasirHTTP(
        target_url=args.target_url,
        final_url=args.final_url,
        output_dir=args.output_dir,
        debug_level=args.debug_level
    )
    
    try:
        # Check if only validation is requested
        if args.check_only:
            logger.info("Checking session validity...")
            is_valid, reason = http_handler.check_session_validity(session_data)
            if is_valid:
                logger.info("Session is valid")
            else:
                logger.warning(f"Session is invalid: {reason}")
            return
        
        # Perform login with session data
        logger.info(f"Attempting login with session data for profile: {args.profile}")
        login_result = http_handler.login(session_data, args.profile)
        
        if login_result:
            logger.info("Login successful")
            cookies, headers = login_result
            
            # Save updated session data
            if not args.no_save:
                profile_dir = os.path.join('data', 'profiles', args.profile)
                os.makedirs(profile_dir, exist_ok=True)
                
                updated_session_data = {
                    'cookies': cookies,
                    'headers': headers,
                    'timestamp': datetime.now().isoformat()
                }
                
                with open(os.path.join(profile_dir, 'session.json'), 'w') as f:
                    json.dump(updated_session_data, f, indent=2)
                
                logger.info(f"Updated session data saved to {os.path.join(profile_dir, 'session.json')}")
        else:
            logger.error("Login failed")
    
    except Exception as e:
        logger.exception(f"Error during HTTP login: {e}")


if __name__ == "__main__":
    # Run the main function when executed directly
    main() 