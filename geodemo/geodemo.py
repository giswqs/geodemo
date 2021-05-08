"""Main module for the geodemo package."""
import os
import ee
import ipyleaflet
from ipyleaflet import (
    FullScreenControl,
    LayersControl,
    DrawControl,
    MeasureControl,
    ScaleControl,
    TileLayer,
)
from .utils import random_string
from .common import ee_initialize, tool_template
from .toolbar import main_toolbar


class Map(ipyleaflet.Map):
    """This Map class inherits the ipyleaflet Map class.

    Args:
        ipyleaflet (ipyleaflet.Map): An ipyleaflet map.
    """

    def __init__(self, **kwargs):

        if "center" not in kwargs:
            kwargs["center"] = [40, -100]

        if "zoom" not in kwargs:
            kwargs["zoom"] = 4

        if "scroll_wheel_zoom" not in kwargs:
            kwargs["scroll_wheel_zoom"] = True

        super().__init__(**kwargs)

        if "height" not in kwargs:
            self.layout.height = "600px"
        else:
            self.layout.height = kwargs["height"]

        self.add_control(FullScreenControl())
        self.add_control(LayersControl(position="topright"))
        self.add_control(DrawControl(position="topleft"))
        self.add_control(MeasureControl())
        self.add_control(ScaleControl(position="bottomleft"))

        main_toolbar(self)

        if "google_map" not in kwargs:
            layer = TileLayer(
                url="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
                attribution="Google",
                name="Google Maps",
            )
            self.add_layer(layer)
        else:
            if kwargs["google_map"] == "ROADMAP":
                layer = TileLayer(
                    url="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
                    attribution="Google",
                    name="Google Maps",
                )
                self.add_layer(layer)
            elif kwargs["google_map"] == "HYBRID":
                layer = TileLayer(
                    url="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
                    attribution="Google",
                    name="Google Satellite",
                )
                self.add_layer(layer)

    def add_geojson(self, in_geojson, style=None, layer_name="Untitled"):
        """Adds a GeoJSON file to the map.

        Args:
            in_geojson (str): The file path to the input GeoJSON.
            style (dict, optional): The style for the GeoJSON layer. Defaults to None.
            layer_name (str, optional): The layer name for the GeoJSON layer. Defaults to "Untitled".

        Raises:
            FileNotFoundError: If the provided file path does not exist.
            TypeError: If the input geojson is not a str or dict.
        """

        import json

        if layer_name == "Untitled":
            layer_name = "Untitled " + random_string()

        if isinstance(in_geojson, str):

            if not os.path.exists(in_geojson):
                raise FileNotFoundError("The provided GeoJSON file could not be found.")

            with open(in_geojson) as f:
                data = json.load(f)

        elif isinstance(in_geojson, dict):
            data = in_geojson

        else:
            raise TypeError("The input geojson must be a type of str or dict.")

        if style is None:
            style = {
                "stroke": True,
                "color": "#000000",
                "weight": 2,
                "opacity": 1,
                "fill": True,
                "fillColor": "#0000ff",
                "fillOpacity": 0.4,
            }

        geo_json = ipyleaflet.GeoJSON(data=data, style=style, name=layer_name)
        self.add_layer(geo_json)

    def add_shapefile(self, in_shp, style=None, layer_name="Untitled"):
        """Adds a shapefile layer to the map.

        Args:
            in_shp (str): The file path to the input shapefile.
            style (dict, optional): The style dictionary. Defaults to None.
            layer_name (str, optional): The layer name for the shapefile layer. Defaults to "Untitled".
        """
        geojson = shp_to_geojson(in_shp)
        self.add_geojson(geojson, style=style, layer_name=layer_name)

    def add_points_from_csv(
        self,
        in_csv,
        x="longitude",
        y="latitude",
        label=None,
        layer_name="Marker cluster",
    ):
        """Adds points from a CSV file containing lat/lon information and display data on the map.

        Args:
            in_csv (str): The file path to the input CSV file.
            x (str, optional): The name of the column containing longitude coordinates. Defaults to "longitude".
            y (str, optional): The name of the column containing latitude coordinates. Defaults to "latitude".
            label (str, optional): The name of the column containing label information to used for marker popup. Defaults to None.
            layer_name (str, optional): The layer name to use. Defaults to "Marker cluster".

        Raises:
            FileNotFoundError: The specified input csv does not exist.
            ValueError: The specified x column does not exist.
            ValueError: The specified y column does not exist.
            ValueError: The specified label column does not exist.
        """
        import pandas as pd
        import ipywidgets as widgets
        from ipyleaflet import Marker, MarkerCluster

        if not os.path.exists(in_csv):
            raise FileNotFoundError("The specified input csv does not exist.")

        df = pd.read_csv(in_csv)
        col_names = df.columns.values.tolist()

        if x not in col_names:
            raise ValueError(f"x must be one of the following: {', '.join(col_names)}")

        if y not in col_names:
            raise ValueError(f"y must be one of the following: {', '.join(col_names)}")

        if label is not None and (label not in col_names):
            raise ValueError(
                f"label must be one of the following: {', '.join(col_names)}"
            )

        points = list(zip(df[y], df[x]))

        self.default_style = {"cursor": "wait"}
        if label is not None:
            labels = df[label]
            markers = [
                Marker(
                    location=point, draggable=False, popup=widgets.HTML(labels[index])
                )
                for index, point in enumerate(points)
            ]
        else:
            markers = [Marker(location=point, draggable=False) for point in points]

        marker_cluster = MarkerCluster(markers=markers, name=layer_name)
        self.add_layer(marker_cluster)
        self.default_style = {"cursor": "default"}

    def add_ee_layer(
        self, ee_object, vis_params={}, name=None, shown=True, opacity=1.0
    ):
        """Adds a given EE object to the map as a layer.
        Args:
            ee_object (Collection|Feature|Image|MapId): The object to add to the map.
            vis_params (dict, optional): The visualization parameters. Defaults to {}.
            name (str, optional): The name of the layer. Defaults to 'Layer N'.
            shown (bool, optional): A flag indicating whether the layer should be on by default. Defaults to True.
            opacity (float, optional): The layer's opacity represented as a number between 0 and 1. Defaults to 1.
        """

        ee_layer = ee_tile_layer(ee_object, vis_params, name, shown, opacity)
        self.add_layer(ee_layer)

    addLayer = add_ee_layer


def shp_to_geojson(in_shp, out_geojson=None):
    """Converts a shapefile to GeoJSON.

    Args:
        in_shp (str): The file path to the input shapefile.
        out_geojson (str, optional): The file path to the output GeoJSON. Defaults to None.

    Raises:
        FileNotFoundError: If the input shapefile does not exist.

    Returns:
        dict: The dictionary of the GeoJSON.
    """
    import json
    import shapefile

    in_shp = os.path.abspath(in_shp)

    if not os.path.exists(in_shp):
        raise FileNotFoundError("The provided shapefile could not be found.")

    sf = shapefile.Reader(in_shp)
    geojson = sf.__geo_interface__

    if out_geojson is None:
        return geojson
    else:
        out_geojson = os.path.abspath(out_geojson)
        out_dir = os.path.dirname(out_geojson)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        with open(out_geojson, "w") as f:
            f.write(json.dumps(geojson))


def csv_to_shp(in_csv, out_shp, x="longitude", y="latitude"):
    """Creates points for a CSV file and exports data as a shapefile.

    Args:
        in_csv (str): The file path to the input CSV file.
        out_shp (str): The file path to the exported shapefile.
        x (str, optional): The name of the column containing longitude coordinates. Defaults to "longitude".
        y (str, optional): The name of the column containing latitude coordinates. Defaults to "latitude".

    Raises:
        FileNotFoundError: The specified input csv does not exist.
        ValueError: The specified x column does not exist.
        ValueError: The specified y column does not exist.
        ValueError: The specified label column does not exist.
    """
    import pandas as pd
    import geopandas as gpd

    if not os.path.exists(in_csv):
        raise FileNotFoundError("The input csv does not exist.")

    if not out_shp.lower().endswith(".shp"):
        raise ValueError("out_shp must be a shapefile ending with .shp")

    out_dir = os.path.dirname(out_shp)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    df = pd.read_csv(in_csv)
    col_names = df.columns.values.tolist()

    if x not in col_names:
        raise ValueError(f"x must be one of the following: {', '.join(col_names)}")

    if y not in col_names:
        raise ValueError(f"y must be one of the following: {', '.join(col_names)}")

    gdf = gpd.GeoDataFrame(
        df, crs="epsg:4326", geometry=gpd.points_from_xy(df[x], df[y])
    )
    gdf.to_file(out_shp)


def csv_to_geojson(in_csv, out_geojson, x="longitude", y="latitude"):
    """Creates points for a CSV file and exports data as a GeoJSON.

    Args:
        in_csv (str): The file path to the input CSV file.
        out_geojson (str): The file path to the exported GeoJSON.
        x (str, optional): The name of the column containing longitude coordinates. Defaults to "longitude".
        y (str, optional): The name of the column containing latitude coordinates. Defaults to "latitude".

    Raises:
        FileNotFoundError: The specified input csv does not exist.
        ValueError: The specified x column does not exist.
        ValueError: The specified y column does not exist.
        ValueError: The specified label column does not exist.
    """
    import pandas as pd
    import geopandas as gpd

    if not os.path.exists(in_csv):
        raise FileNotFoundError("The input csv does not exist.")

    if not out_geojson.lower().endswith(".geojson"):
        raise ValueError("out_geojson must have the .geojson file extension.")

    out_dir = os.path.dirname(out_geojson)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    df = pd.read_csv(in_csv)
    col_names = df.columns.values.tolist()

    if x not in col_names:
        raise ValueError(f"x must be one of the following: {', '.join(col_names)}")

    if y not in col_names:
        raise ValueError(f"y must be one of the following: {', '.join(col_names)}")

    gdf = gpd.GeoDataFrame(
        df, crs="epsg:4326", geometry=gpd.points_from_xy(df[x], df[y])
    )
    gdf.to_file(out_geojson, driver="GeoJSON")


def ee_tile_layer(
    ee_object, vis_params={}, name="Layer untitled", shown=True, opacity=1.0
):
    """Converts and Earth Engine layer to ipyleaflet TileLayer.
    Args:
        ee_object (Collection|Feature|Image|MapId): The object to add to the map.
        vis_params (dict, optional): The visualization parameters. Defaults to {}.
        name (str, optional): The name of the layer. Defaults to 'Layer untitled'.
        shown (bool, optional): A flag indicating whether the layer should be on by default. Defaults to True.
        opacity (float, optional): The layer's opacity represented as a number between 0 and 1. Defaults to 1.
    """

    image = None

    if (
        not isinstance(ee_object, ee.Image)
        and not isinstance(ee_object, ee.ImageCollection)
        and not isinstance(ee_object, ee.FeatureCollection)
        and not isinstance(ee_object, ee.Feature)
        and not isinstance(ee_object, ee.Geometry)
    ):
        err_str = "\n\nThe image argument in 'addLayer' function must be an instace of one of ee.Image, ee.Geometry, ee.Feature or ee.FeatureCollection."
        raise AttributeError(err_str)

    if (
        isinstance(ee_object, ee.geometry.Geometry)
        or isinstance(ee_object, ee.feature.Feature)
        or isinstance(ee_object, ee.featurecollection.FeatureCollection)
    ):
        features = ee.FeatureCollection(ee_object)

        width = 2

        if "width" in vis_params:
            width = vis_params["width"]

        color = "000000"

        if "color" in vis_params:
            color = vis_params["color"]

        image_fill = features.style(**{"fillColor": color}).updateMask(
            ee.Image.constant(0.5)
        )
        image_outline = features.style(
            **{"color": color, "fillColor": "00000000", "width": width}
        )

        image = image_fill.blend(image_outline)
    elif isinstance(ee_object, ee.image.Image):
        image = ee_object
    elif isinstance(ee_object, ee.imagecollection.ImageCollection):
        image = ee_object.mosaic()

    map_id_dict = ee.Image(image).getMapId(vis_params)
    tile_layer = TileLayer(
        url=map_id_dict["tile_fetcher"].url_format,
        attribution="Google Earth Engine",
        name=name,
        opacity=opacity,
        visible=shown,
    )
    return tile_layer
