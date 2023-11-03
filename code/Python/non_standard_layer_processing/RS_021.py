import agol_dirs as dirs
import arcpy
import os
import glob
import re
import pandas as pd
from zipfile import ZipFile

# RS_021 GIRES Rivers

# Import metadata sheet
metadata = pd.read_excel(dirs.metadata_dir, sheet_name="AGOL_properties")
metadata = metadata.set_index("Layer ID")

rs_layer = "RS_021"
gdb_name = metadata.at[rs_layer, "GDB"] + ".gdb"

gires_gdb_dir = r"C:\Users\DominicH\Desktop\GIRES\GIRES_v10_gdb\GIRES_v10.gdb"
outname = f"{rs_layer}_{dirs.clip_boundary_name}"

# Clip layer to boundary
arcpy.Clip_analysis(in_features=os.path.join(gires_gdb_dir, "GIRES_v10_rivers"),
                    clip_features=os.path.join(os.path.join(dirs.proj_dir, "Boundaries.gdb", dirs.clip_boundary_name)),
                    out_feature_class=os.path.join(gires_gdb_dir, outname))

# Import into project GDB
arcpy.FeatureClassToGeodatabase_conversion(Input_Features=os.path.join(gires_gdb_dir, outname),
                                           Output_Geodatabase=os.path.join(dirs.proj_dir, gdb_name))

# Create distance to river raster
river_rast_name = f"RS_079_{dirs.clip_boundary_name}"
arcpy.env.workspace = os.path.join(dirs.proj_dir, gdb_name)
utm_proj = arcpy.SpatialReference(32637)
arcpy.env.outputCoordinateSystem = utm_proj
arcpy.env.cellSize = 100
arcpy.env.cellSizeProjectionMethod = "CONVERT_UNITS"

river_dist = arcpy.sa.DistanceAccumulation(in_source_data=outname)
river_dist.save("river_dist_proj")
arcpy.ProjectRaster_management("river_dist_proj", river_rast_name, out_coor_system=4326)
arcpy.Delete_management("river_dist_proj")

# Copy GIRES river vector file to API input folder
arcpy.env.workspace = gires_gdb_dir
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

# Copy GIRES distance to river raster file API input folder
arcpy.env.workspace = os.path.join(dirs.proj_dir, gdb_name)
api_file_name = os.path.join(dirs.api_input_dir, re.sub(".gdb", "", gdb_name), river_rast_name + ".tif")
if os.path.exists(api_file_name):
    os.remove(api_file_name)
arcpy.CopyRaster_management(in_raster=river_rast_name, out_rasterdataset=api_file_name)

# Rename the band to match layer id (can't do this when layer is in GDB)
rast = arcpy.Raster(api_file_name)
rast.renameBand(1, "temp")
rast.renameBand(1, river_rast_name)
print(rast.bandNames)
