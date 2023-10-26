import os

# Specify arcpro project directory where geodatabases will be created
proj_dir = r"C:\Users\mroga\OneDrive - Natural State\Documents - Data Science Division\General\AGOL\LLBN\AGOLupload"

# File path to metadata excel table with all uploaded layers
metadata_dir = r"C:\Users\mroga\OneDrive - Natural State\Documents - Data Science Division\General\AGOL\agol_layers_metadata_10-2023.xlsx"


# Folder path where layers exported from GEE are stored
gee_dir = r"G:\My Drive\GEE_exports"

# Folder path where study area extent shapefile is stored.
aoi_dir = r"C:\Users\mroga\OneDrive - Natural State\Documents - Data Science Division\General\AGOL\LLBN"

# Name of study area. Should be a [NAME].shp file specifying the study area extent in the aoi_dir. This file is used for clipping.
clip_boundary_name = "LLBN"

# Derived paths
aoi_filepath = os.path.join(aoi_dir, f"{clip_boundary_name}.shp")
api_input_dir = os.path.join(proj_dir, r"api_input")
move_dir = os.path.join(gee_dir, "sent_to_gdb")



