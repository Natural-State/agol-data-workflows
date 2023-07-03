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

rs_layer = "RS_071"
gdb_name = metadata.at[rs_layer, "GDB"] + ".gdb"
gdb_dir = os.path.join(dirs.proj_dir, gdb_name)
outname = f"{rs_layer}_{dirs.clip_boundary_name}"
soils_raw = r"C:\Users\DominicH\Desktop\Soil Atlas of Africa\afticasoilmap.shp"

arcpy.FeatureClassToGeodatabase_conversion(Input_Features=soils_raw,
                                           Output_Geodatabase=gdb_dir)

# Clip to boundary
arcpy.env.workspace = gdb_dir
arcpy.Clip_analysis(in_features="afticasoilmap",
                    clip_features=os.path.join(os.path.join(dirs.proj_dir,
                                                            "Boundaries.gdb", dirs.clip_boundary_name)),
                    out_feature_class="afticasoilmap_clip")

arcpy.Delete_management(in_data="afticasoilmap")
arcpy.Rename_management(in_data="afticasoilmap_clip", out_data=outname)

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
