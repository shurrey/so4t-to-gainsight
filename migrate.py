from typing import List
from dotenv import load_dotenv
import os
import requests

from insided_api import InsidedAPI
from so_api import StackOverflowAPI

load_dotenv(".env", override=True)

so4t_pat = os.getenv("SO4T_PAT")
so4t_slug = os.getenv("SO4T_SLUG")
so4t_uri = os.getenv("SO4T_URI")

headers = {
    "accept" : "application/json",
    "Authorization" : f"Bearer {so4t_pat}"
}

so = StackOverflowAPI()

print("Migrate users...")
user_mapping = so.migrate_all_users()

print(f"user_mapping {user_mapping}")

print("Migrate tags...")
#so.migrate_all_tags()

print("Migrate questions...")
so.migrate_all_questions()
