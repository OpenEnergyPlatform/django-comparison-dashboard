import warnings

import pandas as pd
from django.apps import apps
from django.conf import settings
from django.db.models import Sum
from units import NamedComposedUnit, scaled_unit, unit
from units.exception import IncompatibleUnitsError
from units.predefined import define_units
from units.registry import REGISTRY


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


def get_scalar_data(query: dict[str, str]) -> pd.DataFrame:
    filters, groupby, units = prepare_query(query)
    scalar_model = apps.get_model(settings.DASHBOARD_SCALAR_MODEL)
    queryset = scalar_model.objects.filter(**filters).values(*groupby).annotate(Sum("value"))
    df = pd.DataFrame(queryset)
    return convert_units_in_df(df, units)


def convert_units_in_df(df: pd.DataFrame, units) -> pd.DataFrame:
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

    def convert_units(row, convert_to):
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
    all_units = df["unit"].unique()
    for unit_ in all_units:
        if unit_ not in REGISTRY:
            warnings.warn(f"Unknown unit '{unit_}' found in data.")

    for unit_ in units:
        df = df.apply(convert_units, axis=1, convert_to=unit_)
    return df


def prepare_query(query: dict[str, str]) -> tuple[dict[str, str], list[str], list[str]]:
    """Unpacks filters, groupby and units from query dict"""

    def parse_list(value):
        if value[0] == "[" and value[-1] == "]":
            return value[1:-1].split(",")
        return value

    filters = {k: parse_list(v) for k, v in query.items() if k not in ("groupby", "units")}
    groupby = parse_list(query["groupby"]) if "groupby" in query else []
    units = parse_list(query["units"]) if "units" in query else []
    return filters, groupby, units
