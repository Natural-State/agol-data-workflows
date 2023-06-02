import agol_dirs as dirs
import arcpy
import os
import pandas as pd

metadata = pd.read_excel(dirs.metadata_dir, sheet_name="AGOL_properties")
gdb_list = metadata["GDB"].unique().tolist()

# Create API input parent folder
if os.path.exists(os.path.join(dirs.proj_dir, dirs.api_input_dir)):
    print("API folder already exists")
else:
    os.mkdir(os.path.join(dirs.proj_dir, dirs.api_input_dir))

# Create file GDBs and API sub-folders
for i in gdb_list:
    try:
        arcpy.CreateFileGDB_management(out_folder_path=dirs.proj_dir, out_name=i + ".gdb")
        os.mkdir(os.path.join(dirs.proj_dir, dirs.api_input_dir, i))
        print(i + " GDB created")
    except Exception as e:
        print(f"Skipping iteration for {i} - Error occurred: {str(e)}")
        continue

# Create the Boundaries GDB and import AOI
if os.path.exists(os.path.join(dirs.proj_dir, "Boundaries.gdb")):
    print("Boundaries.gdb already exists")
else:
    arcpy.CreateFileGDB_management(out_folder_path=dirs.proj_dir, out_name="Boundaries.gdb")
    aoi_filepath = r"H:\My Drive\GEE_assets\MKR_PACE.shp"
    arcpy.FeatureClassToGeodatabase_conversion(Input_Features=aoi_filepath,
                                               Output_Geodatabase=os.path.join(dirs.proj_dir, "Boundaries.gdb"))
    print("Boundaries.gdb created and AOI imported")


# Note the name of the AOI which must match that in the subsequent code
arcpy.env.workspace = os.path.join(dirs.proj_dir, "Boundaries.gdb")
print("AOI NAME: " + arcpy.ListFeatureClasses()[0])
