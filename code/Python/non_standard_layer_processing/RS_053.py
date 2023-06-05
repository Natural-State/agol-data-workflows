import agol_dirs as dirs
import arcpy
import os
import glob
import re
import pandas as pd
from zipfile import ZipFile

# Import metadata sheet
metadata = pd.read_excel(dirs.metadata_dir, sheet_name="AGOL_properties")
metadata = metadata.set_index("Layer ID")

rs_layer = "RS_053"
gdb_name = metadata.at[rs_layer, "GDB"] + ".gdb"
gdb_dir = os.path.join(dirs.proj_dir, gdb_name)
outname = f"{rs_layer}_{dirs.clip_boundary_name}"
gpkg_layer = os.path.join(dirs.gee_dir, outname + ".gpkg", "main.edges")

# arcpy.env.workspace = gdb_dir
# arcpy.Delete_management("RS_053_MKR_NS_buff_5km")

# Copy road feature class from Geopackage to GDB
arcpy.FeatureClassToGeodatabase_conversion(Input_Features=gpkg_layer,
                                           Output_Geodatabase=gdb_dir)

# Clip to boundary
arcpy.env.workspace = gdb_dir
arcpy.Clip_analysis(in_features="main_edges",
                    clip_features=os.path.join(os.path.join(dirs.proj_dir,
                                                            "Boundaries.gdb", dirs.clip_boundary_name)),
                    out_feature_class="main_edges_clip")

arcpy.Delete_management(in_data="main_edges")
arcpy.Rename_management(in_data="main_edges_clip", out_data="main_edges")


# Create a new feature layer to apply the filter
arcpy.env.workspace = gdb_dir
arcpy.MakeFeatureLayer_management(in_features="main_edges", out_layer="roads_layer")

# Repair geometries (because this data sets seems to have inherent problems)
arcpy.RepairGeometry_management("roads_layer")

# Get unique values from "highway" field
# Note: Set is a data container that contains unique
# values, so it will deal with uniqueness for us. To change
# a list comprehension to a set comprehension,
# change square brackets to curly brackets
def get_unique(feat_layer, field):
    with arcpy.da.SearchCursor(feat_layer, field) as cursor:
        unique_values = sorted({row[0] for row in cursor})
        return unique_values


print(get_unique("roads_layer", "highway"))

# Define the SQL expression to filter out unwanted network types
sql_expr = "highway NOT LIKE '%path%' AND highway NOT IN ('footway')"

# Apply the filter to the feature layer
arcpy.SelectLayerByAttribute_management("roads_layer", "NEW_SELECTION", sql_expr)
print(get_unique("roads_layer", "highway"))

# Change 'unclassified' segments to 'track' segments in order to group those classes
with arcpy.da.UpdateCursor("roads_layer", "highway") as cursor:
    for row in cursor:
        if row[0] == "unclassified":
            row[0] = "track"
            cursor.updateRow(row)

# Create a new output feature class to store the filtered features
arcpy.CopyFeatures_management(in_features="roads_layer", out_feature_class="roads_filtered")

# Use the Dissolve tool to merge the filtered features based on unique values in the "highway" field
arcpy.Dissolve_management("roads_filtered", "roads_merged", "highway")

# Rename file
arcpy.env.workspace = gdb_dir
arcpy.Rename_management(in_data="roads_merged", out_data=outname)

# Remove intermediate layers
arcpy.Delete_management(in_data=["main_edges", "roads_filtered"])
arcpy.ListFeatureClasses()

# Send to API input and create zip file
arcpy.env.workspace = gdb_dir
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

# Move files out of GEE exports
os.replace(os.path.join(dirs.gee_dir, outname + ".gpkg"),
           os.path.join(dirs.move_dir, outname + ".gpkg"))
