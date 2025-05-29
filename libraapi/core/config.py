import os
import sys

from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent

DATABASE = {
    "dbprod": {
        "stack": "postgresql+asyncpg",
        "dbhost": os.environ.get("DBHOST"),
        "dbport": os.environ.get("DBPORT"),
        "dbuser": os.environ.get("DBUSER"),
        "dbname": os.environ.get("DBNAME"),
        "dbpassword": os.environ.get("DBPASSWORD"),
    }
}



