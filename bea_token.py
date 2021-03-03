import os

from dotenv import load_dotenv

load_dotenv()

BEA_API_TOKEN = os.getenv("BEA_API_TOKEN", None)

if BEA_API_TOKEN is None:
    raise ValueError("No API token found, please store in .env or BEA_API_TOKEN variable")