import warnings

import pandas as pd
from django.db.models import Sum
from units import NamedComposedUnit, scaled_unit, unit
from units.exception import IncompatibleUnitsError
from units.predefined import define_units
from units.registry import REGISTRY

from .settings import GRAPHS_DEFAULT_OPTIONS


class PreprocessingError(Exception):
    """Raised if preprocessing fails"""


def define_energy_model_units():
    scaled_unit("kW", "W", 1e3)
    scaled_unit("MW", "kW", 1e3)
    scaled_unit("GW", "MW", 1e3)
    scaled_unit("TW", "GW", 1e3)

    scaled_unit("a", "day", 365)

    scaled_unit("kt", "t", 1e3)
    scaled_unit("Mt", "kt", 1e3)
    scaled_unit("Gt", "Mt", 1e3)

    NamedComposedUnit("kWh", unit("kW") * unit("h"))
    NamedComposedUnit("MWh", unit("MW") * unit("h"))
    NamedComposedUnit("GWh", unit("GW") * unit("h"))
    NamedComposedUnit("TWh", unit("TW") * unit("h"))

    NamedComposedUnit("kW/h", unit("kW") / unit("h"))
    NamedComposedUnit("MW/h", unit("MW") / unit("h"))
    NamedComposedUnit("GW/h", unit("GW") / unit("h"))
    NamedComposedUnit("TW/h", unit("TW") / unit("h"))


define_units()
define_energy_model_units()


def get_scalar_data(queryset_filtered: dict[str, str], groupby: list[str], units: list[str]) -> pd.DataFrame:
    if groupby:
        queryset = queryset_filtered.values(*(groupby + ["unit"])).annotate(value=Sum("value"))
    else:
        queryset = queryset_filtered.values()
    df = pd.DataFrame(queryset)
    if df.empty:
        return df

    # Following preprocessing steps cannot be done in DB
    df = convert_units_in_df(df, units)
    df = aggregate_df(df, groupby)  # Groupby has to be redone after unit conversion
    return df


def aggregate_df(df: pd.DataFrame, groupby: list[str]) -> pd.DataFrame:
    if df.empty:
        return df

    if groupby:
        if "series" in df and len(df["series"].apply(len).unique()) > 1:
            raise PreprocessingError("Different ts lengths at aggregation found.")
        df = df.groupby(groupby + ["unit"]).aggregate("sum").reset_index()
        keep_columns = groupby + ["unit", "value", "series"]
        df = df[df.columns.intersection(keep_columns)]
    return df


def convert_units_in_df(df: pd.DataFrame, units: list[str]) -> pd.DataFrame:
    """
    Convert values and values in series (timeseries data) depending on given units

    Parameters
    ----------
    df
        Dataframe to convert
    units
        Desired unit conversions
    Returns
    -------
    Dataframe holding converted units
    """

    def convert_units(row: pd.Series, convert_to: str):
        """
        Tries to convert value of row, given current unit of the row and conversion unit

        Parameters
        ----------
        row
            Current dataframe row
        convert_to
            Unit to convert value to
        Returns
        -------
            Converted row if conversion has been successful, otherwise unchanged row is returned
        """
        if "unit" not in row or row["unit"] not in REGISTRY:
            return row
        if "value" in row:
            value = unit(row["unit"])(row["value"])
            try:
                row["value"] = unit(convert_to)(value).get_num()
            except IncompatibleUnitsError:
                return row
        elif "series" in row:
            try:
                mul = unit(convert_to)(unit(row["unit"])(1)).get_num()
            except IncompatibleUnitsError:
                return row
            row["series"] = row["series"] * mul
        else:
            return row
        row["unit"] = convert_to
        return row

    # Check if unit conversion exists in unit registry
    if df.empty:
        return df
    all_units = df["unit"].unique()
    for unit_ in all_units:
        if unit_ not in REGISTRY:
            warnings.warn(f"Unknown unit '{unit_}' found in data.")

    for unit_ in units:
        df = df.apply(convert_units, axis=1, convert_to=unit_)
    return df


def prepare_query(query: dict[str, str]) -> tuple[dict[str, str], list[str], list[str], dict[str, str]]:
    """Unpacks filters, groupby and units from query dict"""

    def parse_list(value):
        if value[0] == "[" and value[-1] == "]":
            return value[1:-1].split(",")
        return value

    plot_option_keys = list(GRAPHS_DEFAULT_OPTIONS["scalars"]["bar"].get_defaults().keys())
    filters = {k: parse_list(v) for k, v in query.items() if k not in plot_option_keys + ["groupby", "units"]}
    groupby = parse_list(query["groupby"]) if "groupby" in query else []
    units = parse_list(query["units"]) if "units" in query else []
    plot_options = {k: parse_list(v) for k, v in query.items() if k not in list(filters) + ["groupby", "units"]}
    return filters, groupby, units, plot_options
