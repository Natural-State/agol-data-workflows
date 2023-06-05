import agol_dirs as dirs
import arcpy
import os
import glob
import re
import pandas as pd

# Import metadata sheet
metadata = pd.read_excel(dirs.metadata_dir, sheet_name="AGOL_properties")
metadata = metadata.set_index("Layer ID")

start, end = 8, 11
rs_layer_list = ["RS_{id:03d}".format(id=i) for i in range(start, end + 1)]
print(rs_layer_list)

# i = rs_layer_list[0]
for i in rs_layer_list:
    print("STARTING LAYER: " + i)
    gdb_name = metadata.at[i, "GDB"] + ".gdb"
    gdb_dir = os.path.join(dirs.proj_dir, gdb_name)
    folder_dir = metadata.at[i, "GDB"]
    data_type = metadata.at[i, "Data type"]
    file_ext = "*.tif" if data_type == "Raster" else "*.shp"

    # Select pattern using glob wildcard (other examples: '*stdDev*.tif' &  '*NDVI*.tif')
    lyr_pattern = "*" + i + file_ext
    # Read layer list from GEE folder
    layer_list = glob.glob(os.path.join(dirs.api_input_dir, folder_dir, lyr_pattern))
    print(layer_list)

    # Remove existing layers (because overwriting doesn't seem to work)
    check_layers = []
    for r in layer_list:
        match = re.search(r'\\([^\\]*)\.tif$', r) if data_type == "Raster" else re.search(r'\\([^\\]*)\.shp$', r)
        check_layers.append(match.group(1))
    print(check_layers)

    arcpy.env.workspace = gdb_dir
    for y in check_layers:
        if arcpy.Exists(y):
            arcpy.Delete_management(y)

    # Import layers  into GDB
    if data_type == "Raster":
        arcpy.env.workspace = gdb_dir
        for x in layer_list:
            arcpy.CopyRaster_management(in_raster=x, out_rasterdataset="temp_ras", nodata_value="nan")
            match = re.search(r'\\([^\\]*)\.tif$', x)
            copy_ras_name = os.path.join(gdb_dir, match.group(1))
            arcpy.Rename_management(in_data="temp_ras", out_data=copy_ras_name)
            print("IMPORT COMPLETE: " + copy_ras_name)
