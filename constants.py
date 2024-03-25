import json
import os
import glob
from pathlib import Path
with open("config/scraper_config.json") as c:
    scraper_config = json.load(c)

#SCRAPER CONSTANTS
API_KEY = scraper_config['api_key']
SEARCH_ENGINE_ID = scraper_config['search_engine_id']
WEBDRIVER = scraper_config["webdriver"]
SCRAPER_PATH = os.path.join(scraper_config["scraper_path"])
FILES_PATH = glob.glob("data/downloads/*")