import os

from dotenv import load_dotenv

load_dotenv()

GITLAB_PRIVATE_TOKEN = os.environ["GITLAB_PRIVATE_TOKEN"]
GITLAB_API_VERSION = "v4"
NUMBER_OF_THREADS = int(os.getenv("NUMBER_OF_THREADS") or 5)
NUMBER_OF_RETRIES = int(os.getenv("NUMBER_OF_RETRIES") or 3)
