import json
import pathlib

APP_DIR = pathlib.Path(__file__).parent
DATA_DIR = APP_DIR / "data"

with (DATA_DIR / "dataset.json").open("r", encoding="utf-8") as dataset_file:
    DATASET = json.load(dataset_file)
