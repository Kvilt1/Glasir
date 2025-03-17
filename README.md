# Glasir Login System

The Glasir Login System is a modular login automation tool that provides a secure and efficient way to log in to the Glasir service. It supports both browser-based automation and direct HTTP requests.

## Features

- **Modern GUI Interface**: Easy-to-use graphical interface
- **Multiple Profiles**: Support for multiple login profiles
- **Session Management**: Automatic session validation and reuse
- **Headless Mode**: Option to run browser in visible or headless mode
- **Debug Levels**: Configurable logging levels for troubleshooting
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation

### Prerequisites

- Python 3.7 or higher
- Tkinter (usually included with Python)
- Git (optional, for cloning the repository)

### Quick Installation

```bash
# Clone the repository (or download and extract the ZIP file)
git clone https://github.com/yourusername/glasir-login.git
cd glasir-login

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install
```

### Manual Installation

If you prefer to install dependencies manually:

```bash
# Install main packages
pip install playwright requests python-dotenv

# Install Playwright browsers
python -m playwright install
```

## File Structure

The system is comprised of several modules:

- `glasir_login.py` - Main entry point
- `glasir_gui.py` - GUI interface
- `glasir_main.py` - Core functionality
- `glasir_browser.py` - Browser automation
- `glasir_http.py` - HTTP requests handling

## Usage

### GUI Mode (Recommended)

Simply run:

```bash
python glasir_login.py
```

or explicitly:

```bash
python glasir_login.py --gui
```

### Command-Line Mode

```bash
python glasir_login.py --cli
```

### CLI Options

```
--profile PROFILE       Profile name to use
--headless              Run browser in headless mode
--visible               Run browser in visible mode
--debug-level LEVEL     Debug level (INFO, DEBUG, TRACE, VERBOSE)
--create-profile        Create a new profile
--delete-session        Delete session for profile
--timing                Enable timing metrics
--visualize             Enable flow visualization
--log-file FILE         Custom log file path
--non-interactive       Run in non-interactive mode (requires --profile)
```

## Getting Started

1. Launch the application in GUI mode
2. Create a new profile with your credentials
3. Click "Login" to log in to the Glasir system
4. The application will automatically save your session for future use

## Directories

- `data/profiles/` - Stores profile credentials and sessions
- `logs/` - Contains log files
- `screenshots/` - Screenshots taken during browser login
- `output/` - Output files from HTTP requests
- `browser_data/` - Browser profile data

## Troubleshooting

If you encounter issues:

### Login Failures

1. Check the logs in the "Login Log" panel
2. View screenshots (click "View Screenshots" button) to see where the login process failed
3. Try increasing the debug level (Settings → Debug Level)
4. Use visible browser mode (uncheck "Headless Browser Mode" in Settings)
5. Delete the session and try again

### Microsoft Login Issues

If the Microsoft login page is not working correctly:

1. Try using visible browser mode (uncheck "Headless Browser Mode")
2. Check if your credentials are correct
3. Look at the screenshots in the screenshots directory
4. Check if your Microsoft account has two-factor authentication (this requires manual login)

### Dependency Issues

If you're having issues with Playwright:

```bash
# Reinstall Playwright and browsers
pip uninstall -y playwright
pip install playwright
python -m playwright install --force
```

### Known Issues

- Two-factor authentication is not fully supported and may require manual intervention
- Some Microsoft login pages may have different layouts which can cause login failures
- Initial login may take longer than subsequent logins due to browser initialization

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Created by Claude AI Assistant
- Based on the original tg_glasir_login scripts 