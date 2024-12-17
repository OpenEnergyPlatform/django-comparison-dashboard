import json
import os
import pathlib
from enum import IntEnum

VERSION = "2.6.0"

USE_DUMMY_DATA = os.environ.get("USE_DUMMY_DATA", "False") == "True"
SKIP_TS = os.environ.get("SKIP_TS", "False") == "True"

DATAPACKAGE_PATH = pathlib.Path(__file__).parent / "datamodel" / "datapackage.json"
COLOR_DICT_PATH = pathlib.Path(__file__).parent / "datamodel" / "color_dict.json"


class DataType(IntEnum):
    Scalar = 0
    Timeseries = 1

    def __str__(self):
        if self.value == 0:
            return "oed_scalars"
        else:
            return "oed_timeseries"


COLUMN_JOINER = "-"

with DATAPACKAGE_PATH.open("r", encoding="UTF-8") as datapackage_file:
    datapackage = json.loads(datapackage_file.read())
    MODEX_OUTPUT_SCHEMA = {resource["name"]: resource["schema"] for resource in datapackage["resources"]}


# GRAPHS

GRID_COLOR = "lightgray"

GRAPHS_DEFAULT_TEMPLATE = "plotly_white"
GRAPHS_DEFAULT_LAYOUT = {
    "legend": {"font": {"size": 14}},
}
GRAPHS_DEFAULT_XAXES_LAYOUT = {
    "autorange": True,
    "title": {"font": {"size": 18}},
    "gridcolor": GRID_COLOR,
    "linecolor": GRID_COLOR,
    "linewidth": 2,
    "mirror": True,
    "showline": True,
    "ticks": "outside",
    "tickcolor": GRID_COLOR,
    "tickfont": {"size": 14},
}
GRAPHS_DEFAULT_YAXES_LAYOUT = {
    "autorange": True,
    "title": {"font": {"size": 18}},
    "gridcolor": GRID_COLOR,
    "linecolor": GRID_COLOR,
    "linewidth": 2,
    "mirror": True,
    "showline": True,
    "ticks": "outside",
    "tickcolor": GRID_COLOR,
    "tickfont": {"size": 14},
}
GRAPHS_DEFAULT_ANNOTATIONS_LAYOUT = {"font_size": 14}

# Load the color dictionary from the JSON file
if os.path.exists(COLOR_DICT_PATH):
    with open(COLOR_DICT_PATH, encoding="UTF-8") as color_file:
        COLOR_DICT = json.load(color_file)
else:
    COLOR_DICT = {}
