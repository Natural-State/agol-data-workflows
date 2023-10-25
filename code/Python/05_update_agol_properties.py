import agol_dirs as dirs
from arcgis.gis import GIS
import pandas as pd
import logging
from agol_credentials import agol_username, agol_password

# Set up logging config
logging.basicConfig(filename='logfile_05.log', filemode="w", level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Update-AGOL_properties logger')

# Silence other loggers
logger_azure = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
logger_azure.setLevel(logging.WARNING)

logger_arcgis = logging.getLogger("arcgis.geoprocessing._support")
logger_arcgis.setLevel(logging.WARNING)

# Connect to AGOL
gis = GIS("https://naturalstate.maps.arcgis.com/", agol_username, agol_password)
type(gis)
gis.admin.license.all()

# Read in metadata
metadata = pd.read_excel(dirs.metadata_dir, sheet_name="AGOL_properties")
metadata = metadata.set_index("Layer ID")
metadata = metadata.fillna("")

# Choose layers to upload: sequence with start and end points
start, end = 1, 77
rs_layer_list = ["RS_{id:03d}".format(id=i) for i in range(start, end + 1)]

# Choose layers to upload: custom sequence
# layer_seq = [1]
# rs_layer_list = ["RS_{id:03d}".format(id=i) for i in layer_seq]

# i = rs_layer_list[0]
for i in rs_layer_list:
    logger.info(f"Starting RS group: {i}")
    data_type = metadata.at[i, "Data type"]
    query_str = metadata.at[i, "Layer Shortname"]
    if data_type == "Raster":
        layer_list = gis.content.search(query=query_str + "*", item_type="Image Service", max_items=200)
    elif data_type == "Vector":
        layer_list = gis.content.search(query=query_str + "*", item_type="Feature Layer", max_items=200)

    # j = layer_list[0]
    for j in layer_list:
        logger.info(f"Starting layer: {j.title}")
        tags = metadata.at[i, "Tags"].split(", ")
        # print(tags)
        cats = "/Categories/" + metadata.at[i, "Realm"] + "/" + metadata.at[i, "Content"] + "/" + metadata.at[
            i, "Label"]
        cats = cats.rstrip("/")
        # print(cats)
        description = metadata.at[i, "Description"]
        # print(description)
        snippet = metadata.at[i, "Layer Name"]
        # print(snippet)

        j.update(item_properties={
            "snippet": snippet,
            "description": description,
            "tags": tags,
            "accessInformation": "Natural State (add citation).",
            "licenseInfo": "This layer is licensed under the GNU General Public License v3.0."
        })

        gis.content.categories.assign_to_items(items=[{j.itemid: {
            "categories": [cats]}}])

        logger.info(f"Layer updated: {j.title}")
    logger.info(f"RS group complete: {i}")
