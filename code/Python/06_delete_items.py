import agol_dirs as dirs
from arcgis.gis import GIS
import pandas as pd
import logging
from agol_credentials import agol_username, agol_password

# Set up logging config
logging.basicConfig(filename='logfile_06.log', filemode="w", level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Delete-AGOL-items logger')

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
start, end = 74, 74
rs_layer_list = ["RS_{id:03d}".format(id=i) for i in range(start, end + 1)]

# Choose layers to delete: custom sequence
# layer_seq = [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 39, 40, 53, 71]
# rs_layer_list = ["RS_{id:03d}".format(id=i) for i in layer_seq]

# i = rs_layer_list[0]
for i in rs_layer_list:
    logger.info(f"Starting RS layer: {i}")
    data_type = metadata.at[i, "Data type"]
    query_str = metadata.at[i, "Layer Shortname"]
    if data_type == "Raster":
        layer_list = gis.content.search(query=query_str + "*", item_type="Image Service", max_items=200)
    elif data_type == "Vector":
        feature_list = gis.content.search(query=query_str + "*", item_type="Feature Layer", max_items=200)
        shp_list = gis.content.search(query=query_str + "*", item_type="Shapefile", max_items=200)
        layer_list = [feature_list[0], shp_list[0]] if len(feature_list) > 0 else []
    else:
        layer_list = []

    if len(layer_list) == 0:
        logger.warning(f"No layers found for: {i}")
    elif len(layer_list) > 0:
        gis.content.delete_items(items=layer_list)
        logger.info(f"RS group deleted: {i}")
