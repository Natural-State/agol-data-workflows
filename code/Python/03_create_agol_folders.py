import agol_dirs as dirs
from arcgis.gis import GIS
import pandas as pd
import logging
from agol_credentials import agol_username, agol_password

# Set up logging config
logging.basicConfig(filename='logfile_03.log', filemode="w", level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Create-AGOL-folders logger')

# Connect to AGOL
gis = GIS("https://naturalstate.maps.arcgis.com/", agol_username, agol_password)
type(gis)
gis.admin.license.all()

# Read in metadata
metadata = pd.read_excel(dirs.metadata_dir, sheet_name="AGOL_properties")
metadata = metadata.set_index("Layer ID")
agol_folders = sorted(set(metadata["GDB"].tolist()),  key=str.casefold)

for i in agol_folders:
    gis.content.create_folder(i)

# List of categories to add manually (beware of typos)
agol_cats = metadata["Realm"] + "/" + metadata["Content"].fillna("") + "/" + metadata["Label"].fillna("")
agol_cats = sorted(set(agol_cats.tolist()), key=str.casefold)
for i in agol_cats:
    logger.info(f"Add this category by hand: {i}")
