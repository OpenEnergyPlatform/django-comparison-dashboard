import math

import numpy as np
import pandas as pd
import random
from plotly import express as px
from plotly import graph_objects as go

from .forms import BarGraphFilterSet, LineGraphFilterSet, PlotFilterSet, SankeyGraphFilterSet
from .settings import (
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
    value_axis = (
        "x" if "orientation" in filter_set.plot_options and filter_set.plot_options["orientation"] == "h" else "y"
    )
    unit = get_unit_from_data(data)
    if value_axis == "x" and not xaxis_title:
        layout["xaxis_title"] = (
            filter_set.plot_options["x"] if unit is None else f"{filter_set.plot_options['x']} [{unit}]"
        )
    if value_axis == "y" and not yaxis_title:
        layout["yaxis_title"] = (
            filter_set.plot_options["y"] if unit is None else f"{filter_set.plot_options['y']} [{unit}]"
        )
    if xaxis_title:
        figure.update_xaxes(title=xaxis_title)
    if yaxis_title:
        figure.update_yaxes(row=1, col=1, title=yaxis_title)

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

    node_colors = [
        f'rgba{(*hex_to_rgb(color_dict[label]), 16)}'
        if label in color_dict else
        f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.75)'
        for label in labels
    ]

    # Map colors to links based on their source node with reduced opacity (alpha = 0.5)
    link_colors = [
        f'rgba({int(color_dict[labels[src]][1:3], 16)}, {int(color_dict[labels[src]][3:5], 16)}, {int(color_dict[labels[src]][5:7], 16)}, 0.25)'
        if labels[src] in color_dict else
        f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.25)'
        for src in source
    ]

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
                    color=node_colors,
                ),
                # Add links
                link=dict(
                    source=source,
                    target=target,
                    value=value,
                    label=label,
                    color=link_colors
                ),
            )
        ]
    )

    font_size = filter_set.plot_options.get("font_size", 10)
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

# Define the color dictionary
color_dict = {
    "pri_solar_radiation": "#FFC000",
    "pri_wind_energy": "#77D5E0",
    "pri_hydro_energy": "#0070C0",
    "pri_hydro_nat_inflow": "#0070C0",
    "pri_geoth_heat": "#EE0056",
    "pri_envir_heat": "#EE0056",
    "pri_biomass_stemwood": "#36BA19",
    "pri_biomass_pellets_pp": "#36BA20",
    "pri_biomass_wood_chips_pp": "#36BA21",
    "pri_biomass_wood_chips_pr": "#36BA22",
    "pri_biomass_straw_bales_pr": "#36BA23",
    "pri_biomass_wood_chips_sr": "#36BA24",
    "pri_biomass_pellets_sr": "#36BA25",
    "pri_waste_other_bio_sr": "#36BA26",
    "pri_waste_municipal_bio": "#36BA27",
    "pri_waste_wood": "#36BA28",
    "pri_waste_animal": "#36BA29",
    "pri_sewage_gas": "#36BA30",
    "pri_sewage_sludge": "#36BA31",
    "pri_waste_non_bio": "#7D823A",
    "pri_landfill_gas": "#7D823A",
    "pri_cbm": "#7D823A",
    "pri_natural_gas": "#ED7DD7",
    "pri_coal": "#A6A6A6",
    "pri_crude_oil": "#916123",
    "pri_uran": "#FFFFFF",
    "pri_deuterium": "#FFFFFF",
    "sec_elec": "#FFFF00",
    "sec_elec_ind": "#FFFF00",
    "sec_elec_wallbox": "#FFFF00",
    "sec_elec_battery": "#FFFF00",
    "sec_biogas": "#ED7DD7",
    "sec_natural_gas_syn": "#ED7DD7",
    "sec_lng": "#ED7DD7",
    "sec_lng_orig": "#ED7DD7",
    "sec_cng": "#ED7DD7",
    "sec_cng_orig": "#ED7DD7",
    "sec_lpg": "#ED7DD7",
    "sec_lpg_orig": "#ED7DD7",
    "sec_methane": "#ED7DD7",
    "sec_methane_orig": "#ED7DD7",
    "sec_hydrogen": "#7E4AA8",
    "sec_hydrogen_orig": "#7E4AA8",
    "sec_syngas": "#7E4AA8",
    "sec_syngas_sr": "#7E4AA8",
    "sec_heating_oil": "#916123",
    "sec_heavy_fuel_oil": "#916123",
    "sec_heavy_fuel_oil_orig": "#916123",
    "sec_diesel": "#439b80",
    "sec_diesel_orig": "#439b80",
    "sec_diesel_fos_orig": "#439b80",
    "sec_diesel_syn_orig": "#439b80",
    "sec_biodiesel_orig": "#439b80",
    "sec_gasoline": "#439b80",
    "sec_gasoline_orig": "#439b80",
    "sec_gasoline_fos_orig": "#439b80",
    "sec_gasoline_syn_orig": "#439b80",
    "sec_ammonia": "#439b80",
    "sec_ammonia_orig": "#439b80",
    "sec_naphtha": "#439b80",
    "sec_naphtha_orig": "#439b80",
    "sec_naphtha_syn_orig": "#439b80",
    "sec_naphtha_fos_orig": "#439b80",
    "sec_kerosene": "#439b80",
    "sec_kerosene_orig": "#439b80",
    "sec_kerosene_fos_orig": "#439b80",
    "sec_kerosene_syn_orig": "#439b80",
    "sec_biokerosene_orig": "#9CD4C3",
    "sec_ethanol": "#9CD4C3",
    "sec_ethanol_orig": "#9CD4C3",
    "sec_methanol": "#9CD4C3",
    "sec_methanol_orig": "#9CD4C3",
    "sec_biomethanol_orig": "#9CD4C3",
    "sec_heat_low": "#EE0056",
    "sec_heat_high": "#EE0056",
    "sec_heat_district_low_hh": "#EE0056",
    "sec_heat_district_high_hh": "#EE0056",
    "sec_heat_district_low_cts": "#EE0056",
    "sec_heat_district_high_cts": "#EE0056",
    "sec_heat_district_high_ind": "#EE0056",
    "sec_saving": "#EE0056",
    "sec_waste_heat_high_chemi": "#EE0056",
    "sec_waste_heat_high_cement": "#EE0056",
    "sec_waste_heat_high_glass": "#EE0056",
    "sec_waste_heat_low_aluminum": "#EE0056",
    "sec_waste_heat_low_copper": "#EE0056",
    "sec_waste_heat_low_paper": "#EE0056",
    "exo_air_pkm": "#ED7D31",
    "exo_air_natio_pkm": "#ED7D31",
    "exo_air_europ_pkm": "#ED7D31",
    "exo_air_inter_pkm": "#ED7D31",
    "exo_rail_pkm": "#ED7D31",
    "exo_rail_short_pkm": "#ED7D31",
    "exo_rail_long_pkm": "#ED7D31",
    "exo_rail_tkm": "#ED7D31",
    "exo_rail_short_tkm": "#ED7D31",
    "exo_rail_long_tkm": "#ED7D31",
    "exo_rail_coal_pkm": "#ED7D31",
    "exo_water_tkm": "#ED7D31",
    "exo_road_car_pkm": "#ED7D31",
    "exo_road_lcar_pkm": "#ED7D31",
    "exo_road_mcar_pkm": "#ED7D31",
    "exo_road_hcar_pkm": "#ED7D31",
    "exo_road_motorc_pkm": "#ED7D31",
    "exo_road_truck_tkm": "#ED7D31",
    "exo_road_ltruck_tkm": "#ED7D31",
    "exo_road_mtruck_tkm": "#ED7D31",
    "exo_road_htruck_tkm": "#ED7D31",
    "exo_road_bus_pkm": "#ED7D31",
    "exo_road_bus_short_pkm": "#ED7D31",
    "exo_road_bus_long_pkm": "#ED7D31",
    "exo_road_agri_diesel": "#ED7D31",
    "exo_road_const_diesel": "#ED7D31",
    "exo_hh_space_heat": "#F4AF80",
    "exo_hh_hot_water": "#F4AF80",
    "exo_hh_space_cooling": "#F4AF80",
    "exo_hh_re1_space_heat": "#F4AF80",
    "exo_hh_re1_hot_water": "#F4AF80",
    "exo_hh_re1_space_cooling": "#F4AF80",
    "exo_hh_re2_space_heat": "#F4AF80",
    "exo_hh_re2_hot_water": "#F4AF80",
    "exo_hh_re2_space_cooling": "#F4AF80",
    "exo_hh_re3_space_heat": "#F4AF80",
    "exo_hh_re3_hot_water": "#F4AF80",
    "exo_hh_re3_space_cooling": "#F4AF80",
    "exo_hh_rn1_space_heat": "#F4AF80",
    "exo_hh_rn1_hot_water": "#F4AF80",
    "exo_hh_rn1_space_cooling": "#F4AF80",
    "exo_hh_ue1_space_heat": "#F4AF80",
    "exo_hh_ue1_hot_water": "#F4AF80",
    "exo_hh_ue1_space_cooling": "#F4AF80",
    "exo_hh_ue2_space_heat": "#F4AF80",
    "exo_hh_ue2_hot_water": "#F4AF80",
    "exo_hh_ue2_space_cooling": "#F4AF80",
    "exo_hh_ue3_space_heat": "#F4AF80",
    "exo_hh_ue3_hot_water": "#F4AF80",
    "exo_hh_ue3_space_cooling": "#F4AF80",
    "exo_hh_un1_space_heat": "#F4AF80",
    "exo_hh_un1_hot_water": "#F4AF80",
    "exo_hh_un1_space_cooling": "#F4AF80",
    "exo_hh_me1_space_heat": "#F4AF80",
    "exo_hh_me1_hot_water": "#F4AF80",
    "exo_hh_me1_space_cooling": "#F4AF80",
    "exo_hh_me2_space_heat": "#F4AF80",
    "exo_hh_me2_hot_water": "#F4AF80",
    "exo_hh_me2_space_cooling": "#F4AF80",
    "exo_hh_me3_space_heat": "#F4AF80",
    "exo_hh_me3_hot_water": "#F4AF80",
    "exo_hh_me3_space_cooling": "#F4AF80",
    "exo_hh_mn1_space_heat": "#F4AF80",
    "exo_hh_mn1_hot_water": "#F4AF80",
    "exo_hh_mn1_space_cooling": "#F4AF80",
    "exo_cts_space_heat": "#F4AF80",
    "exo_cts_hot_water": "#F4AF80",
    "exo_cts_space_cooling": "#F4AF80",
    "exo_cts_proc_cooling": "#F4AF80",
    "exo_cts_t1e_space_heat": "#F4AF80",
    "exo_cts_t1e_hot_water": "#F4AF80",
    "exo_cts_t1e_space_cooling": "#F4AF80",
    "exo_cts_t1n_space_heat": "#F4AF80",
    "exo_cts_t1n_hot_water": "#F4AF80",
    "exo_cts_t1n_space_cooling": "#F4AF80",
    "exo_cts_t2e_space_heat": "#F4AF80",
    "exo_cts_t2e_hot_water": "#F4AF80",
    "exo_cts_t2e_space_cooling": "#F4AF80",
    "exo_cts_t2n_space_heat": "#F4AF80",
    "exo_cts_t2n_hot_water": "#F4AF80",
    "exo_cts_t2n_space_cooling": "#F4AF80",
    "exo_aluminum": "#C85C12",
    "exo_cement": "#C85C12",
    "exo_copper": "#C85C12",
    "exo_glass_cont": "#C85C12",
    "exo_glass_fibe": "#C85C12",
    "exo_glass_flat": "#C85C12",
    "exo_glass_spec": "#C85C12",
    "exo_paper_hq": "#C85C12",
    "exo_paper_lq": "#C85C12",
    "exo_steel": "#C85C12",
    "exo_auto_pc_icev": "#C85C12",
    "exo_auto_pc_phev": "#C85C12",
    "exo_auto_pc_bev": "#C85C12",
    "exo_auto_pc_fcev": "#C85C12",
    "exo_auto_lcv_icev": "#C85C12",
    "exo_auto_lcv_bev": "#C85C12",
    "exo_auto_lcv_fcev": "#C85C12",
    "exo_auto_hcv_icev": "#C85C12",
    "exo_auto_hcv_bev": "#C85C12",
    "exo_auto_hcv_fcev": "#C85C12",
    "exo_chemi_olefins": "#C85C12",
    "exo_chemi_btx": "#C85C12",
    "exo_chemi_nh3": "#C85C12",
    "exo_chemi_cl2": "#C85C12",
    "exo_chemi_methanol": "#C85C12",
    "exo_chemi_others": "#C85C12",
    "exo_other_ind": "#C85C12",
    "exo_cooling_normal": "#C85C12",
    "exo_space_heat": "#C85C12",
    "exo_agri_livestock": "#C85C12",
    "iip_aluminum_alumina": "#9999CC",
    "iip_aluminum_crude": "#9999CC",
    "iip_aluminum_scrap": "#9999CC",
    "iip_auto_btry_hcv_bev": "#9999CC",
    "iip_auto_btry_hcv_fcev": "#9999CC",
    "iip_auto_btry_hcv_icev": "#9999CC",
    "iip_auto_btry_lcv_bev": "#9999CC",
    "iip_auto_btry_lcv_fcev": "#9999CC",
    "iip_auto_btry_lcv_icev": "#9999CC",
    "iip_auto_btry_pc_bev": "#9999CC",
    "iip_auto_btry_pc_fcev": "#9999CC",
    "iip_auto_btry_pc_icev": "#9999CC",
    "iip_auto_btry_pc_phev": "#9999CC",
    "iip_auto_heat_proc": "#9999CC",
    "iip_auto_hot_water": "#9999CC",
    "iip_auto_hvlt": "#9999CC",
    "iip_auto_mcmp": "#9999CC",
    "iip_auto_painted_hcv_bev": "#9999CC",
    "iip_auto_painted_hcv_fcev": "#9999CC",
    "iip_auto_painted_hcv_icev": "#9999CC",
    "iip_auto_painted_lcv_bev": "#9999CC",
    "iip_auto_painted_lcv_fcev": "#9999CC",
    "iip_auto_painted_lcv_icev": "#9999CC",
    "iip_auto_painted_pc_bev": "#9999CC",
    "iip_auto_painted_pc_fcev": "#9999CC",
    "iip_auto_painted_pc_icev": "#9999CC",
    "iip_auto_painted_pc_phev": "#9999CC",
    "iip_auto_parts_hcv_bev": "#9999CC",
    "iip_auto_parts_hcv_fcev": "#9999CC",
    "iip_auto_parts_hcv_icev": "#9999CC",
    "iip_auto_parts_lcv_bev": "#9999CC",
    "iip_auto_parts_lcv_fcev": "#9999CC",
    "iip_auto_parts_lcv_icev": "#9999CC",
    "iip_auto_parts_pc_bev": "#9999CC",
    "iip_auto_parts_pc_fcev": "#9999CC",
    "iip_auto_parts_pc_icev": "#9999CC",
    "iip_auto_parts_pc_phev": "#9999CC",
    "iip_auto_space_heat": "#9999CC",
    "iip_auto_steam": "#9999CC",
    "iip_biogas_ind": "#9999CC",
    "iip_black_liquor": "#9999CC",
    "iip_blafu_gas": "#9999CC",
    "iip_cement_clinker": "#9999CC",
    "iip_cement_rawmeal": "#9999CC",
    "iip_chemi_biomass": "#9999CC",
    "iip_chemi_biomethanol": "#9999CC",
    "iip_chemi_electro_chem": "#9999CC",
    "iip_chemi_heavy_fuel_oil": "#9999CC",
    "iip_chemi_machine_drive": "#9999CC",
    "iip_chemi_meoh_f_h2": "#9999CC",
    "iip_chemi_meoh_h2": "#9999CC",
    "iip_chemi_methane": "#9999CC",
    "iip_chemi_methanol": "#9999CC",
    "iip_chemi_naphtha": "#9999CC",
    "iip_chemi_nh3_h2": "#9999CC",
    "iip_chemi_mtg_mtk_h2": "#9999CC",
    "iip_chemi_lpg": "#9999CC",
    "iip_chemi_processes_others": "#9999CC",
    "iip_chemi_process_heat": "#9999CC",
    "iip_chemi_steam": "#9999CC",
    "iip_coke": "#9999CC",
    "iip_coke_oven_gas": "#9999CC",
    "iip_copper_crude": "#9999CC",
    "iip_copper_scrap": "#9999CC",
    "iip_elec": "#9999CC",
    "iip_glass_cont_batch": "#9999CC",
    "iip_glass_cont_melt": "#9999CC",
    "iip_glass_flat_batch": "#9999CC",
    "iip_glass_flat_form": "#9999CC",
    "iip_glass_flat_melt": "#9999CC",
    "iip_heat_proc": "#9999CC",
    "iip_hot_water": "#9999CC",
    "iip_paper_pulp": "#9999CC",
    "iip_paper_recycle": "#9999CC",
    "iip_sludge": "#9999CC",
    "iip_steam": "#9999CC",
    "iip_steel_blafu_slag": "#9999CC",
    "iip_steel_crudesteel": "#9999CC",
    "iip_steel_iron_ore": "#9999CC",
    "iip_steel_iron_pellets": "#9999CC",
    "iip_steel_oxygen": "#9999CC",
    "iip_steel_raw_iron": "#9999CC",
    "iip_steel_scrap": "#9999CC",
    "iip_steel_scrap_iron": "#9999CC",
    "iip_steel_sinter": "#9999CC",
    "iip_steel_sponge_iron": "#9999CC",
    "iip_heat_high": "#9999CC",
    "iip_heat_high_other": "#9999CC",
    "emi_co2_f_pow": "#A6A6A6",
    "emi_co2_f_hea": "#A6A6A6",
    "emi_co2_f_x2x": "#A6A6A6",
    "emi_co2_f_tra": "#A6A6A6",
    "emi_co2_f_ind": "#A6A6A6",
    "emi_co2_p_ind": "#A6A6A6",
    "emi_co2_p_x2x": "#A6A6A6",
    "emi_ch4_f_pow": "#A6A6A6",
    "emi_ch4_f_hea": "#A6A6A6",
    "emi_ch4_f_x2x": "#A6A6A6",
    "emi_ch4_p_x2x": "#A6A6A6",
    "emi_ch4_f_tra": "#A6A6A6",
    "emi_ch4_f_ind": "#A6A6A6",
    "emi_ch4_p_ind": "#A6A6A6",
    "emi_n2o_f_ind": "#A6A6A6",
    "emi_n2o_f_pow": "#A6A6A6",
    "emi_n2o_f_hea": "#A6A6A6",
    "emi_n2o_f_tra": "#A6A6A6",
    "emi_n2o_f_x2x": "#A6A6A6",
    "emi_n2o_p_x2x": "#A6A6A6",
    "emi_co2_neg_air_dacc": "#A6A6A6",
    "emi_co2_neg_fuel_cc_pow": "#A6A6A7",
    "emi_co2_neg_fuel_cc_ind": "#A6A6A7",
    "emi_co2_neg_fuel_cc_x2x": "#A6A6A7",
    "emi_co2_neg_proc_cc_ind": "#A6A6A7",
    "emi_co2_neg_air_bio": "#A6A6A6",
    "emi_co2_neg_imp": "#A6A6A6",
    "emi_co2_reusable": "#A6A6A6",
    "emi_co2_stored": "#A6A6A6"
}