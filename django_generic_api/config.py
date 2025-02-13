import configparser
import os


def get_project_root():
    # Get the project root directory (where manage.py is located)
    current_dir = os.getcwd()  # Start from the current working directory
    while not os.path.isfile(
        os.path.join(current_dir, "manage.py")
    ):  # Look for manage.py
        current_dir = os.path.dirname(current_dir)  # Go up one level
    return current_dir


# Get the project root directory
project_root = get_project_root()

# Path for user's config.ini
user_config_path = os.path.join(project_root, "django_generic_api.ini")

# Path for default.ini file
default_config_path = os.path.join(os.path.dirname(__file__), "default.ini")

config = configparser.ConfigParser()

# If user's .ini file exists, read it. Else read default.ini file
if os.path.exists(user_config_path):
    config.read(user_config_path)

else:
    config.read(default_config_path)

try:
    # Rest framework settings
    # todo : for user convenience let them set these in settings
    user_rate = config.getint("REST_FRAMEWORK", "USER_RATE", fallback=1000)
    anon_rate = config.getint("REST_FRAMEWORK", "ANON_RATE", fallback=30)

    # Save
    create_batch_size = config.getint(
        "SAVE_SETTINGS", "CREATE_BATCH_SIZE", fallback=10
    )

    # Email activation link expiry hours
    expiry_hours = config.getint(
        "EMAIL_SETTINGS", "EMAIL_ACTIVATION_LINK_EXPIRY_HOURS", fallback=24
    )

except configparser.NoOptionError as e:
    raise ValueError(
        f"Improperly configured: Missing required configuration key: {e}"
    )
