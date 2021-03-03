import os

from dotenv import load_dotenv

load_dotenv()

BEA_API_TOKEN = os.getenv("BEA_API_TOKEN", None)

assert BEA_API_TOKEN is not None