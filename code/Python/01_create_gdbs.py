import agol_dirs as dirs
import arcpy
import os
import pandas as pd
import logging

# Set up logging config
logging.basicConfig(filename='logfile_01.log', filemode="w", level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Create-GDBs logger')

metadata = pd.read_excel(dirs.metadata_dir, sheet_name="AGOL_properties")
gdb_list = metadata["GDB"].unique().tolist()

# Create "sent_to_gdb" folder within GEE exports
if os.path.exists(os.path.join(dirs.gee_dir, "sent_to_gdb")):
    logger.warning(f"Sent to GDB folder already exists")
else:
    os.mkdir(os.path.join(dirs.gee_dir, "sent_to_gdb"))

# Create API input parent folder
if os.path.exists(os.path.join(dirs.proj_dir, dirs.api_input_dir)):
    logger.warning(f"API folder already exists")
else:
    os.mkdir(os.path.join(dirs.proj_dir, dirs.api_input_dir))

# Create file GDBs and API sub-folders
for i in gdb_list:
    try:
        arcpy.CreateFileGDB_management(out_folder_path=dirs.proj_dir, out_name=i + ".gdb")
        os.mkdir(os.path.join(dirs.proj_dir, dirs.api_input_dir, i))
        logger.info(f"{i} GDB created")
    except Exception as e:
        logger.error(f"Skipping iteration for {i} - Error occurred: {str(e)}")
        continue

# Create the Boundaries GDB and import AOI
if os.path.exists(os.path.join(dirs.proj_dir, "Boundaries.gdb")):
    logger.warning("Boundaries.gdb already exists")
else:
    arcpy.CreateFileGDB_management(out_folder_path=dirs.proj_dir, out_name="Boundaries.gdb")
    aoi_filepath = r"H:\My Drive\GEE_assets\LLBN.shp"
    arcpy.FeatureClassToGeodatabase_conversion(Input_Features=aoi_filepath,
                                               Output_Geodatabase=os.path.join(dirs.proj_dir, "Boundaries.gdb"))
    logger.info("Boundaries.gdb created and AOI imported")

# Note the name of the AOI which must match that in the subsequent code
arcpy.env.workspace = os.path.join(dirs.proj_dir, "Boundaries.gdb")
logger.info(f"AOI name: {arcpy.ListFeatureClasses()[0]}")
