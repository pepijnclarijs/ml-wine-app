from dotenv import load_dotenv
import os

if os.getenv("ENV") == "local" or os.getenv("ENV") is None:
    load_dotenv()  # Only load .env if running locally (not in container)
