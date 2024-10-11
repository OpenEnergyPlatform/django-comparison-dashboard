import math
import random

import numpy as np
import pandas as pd
from plotly import express as px
from plotly import graph_objects as go

from .forms import BarGraphFilterSet, LineGraphFilterSet, PlotFilterSet, SankeyGraphFilterSet
from .settings import (
    COLOR_DICT,
    GRAPHS_DEFAULT_LAYOUT,
    GRAPHS_DEFAULT_TEMPLATE,
    GRAPHS_DEFAULT_XAXES_LAYOUT,
    GRAPHS_DEFAULT_YAXES_LAYOUT,
)


class PlottingError(Exception):
    """Thrown if plotting goes wrong"""


def get_logarithmic_range(max_value):
    return [0, math.ceil(math.log10(max_value))]


def get_empty_fig():
    empty_fig = px.bar()
    empty_fig.update_layout(template=GRAPHS_DEFAULT_TEMPLATE, **GRAPHS_DEFAULT_LAYOUT)
    return empty_fig


def get_unit_from_data(data: pd.DataFrame) -> str | None:
    """
    Return unit from data if unit is unique, otherwise return None.
    Parameters
    ----------
    data: pd.DataFrame
        Dat containing unit column

    Returns
    -------
    str | None
        Unit of given value column if unit is unique, otherwise None.
    """
    units = data["unit"].unique()
    if len(units) == 1:
        return units[0]
    return None


def adapt_plot_figure(figure: go.Figure, filter_set: PlotFilterSet, data: pd.DataFrame) -> go.Figure:
    """
    Adapt display options to given figure

    Parameters
    ----------
    figure: go.Figure
        adapt options to this figure
    filter_set: PlotFilterSet
        Options from PlotFilterSet
    data: pd.DataFrame
        Data set to extract unit and other stuff from

    Returns
    -------
    go.Figure
        adapted figure
    """
    options = filter_set.display_options

    # Add simple layout fields
    layout = {
        "showlegend": options.pop("show_legend"),
        "legend_title": options.pop("legend_title"),
        "bargap": options.pop("bar_gap"),
        "margin_l": options.pop("margin_left"),
        "margin_r": options.pop("margin_right"),
        "margin_t": options.pop("margin_top"),
        "margin_b": options.pop("margin_bottom"),
    }

    # Add x/y-Axis title
    xaxis_title = options.pop("x_title")
    yaxis_title = options.pop("y_title")
    n_cols = filter_set.plot_options["facet_col_wrap"]
    n_rows = int(len(figure.layout.annotations) / n_cols)

    value_axis = (
        "x" if "orientation" in filter_set.plot_options and filter_set.plot_options["orientation"] == "h" else "y"
    )
    unit = get_unit_from_data(data)
    if value_axis == "x" and not xaxis_title:
        layout["xaxis_title"] = (
            filter_set.plot_options["x"] if unit is None else f"{filter_set.plot_options['x']} [{unit}]"
        )
    if value_axis == "x":
        xaxis_title_value = xaxis_title or (
            f"{filter_set.plot_options['x']} [{unit}]" if unit else filter_set.plot_options["x"])
        if filter_set.plot_options["facet_col"] and n_cols > 1:
            for c in range(1, n_cols + 1):
                figure.update_xaxes(row=1, col=c, title=xaxis_title_value)
        else:
            figure.update_xaxes(row=1, col=1, title=xaxis_title_value)
    if value_axis == "y":
        yaxis_title_value = yaxis_title or (
            f"{filter_set.plot_options['y']} [{unit}]" if unit else filter_set.plot_options["y"])
        if filter_set.plot_options["facet_col"] and n_rows > 1:
            for r in range(1, n_rows + 1):
                figure.update_yaxes(row=r, col=1, title=yaxis_title_value)
        else:
            figure.update_yaxes(row=1, col=1, title=yaxis_title_value)

    # Add subplot titles
    subplot_title = options.pop("subplot_title")
    if subplot_title:
        if "," in subplot_title and len(subplot_title.split(",")) == len(figure.layout.annotations):
            label_iter = iter(subplot_title.split(","))
            figure.for_each_annotation(lambda a: a.update(text=next(label_iter)))
        else:
            figure.for_each_annotation(lambda a: a.update(text=f"{subplot_title} {a.text.split('=')[-1]}"))
    else:
        figure.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    # Move legend above plot in subplots:
    if filter_set.plot_options["facet_col"]:
        figure.update_layout(legend={"orientation": "h", "yanchor": "bottom", "y": 1.06, "xanchor": "right", "x": 1})

    # Remove padding between stacked bars:
    figure.update_traces(marker={"line": {"width": 0}})

    # Update default layouts:
    figure.update_layout(template=GRAPHS_DEFAULT_TEMPLATE, **layout, **GRAPHS_DEFAULT_LAYOUT)
    figure.update_xaxes(GRAPHS_DEFAULT_XAXES_LAYOUT)
    figure.update_yaxes(GRAPHS_DEFAULT_YAXES_LAYOUT)

    return figure


def bar_plot(data: pd.DataFrame, filter_set: BarGraphFilterSet):
    data_json = data.to_dict(orient="records")
    try:
        fig = px.bar(data_json, **filter_set.plot_options)
    except ValueError as ve:
        if str(ve) == "nan is not in list":
            raise PlottingError(
                f"Scalar plot error: {ve} "
                + "(This might occur due to 'nan' values in data. Please check data via 'Show data')",
            )
        else:
            raise PlottingError(f"Scalar plot error: {ve}")

    return adapt_plot_figure(fig, filter_set, data)


def line_plot(data, filter_set: LineGraphFilterSet):
    data_json = data.to_dict(orient="records")
    try:
        fig = px.line(data_json, **filter_set.plot_options)
    except ValueError as ve:
        if str(ve) == "nan is not in list":
            raise PlottingError(
                f"Scalar plot error: {ve} "
                + "(This might occur due to 'nan' values in data. Please check data via 'Show data')",
            )
        else:
            raise PlottingError(f"Scalar plot error: {ve}")

    return adapt_plot_figure(fig, filter_set, data)


def sankey(data, filter_set: SankeyGraphFilterSet):
    """
    Return a dict containing the options for a plotly sankey diagram

    Nodes can be set via graph options, input and output commodities
    """

    def get_color(lookup_key: str, opacity: float = 0.75) -> str:
        """Return color for given key."""
        if lookup_key in colors:
            return f"rgba{(*hex_to_rgb(colors[lookup_key]), opacity)}"
        if lookup_key in COLOR_DICT:
            return f"rgba{(*hex_to_rgb(COLOR_DICT[lookup_key]), opacity)}"
        return f"rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, {opacity})"

    process_column = filter_set.cleaned_data["nodes"]
    inflow_column = filter_set.cleaned_data["inflow"]
    outflow_column = filter_set.cleaned_data["outflow"]

    labels = set(data[process_column]) | set(data[inflow_column]) | set(data[outflow_column])
    labels.discard(np.nan)
    labels = list(labels)

    source = []
    target = []
    value = []
    label = []
    # color = []
    # TODO: Better detection of flows
    # Currently, it is not checked if there is an input or output
    for _, flow in data.iterrows():
        if not isinstance(flow[inflow_column], str) or flow[inflow_column] == "":
            source.append(labels.index(flow[process_column]))
            target.append(labels.index(flow[outflow_column]))
            label.append(flow[outflow_column])
        elif not isinstance(flow[outflow_column], str) or flow[outflow_column] == "":
            source.append(labels.index(flow[inflow_column]))
            target.append(labels.index(flow[process_column]))
            label.append(flow[inflow_column])
        else:
            continue

        value.append(flow["value"])

    colors_raw = filter_set.bound_forms["color_form"].cleaned_data
    colors = {key: value for key, value in zip(colors_raw["color_key"], colors_raw["color_value"])}
    node_colors = [get_color(label) for label in labels]

    # Map colors to links based on their source node with reduced opacity
    link_colors = [get_color(labels[src], opacity=0.25) for src in source]
    unit = get_unit_from_data(data)
    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="fixed",
                valueformat=".0f",
                valuesuffix=unit,
                # Define nodes
                node=dict(
                    pad=15,
                    thickness=15,
                    line=dict(color="black", width=0.5),
                    label=labels,
                    color=node_colors,
                ),
                # Add links
                link=dict(source=source, target=target, value=value, label=label, color=link_colors),
            )
        ]
    )

    # font_size = filter_set.plot_options.get("font_size", 10)
    # title_text = filter_set.plot_options.get("title_text", "Flows")
    # fig.update_layout(
    #     title_text=title_text,
    #     font_size=font_size,
    # )
    return fig


CHART_DATA = {
    "bar": {"chart_function": bar_plot, "form_class": BarGraphFilterSet},
    "sankey": {"chart_function": sankey, "form_class": SankeyGraphFilterSet},
    "line": {"chart_function": line_plot, "form_class": LineGraphFilterSet},
}


def hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = hex_color * 2
    return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
