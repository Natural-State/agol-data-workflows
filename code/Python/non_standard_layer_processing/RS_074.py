import agol_dirs as dirs
import arcpy
import os
import re
import pandas as pd
import glob
from zipfile import ZipFile

# Import metadata sheet
metadata = pd.read_excel(dirs.metadata_dir, sheet_name="AGOL_properties")
metadata = metadata.set_index("Layer ID")

rs_layer = "RS_074"
gdb_name = metadata.at[rs_layer, "GDB"] + ".gdb"
gdb_dir = os.path.join(dirs.proj_dir, gdb_name)
outname = f"{rs_layer}_{dirs.clip_boundary_name}"
lithology_raw = r"C:\Users\DominicH\Desktop\GLiM\LiMW_GIS 2015.gdb\GLiM_export"

# Clip to boundary
arcpy.env.workspace = gdb_dir
arcpy.Clip_analysis(in_features=lithology_raw,
                    clip_features=os.path.join(os.path.join(dirs.proj_dir,
                                                            "Boundaries.gdb", dirs.clip_boundary_name)),
                    out_feature_class=outname)

# Send to API input and create zip file
api_folder = os.path.join(dirs.api_input_dir, re.sub(".gdb", "", gdb_name))
arcpy.FeatureClassToShapefile_conversion(Input_Features=outname, Output_Folder=api_folder)

lyr_pattern = outname + "*"
vector_files = glob.glob(os.path.join(dirs.api_input_dir, re.sub(".gdb", "", gdb_name), lyr_pattern))
print(vector_files)
# Define the name and path of the output zip file
zip_filename = os.path.join(dirs.api_input_dir, re.sub(".gdb", "", gdb_name), outname + ".zip")
# Open the output zip file in write mode
with ZipFile(zip_filename, "w") as zip:
    # Loop through the list of files and add each file to the zip file
    for file in vector_files:
        base_name = os.path.basename(file)
        zip.write(file, arcname=base_name)
