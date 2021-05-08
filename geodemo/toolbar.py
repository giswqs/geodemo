import os
import ipywidgets as widgets
from ipyleaflet import WidgetControl
from ipyfilechooser import FileChooser
from IPython.display import display


def main_toolbar(m):

    padding = "0px 0px 0px 5px"  # upper, right, bottom, left

    toolbar_button = widgets.ToggleButton(
        value=False,
        tooltip="Toolbar",
        icon="wrench",
        layout=widgets.Layout(width="28px", height="28px", padding=padding),
    )

    close_button = widgets.ToggleButton(
        value=False,
        tooltip="Close the tool",
        icon="times",
        button_style="primary",
        layout=widgets.Layout(height="28px", width="28px", padding=padding),
    )

    toolbar = widgets.HBox([toolbar_button])

    def close_click(change):
        if change["new"]:
            toolbar_button.close()
            close_button.close()
            toolbar.close()

    close_button.observe(close_click, "value")

    rows = 2
    cols = 2
    grid = widgets.GridspecLayout(
        rows, cols, grid_gap="0px", layout=widgets.Layout(width="62px")
    )

    icons = ["folder-open", "map", "gears", "map-marker"]

    for i in range(rows):
        for j in range(cols):
            grid[i, j] = widgets.Button(
                description="",
                button_style="primary",
                icon=icons[i * rows + j],
                layout=widgets.Layout(width="28px", padding="0px"),
            )

    toolbar = widgets.VBox([toolbar_button])

    def toolbar_click(change):
        if change["new"]:
            toolbar.children = [widgets.HBox([close_button, toolbar_button]), grid]
        else:
            toolbar.children = [toolbar_button]

    toolbar_button.observe(toolbar_click, "value")

    toolbar_ctrl = WidgetControl(widget=toolbar, position="topright")

    m.add_control(toolbar_ctrl)

    output = widgets.Output()
    output_ctrl = WidgetControl(widget=output, position="topright")

    buttons = widgets.ToggleButtons(
        value=None,
        options=["Apply", "Reset", "Close"],
        tooltips=["Apply", "Reset", "Close"],
        button_style="primary",
    )
    buttons.style.button_width = "80px"

    data_dir = os.path.abspath("./data")

    fc = FileChooser(data_dir)
    fc.use_dir_icons = True
    fc.filter_pattern = ["*.shp", "*.geojson"]

    filechooser_widget = widgets.VBox([fc, buttons])

    def button_click(change):
        if change["new"] == "Apply" and fc.selected is not None:
            if fc.selected.endswith(".shp"):
                m.add_shapefile(fc.selected, layer_name="Shapefile")
            elif fc.selected.endswith(".geojson"):
                m.add_geojson(fc.selected, layer_name="GeoJSON")
        elif change["new"] == "Reset":
            fc.reset()
        elif change["new"] == "Close":
            fc.reset()
            m.remove_control(output_ctrl)
            buttons.value = None

    buttons.observe(button_click, "value")

    def tool_click(b):
        with output:
            output.clear_output()
            if b.icon == "folder-open":
                display(filechooser_widget)
                m.add_control(output_ctrl)
            elif b.icon == "gears":
                import whiteboxgui.whiteboxgui as wbt

                if hasattr(m, "whitebox") and m.whitebox is not None:
                    if m.whitebox in m.controls:
                        m.remove_control(m.whitebox)

                tools_dict = wbt.get_wbt_dict()
                wbt_toolbox = wbt.build_toolbox(
                    tools_dict, max_width="800px", max_height="500px"
                )

                wbt_control = WidgetControl(widget=wbt_toolbox, position="bottomright")

                m.whitebox = wbt_control
                m.add_control(wbt_control)

            elif b.icon == "map-marker":
                fc = FileChooser(data_dir)
                fc.use_dir_icons = True
                fc.filter_pattern = ["*.csv"]

                x_widget = widgets.Dropdown(
                    description="X:",
                    layout=widgets.Layout(width="122px", padding="0px"),
                    style={"description_width": "initial"},
                )
                y_widget = widgets.Dropdown(
                    description="Y:",
                    layout=widgets.Layout(width="122px", padding="0px"),
                    style={"description_width": "initial"},
                )

                label_widget = widgets.Dropdown(
                    description="Label:",
                    layout=widgets.Layout(width="248px", padding="0px"),
                    style={"description_width": "initial"},
                )

                layer_widget = widgets.Text(
                    description="Layer name: ",
                    value="Marker cluster",
                    layout=widgets.Layout(width="248px", padding="0px"),
                    style={"description_width": "initial"},
                )

                btns = widgets.ToggleButtons(
                    value=None,
                    options=["Read data", "Display", "Close"],
                    tooltips=["Read data", "Display", "Close"],
                    button_style="primary",
                )
                btns.style.button_width = "80px"

                def btn_click(change):
                    if change["new"] == "Read data" and fc.selected is not None:
                        import pandas as pd

                        df = pd.read_csv(fc.selected)
                        col_names = df.columns.values.tolist()
                        x_widget.options = col_names
                        y_widget.options = col_names
                        label_widget.options = col_names

                        if "longitude" in col_names:
                            x_widget.value = "longitude"

                        if "latitude" in col_names:
                            y_widget.value = "latitude"

                        if "name" in col_names:
                            label_widget.value = "name"

                    elif change["new"] == "Display":

                        if x_widget.value is not None and (y_widget.value is not None):
                            m.add_points_from_csv(
                                fc.selected,
                                x=x_widget.value,
                                y=y_widget.value,
                                label=label_widget.value,
                                layer_name=layer_widget.value,
                            )

                    elif change["new"] == "Close":
                        fc.reset()
                        m.remove_control(output_ctrl)

                btns.observe(btn_click, "value")

                csv_widget = widgets.VBox(
                    [
                        fc,
                        widgets.HBox([x_widget, y_widget]),
                        label_widget,
                        layer_widget,
                        btns,
                    ]
                )

                display(csv_widget)
                m.add_control(output_ctrl)

    for i in range(rows):
        for j in range(cols):
            tool = grid[i, j]
            tool.on_click(tool_click)
