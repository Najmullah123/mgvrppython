import os
from dotenv import load_dotenv

load_dotenv()

EARLY_ACCESS_CHANNEL = int(os.environ.get("EARLY_ACCESS_CHANNEL"))
SETTING_UP_CHANNEL = int(os.environ.get("SETTING_UP_CHANNEL"))
CONCLUSION_CHANNEL = int(os.environ.get("CONCLUSION_CHANNEL"))
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL"))
