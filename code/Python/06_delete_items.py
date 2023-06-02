import agol_dirs as dirs
from arcgis.gis import GIS
import pandas as pd

# Connect to AGOL
gis = GIS("https://naturalstate.maps.arcgis.com/", "dhenry_naturalstate", "mX!!49&aOfGNva")
type(gis)
gis.admin.license.all()

# Read in metadata
metadata = pd.read_excel(dirs.metadata_dir, sheet_name="AGOL_properties")
metadata = metadata.set_index("Layer ID")

# Choose layers to upload: sequence with start and end points
# start, end = 59, 61
# rs_layer_list = ["RS_{id:03d}".format(id=i) for i in range(start, end + 1)]
# print(rs_layer_list)

# Choose layers to upload: custom sequence
layer_seq = [40]
rs_layer_list = ["RS_{id:03d}".format(id=i) for i in layer_seq]
print(rs_layer_list)


# i = rs_layer_list[0]
for i in rs_layer_list:
    print("STARTING RS LAYER: " + i)
    data_type = metadata.at[i, "Data type"]

    if data_type == "Raster":
        layer_list = gis.content.search(query=i + "*", item_type="Image Service")
    elif data_type == "Vector":
        feature_list = gis.content.search(query=i + "*", item_type="Feature Layer")
        shp_list = gis.content.search(query=i + "*", item_type="Shapefile")
        layer_list = [feature_list[0], shp_list[0]] if len(feature_list) > 0 else []
    else:
        layer_list = []

    if len(layer_list) == 0:
        print("NO LAYERS FOUND FOR: " + i)
    elif len(layer_list) > 0:
        gis.content.delete_items(items=layer_list)
        print("RS GROUP DELETED: " + i)
