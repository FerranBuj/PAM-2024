import json
import os
import glob
from pathlib import Path
with open("config.json") as c:
    config = json.load(c)

SIZE_W = config["size_w"]
SIZE_H = config["size_h"]
TILE_X = config["tile_x"]
TILE_Y = config["tile_y"]
TILE_W = int(SIZE_W/TILE_X)
TILE_H = int(SIZE_H/TILE_Y)
MATRIX_X = config["matrix_x"]
MATRIX_Y = config["matrix_y"]
MATRIX_W = int(TILE_W/MATRIX_X)
MATRIX_H = int(TILE_H/MATRIX_Y)
FRAMES = glob.glob(os.path.join("data/frames/*"))
FILES = glob.glob(os.path.join("data/downloads/*"))
COLLECTION_PATH = os.path.join("chromadb/collection")
OVERRIDE_ASPECT_RATIO = config["override_aspect_ratio"]
COLLECTION_NAME = f"{TILE_X}{TILE_Y}{MATRIX_X}{MATRIX_Y}{OVERRIDE_ASPECT_RATIO}"

API_KEY = config['api_key']
SEARCH_ENGINE_ID = config['search_engine_id']
WEBDRIVER = config["webdriver"]
