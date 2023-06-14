import agol_dirs as dirs
from arcgis.gis import GIS
import pandas as pd
import logging

# Set up logging config
logging.basicConfig(filename='logfile_03.log', filemode="w", level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Create-AGOL-folders logger')

# Connect to AGOL
gis = GIS("https://naturalstate.maps.arcgis.com/", "dhenry_naturalstate", "mX!!49&aOfGNva")
type(gis)
gis.admin.license.all()

# Read in metadata
metadata = pd.read_excel(dirs.metadata_dir, sheet_name="AGOL_properties")
metadata = metadata.set_index("Layer ID")
agol_folders = sorted(set(metadata["GDB"].tolist()),  key=str.casefold)

for i in agol_folders:
    gis.content.create_folder(i)

# List of categories to add manually (make sure there are no typos when adding categories)
agol_cats = sorted(set(metadata["Categories"].tolist()),  key=str.casefold)
for i in agol_cats:
    logger.info(f"Add this category by hand: {i}")


