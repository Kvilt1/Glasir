#!/usr/bin/env python3
"""
Glasir Schedule Module - Export class schedules

This module provides functionality to extract and export class schedules
from the Glasir system.

Author: Claude AI Assistant
"""

import asyncio
import csv
import json
import logging
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

# Import required Playwright modules
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Configure logging
logger = logging.getLogger(__name__)

class GlasirSchedule:
    """
    Class for handling class schedule operations from the Glasir system.
    """
    
    def __init__(self, session, output_dir="schedules", debug_level="INFO"):
        """
        Initialize the Glasir Schedule handler.
        
        Args:
            session: The GlasirSession object with authentication information
            output_dir (str): Directory to save exported schedules
            debug_level (str): Debug level for logging
        """
        self.session = session
        self.output_dir = output_dir
        self.debug_level = debug_level
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Parse the target URL from the session data
        self.target_url = getattr(session.http, 'final_url', "https://tg.glasir.fo/132n/")
        
        # Set up class information regex patterns
        self.class_pattern = re.compile(r'([a-zæøåðýí]+)-([A-C])-(\d+)-(\d+)-(\d+[a-zæøåðýí]*)')
        self.teacher_pattern = re.compile(r'([A-ZÆØÅÐÝÍ]{2,5})\s+st\.\s+(\d+)')
        
        logger.info(f"Initialized GlasirSchedule with output directory: {output_dir}")
    
    async def extract_schedule(self, browser_context=None, close_browser=True):
        """
        Extract the class schedule from the Glasir system.
        
        Args:
            browser_context: Optional existing browser context to use
            close_browser: Whether to close the browser after extraction
            
        Returns:
            dict: The extracted schedule data
        """
        logger.info("Starting schedule extraction")
        
        should_close_playwright = False
        browser = None
        playwright = None
        
        try:
            # Initialize Playwright if no browser context is provided
            if not browser_context:
                playwright = await async_playwright().start()
                should_close_playwright = True
                
                # Create browser and context
                browser = await playwright.chromium.launch(headless=True)
                browser_context = await browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                )
            
            # Create a new page
            page = await browser_context.new_page()
            
            # Navigate to the target URL and apply session cookies
            if self.session and hasattr(self.session, 'session_data') and self.session.session_data:
                logger.info("Using existing session cookies")
                
                # Add cookies from session data
                cookies = self.session.session_data.get("cookies", [])
                if cookies:
                    # Ensure we have all required cookie fields
                    processed_cookies = []
                    for cookie in cookies:
                        if isinstance(cookie, dict) and 'name' in cookie and 'value' in cookie:
                            cookie_dict = {
                                'name': cookie['name'],
                                'value': cookie['value'],
                                'domain': cookie.get('domain', '.glasir.fo'),
                                'path': cookie.get('path', '/')
                            }
                            processed_cookies.append(cookie_dict)
                    
                    # Add cookies to browser context
                    if processed_cookies:
                        await browser_context.add_cookies(processed_cookies)
                        logger.info(f"Added {len(processed_cookies)} cookies to browser")
                    else:
                        logger.warning("No valid cookies found in session data")
                else:
                    logger.warning("No cookies found in session data")
            else:
                logger.warning("No valid session data available")
            
            # Navigate to the schedule page
            logger.info(f"Navigating to {self.target_url}")
            await page.goto(self.target_url)
            
            # Wait for the schedule table to load
            logger.info("Waiting for schedule table to load")
            try:
                await page.wait_for_selector('table.time_8_16', timeout=30000)
            except PlaywrightTimeoutError:
                # Take a screenshot of the error state
                error_screenshot_path = os.path.join(self.output_dir, "error_screenshot.png")
                await page.screenshot(path=error_screenshot_path)
                logger.error(f"Timed out waiting for schedule table. Saved error screenshot to {error_screenshot_path}")
                
                # Check if we're on a login page
                if await page.get_by_text("Login").count() > 0 or "login" in page.url.lower():
                    logger.error("Login required. Session cookies may be invalid.")
                    raise Exception("Login required. The session may have expired.")
                
                raise Exception("Could not find schedule table on the page. Page may have changed or session expired.")
            
            # Extract the schedule data
            logger.info("Extracting schedule data")
            schedule_data = await self._extract_schedule_data(page)
            
            # Take a screenshot of the schedule for reference
            screenshot_path = os.path.join(self.output_dir, "schedule_screenshot.png")
            await page.screenshot(path=screenshot_path)
            logger.info(f"Saved schedule screenshot to {screenshot_path}")
            
            return schedule_data
            
        except Exception as e:
            logger.error(f"Error extracting schedule: {str(e)}")
            raise
        
        finally:
            # Clean up resources
            if close_browser and browser:
                try:
                    await browser.close()
                    logger.info("Browser closed")
                except Exception as e:
                    logger.error(f"Error closing browser: {str(e)}")
                
                if should_close_playwright and playwright:
                    try:
                        await playwright.stop()
                        logger.info("Playwright stopped")
                    except Exception as e:
                        logger.error(f"Error stopping playwright: {str(e)}")
    
    async def _extract_schedule_data(self, page):
        """
        Extract schedule data from the page.
        
        Args:
            page: The Playwright page object
            
        Returns:
            dict: The extracted schedule data
        """
        # Extract the current week information
        week_info = await page.evaluate('''
            () => {
                const weekElement = document.querySelector('div.uge');
                return weekElement ? weekElement.textContent.trim() : '';
            }
        ''')
        
        # Extract the schedule table
        schedule_rows = await page.evaluate('''
            () => {
                const rows = [];
                const table = document.querySelector('table.time_8_16');
                if (!table) return rows;
                
                const trs = table.querySelectorAll('tr');
                for (let i = 0; i < trs.length; i++) {
                    const tr = trs[i];
                    const cells = [];
                    const tds = tr.querySelectorAll('td');
                    
                    for (let j = 0; j < tds.length; j++) {
                        const td = tds[j];
                        cells.push({
                            text: td.textContent.trim(),
                            className: td.className,
                            html: td.innerHTML,
                            style: td.getAttribute('style')
                        });
                    }
                    
                    if (cells.length > 0) {
                        rows.push(cells);
                    }
                }
                
                return rows;
            }
        ''')
        
        # Extract specific class information (e.g., for classes like søg-A-22-2425-22y)
        classes = await page.evaluate('''
            () => {
                const classes = [];
                const tds = document.querySelectorAll('td[onmouseover]');
                
                for (let i = 0; i < tds.length; i++) {
                    const td = tds[i];
                    const text = td.textContent.trim();
                    const bgColor = td.style.backgroundColor;
                    const isAvailable = bgColor === 'rgb(184, 218, 255)' || !bgColor;
                    const isCancelled = bgColor === 'rgb(255, 184, 184)' || td.style.textDecoration === 'line-through';
                    
                    const classMatch = text.match(/([a-zæøåðýí]+)-([A-C])-(\d+)-(\d+)-(\d+[a-zæøåðýí]*)/);
                    if (classMatch) {
                        const teacherMatch = text.match(/([A-ZÆØÅÐÝÍ]{2,5})\s+st\.\s+(\d+)/);
                        classes.push({
                            fullText: text,
                            subject: classMatch[1],
                            level: classMatch[2],
                            classId: classMatch[5],
                            teacher: teacherMatch ? teacherMatch[1] : null,
                            room: teacherMatch ? teacherMatch[2] : null,
                            isAvailable: isAvailable,
                            isCancelled: isCancelled,
                            dayIndex: Math.floor(i / 10), // Approximate day index
                            timeSlot: i % 10 // Approximate time slot
                        });
                    }
                }
                
                return classes;
            }
        ''')
        
        # Format the data
        schedule_data = {
            'week_info': week_info,
            'raw_rows': schedule_rows,
            'classes': classes,
            'extracted_at': datetime.now().isoformat()
        }
        
        return schedule_data
    
    async def export_schedule(self, format='all'):
        """
        Export the class schedule to various formats.
        
        Args:
            format (str): The format to export to ('json', 'csv', 'excel', 'ical', or 'all')
            
        Returns:
            dict: Paths to the exported files
        """
        logger.info(f"Exporting schedule to format: {format}")
        
        # Extract the schedule data
        schedule_data = await self.extract_schedule()
        
        # Create timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Define base filename
        base_filename = f"glasir_schedule_{timestamp}"
        
        # Initialize paths dictionary
        paths = {}
        
        # Export to JSON
        if format in ['json', 'all']:
            json_path = os.path.join(self.output_dir, f"{base_filename}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(schedule_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Exported schedule to JSON: {json_path}")
            paths['json'] = json_path
        
        # Export to CSV
        if format in ['csv', 'all'] and schedule_data.get('classes'):
            csv_path = os.path.join(self.output_dir, f"{base_filename}.csv")
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'subject', 'level', 'classId', 'teacher', 'room',
                    'isAvailable', 'isCancelled', 'dayIndex', 'timeSlot', 'fullText'
                ])
                writer.writeheader()
                writer.writerows(schedule_data['classes'])
            logger.info(f"Exported schedule to CSV: {csv_path}")
            paths['csv'] = csv_path
        
        # Export to Excel
        if format in ['excel', 'all'] and schedule_data.get('classes'):
            try:
                excel_path = os.path.join(self.output_dir, f"{base_filename}.xlsx")
                df = pd.DataFrame(schedule_data['classes'])
                df.to_excel(excel_path, index=False)
                logger.info(f"Exported schedule to Excel: {excel_path}")
                paths['excel'] = excel_path
            except Exception as e:
                logger.error(f"Error exporting to Excel: {str(e)}")
        
        # Export to iCalendar
        if format in ['ical', 'all'] and schedule_data.get('classes'):
            try:
                from icalendar import Calendar, Event
                from datetime import date, datetime, timedelta
                
                # Create a calendar
                cal = Calendar()
                cal.add('prodid', '-//Glasir Schedule Exporter//Claude AI//EN')
                cal.add('version', '2.0')
                
                # Parse the week information to get the current week dates
                week_info = schedule_data.get('week_info', '')
                current_week = datetime.now().isocalendar()[1]  # Default to current week
                current_year = datetime.now().year
                
                # Try to extract week number from week_info
                week_match = re.search(r'(\d+)\.?\s*uge', week_info, re.IGNORECASE)
                if week_match:
                    try:
                        extracted_week = int(week_match.group(1))
                        if 1 <= extracted_week <= 53:  # Valid week numbers
                            current_week = extracted_week
                    except (ValueError, IndexError):
                        pass
                
                # Get the first day of the week (Monday)
                first_day_of_week = datetime.strptime(f'{current_year}-{current_week}-1', '%Y-%W-%w').date()
                if first_day_of_week.year < current_year:
                    # Handle the case where the week spans years
                    first_day_of_week = datetime.strptime(f'{current_year}-{current_week}-1', '%Y-%W-%w').date()
                
                # Define time slots (8:00 to 16:00)
                time_slots = [
                    "08:00", "09:00", "10:00", "11:00", "12:00", 
                    "13:00", "14:00", "15:00", "16:00", "17:00"
                ]
                
                # Duration of each class (in minutes)
                class_duration = 45
                
                # Process each class entry
                for class_entry in schedule_data['classes']:
                    if not class_entry.get('isAvailable', True) or class_entry.get('isCancelled', False):
                        continue  # Skip unavailable or cancelled classes
                    
                    # Create a new event
                    event = Event()
                    
                    # Add summary (class name)
                    event.add('summary', f"{class_entry.get('subject', 'Class')} - {class_entry.get('level', '')}")
                    
                    # Get the day index (0=Monday, 4=Friday)
                    day_index = min(max(class_entry.get('dayIndex', 0), 0), 4)
                    
                    # Get the time slot
                    time_slot = min(max(class_entry.get('timeSlot', 0), 0), len(time_slots)-1)
                    
                    # Calculate the class date and time
                    class_date = first_day_of_week + timedelta(days=day_index)
                    class_time = datetime.strptime(time_slots[time_slot], "%H:%M").time()
                    
                    # Combine date and time
                    start_datetime = datetime.combine(class_date, class_time)
                    end_datetime = start_datetime + timedelta(minutes=class_duration)
                    
                    # Add dtstart and dtend
                    event.add('dtstart', start_datetime)
                    event.add('dtend', end_datetime)
                    
                    # Create description with details
                    description = (
                        f"Subject: {class_entry.get('subject', 'N/A')}\n"
                        f"Level: {class_entry.get('level', 'N/A')}\n"
                        f"Class ID: {class_entry.get('classId', 'N/A')}\n"
                        f"Teacher: {class_entry.get('teacher', 'N/A')}\n"
                        f"Room: {class_entry.get('room', 'N/A')}"
                    )
                    event.add('description', description)
                    
                    # Add location
                    if class_entry.get('room'):
                        event.add('location', f"Room {class_entry.get('room')}")
                    
                    # Add to calendar
                    cal.add_component(event)
                
                # Save to file
                ical_path = os.path.join(self.output_dir, f"{base_filename}.ics")
                with open(ical_path, 'wb') as f:
                    f.write(cal.to_ical())
                logger.info(f"Exported schedule to iCalendar: {ical_path}")
                paths['ical'] = ical_path
            except Exception as e:
                logger.error(f"Error exporting to iCalendar: {str(e)}. This feature requires the icalendar package.")
                logger.exception("iCalendar export failed")
        
        return paths
    
    def parse_class_info(self, class_text):
        """
        Parse class information from text.
        
        Args:
            class_text (str): The text containing class information
            
        Returns:
            dict: Parsed class information
        """
        class_info = {}
        
        # Parse class code
        class_match = self.class_pattern.search(class_text)
        if class_match:
            class_info.update({
                'subject': class_match.group(1),
                'level': class_match.group(2),
                'class_id': class_match.group(5)
            })
        
        # Parse teacher and room
        teacher_match = self.teacher_pattern.search(class_text)
        if teacher_match:
            class_info.update({
                'teacher_code': teacher_match.group(1),
                'room': teacher_match.group(2)
            })
        
        # Check availability/cancellation
        if "line-through" in class_text.lower() or "rgb(255, 184, 184)" in class_text.lower():
            class_info['status'] = 'cancelled'
        else:
            class_info['status'] = 'available'
        
        return class_info

async def setup_environment():
    """
    Set up the necessary environment for schedule module.
    Creates required directories and installs dependencies if needed.
    """
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('schedules', exist_ok=True)
    
    # Check for required dependencies
    missing_deps = []
    try:
        import pandas as pd
    except ImportError:
        missing_deps.append("pandas")
    
    try:
        import icalendar
    except ImportError:
        missing_deps.append("icalendar")
    
    # Return missing dependencies
    return missing_deps

async def main():
    """
    Main function for standalone execution of the schedule module.
    """
    import argparse
    import sys
    
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Glasir Schedule Module - Standalone Execution')
    parser.add_argument('--profile', type=str, default='default', help='Profile name to use')
    parser.add_argument('--format', type=str, choices=['json', 'csv', 'excel', 'ical', 'all'], 
                        default='all', help='Export format')
    parser.add_argument('--output-dir', type=str, default='schedules', help='Output directory')
    parser.add_argument('--debug-level', type=str, default='INFO', help='Debug level')
    parser.add_argument('--install-deps', action='store_true', 
                        help='Automatically install missing dependencies')
    
    args = parser.parse_args()
    
    # Configure logging
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, args.debug_level, logging.INFO),
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(os.path.join(log_dir, 'glasir_schedule.log'))
        ]
    )
    
    print("Glasir Schedule Export Tool")
    print("==========================")
    
    # Check environment
    missing_deps = await setup_environment()
    if missing_deps:
        if args.install_deps:
            print(f"Installing missing dependencies: {', '.join(missing_deps)}")
            import subprocess
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_deps)
                print("Dependencies installed successfully")
            except subprocess.CalledProcessError:
                print("Failed to install dependencies. Please install manually: " +
                      f"pip install {' '.join(missing_deps)}")
                return 1
        else:
            print(f"Missing required dependencies: {', '.join(missing_deps)}")
            print(f"Please install them using: pip install {' '.join(missing_deps)}")
            print("Or run with --install-deps flag to install automatically")
            return 1
    
    try:
        # Import GlasirSession here to avoid errors if not available
        try:
            from glasir_main import GlasirSession
        except ImportError:
            print("Error: Could not import GlasirSession. Make sure glasir_main.py is in the same directory.")
            return 1
        
        # Initialize GlasirSession with the specified profile
        try:
            print(f"Initializing session with profile: {args.profile}")
            session = GlasirSession(profile_name=args.profile)
        except Exception as e:
            print(f"Error initializing session: {str(e)}")
            return 1
        
        # Check if we have valid session data
        has_valid_session = False
        try:
            if session.session_data:
                print("Checking existing session validity...")
                is_valid, reason = session.check_session_validity()
                if is_valid:
                    print("Existing session is valid")
                    has_valid_session = True
                else:
                    print(f"Existing session is invalid: {reason}")
        except Exception as e:
            print(f"Error checking session: {str(e)}")
        
        # Log in if necessary
        if not has_valid_session:
            print("No valid session found, logging in...")
            try:
                login_success = await session.login()
                if not login_success:
                    print("Login failed. Cannot export schedule.")
                    return 1
                print("Login successful")
            except Exception as e:
                print(f"Login error: {str(e)}")
                return 1
        
        # Create output directory
        output_dir = os.path.abspath(args.output_dir)
        os.makedirs(output_dir, exist_ok=True)
        print(f"Using output directory: {output_dir}")
        
        # Initialize GlasirSchedule with the session
        print("Initializing schedule exporter...")
        schedule = GlasirSchedule(session, output_dir=output_dir, debug_level=args.debug_level)
        
        # Export the schedule
        print(f"Exporting schedule in format: {args.format}")
        export_paths = await schedule.export_schedule(format=args.format)
        
        if export_paths:
            print("\nSchedule exported successfully:")
            for format_name, path in export_paths.items():
                print(f"  - {format_name.upper()}: {path}")
            return 0
        else:
            print("No schedule data was exported.")
            return 1
    
    except ImportError as e:
        print(f"Error importing required module: {str(e)}")
        logger.exception("Import error")
        return 1
    except Exception as e:
        print(f"Error in schedule export: {str(e)}")
        logger.exception("General error")
        return 1

if __name__ == "__main__":
    # Run the main function
    import sys
    sys.exit(asyncio.run(main())) 