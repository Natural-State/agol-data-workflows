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
agol_folders = metadata["GDB"].unique().tolist()

for i in agol_folders:
    gis.content.create_folder(i)

# List of categories to add manually (make sure there are no typos when adding categories)
print(metadata["Categories"].unique().tolist())



