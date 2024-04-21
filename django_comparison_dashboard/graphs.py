import itertools
import math
import warnings
from collections import ChainMap

import numpy as np
import pandas
from plotly import express as px
from plotly import graph_objects as go

from .forms import BarGraphFilterSet
from .settings import (
    COLUMN_JOINER,
    GRAPHS_DEFAULT_LAYOUT,
    GRAPHS_DEFAULT_OPTIONS,
    GRAPHS_DEFAULT_TEMPLATE,
    GRAPHS_DEFAULT_XAXES_LAYOUT,
    GRAPHS_DEFAULT_YAXES_LAYOUT,
    GRAPHS_MAX_TS_PER_PLOT,
)


class PlottingError(Exception):
    """Thrown if plotting goes wrong"""


def get_logarithmic_range(max_value):
    return [0, math.ceil(math.log10(max_value))]


def get_empty_fig():
    empty_fig = px.bar()
    empty_fig.update_layout(template=GRAPHS_DEFAULT_TEMPLATE, **GRAPHS_DEFAULT_LAYOUT)
    return empty_fig


def trim_timeseries(timeseries, max_entries=GRAPHS_MAX_TS_PER_PLOT):
    if len(timeseries.columns) > max_entries:
        warnings.warn(
            f"Too many timeseries to plot; only {max_entries} series are plotted.",
        )
        timeseries = timeseries.loc[:, timeseries.columns[:max_entries]]
    return timeseries


def add_unit_to_label(label, data):
    if isinstance(data.columns, pandas.MultiIndex):
        units = data.columns.get_level_values("unit").unique()
    else:
        units = data["unit"].unique()
    if len(units) == 1:
        return f"{label} [{units[0]}]"
    return label


def get_scalar_plot(data, options):
    if options["type"] == "bar":
        return bar_plot(data, options["options"])
    elif options["type"] == "radar":
        return radar_plot(data, options["options"])
    elif options["type"] == "dot":
        return dot_plot(data, options["options"])


def bar_plot(data, filter_set: BarGraphFilterSet):
    # xaxis_title = options.pop("xaxis_title")
    # yaxis_title = options.pop("yaxis_title")
    # axis_type = options.pop("axis_type")
    # layout = {
    #     "showlegend": "showlegend" in options.pop("showlegend"),
    #     "legend_title": options.pop("legend_title"),
    #     "bargap": options.pop("bargap"),
    #     "margin_l": options.pop("margin_l"),
    #     "margin_r": options.pop("margin_r"),
    #     "margin_t": options.pop("margin_t"),
    #     "margin_b": options.pop("margin_b"),
    # }
    # subplot_label = options.pop("subplot_label")

    # fig_options = ChainMap(
    #     options, GRAPHS_DEFAULT_OPTIONS["scalars"]["bar"].get_defaults(exclude_non_plotly_options=True)
    # )
    # fig_options = {}
    try:
        fig = px.bar(data, **filter_set.plot_options)
    except ValueError as ve:
        if str(ve) == "nan is not in list":
            raise PlottingError(
                f"Scalar plot error: {ve} "
                + "(This might occur due to 'nan' values in data. Please check data via 'Show data')",
            )
        else:
            raise PlottingError(f"Scalar plot error: {ve}")

    return fig

    # # Plot Labels:
    # if subplot_label:
    #     if "," in subplot_label and len(subplot_label.split(",")) == len(fig.layout.annotations):
    #         label_iter = iter(subplot_label.split(","))
    #         fig.for_each_annotation(lambda a: a.update(text=next(label_iter)))
    #     else:
    #         fig.for_each_annotation(lambda a: a.update(text=f"{subplot_label} {a.text.split('=')[-1]}"))
    # else:
    #     fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    #
    # value_axis = "x" if fig_options["orientation"] == "h" else "y"
    # if value_axis == "x" and not xaxis_title:
    #     layout["xaxis_title"] = add_unit_to_label(fig_options["x"], data)
    # if value_axis == "y" and not yaxis_title:
    #     layout["yaxis_title"] = add_unit_to_label(fig_options["y"], data)
    # if xaxis_title:
    #     fig.update_xaxes(title=xaxis_title)
    # if yaxis_title:
    #     fig.update_yaxes(row=1, col=1, title=yaxis_title)
    #
    # # Axis Type:
    # axis = {"type": axis_type}
    # if axis_type == "log":
    #     max_value = max(data["value"])
    #     axis["range"] = get_logarithmic_range(max_value)
    # if value_axis == "x":
    #     fig.update_xaxes(**axis)
    # else:
    #     fig.update_yaxes(**axis)
    #
    # # Move legend above plot in subplots:
    # if fig_options["facet_col"]:
    #     fig.update_layout(legend={"orientation": "h", "yanchor": "bottom", "y": 1.06, "xanchor": "right", "x": 1})
    #
    # # Remove padding between stacked bars:
    # fig.update_traces(marker={"line": {"width": 0}})
    #
    # try:
    #     fig.update_layout(template=GRAPHS_DEFAULT_TEMPLATE, **layout, **GRAPHS_DEFAULT_LAYOUT)
    # except ValueError as ve:
    #     raise PlottingError(f"Scalar layout error: {ve}")
    # fig.update_xaxes(GRAPHS_DEFAULT_XAXES_LAYOUT)
    # fig.update_yaxes(GRAPHS_DEFAULT_YAXES_LAYOUT)
    # return fig


def radar_plot(data, options):
    def normalize_by_theta(series, tm):
        series["value"] = series["value"] / tm[series[options["theta"]]]
        return series

    axis_title = options.pop("axis_title") or add_unit_to_label(options["r"], data)
    layout = {
        "showlegend": "showlegend" in options.pop("showlegend"),
        "legend_title": options.pop("legend_title"),
        "margin_l": options.pop("margin_l"),
        "margin_r": options.pop("margin_r"),
        "margin_t": options.pop("margin_t"),
        "margin_b": options.pop("margin_b"),
    }
    normalize_theta = "normalize" in options.pop("normalize_theta")
    if normalize_theta:
        theta_max = data[[options["theta"], "value"]].groupby(options["theta"]).max()["value"]
        data = data.apply(normalize_by_theta, axis=1, args=[theta_max])

    fig_options = ChainMap(
        options, GRAPHS_DEFAULT_OPTIONS["scalars"]["radar"].get_defaults(exclude_non_plotly_options=True)
    )

    fig = px.line_polar(data, line_close=True, title=axis_title, **fig_options)

    fig.update_traces(line={"width": 4})

    fig.update_layout(
        template=GRAPHS_DEFAULT_TEMPLATE,
        polar={
            "radialaxis": {
                "gridwidth": 4,
                "linewidth": 4,
            },
            "angularaxis": {
                "gridwidth": 4,
                "linewidth": 4,
            },
        },
        **layout,
        **GRAPHS_DEFAULT_LAYOUT,
    )
    fig.update_xaxes(GRAPHS_DEFAULT_XAXES_LAYOUT)
    fig.update_yaxes(GRAPHS_DEFAULT_YAXES_LAYOUT)
    return fig


def dot_plot(data, options):
    y = data[options["y"]].unique()
    xaxis_title = options.pop("xaxis_title") or add_unit_to_label(options["x"], data)
    legend_title = options.pop("legend_title")

    fig = go.Figure()

    for category in data[options["color"]].unique():
        cat_data = data[data[options["color"]] == category][options["x"]]
        fig.add_trace(
            go.Scatter(
                x=cat_data,
                y=y,
                name=category,
            )
        )

    fig.update_traces(mode="markers", marker=dict(line_width=1, symbol="circle", size=16))
    fig.update_layout(
        xaxis_title=xaxis_title, legend_title=legend_title, template=GRAPHS_DEFAULT_TEMPLATE, **GRAPHS_DEFAULT_LAYOUT
    )
    fig.update_xaxes(GRAPHS_DEFAULT_XAXES_LAYOUT)
    fig.update_yaxes(GRAPHS_DEFAULT_YAXES_LAYOUT)
    return fig


def get_timeseries_plot(data, options):
    if options["type"] == "line":
        return line_plot(data, options["options"])
    elif options["type"] == "box":
        return box_plot(data, options["options"])
    elif options["type"] == "heat_map":
        return heat_map(data, options["options"])


def line_plot(data, options):
    xaxis_title = options.pop("xaxis_title") or "Timeindex"
    yaxis_title = options.pop("yaxis_title") or add_unit_to_label("", data)
    legend_title = options.pop("legend_title")

    fig_options = ChainMap(
        options, GRAPHS_DEFAULT_OPTIONS["timeseries"]["line"].get_defaults(exclude_non_plotly_options=True)
    )
    data = trim_timeseries(data)
    data.columns = [COLUMN_JOINER.join(map(str, column)) for column in data.columns]
    fig_options["y"] = [column for column in data.columns]
    try:
        fig = px.line(data.reset_index(), x="index", **fig_options)
    except ValueError as ve:
        raise PlottingError(f"Timeseries plot error: {ve}")
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector={
            "buttons": [
                {"count": 1, "label": "1d", "step": "day", "stepmode": "backward"},
                {"count": 7, "label": "1w", "step": "day", "stepmode": "backward"},
                {"count": 1, "label": "1m", "step": "month", "stepmode": "backward"},
                {"count": 6, "label": "6m", "step": "month", "stepmode": "backward"},
                {"step": "all"},
            ]
        },
    )

    fig.update_layout(
        yaxis_title=yaxis_title,
        xaxis_title=xaxis_title,
        legend_title=legend_title,
        template=GRAPHS_DEFAULT_TEMPLATE,
        **GRAPHS_DEFAULT_LAYOUT,
    )
    fig.update_xaxes(GRAPHS_DEFAULT_XAXES_LAYOUT)
    fig.update_yaxes(GRAPHS_DEFAULT_YAXES_LAYOUT)
    return fig


def box_plot(data, options):
    xaxis_title = options.pop("xaxis_title") or "Time"
    yaxis_title = options.pop("yaxis_title")
    legend_title = options.pop("legend_title")
    sample = options.pop("sample")
    fig_options = ChainMap(
        options, GRAPHS_DEFAULT_OPTIONS["timeseries"]["box"].get_defaults(exclude_non_plotly_options=True)
    )
    fig_options["x"] = "time"
    fig_options["y"] = "value"

    ts_resampled = data.resample(sample).sum()
    ts_resampled.index.name = "time"
    ts_unstacked = ts_resampled.unstack()
    ts_unstacked.name = "value"
    ts_flattened = ts_unstacked.reset_index()

    try:
        fig = px.box(ts_flattened, points="outliers", **fig_options)
    except ValueError as ve:
        raise PlottingError(f"Timeseries plot error: {ve}")

    fig.update_layout(
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title or add_unit_to_label(fig_options["y"], ts_flattened),
        legend_title=legend_title,
        template=GRAPHS_DEFAULT_TEMPLATE,
        **GRAPHS_DEFAULT_LAYOUT,
    )
    fig.update_xaxes(GRAPHS_DEFAULT_XAXES_LAYOUT)
    fig.update_yaxes(GRAPHS_DEFAULT_YAXES_LAYOUT)
    return fig


def heat_map(data, options):
    del options["color_discrete_map"]  # Not available in heat maps
    x = options.pop("x")
    y = options.pop("y")
    xaxis_title = options.pop("xaxis_title") or x
    yaxis_title = options.pop("yaxis_title") or y
    legend_title = options.pop("legend_title") or add_unit_to_label("Value", data)

    fig_options = ChainMap(
        options, GRAPHS_DEFAULT_OPTIONS["timeseries"]["heat_map"].get_defaults(exclude_non_plotly_options=True)
    )

    data.index.name = "time"
    ts_unstacked = data.unstack()
    ts_unstacked.name = "value"
    ts_flattened = ts_unstacked.reset_index()
    ts_flattened["day"] = ts_flattened["time"].apply(lambda time: time.day)
    ts_flattened["month"] = ts_flattened["time"].apply(lambda time: time.month)
    ts_flattened["year"] = ts_flattened["time"].apply(lambda time: time.year)
    ts_grouped = ts_flattened.groupby([x, y], as_index=False).sum()
    ts_pivot = ts_grouped.pivot(index=y, columns=x, values="value")

    try:
        fig = px.imshow(ts_pivot, labels={"x": xaxis_title, "y": yaxis_title, "color": legend_title}, **fig_options)
    except ValueError as ve:
        raise PlottingError(f"Timeseries plot error: {ve}")

    fig.update_xaxes(side="top")
    fig.update_layout(template=GRAPHS_DEFAULT_TEMPLATE, **GRAPHS_DEFAULT_LAYOUT)
    fig.update_xaxes(GRAPHS_DEFAULT_XAXES_LAYOUT)
    fig.update_yaxes(GRAPHS_DEFAULT_YAXES_LAYOUT)
    return fig


def sankey(data, options):
    """Return a dict to a plotly sankey diagram"""
    RESULTS_FILE = "/industry_scratch.csv"

    data = pandas.read_csv(RESULTS_FILE, delimiter=";")

    labels = set(data["process"]) | set(data["input_commodity"]) | set(data["output_commodity"])
    labels.discard(np.nan)
    labels = list(labels)

    imports = []
    primary = []
    secondary = []
    others = []

    for label in labels:
        if "import" in label:
            imports.append(label)
        elif label.startswith("pri"):
            primary.append(label)
        elif label.startswith("sec"):
            secondary.append(label)
        else:
            others.append(label)
    labels = imports + primary + secondary + others
    x = list(
        itertools.chain(
            itertools.repeat(0.1, len(imports)),
            itertools.repeat(0.2, len(primary)),
            itertools.repeat(None, len(secondary)),
            itertools.repeat(None, len(others)),
        )
    )
    y = (
        list(np.linspace(1 / len(imports), 1, len(imports) + 1, endpoint=False))
        + list(np.linspace(1 / len(primary), 1, len(primary) + 1, endpoint=False))
        + list(itertools.repeat(None, len(secondary)))
        + list(itertools.repeat(None, len(others)))
    )

    source = []
    target = []
    value = []
    label = []
    # color = []
    for _, flow in data.iterrows():
        if not isinstance(flow["input_commodity"], str):
            source.append(labels.index(flow["process"]))
            target.append(labels.index(flow["output_commodity"]))
            label.append(flow["output_commodity"])
        elif not isinstance(flow["output_commodity"], str):
            source.append(labels.index(flow["input_commodity"]))
            target.append(labels.index(flow["process"]))
            label.append(flow["input_commodity"])
        else:
            continue

        value.append(flow["value"])

    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="fixed",
                valueformat=".0f",
                valuesuffix="TWh",
                # Define nodes
                node=dict(
                    pad=15,
                    thickness=15,
                    line=dict(color="black", width=0.5),
                    label=labels,
                    x=x,
                    y=y,
                ),
                # Add links
                link=dict(
                    source=source,
                    target=target,
                    value=value,
                    label=label,
                ),
            )
        ]
    )

    fig.update_layout(
        title_text="Industriesektor",
        font_size=10,
    )
    return fig
