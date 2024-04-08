import os

from dotenv import load_dotenv, find_dotenv

from .credentials import OnePasswordItem
from .usersettings import UserSettings

# Load environment variables

environment = os.environ
load_dotenv()
find_dotenv()
