#!/usr/bin/env python3
"""
Glasir Login System - GUI Module

This module provides a modern graphical user interface for the Glasir login system,
making it more user-friendly and intuitive.

Author: Claude AI Assistant
"""

import asyncio
import json
import logging
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import webbrowser
from datetime import datetime

# Import the other components
from glasir_main import GlasirSession, get_profile_list, LOGS_DIR, DEBUG_LEVELS
from glasir_browser import GlasirBrowser
from glasir_http import GlasirHTTP

# Configure logging
logger = logging.getLogger(__name__)

# Define theme colors
COLORS = {
    "primary": "#3498db",
    "secondary": "#2980b9",
    "accent": "#e74c3c",
    "background": "#f5f5f5",
    "dark_bg": "#333333",
    "text": "#2c3e50",
    "light_text": "#ecf0f1",
    "success": "#2ecc71",
    "warning": "#f39c12",
    "error": "#e74c3c"
}

class AsyncRunner:
    """Helper class to run async functions from tkinter"""
    @staticmethod
    def run_async(coro, callback=None):
        """Run an async coroutine in a thread and optionally call a callback with the result"""
        async def _run_and_store():
            try:
                result = await coro
                return result
            except Exception as e:
                logger.exception(f"Error in async operation: {e}")
                return None
                
        def _thread_target():
            result = asyncio.run(_run_and_store())
            if callback:
                # Schedule callback to run in the main thread
                if result is not None:
                    root.after(0, lambda: callback(result))
                else:
                    root.after(0, lambda: callback(False))
        
        # Get the global root window
        root = tk._default_root
        if not root:
            raise RuntimeError("Tkinter root window not created yet")
            
        thread = Thread(target=_thread_target)
        thread.daemon = True
        thread.start()
        return thread

class ProfileSelector(tk.Toplevel):
    """Dialog for selecting or creating a profile"""
    def __init__(self, parent, current_profile=None):
        super().__init__(parent)
        self.parent = parent
        self.result = None
        self.current_profile = current_profile
        
        self.title("Select Profile")
        self.geometry("400x300")
        self.configure(background=COLORS["background"])
        self.resizable(False, False)
        
        # Center the window
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        
        self.create_widgets()
        self.load_profiles()
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.wait_window(self)
    
    def create_widgets(self):
        # Frame for the profile list
        list_frame = ttk.Frame(self, padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label
        ttk.Label(list_frame, text="Select a profile:").pack(anchor=tk.W, pady=(0, 5))
        
        # Profile listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.profile_listbox = tk.Listbox(list_container, height=10, 
                                          yscrollcommand=scrollbar.set,
                                          selectbackground=COLORS["primary"],
                                          selectforeground=COLORS["light_text"])
        self.profile_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.profile_listbox.yview)
        
        # Double-click to select
        self.profile_listbox.bind("<Double-1>", lambda e: self.on_select())
        
        # Buttons frame
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill=tk.X)
        
        # Buttons
        ttk.Button(btn_frame, text="New Profile", command=self.on_new_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Profile", command=self.on_delete_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Select", command=self.on_select).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.on_cancel).pack(side=tk.RIGHT, padx=5)
    
    def load_profiles(self):
        """Load available profiles into the listbox"""
        profiles = get_profile_list()
        self.profile_listbox.delete(0, tk.END)
        
        for profile in profiles:
            self.profile_listbox.insert(tk.END, profile)
            # Select the current profile if it exists
            if profile == self.current_profile:
                self.profile_listbox.selection_set(profiles.index(profile))
    
    def on_new_profile(self):
        """Create a new profile"""
        profile_name = simpledialog.askstring("New Profile", "Enter profile name:", parent=self)
        if not profile_name:
            return
        
        # Check if profile exists
        profiles = get_profile_list()
        if profile_name in profiles:
            if not messagebox.askyesno("Profile Exists", 
                                      f"Profile '{profile_name}' already exists. Overwrite?", 
                                      parent=self):
                return
        
        # Get credentials
        email = simpledialog.askstring("Email", "Enter your email:", parent=self)
        if not email:
            return
            
        password = simpledialog.askstring("Password", "Enter your password:", 
                                         show="*", parent=self)
        if not password:
            return
        
        # Create profile directories and save credentials
        try:
            # Define profile path
            profile_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                      "data", "profiles", profile_name)
            os.makedirs(profile_dir, exist_ok=True)
            
            credentials = {
                "email": email,
                "password": password
            }
            
            # Save credentials
            with open(os.path.join(profile_dir, "credentials.json"), 'w') as f:
                json.dump(credentials, f, indent=4)
            
            messagebox.showinfo("Success", f"Profile '{profile_name}' created successfully!", parent=self)
            self.load_profiles()
            
            # Select the new profile
            profiles = get_profile_list()
            if profile_name in profiles:
                self.profile_listbox.selection_set(profiles.index(profile_name))
                
        except Exception as e:
            logger.error(f"Error creating profile: {str(e)}")
            messagebox.showerror("Error", f"Failed to create profile: {str(e)}", parent=self)
    
    def on_delete_profile(self):
        """Delete the selected profile"""
        selection = self.profile_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a profile to delete.", parent=self)
            return
        
        profile_name = self.profile_listbox.get(selection[0])
        if not messagebox.askyesno("Confirm Delete", 
                                  f"Are you sure you want to delete profile '{profile_name}'?\n\nThis action cannot be undone!", 
                                  parent=self):
            return
        
        try:
            # Define profile path
            profile_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                      "data", "profiles", profile_name)
            
            # Check if directory exists
            if os.path.exists(profile_dir):
                import shutil
                shutil.rmtree(profile_dir)
                messagebox.showinfo("Success", f"Profile '{profile_name}' deleted successfully!", parent=self)
                self.load_profiles()
            else:
                messagebox.showerror("Error", f"Profile directory not found: {profile_dir}", parent=self)
                
        except Exception as e:
            logger.error(f"Error deleting profile: {str(e)}")
            messagebox.showerror("Error", f"Failed to delete profile: {str(e)}", parent=self)
    
    def on_select(self):
        """Set the selected profile as the result and close the dialog"""
        selection = self.profile_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a profile.", parent=self)
            return
        
        self.result = self.profile_listbox.get(selection[0])
        self.destroy()
    
    def on_cancel(self):
        """Cancel the operation and close the dialog"""
        self.destroy()

class DebugLevelSelector(tk.Toplevel):
    """Dialog for selecting debug level"""
    def __init__(self, parent, current_level="INFO"):
        super().__init__(parent)
        self.parent = parent
        self.result = current_level
        
        self.title("Select Debug Level")
        self.geometry("350x250")
        self.configure(background=COLORS["background"])
        self.resizable(False, False)
        
        # Center the window
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        
        self.create_widgets(current_level)
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.wait_window(self)
    
    def create_widgets(self, current_level):
        # Frame for the level list
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label with explanation
        ttk.Label(main_frame, text="Select Debug Level:").pack(anchor=tk.W, pady=(0, 5))
        
        # Information frame
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        # Radiobuttons for debug levels
        self.level_var = tk.StringVar(value=current_level)
        
        level_descriptions = {
            "INFO": "Normal operation, minimal logging",
            "DEBUG": "Detailed information for troubleshooting",
            "TRACE": "Very detailed operation tracing",
            "VERBOSE": "Most detailed logging, all operations"
        }
        
        for level, description in level_descriptions.items():
            level_frame = ttk.Frame(main_frame)
            level_frame.pack(fill=tk.X, pady=2)
            
            rb = ttk.Radiobutton(level_frame, text=level, value=level, variable=self.level_var)
            rb.pack(side=tk.LEFT)
            
            ttk.Label(level_frame, text=f"- {description}").pack(side=tk.LEFT, padx=5)
        
        # Buttons frame
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill=tk.X)
        
        # Buttons
        ttk.Button(btn_frame, text="OK", command=self.on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.on_cancel).pack(side=tk.RIGHT, padx=5)
    
    def on_ok(self):
        """Set the selected level as the result and close the dialog"""
        self.result = self.level_var.get()
        self.destroy()
    
    def on_cancel(self):
        """Cancel the operation and close the dialog"""
        self.destroy()

class GlasirGUI(tk.Tk):
    """Main application window for the Glasir Login System"""
    def __init__(self):
        super().__init__()
        
        self.title("Glasir Login System")
        self.geometry("600x450")
        self.configure(background=COLORS["background"])
        self.minsize(600, 450)
        
        # Initialize application state
        self.current_profile = None
        self.headless_mode = True
        self.debug_level = "INFO"
        self.glasir_session = None
        self.login_in_progress = False
        
        # Set up the application
        self.setup_styles()
        self.create_menu()
        self.create_widgets()
        
        # Configure logging for the GUI
        self.configure_logging()
        
        # Center the window
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        
        # Initialize with first available profile
        self.load_initial_profile()
        
        # Track window close
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_styles(self):
        """Configure ttk styles for the application"""
        style = ttk.Style()
        
        # Configure colors
        style.configure("TFrame", background=COLORS["background"])
        style.configure("TLabel", background=COLORS["background"], foreground=COLORS["text"])
        style.configure("TButton", background=COLORS["primary"], foreground=COLORS["light_text"])
        
        # Header style
        style.configure("Header.TLabel", font=("Arial", 16, "bold"), foreground=COLORS["primary"])
        
        # Status styles
        style.configure("Success.TLabel", foreground=COLORS["success"])
        style.configure("Warning.TLabel", foreground=COLORS["warning"])
        style.configure("Error.TLabel", foreground=COLORS["error"])
        
        # Button styles
        style.configure("Primary.TButton", background=COLORS["primary"])
        style.configure("Secondary.TButton", background=COLORS["secondary"])
        style.configure("Accent.TButton", background=COLORS["accent"])
    
    def create_menu(self):
        """Create the application menu"""
        menubar = tk.Menu(self)
        
        # Profile menu
        profile_menu = tk.Menu(menubar, tearoff=0)
        profile_menu.add_command(label="Select Profile", command=self.on_select_profile)
        profile_menu.add_command(label="New Profile", command=self.on_new_profile)
        profile_menu.add_separator()
        profile_menu.add_command(label="Delete Session", command=self.on_delete_session)
        menubar.add_cascade(label="Profile", menu=profile_menu)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        
        # Headless mode submenu
        self.headless_var = tk.BooleanVar(value=self.headless_mode)
        settings_menu.add_checkbutton(label="Headless Browser Mode", 
                                     variable=self.headless_var,
                                     command=self.on_toggle_headless)
        
        settings_menu.add_command(label="Debug Level", command=self.on_change_debug_level)
        settings_menu.add_command(label="View Logs", command=self.on_view_logs)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.on_about)
        help_menu.add_command(label="Documentation", command=self.on_documentation)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.config(menu=menubar)
    
    def create_widgets(self):
        """Create the main application widgets"""
        # Main container
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(header_frame, text="Glasir Login System", style="Header.TLabel").pack(side=tk.LEFT)
        
        # Status panel
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding=10)
        status_frame.pack(fill=tk.X, pady=5)
        
        # Profile info
        profile_frame = ttk.Frame(status_frame)
        profile_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(profile_frame, text="Current Profile:").pack(side=tk.LEFT, padx=(0, 5))
        self.profile_label = ttk.Label(profile_frame, text="None")
        self.profile_label.pack(side=tk.LEFT)
        
        # Browser mode
        browser_frame = ttk.Frame(status_frame)
        browser_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(browser_frame, text="Browser Mode:").pack(side=tk.LEFT, padx=(0, 5))
        self.browser_mode_label = ttk.Label(browser_frame, text="Headless (Hidden)")
        self.browser_mode_label.pack(side=tk.LEFT)
        
        # Session status
        session_frame = ttk.Frame(status_frame)
        session_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(session_frame, text="Session Status:").pack(side=tk.LEFT, padx=(0, 5))
        self.session_status_label = ttk.Label(session_frame, text="No session")
        self.session_status_label.pack(side=tk.LEFT)
        
        # Debug level
        debug_frame = ttk.Frame(status_frame)
        debug_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(debug_frame, text="Debug Level:").pack(side=tk.LEFT, padx=(0, 5))
        self.debug_level_label = ttk.Label(debug_frame, text="INFO")
        self.debug_level_label.pack(side=tk.LEFT)
        
        # Action buttons
        actions_frame = ttk.Frame(main_frame)
        actions_frame.pack(fill=tk.X, pady=15)
        
        self.login_button = ttk.Button(actions_frame, text="Login", 
                                       command=self.on_login, 
                                       style="Primary.TButton")
        self.login_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(actions_frame, text="Select Profile", 
                  command=self.on_select_profile,
                  style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(actions_frame, text="Delete Session", 
                  command=self.on_delete_session).pack(side=tk.LEFT, padx=5)
        
        # Add View Screenshots button
        ttk.Button(actions_frame, text="View Screenshots", 
                  command=self.on_view_screenshots).pack(side=tk.RIGHT, padx=5)
        
        # Progress bar 
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", 
                                           style="TProgressbar")
        self.progress_bar.pack(fill=tk.X)
        
        # Progress status text
        self.progress_text = ttk.Label(progress_frame, text="", anchor=tk.CENTER)
        self.progress_text.pack(fill=tk.X, pady=3)
        
        # Log display
        log_frame = ttk.LabelFrame(main_frame, text="Login Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create a scrolled text widget for logs
        log_container = ttk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_container, height=10, width=50, wrap=tk.WORD, 
                               background="#f8f9fa", foreground="#333333",
                               font=("Consolas", 9))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_container, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        self.log_text.config(state=tk.DISABLED)  # Make it read-only
        
        # Status bar at bottom
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def configure_logging(self):
        """Configure logging for the GUI"""
        # Create a custom handler to redirect logs to the text widget
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                logging.Handler.__init__(self)
                self.text_widget = text_widget
                
                # Configure the formatter
                formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', 
                                             datefmt='%H:%M:%S')
                self.setFormatter(formatter)
                
                # Define colors for different log levels
                self.level_colors = {
                    logging.DEBUG: "#666666",  # Gray
                    logging.INFO: "#000000",   # Black
                    logging.WARNING: "#FF9800", # Orange
                    logging.ERROR: "#F44336",  # Red
                    logging.CRITICAL: "#B71C1C" # Dark Red
                }
                
                # Custom levels
                self.level_colors[5] = "#2196F3"  # Blue for TRACE
                self.level_colors[1] = "#4CAF50"  # Green for VERBOSE
            
            def emit(self, record):
                msg = self.format(record)
                
                # Get the appropriate color for this log level
                level_color = self.level_colors.get(record.levelno, "#000000")
                
                # Use after() to safely update the text widget from any thread
                self.text_widget.after(0, self._insert_message, msg, level_color)
            
            def _insert_message(self, msg, color):
                self.text_widget.config(state=tk.NORMAL)
                self.text_widget.insert(tk.END, msg + "\n", color)
                self.text_widget.see(tk.END)  # Scroll to the end
                self.text_widget.config(state=tk.DISABLED)
                
                # Add tags for color formatting
                self.text_widget.tag_config(color, foreground=color)
        
        # Set up tags for different colors
        for level, color in TextHandler(self.log_text).level_colors.items():
            self.log_text.tag_configure(color, foreground=color)
        
        # Create and set up the handler
        text_handler = TextHandler(self.log_text)
        
        # Set up the root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(DEBUG_LEVELS.get(self.debug_level, logging.INFO))
        
        # Remove existing handlers and add the text handler
        for handler in root_logger.handlers[:]:
            if isinstance(handler, TextHandler):
                root_logger.removeHandler(handler)
        
        root_logger.addHandler(text_handler)
        
        # Add a message to the log
        logger.info("GUI application started")
    
    def load_initial_profile(self):
        """Load the first available profile on startup"""
        profiles = get_profile_list()
        if profiles:
            self.current_profile = profiles[0]
            self.update_profile_display()
            self.initialize_session()
    
    def initialize_session(self):
        """Initialize the Glasir session with the current profile"""
        if self.current_profile:
            # Configure debug settings
            debug_config = {
                "debug_level": self.debug_level,
                "timing_metrics": True,
                "visualize_flow": False
            }
            
            # Create the session
            self.glasir_session = GlasirSession(
                profile_name=self.current_profile,
                headless=self.headless_mode,
                debug_config=debug_config
            )
            
            # Update session status display
            self.update_session_status()
            
            logger.info(f"Initialized session for profile: {self.current_profile}")
        else:
            self.glasir_session = None
            self.session_status_label.config(text="No profile selected")
    
    def update_profile_display(self):
        """Update the profile display in the UI"""
        if self.current_profile:
            self.profile_label.config(text=self.current_profile)
        else:
            self.profile_label.config(text="None")
    
    def update_session_status(self):
        """Update the session status display in the UI"""
        if not self.glasir_session:
            self.session_status_label.config(text="No session")
            return
            
        if self.glasir_session.session_data:
            try:
                is_valid, reason = self.glasir_session.check_session_validity()
                if is_valid:
                    self.session_status_label.config(text="Valid session", style="Success.TLabel")
                else:
                    self.session_status_label.config(text=f"Invalid: {reason}", style="Warning.TLabel")
            except Exception as e:
                logger.error(f"Error checking session validity: {str(e)}")
                self.session_status_label.config(text=f"Error: {str(e)}", style="Error.TLabel")
        else:
            self.session_status_label.config(text="No session")
    
    def update_debug_level_display(self):
        """Update the debug level display in the UI"""
        self.debug_level_label.config(text=self.debug_level)
    
    def update_browser_mode_display(self):
        """Update the browser mode display in the UI"""
        mode_text = "Headless (Hidden)" if self.headless_mode else "Visible"
        self.browser_mode_label.config(text=mode_text)
    
    def on_login(self):
        """Handle the login button click"""
        if self.login_in_progress:
            logger.warning("Login already in progress")
            return
            
        if not self.current_profile:
            messagebox.showwarning("No Profile", "Please select a profile first.")
            return
        
        if not self.glasir_session:
            self.initialize_session()
            
        # Update status
        self.login_in_progress = True
        self.login_button.config(state=tk.DISABLED)
        self.status_var.set("Login in progress...")
        
        # Start progress indicator
        self.progress_bar.start(10)
        self.progress_text.config(text="Logging in... This may take a moment")
        
        # Clear the log display
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        logger.info(f"Starting login with profile: {self.current_profile}")
        
        # Use AsyncRunner to run the login process
        AsyncRunner.run_async(
            self.glasir_session.login(),
            self.on_login_complete
        )
        
        # Start periodic updates of progress status
        self._login_start_time = datetime.now()
        self._update_progress_status()
    
    def _update_progress_status(self):
        """Update progress status with elapsed time"""
        if self.login_in_progress:
            elapsed = datetime.now() - self._login_start_time
            elapsed_seconds = int(elapsed.total_seconds())
            self.progress_text.config(text=f"Logging in... ({elapsed_seconds}s elapsed)")
            # Schedule next update in 1 second
            self.after(1000, self._update_progress_status)
    
    def on_login_complete(self, result):
        """Handle the completion of the login process"""
        self.login_in_progress = False
        self.login_button.config(state=tk.NORMAL)
        
        # Stop progress indicator
        self.progress_bar.stop()
        self.progress_text.config(text="")
        
        if result:
            self.status_var.set("Login successful")
            logger.info("Login completed successfully")
            
            # Update session status
            try:
                self.update_session_status()
            except Exception as e:
                logger.error(f"Error updating session status: {str(e)}")
                # Don't let this error affect the success message
            
            # Show success message
            messagebox.showinfo("Login Successful", 
                               "You have successfully logged in to the Glasir system.")
        else:
            self.status_var.set("Login failed")
            logger.error("Login failed")
            
            # Show error message with options
            response = messagebox.askquestion("Login Failed", 
                                            "Failed to log in to the Glasir system.\n\n"
                                            "Would you like to view the screenshots to troubleshoot?",
                                            icon='error')
            if response == 'yes':
                self.on_view_screenshots()
    
    def on_view_screenshots(self):
        """Open screenshots directory"""
        screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
        
        if os.path.exists(screenshots_dir):
            # On Windows
            if os.name == 'nt':
                os.startfile(screenshots_dir)
            # On macOS
            elif sys.platform == 'darwin':
                import subprocess
                subprocess.call(['open', screenshots_dir])
            # On Linux
            else:
                import subprocess
                subprocess.call(['xdg-open', screenshots_dir])
        else:
            messagebox.showwarning("Screenshots Not Found", 
                                  f"Screenshots directory not found at {screenshots_dir}")
    
    def on_select_profile(self):
        """Handle the select profile action"""
        profile_selector = ProfileSelector(self, self.current_profile)
        if profile_selector.result:
            self.current_profile = profile_selector.result
            self.update_profile_display()
            self.initialize_session()
            logger.info(f"Switched to profile: {self.current_profile}")
    
    def on_new_profile(self):
        """Handle the new profile action"""
        profile_selector = ProfileSelector(self, self.current_profile)
        if profile_selector.result:
            self.current_profile = profile_selector.result
            self.update_profile_display()
            self.initialize_session()
    
    def on_delete_session(self):
        """Handle the delete session action"""
        if not self.current_profile:
            messagebox.showwarning("No Profile", "Please select a profile first.")
            return
            
        if not self.glasir_session:
            self.initialize_session()
            
        if not self.glasir_session.session_data:
            messagebox.showinfo("No Session", f"No session exists for profile '{self.current_profile}'.")
            return
            
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete the session for '{self.current_profile}'?"):
            try:
                result = self.glasir_session.delete_session()
                if result:
                    messagebox.showinfo("Success", "Session deleted successfully.")
                    logger.info(f"Session deleted for profile: {self.current_profile}")
                    self.update_session_status()
                else:
                    messagebox.showerror("Error", "Failed to delete session.")
                    logger.error(f"Failed to delete session for profile: {self.current_profile}")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting session: {str(e)}")
                logger.exception(f"Error deleting session: {e}")
    
    def on_toggle_headless(self):
        """Handle toggling the headless mode"""
        self.headless_mode = self.headless_var.get()
        self.update_browser_mode_display()
        logger.info(f"Browser mode set to: {'headless' if self.headless_mode else 'visible'}")
        
        # Reinitialize the session with the new setting
        if self.glasir_session:
            self.initialize_session()
    
    def on_change_debug_level(self):
        """Handle changing the debug level"""
        level_selector = DebugLevelSelector(self, self.debug_level)
        if level_selector.result != self.debug_level:
            self.debug_level = level_selector.result
            self.update_debug_level_display()
            
            # Update logging level
            root_logger = logging.getLogger()
            root_logger.setLevel(DEBUG_LEVELS.get(self.debug_level, logging.INFO))
            
            logger.info(f"Debug level set to: {self.debug_level}")
            
            # Reinitialize the session with the new setting
            if self.glasir_session:
                self.initialize_session()
    
    def on_view_logs(self):
        """Handle viewing the log files"""
        log_path = os.path.join(LOGS_DIR, "glasir_login.log")
        
        if os.path.exists(log_path):
            # On Windows
            if os.name == 'nt':
                os.startfile(log_path)
            # On macOS
            elif sys.platform == 'darwin':
                import subprocess
                subprocess.call(['open', log_path])
            # On Linux
            else:
                import subprocess
                subprocess.call(['xdg-open', log_path])
        else:
            messagebox.showwarning("Log Not Found", f"Log file not found at {log_path}")
    
    def on_about(self):
        """Show the about dialog"""
        about_text = """Glasir Login System

A secure and efficient system for logging in to the Glasir service.

Author: Claude AI Assistant
Version: 1.0.0
"""
        messagebox.showinfo("About Glasir Login System", about_text)
    
    def on_documentation(self):
        """Open the documentation"""
        # You would typically put a URL to your documentation here
        messagebox.showinfo("Documentation", 
                           "Documentation is not yet available online.\n\n"
                           "For help, check the README file or contact support.")
    
    def on_close(self):
        """Handle the window close event"""
        logger.info("Application shutting down")
        self.destroy()

def main():
    """Main function to start the application"""
    # Configure root logger for file output
    os.makedirs(LOGS_DIR, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(LOGS_DIR, "glasir_gui.log"))
        ]
    )
    
    # Create and start the application
    app = GlasirGUI()
    app.mainloop()
    
    return 0

if __name__ == "__main__":
    # Run the main function
    sys.exit(main()) 