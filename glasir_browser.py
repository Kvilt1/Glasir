#!/usr/bin/env python3
"""
Glasir Browser Module - Playwright-based browser automation

This module handles browser-based login operations for the Glasir system using Playwright.

Author: Claude AI Assistant
"""

import asyncio
import json
import logging
import os
import re
import argparse
from datetime import datetime

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Configure logging
logger = logging.getLogger(__name__)

# Define login flow states based on URLs
LOGIN_STATES = {
    "INITIAL": {"url_pattern": r"^https://tg\.glasir\.fo/?$"},
    "LOGIN_PAGE": {"url_pattern": r"^https://tg\.glasir\.fo/login"},
    "MICROSOFT_LOGIN": {"url_pattern": r"^https://login\.microsoftonline\.com/"},
    "ADFS_LOGIN": {"url_pattern": r"^https://adfs\.glasir\.fo/adfs/ls/"},
    "RETURN_PAGE": {"url_pattern": r"^https://tg\.glasir\.fo/auth/openid/return"},
    "FINAL_PAGE": {"url_pattern": r"^https://tg\.glasir\.fo/132n/"}
}

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

# Add timeout and retry configuration
DEFAULT_TIMEOUT = 30000  # 30 seconds
MAX_RETRIES = 3

class GlasirBrowser:
    """
    Class for handling browser-based login operations using Playwright.
    """
    
    def __init__(self, credentials=None, profile_name="default", headless=True, 
                 target_url="https://tg.glasir.fo", 
                 final_url="https://tg.glasir.fo/132n/",
                 screenshots_dir="screenshots",
                 debug_level="INFO",
                 timeout=DEFAULT_TIMEOUT):
        """
        Initialize the Glasir Browser automation.
        
        Args:
            credentials (dict): User credentials for login
            profile_name (str): Profile name to use
            headless (bool): Whether to run the browser in headless mode
            target_url (str): The initial URL to navigate to
            final_url (str): The expected final URL after successful login
            screenshots_dir (str): Directory to save screenshots
            debug_level (str): Debug level (INFO, DEBUG, TRACE, VERBOSE)
            timeout (int): Timeout in milliseconds for page operations
        """
        self.credentials = credentials
        self.profile_name = profile_name
        self.headless = headless
        self.target_url = target_url
        self.final_url = final_url
        self.timeout = timeout
        
        # Set up screenshots directory
        self.screenshots_dir = screenshots_dir
        os.makedirs(screenshots_dir, exist_ok=True)
        
        # Configure debug level
        self._configure_debug_level(debug_level)
        
        # Log initialization
        logger.debug(f"Initialized GlasirBrowser with profile: {profile_name}, headless: {headless}")
    
    def _configure_debug_level(self, level):
        """Configure logging level based on debug level string."""
        if level in DEBUG_LEVELS:
            logger.setLevel(DEBUG_LEVELS[level])
            logger.debug(f"Set debug level to {level}")
        else:
            logger.warning(f"Unknown debug level: {level}. Using INFO.")
            logger.setLevel(logging.INFO)
    
    async def determine_state(self, page):
        """Determine the current login state based on page URL."""
        current_url = page.url
        for state, info in LOGIN_STATES.items():
            if re.match(info["url_pattern"], current_url):
                return state
        return "UNKNOWN"
    
    async def handle_state_actions(self, page, state):
        """Perform actions based on the current login state."""
        logger.info(f"Current state: {state}")
        
        if state == "INITIAL" or state == "LOGIN_PAGE":
            # Just wait for redirect to Microsoft login
            pass
        
        elif state == "MICROSOFT_LOGIN":
            # Handle Microsoft login form
            try:
                # Take a screenshot for debugging
                screenshot_path = os.path.join(self.screenshots_dir, f"{self.profile_name}_microsoft_login.png")
                await page.screenshot(path=screenshot_path)
                logger.debug(f"Saved Microsoft login screenshot to {screenshot_path}")
                
                # Wait for the page to stabilize
                await page.wait_for_load_state("networkidle", timeout=self.timeout)
                
                # Check if email input is available
                email_input = await page.wait_for_selector('input[type="email"]', timeout=self.timeout, state='visible')
                if email_input:
                    logger.info(f"Filling in email address: {self.credentials['email']}")
                    await email_input.fill(self.credentials["email"])
                    
                    # Find and click the Next button
                    next_button = await page.wait_for_selector('input[type="submit"]', timeout=self.timeout)
                    if next_button:
                        await next_button.click()
                        # Wait for navigation to complete after clicking Next
                        await page.wait_for_load_state("networkidle", timeout=self.timeout)
                    else:
                        logger.warning("Next button not found after entering email")
                else:
                    logger.warning("Email input field not found")
                
                # Wait for password field to appear
                await page.wait_for_timeout(1000)  # Small delay to ensure page updates
                
                # Check if password input is available on this page
                password_input = await page.wait_for_selector('input[type="password"]', timeout=self.timeout, state='visible')
                if password_input:
                    logger.info("Filling in password on Microsoft page")
                    await password_input.fill(self.credentials["password"])
                    
                    # Take another screenshot for debugging
                    screenshot_path = os.path.join(self.screenshots_dir, f"{self.profile_name}_microsoft_password.png")
                    await page.screenshot(path=screenshot_path)
                    
                    # Look for submit button or press Enter
                    submit_button = await page.query_selector('input[type="submit"]')
                    if submit_button:
                        await submit_button.click()
                    else:
                        await page.press('input[type="password"]', 'Enter')
                    
                    # Wait for navigation to complete after entering password
                    await page.wait_for_load_state("networkidle", timeout=self.timeout)
                else:
                    logger.warning("Password input field not found")
                    
                # Check for "Stay signed in?" prompt and handle it
                try:
                    stay_signed_in = await page.wait_for_selector('#idSIButton9', timeout=5000, state='visible')
                    if stay_signed_in:
                        logger.info("Clicking 'Yes' on Stay signed in prompt")
                        await stay_signed_in.click()
                except Exception as e:
                    logger.debug(f"No 'Stay signed in' prompt found (this is often normal): {str(e)}")
                    
            except Exception as e:
                logger.warning(f"Error on Microsoft login page: {str(e)}")
                # Take error screenshot
                screenshot_path = os.path.join(self.screenshots_dir, f"{self.profile_name}_microsoft_error.png")
                await page.screenshot(path=screenshot_path)
        
        elif state == "ADFS_LOGIN":
            # Handle ADFS login form
            try:
                # Check if password field is available
                password_input = await page.query_selector('input[type="password"]')
                if password_input:
                    # First check for the "Keep me signed in" checkbox and ensure it's checked
                    logger.info("Ensuring 'Keep me signed in' checkbox is checked")
                    
                    # Check if the checkbox exists using the specific ID
                    checkbox_exists = await page.is_visible("#kmsiInput")
                    
                    if checkbox_exists:
                        # Check if the checkbox is already checked
                        is_checked = await page.is_checked("#kmsiInput")
                        
                        if not is_checked:
                            logger.info("Checking 'Keep me signed in' checkbox")
                            await page.check("#kmsiInput")
                        else:
                            logger.info("'Keep me signed in' checkbox is already checked")
                    else:
                        # Fall back to the older method if the specific ID isn't found
                        checkbox = await page.query_selector('input[type="checkbox"][name="Kmsi"]')
                        if checkbox:
                            is_checked = await checkbox.is_checked()
                            if not is_checked:
                                logger.info("Clicking 'Keep me signed in' checkbox (fallback method)")
                                await checkbox.click()
                    
                    # Now fill in the password
                    logger.info("Filling in password on ADFS page")
                    await page.fill('input[type="password"]', self.credentials["password"])
                    
                    # Try to find the submit button
                    submit_button = await page.query_selector('#submitButton, span.submit, input[type="submit"]')
                    if submit_button:
                        logger.info("Clicking sign in button")
                        await submit_button.click()
                    else:
                        # If no submit button found, press Enter
                        logger.info("No submit button found, pressing Enter on password field")
                        await page.press('input[type="password"]', 'Enter')
            except Exception as e:
                logger.warning(f"Error on ADFS login page: {str(e)}")
        
        elif state == "FINAL_PAGE":
            logger.info("Reached the final destination page")
        
        # Wait for any navigation to complete
        try:
            await page.wait_for_load_state("networkidle", timeout=self.timeout)
        except Exception as e:
            logger.debug(f"Wait for load state error (can be normal): {str(e)}")
    
    async def login(self):
        """
        Perform login using Playwright browser automation.
        Returns a tuple of (success, session_data) where success is a boolean and
        session_data contains cookies and storage data if successful.
        """
        logger.info(f"Starting browser-based login for profile: {self.profile_name}")
        
        if not self.credentials:
            logger.error("Cannot login with Playwright: No credentials available")
            return False, None
        
        # Check if email and password are available
        email = self.credentials.get("email", "")
        password = self.credentials.get("password", "")
        if not email or not password:
            logger.error("Email or password is empty")
            return False, None
        
        # Track cookies and other session data
        collected_cookies = []
        collected_storage = []
        redirections = []
        session_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "targetUrl": self.final_url,
            "cookies": [],
            "localStorage": [],
            "sessionStorage": [],
            "redirections": [],
            "requestHeaders": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Accept-Language": "en-US,en;q=0.9"
            }
        }
        
        # Configure retry mechanism
        retry_count = 0
        max_retries = MAX_RETRIES
        
        while retry_count <= max_retries:
            if retry_count > 0:
                logger.info(f"Retry attempt {retry_count} of {max_retries}")
                
            try:
                async with async_playwright() as p:
                    # Create a persistent browser context to maintain login state
                    user_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                                "browser_data", self.profile_name)
                    os.makedirs(user_data_dir, exist_ok=True)
                    
                    browser = await p.chromium.launch(
                        headless=self.headless,
                        args=['--disable-blink-features=AutomationControlled']  # Avoid detection
                    )
                    
                    context = await browser.new_context(
                        viewport={"width": 1280, "height": 800},
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                        locale="en-US",
                        timezone_id="Europe/London"
                    )
                    
                    # Set default timeout for all operations
                    context.set_default_timeout(self.timeout)
                    
                    page = await context.new_page()
                    
                    # Set up redirection logging
                    async def log_navigation(response):
                        if response.status >= 300 and response.status < 400:
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                            from_url = response.request.url
                            to_url = response.headers.get("location", "unknown")
                            redirect_info = {
                                "timestamp": timestamp,
                                "from": from_url,
                                "to": to_url,
                                "status": response.status
                            }
                            redirections.append(redirect_info)
                            logger.info(f"Navigation: {from_url} -> {to_url} (Status: {response.status})")
                    
                    # Set up URL change logging
                    async def log_url_change(url):
                        logger.info(f"URL changed to: {url}")
                    
                    # Listen for events
                    page.on("response", log_navigation)
                    page.on("framenavigated", lambda frame: asyncio.create_task(log_url_change(frame.url)) if frame is page.main_frame else None)
                    
                    # Take initial screenshot
                    screenshot_path = os.path.join(self.screenshots_dir, f"{self.profile_name}_start.png")
                    await page.screenshot(path=screenshot_path)
                    
                    # Navigate to the target URL
                    logger.info(f"Navigating to {self.target_url}")
                    await page.goto(self.target_url, wait_until="domcontentloaded", timeout=self.timeout)
                    
                    # State-based login flow
                    max_state_transitions = 30
                    current_transitions = 0
                    last_state = None
                    max_same_state = 5  # Maximum times to try if state doesn't change
                    same_state_count = 0
                    
                    while current_transitions < max_state_transitions:
                        # Determine current state
                        current_state = await self.determine_state(page)
                        
                        # If we've reached the final page, we're done
                        if current_state == "FINAL_PAGE" or self.final_url in page.url:
                            logger.info("Reached final destination URL")
                            break
                        
                        # If state hasn't changed, increment counter
                        if current_state == last_state:
                            same_state_count += 1
                            if same_state_count >= max_same_state:
                                logger.warning(f"State '{current_state}' has not changed for {max_same_state} iterations, attempting recovery")
                                
                                # Take a debug screenshot 
                                screenshot_path = os.path.join(self.screenshots_dir, f"{self.profile_name}_stuck_{current_state}.png")
                                await page.screenshot(path=screenshot_path)
                                
                                # Try a refresh to recover
                                try:
                                    await page.reload(wait_until="domcontentloaded", timeout=self.timeout)
                                    same_state_count = 0
                                except Exception as e:
                                    logger.error(f"Failed to reload page: {str(e)}")
                                    break
                        else:
                            same_state_count = 0
                        
                        # Handle actions for current state
                        await self.handle_state_actions(page, current_state)
                        
                        # Update last state
                        last_state = current_state
                        current_transitions += 1
                        
                        # Wait for navigation to complete
                        try:
                            await page.wait_for_load_state("networkidle", timeout=5000)
                        except Exception:
                            pass  # Ignore timeout errors
                    
                    # Wait a moment to ensure the page is fully loaded
                    await page.wait_for_timeout(3000)
                    
                    # Check if we reached a success indicator in the URL
                    success = self.final_url in page.url or "/132n/" in page.url
                    
                    if success:
                        logger.info("Login successful!")
                        
                        # Take final screenshot
                        screenshot_path = os.path.join(self.screenshots_dir, f"{self.profile_name}_success.png")
                        await page.screenshot(path=screenshot_path)
                        
                        # Collect cookies and other session data
                        collected_cookies = await context.cookies()
                        
                        # Try to collect local/session storage
                        try:
                            local_storage = await page.evaluate("() => Object.entries(localStorage)")
                            session_storage = await page.evaluate("() => Object.entries(sessionStorage)")
                            collected_storage = {
                                "localStorage": local_storage,
                                "sessionStorage": session_storage
                            }
                        except Exception as e:
                            logger.warning(f"Error collecting storage: {str(e)}")
                        
                        # Wait a bit to make sure everything is loaded
                        await page.wait_for_timeout(3000)
                        
                        # Save collected data
                        session_data["finalUrl"] = page.url
                        session_data["pageTitle"] = await page.title()
                        session_data["cookies"] = collected_cookies
                        session_data["localStorage"] = collected_storage.get("localStorage", [])
                        session_data["sessionStorage"] = collected_storage.get("sessionStorage", [])
                        session_data["redirections"] = redirections
                        session_data["last_access_success"] = datetime.now().timestamp()
                        
                        await browser.close()
                        return True, session_data
                    else:
                        logger.warning(f"Failed to reach final destination. Current URL: {page.url}")
                        # Take error screenshot
                        screenshot_path = os.path.join(self.screenshots_dir, f"{self.profile_name}_error.png")
                        await page.screenshot(path=screenshot_path)
                        await browser.close()
                        
                        # Increment retry counter and try again if allowed
                        retry_count += 1
                        if retry_count <= max_retries:
                            logger.info(f"Will retry login ({retry_count}/{max_retries})")
                            await asyncio.sleep(2)  # Wait a bit before retrying
                            continue
                        else:
                            logger.error(f"Maximum retries ({max_retries}) exceeded")
                            return False, None
                    
            except Exception as e:
                logger.error(f"Error during browser-based login: {str(e)}")
                # Take error screenshot if possible
                try:
                    screenshot_path = os.path.join(self.screenshots_dir, f"{self.profile_name}_exception.png")
                    await page.screenshot(path=screenshot_path)
                except Exception:
                    pass
                
                # Increment retry counter and try again if allowed
                retry_count += 1
                if retry_count <= max_retries:
                    logger.info(f"Will retry login after error ({retry_count}/{max_retries})")
                    await asyncio.sleep(2)  # Wait a bit before retrying
                    continue
                else:
                    logger.error(f"Maximum retries ({max_retries}) exceeded")
                    return False, None
        
        # If we get here, all retries failed
        return False, None

async def main():
    """
    Main function for standalone execution of the browser module.
    """
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Glasir Browser Module - Standalone Execution')
    parser.add_argument('--profile', type=str, default='default', help='Profile name to use')
    parser.add_argument('--username', type=str, help='Username for login')
    parser.add_argument('--password', type=str, help='Password for login')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--visible', dest='headless', action='store_false', help='Run browser in visible mode')
    parser.add_argument('--target-url', type=str, default='https://tg.glasir.fo', help='Target URL')
    parser.add_argument('--final-url', type=str, default='https://tg.glasir.fo/132n/', help='Expected final URL')
    parser.add_argument('--screenshots', type=str, default='screenshots', help='Directory for screenshots')
    parser.add_argument('--debug-level', type=str, choices=DEBUG_LEVELS.keys(), default='INFO', help='Debug level')
    parser.set_defaults(headless=True)
    
    args = parser.parse_args()
    
    # Configure logging
    log_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    handlers = [
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', 'glasir_browser.log'))
    ]
    
    logging.basicConfig(
        level=DEBUG_LEVELS[args.debug_level],
        format=log_format,
        handlers=handlers
    )
    
    # Create directories if they don't exist
    os.makedirs('logs', exist_ok=True)
    os.makedirs(args.screenshots, exist_ok=True)
    
    # Prepare credentials
    credentials = None
    if args.username and args.password:
        credentials = {
            'username': args.username,
            'password': args.password
        }
    else:
        # If credentials not provided, try to load from file
        try:
            profile_dir = os.path.join('data', 'profiles', args.profile)
            credentials_file = os.path.join(profile_dir, 'credentials.json')
            if os.path.exists(credentials_file):
                with open(credentials_file, 'r') as f:
                    credentials = json.load(f)
                logger.info(f"Loaded credentials from {credentials_file}")
            else:
                logger.error(f"Credentials file not found: {credentials_file}")
                return
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            return
    
    # Initialize browser and perform login
    try:
        logger.info(f"Starting browser login with profile: {args.profile}")
        browser = GlasirBrowser(
            credentials=credentials,
            profile_name=args.profile,
            headless=args.headless,
            target_url=args.target_url,
            final_url=args.final_url,
            screenshots_dir=args.screenshots,
            debug_level=args.debug_level
        )
        
        login_result = await browser.login()
        
        if login_result:
            logger.info("Login successful")
            cookies, headers = login_result
            
            # Save session data for reference
            session_dir = os.path.join('data', 'profiles', args.profile)
            os.makedirs(session_dir, exist_ok=True)
            
            session_data = {
                'cookies': cookies,
                'headers': headers,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(os.path.join(session_dir, 'session.json'), 'w') as f:
                json.dump(session_data, f, indent=2)
            
            logger.info(f"Session data saved to {os.path.join(session_dir, 'session.json')}")
        else:
            logger.error("Login failed")
    
    except Exception as e:
        logger.exception(f"Error during browser login: {e}")


if __name__ == "__main__":
    # Run the main function when executed directly
    asyncio.run(main()) 