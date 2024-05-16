import warnings

import pandas as pd
from django.db.models import Sum
from units import NamedComposedUnit, scaled_unit, unit
from units.exception import IncompatibleUnitsError
from units.predefined import define_units
from units.registry import REGISTRY

from .forms import DataFilterSet


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


def get_scalar_data(filter_set: DataFilterSet) -> pd.DataFrame:
    if filter_set.order_by or filter_set.group_by:
        # looks like: {'order_by': ['region'], 'group_by': ['year'], 'normalize': False}
        if filter_set.group_by:
            queryset = filter_set.queryset.values(*(filter_set.group_by + ["unit"])).annotate(value=Sum("value"))
        else:
            queryset = filter_set.queryset.values()
        df = pd.DataFrame(queryset)
        # Following preprocessing steps cannot be done in DB
        df = apply_labels_in_df(df, filter_set.labels)
        df = convert_units_in_df(df, filter_set.units)
        df = aggregate_df(df, filter_set.group_by)
        df = df.sort_values(filter_set.order_by)
        # Groupby has to be redone after unit conversion, and if orderby is provided it will also be applied here
        return df

    queryset = filter_set.queryset.values()
    df = pd.DataFrame(queryset)
    # Following preprocessing steps cannot be done in DB
    df = apply_labels_in_df(df, filter_set.labels)
    df = convert_units_in_df(df, filter_set.units)
    df = df.sort_values(filter_set.order_by)
    return df


def aggregate_df(df: pd.DataFrame, groupby: list[str]) -> pd.DataFrame:
    if df.empty:
        return df

    if groupby:
        if "series" in df and len(df["series"].apply(len).unique()) > 1:
            raise PreprocessingError("Different ts lengths at aggregation found.")

        # Columns containing list have to be converted as they are unhashable
        list_columns = [column for column in df.columns if isinstance(df[column][0], list)]
        df[list_columns] = df[list_columns].map(frozenset)

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


def apply_labels_in_df(df: pd.DataFrame, labels: dict[str, str]) -> pd.DataFrame:
    """
    Map labels to their respective values given by user

    Parameters
    ----------
    df: pd.DataFrame
        Data to apply labels on
    labels: dict[str, str]
        Labels to apply, each found key is replaced with their corresponding value

    Returns
    -------
    pd.DataFrame
        Resulting dataframe with labels applied
    """

    def apply_label(value, labels):
        try:
            return labels.get(value, value)
        except TypeError:
            return value

    return df.applymap(apply_label, labels=labels)
