import agol_dirs as dirs
import arcpy
import os
import re
import pandas as pd
import time
import logging

# RS-78 Global Surface Water Occurrence

# Specify run variables
rs_layer = "RS_078"
rawDir = r"C:\Users\mroga\Dropbox\Natural_State\GIS\Rangelands\Hydrology"
pattern = f"InlandWater.*\.tif$"

# get files
files = [f for f in os.listdir(rawDir) if re.match(pattern, f)]

# Set up logging config
logging.basicConfig(filename='logfile_' + rs_layer + '.log',
                    filemode="w",
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(rs_layer + ' logger')

logger.info(f"Starting layer: {rs_layer}")

logger.info(f"Importing data from {rawDir}.")


# Import metadata sheet
metadata = pd.read_excel(dirs.metadata_dir, sheet_name="AGOL_properties")
metadata = metadata.set_index("Layer ID")

# Get local GDB info
gdb_name = metadata.at[rs_layer, "GDB"] + ".gdb"
gdb_dir = os.path.join(dirs.proj_dir, gdb_name)

# Specify the number of tiles covering the AOI
n_tiles = len(files)

logger.info(f"Importing {n_tiles} tiles.")

start_processing = time.time()
outname = f"{rs_layer}_{dirs.clip_boundary_name}"

# Overwrite layer
arcpy.env.workspace = gdb_dir
if arcpy.Exists(outname):
    arcpy.Delete_management(outname)
    logger.info(f"Existing layer deleted: {rs_layer}")

if n_tiles == 1:

    raw = arcpy.Raster(
            os.path.join(rawDir, files[0])
    )

    arcpy.env.workspace = gdb_dir

    arcpy.Clip_management(in_raster=raw, out_raster=os.path.join(gdb_dir, outname),
                          in_template_dataset=os.path.join(os.path.join(dirs.proj_dir,
                                                                        "Boundaries.gdb", dirs.clip_boundary_name)),
                          clipping_geometry="ClippingGeometry",
                          nodata_value="nan", maintain_clipping_extent="NO_MAINTAIN_EXTENT")
elif n_tiles > 1:

    input_rasters = [f"temp{i + 1}" for i in range(len(files))]

    for i in range(len(files)):
        raw = arcpy.Raster(
            os.path.join(rawDir, files[i])
        )

        arcpy.Clip_management(in_raster=raw,
                              out_raster=os.path.join(gdb_dir, input_rasters[i]),
                              in_template_dataset=os.path.join(os.path.join(dirs.proj_dir,
                                                                            "Boundaries.gdb",
                                                                            dirs.clip_boundary_name)),
                              clipping_geometry="ClippingGeometry",
                              nodata_value="nan",
                              maintain_clipping_extent="NO_MAINTAIN_EXTENT")



    arcpy.env.workspace = gdb_dir
    arcpy.MosaicToNewRaster_management(input_rasters=input_rasters,
                                       output_location=gdb_dir,
                                       raster_dataset_name_with_extension=outname,
                                       number_of_bands=1)

    arcpy.Delete_management(in_data=input_rasters)

# Copy to API folder
arcpy.env.workspace = gdb_dir
api_file_name = os.path.join(dirs.api_input_dir, re.sub(".gdb", "", gdb_name), outname + ".tif")
if os.path.exists(api_file_name):
    os.remove(api_file_name)
arcpy.CopyRaster_management(in_raster=outname, out_rasterdataset=api_file_name)

# Rename the band to match layer id (can't do this when layer is in GDB)
rast = arcpy.Raster(api_file_name)
rast.renameBand(1, outname)

end_processing = time.time()
logger.info(f"Layer completed: {rs_layer}")
logger.info(f"Total processing time for {rs_layer} (minutes): {str((end_processing - start_processing) / 60)}")

