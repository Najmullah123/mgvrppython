import os
from dotenv import load_dotenv

load_dotenv()

# Channel IDs
EARLY_ACCESS_CHANNEL = int(os.environ.get("EARLY_ACCESS_CHANNEL"))
SETTING_UP_CHANNEL = int(os.environ.get("SETTING_UP_CHANNEL"))
CONCLUSION_CHANNEL = int(os.environ.get("CONCLUSION_CHANNEL"))
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL"))

# Role IDs
ADMIN_ROLES = [
    1400212028353810572,  # Main admin role
    # Add more admin role IDs as needed
]

# Bot settings
GUILD_ID = int(os.environ.get("GUILD_ID", "1277047315047120978"))

# Economy settings
ECONOMY_CHANNEL = int(os.environ.get("ECONOMY_CHANNEL", "1403779808135090186"))

# Moderation settings
MOD_LOG_CHANNEL = int(os.environ.get("MOD_LOG_CHANNEL", "1339764330425487460"))
