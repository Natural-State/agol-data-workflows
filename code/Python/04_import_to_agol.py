import agol_dirs as dirs
from arcgis.gis import GIS
from arcgis.raster.analytics import copy_raster
import re
import os
import pandas as pd
import glob

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
layer_seq = [1]
rs_layer_list = ["RS_{id:03d}".format(id=i) for i in layer_seq]
print(rs_layer_list)

# i = rs_layer_list[0]
for i in rs_layer_list:
    print("STARTING RS LAYER: " + i)
    folder_dir = metadata.at[i, "GDB"]
    data_type = metadata.at[i, "Data type"]
    file_ext = "*.tif" if data_type == "Raster" else "*.zip"
    lyr_pattern = "*" + i + file_ext
    layer_list = glob.glob(os.path.join(dirs.api_input_dir, folder_dir, lyr_pattern))

    # j = layer_list[0]
    for j in layer_list:
        print("STARTING FILE:" + j)
        tags = metadata.at[i, "Tags"].split(", ")
        print(tags)
        cats = "/Categories/" + metadata.at[i, "Categories"]
        print(cats)
        description = metadata.at[i, "Description"]
        print(description)
        snippet = metadata.at[i, "Snippet"]
        print(snippet)
        match = re.search(r'\\([^\\]*)\.tif$', j) if data_type == "Raster" else re.search(r'\\([^\\]*)\.zip$', j)
        layer_name = match.group(1)
        print(layer_name)

        if data_type == "Raster":
            layer_search = gis.content.search(query=layer_name, item_type="Image Service")
        elif data_type == "Vector":
            layer_search = gis.content.search(query=layer_name, item_type="Feature Layer")

        if len(layer_search) == 0:
            if data_type == "Raster":
                single_image_layer = copy_raster(input_raster=j,
                                                 output_name=layer_name,
                                                 folder=folder_dir,
                                                 gis=gis)

                single_image_layer.update(item_properties={
                    # "title": "new_title",
                    "snippet": snippet,
                    "description": description,
                    "tags": tags,
                    "accessInformation": "Natural State",
                    "licenseInfo": "This layer is licensed under the GNU General Public License v3.0."
                })

                gis.content.categories.assign_to_items(items=[{single_image_layer.itemid: {
                    "categories": [cats]}}])
                print("LAYER UPLOADED: " + layer_name)

            elif data_type == "Vector":
                shp_file = gis.content.add({}, j)
                published_service = shp_file.publish()
                published_service.move(folder_dir)
                shp_file.move(folder_dir)

                published_service.update(item_properties={
                    # "title": "new_title",
                    "snippet": snippet,
                    "description": description,
                    "tags": tags,
                    "accessInformation": "Natural State",
                    "licenseInfo": "This layer is licensed under the GNU General Public License v3.0."
                })

                gis.content.categories.assign_to_items(items=[{published_service.itemid: {
                    "categories": [cats]}}])
                print("LAYER UPLOADED: " + layer_name)

        elif len(layer_search) > 0:
            print("LAYER ALREADY EXISTS")
        print("FILE COMPLETE: " + j)
    print("RS LAYER COMPLETE: " + i)

# Update GIS Catalog file
metadata_file = gis.content.search(query="agol_layers_metadata")

if len(metadata_file) == 0:
    metadata_file = gis.content.add({"snippet": "Metadata for remote sensing layers"}, dirs.metadata_dir)
    print("Metadata uploaded")
else:
    metadata_file[0].update({"snippet": "Metadata for remote sensing layers"}, dirs.metadata_dir)
    print("Metadata updated")
