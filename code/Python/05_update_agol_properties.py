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
layer_seq = [1]
rs_layer_list = ["RS_{id:03d}".format(id=i) for i in layer_seq]
print(rs_layer_list)


# i = rs_layer_list[0]
for i in rs_layer_list:
    print("STARTING RS LAYER: " + i)
    data_type = metadata.at[i, "Data type"]
    if data_type == "Raster":
        layer_list = gis.content.search(query=i + "*", item_type="Image Service")
    elif data_type == "Vector":
        layer_list = gis.content.search(query=i + "*", item_type="Feature Layer")

    # j = layer_list[0]
    for j in layer_list:
        print("STARTING LAYER: " + j.title)
        tags = metadata.at[i, "Tags"].split(", ")
        print(tags)
        cats = "/Categories/" + metadata.at[i, "Categories"]
        print(cats)
        description = metadata.at[i, "Description"]
        print(description)
        snippet = metadata.at[i, "Snippet"]
        print(snippet)

        j.update(item_properties={
            "snippet": snippet,
            "description": description,
            "tags": tags,
            "accessInformation": "Natural State (citation).",
            "licenseInfo": "This layer is licensed under the GNU General Public License v3.0."
        })

        # Add thumbnail
        # j.update(item_properties={
        #     "snippet": snippet,
        #     "description": description,
        #     "tags": tags,
        #     "accessInformation": "Natural State (citation).",
        #     "licenseInfo": "This layer is licensed under the GNU General Public License v3.0."
        # }, thumbnail=r"H:\My Drive\ArcPro projects\GEE export layers\thumbnails\thumb_npp.png")

        gis.content.categories.assign_to_items(items=[{j.itemid: {
            "categories": [cats]}}])

        print("LAYER COMPLETE:" + j.title)
    print("RS GROUP COMPLETE:" + i)
