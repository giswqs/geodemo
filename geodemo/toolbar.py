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
    grid = widgets.GridspecLayout(rows, cols, grid_gap="0px", layout=widgets.Layout(width="62px"))

    icons = ["folder-open", "map", "info", "question"]

    for i in range(rows):
        for j in range(cols):
            grid[i, j] = widgets.Button(description="", button_style="primary", icon=icons[i*rows+j], 
                                        layout=widgets.Layout(width="28px", padding="0px"))

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

    data_dir = os.path.abspath('./data')

    fc = FileChooser(data_dir)
    fc.use_dir_icons = True
    fc.filter_pattern = ['*.shp', '*.geojson']

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
    buttons.observe(button_click, "value")     

    def tool_click(b):    
        with output:
            output.clear_output()
            if b.icon == "folder-open":
                display(filechooser_widget)
                m.add_control(output_ctrl)

    for i in range(rows):
        for j in range(cols):
            tool = grid[i, j]
            tool.on_click(tool_click)