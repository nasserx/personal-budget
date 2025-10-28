import sys
from pathlib import Path


def resource_path(relative_path: str) -> Path:
    """
    Return the absolute path for a resource file.
    Works correctly both in development and after conversion to an executable using PyInstaller.
    This function is used for read-only assets such as QSS files and icons.
    """
    try:
        # Temporary path created by PyInstaller at runtime
        base_path = Path(sys._MEIPASS)
    except Exception:
        # Development environment path (before conversion to exe)
        base_path = Path(__file__).resolve().parent.parent
    return base_path / relative_path


# Base directory of the project (development environment)
BASE_DIR = Path(__file__).resolve().parent.parent

# UI-related directories (read-only)
CORE_DIR = resource_path("core")
UI_DIR = resource_path("ui")
QSS_DIR = resource_path("ui/qss")
ICONS_DIR = resource_path("ui/icons")

# General application settings
APP_TITLE = "الميزانية الشخصية"
APP_ICON = resource_path("ui/icons/app_icon.ico")
CURRENCY = "ريال"

# Handle user data (writable section)
# Store user data alongside the executable when frozen
if getattr(sys, 'frozen', False):
    # Running from an executable file
    BASE_PATH = Path(sys.executable).parent
else:
    # Development environment
    BASE_PATH = BASE_DIR

# Writable data directory
DATA_DIR = BASE_PATH / "core" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists

# JSON data file path
DATA_FILE = DATA_DIR / "data.json"
