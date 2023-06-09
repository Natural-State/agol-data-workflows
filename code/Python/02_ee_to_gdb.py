import agol_dirs as dirs
import arcpy
import os
import glob
import re
import pandas as pd
import time
from zipfile import ZipFile

# Import metadata sheet
metadata = pd.read_excel(dirs.metadata_dir, sheet_name="AGOL_properties")
metadata = metadata.set_index("Layer ID")

# Define which RS layers need to be processed (rs_layer_list = ["RS_005"])

# Choose layer start and end points
start, end = 5, 7
rs_layer_list = ["RS_{id:03d}".format(id=i) for i in range(start, end + 1)]
print(rs_layer_list)

# Alternative specification using layer sequence
# layer_seq = [*range(1, 3+1), 5, *range(25, 31+1)]
# rs_layer_list = ["RS_{id:03d}".format(id=i) for i in layer_seq]
# print(rs_layer_list)

start_processing = time.time()

# i = rs_layer_list[0]
for i in rs_layer_list:
    print("STARTING LAYER: " + i)
    gdb_name = metadata.at[i, "GDB"] + ".gdb"
    gdb_dir = os.path.join(dirs.proj_dir, gdb_name)
    data_type = metadata.at[i, "Data type"]
    file_ext = "*.tif" if data_type == "Raster" else "*.shp"
    clip_layer = metadata.at[i, "Clip"]

    # Select pattern using glob wildcard (other examples: '*stdDev*.tif' &  '*NDVI*.tif')
    lyr_pattern = "*" + i + file_ext
    # Read layer list from GEE folder
    layer_list = glob.glob(os.path.join(dirs.gee_dir, lyr_pattern))
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

    elif data_type == "Vector":
        arcpy.env.workspace = gdb_dir
        for x in layer_list:
            arcpy.FeatureClassToGeodatabase_conversion(Input_Features=x, Output_Geodatabase=gdb_dir)
            print("IMPORT COMPLETE: " + x)

        if clip_layer:
            print("Start clipping")
            arcpy.env.overwriteOutput = True
            # c = check_layers[0]
            for c in check_layers:
                vec_name = os.path.join(gdb_dir, c)
                arcpy.env.overwriteOutput = True
                arcpy.Clip_analysis(in_features=vec_name,
                                    clip_features=os.path.join(os.path.join(dirs.proj_dir,
                                                                            "Boundaries.gdb", dirs.clip_boundary_name)),
                                    out_feature_class=vec_name + "_clip")
                arcpy.Delete_management(in_data=vec_name)
                arcpy.Rename_management(in_data=vec_name + "_clip", out_data=vec_name)
                print("Clipping complete for layer: " + c)

    # Export layer to api_input
    arcpy.env.workspace = gdb_dir

    if data_type == "Raster":
        for z in check_layers:
            api_file_name = os.path.join(dirs.api_input_dir, re.sub(".gdb", "", gdb_name), z + ".tif")
            if os.path.exists(api_file_name):
                os.remove(api_file_name)
            arcpy.CopyRaster_management(in_raster=z, out_rasterdataset=api_file_name)

    elif data_type == "Vector":
        # Send to API folder
        for z in check_layers:
            api_folder = os.path.join(dirs.api_input_dir, re.sub(".gdb", "", gdb_name))
            existing_files = glob.glob(os.path.join(api_folder,  z + "*"))
            if len(existing_files) > 0:
                for f in existing_files:
                    os.remove(f)
            arcpy.FeatureClassToShapefile_conversion(Input_Features=z, Output_Folder=api_folder)

        # Create zip files
        for y in check_layers:
            lyr_pattern = y + "*"
            vector_files = glob.glob(os.path.join(dirs.api_input_dir, re.sub(".gdb", "", gdb_name), lyr_pattern))
            print(vector_files)
            # Define the name and path of the output zip file
            zip_filename = os.path.join(dirs.api_input_dir, re.sub(".gdb", "", gdb_name), y + ".zip")
            # Open the output zip file in write mode
            with ZipFile(zip_filename, "w") as zip:
                # Loop through the list of files and add each file to the zip file
                for file in vector_files:
                    base_name = os.path.basename(file)
                    zip.write(file, arcname=base_name)

    if data_type == "Raster":
        for x in range(len(layer_list)):
            if os.path.exists(os.path.join(dirs.move_dir, check_layers[x] + ".tif")):
                os.remove(os.path.join(dirs.move_dir, check_layers[x] + ".tif"))
                print("FILE REMOVED:" + check_layers[x])
            else:
                print("NO FILE EXISTS")
            os.replace(layer_list[x], os.path.join(dirs.move_dir, check_layers[x] + ".tif"))
            print("LAYER MOVED:" + check_layers[x])

    elif data_type == "Vector":
        for y in check_layers:
            existing_files = glob.glob(os.path.join(dirs.gee_dir, y + "*"))
            for v in existing_files:
                os.replace(v, os.path.join(dirs.move_dir, v.rsplit('\\', 1)[1]))

    # Check GDB
    print(arcpy.ListRasters("*", raster_type="All")) if data_type == "Raster" else print(arcpy.ListFeatureClasses())
    print("FINISHED LAYER: " + i)

end_processing = time.time()

print("TOTAL PROCESSING TIME (MINS): " + str((end_processing - start_processing)/60))
