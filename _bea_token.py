import os

from dotenv import load_dotenv

import getpass

load_dotenv()

BEA_API_TOKEN = os.getenv("BEA_API_TOKEN", None)

if BEA_API_TOKEN is None:
    BEA_API_TOKEN = getpass.getpass("What is your BEA API Token?")

assert BEA_API_TOKEN is not None