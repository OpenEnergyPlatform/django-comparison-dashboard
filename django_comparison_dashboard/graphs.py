import math

import numpy as np
import pandas
import pandas as pd
from plotly import express as px
from plotly import graph_objects as go

from .forms import BarGraphFilterSet, LineGraphFilterSet, SankeyGraphFilterSet
from .settings import GRAPHS_DEFAULT_LAYOUT, GRAPHS_DEFAULT_TEMPLATE


class PlottingError(Exception):
    """Thrown if plotting goes wrong"""


def get_logarithmic_range(max_value):
    return [0, math.ceil(math.log10(max_value))]


def get_empty_fig():
    empty_fig = px.bar()
    empty_fig.update_layout(template=GRAPHS_DEFAULT_TEMPLATE, **GRAPHS_DEFAULT_LAYOUT)
    return empty_fig


def add_unit_to_label(label, data):
    if isinstance(data.columns, pandas.MultiIndex):
        units = data.columns.get_level_values("unit").unique()
    else:
        units = data["unit"].unique()
    if len(units) == 1:
        return f"{label} [{units[0]}]"
    return label


def bar_plot(data: pd.DataFrame, filter_set: BarGraphFilterSet):
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
    data = data.to_dict(orient="records")
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


def line_plot(data, filter_set: LineGraphFilterSet):
    data = data.to_dict(orient="records")
    try:
        fig = px.line(data, **filter_set.plot_options)
    except ValueError as ve:
        if str(ve) == "nan is not in list":
            raise PlottingError(
                f"Scalar plot error: {ve} "
                + "(This might occur due to 'nan' values in data. Please check data via 'Show data')",
            )
        else:
            raise PlottingError(f"Scalar plot error: {ve}")

    return fig

    # xaxis_title = options.pop("xaxis_title") or "Timeindex"
    # yaxis_title = options.pop("yaxis_title") or add_unit_to_label("", data)
    # legend_title = options.pop("legend_title")
    #
    # fig_options = ChainMap(
    #     options, GRAPHS_DEFAULT_OPTIONS["timeseries"]["line"].get_defaults(exclude_non_plotly_options=True)
    # )
    # data = trim_timeseries(data)
    # data.columns = [COLUMN_JOINER.join(map(str, column)) for column in data.columns]
    # fig_options["y"] = [column for column in data.columns]
    # try:
    #     fig = px.line(data.reset_index(), x="index", **fig_options)
    # except ValueError as ve:
    #     raise PlottingError(f"Timeseries plot error: {ve}")
    # fig.update_xaxes(
    #     rangeslider_visible=True,
    #     rangeselector={
    #         "buttons": [
    #             {"count": 1, "label": "1d", "step": "day", "stepmode": "backward"},
    #             {"count": 7, "label": "1w", "step": "day", "stepmode": "backward"},
    #             {"count": 1, "label": "1m", "step": "month", "stepmode": "backward"},
    #             {"count": 6, "label": "6m", "step": "month", "stepmode": "backward"},
    #             {"step": "all"},
    #         ]
    #     },
    # )
    #
    # fig.update_layout(
    #     yaxis_title=yaxis_title,
    #     xaxis_title=xaxis_title,
    #     legend_title=legend_title,
    #     template=GRAPHS_DEFAULT_TEMPLATE,
    #     **GRAPHS_DEFAULT_LAYOUT,
    # )
    # fig.update_xaxes(GRAPHS_DEFAULT_XAXES_LAYOUT)
    # fig.update_yaxes(GRAPHS_DEFAULT_YAXES_LAYOUT)
    # return fig


def sankey(data, filter_set: SankeyGraphFilterSet):
    """
    Return a dict containing the options for a plotly sankey diagram

    Nodes can be set via graph options, input and output commodities
    """
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

    font_size = filter_set.plot_options.get("font_size", 10)
    title_text = filter_set.plot_options.get("title_text", "Flows")
    fig.update_layout(
        title_text=title_text,
        font_size=font_size,
    )
    return fig


CHART_DATA = {
    "bar": {"chart_function": bar_plot, "form_class": BarGraphFilterSet},
    "sankey": {"chart_function": sankey, "form_class": SankeyGraphFilterSet},
    "line": {"chart_function": line_plot, "form_class": LineGraphFilterSet},
}
