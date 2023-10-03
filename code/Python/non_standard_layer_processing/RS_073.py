import agol_dirs as dirs
import arcpy
import os
import re
import pandas as pd
import time
import logging

# Set up logging config
logging.basicConfig(filename='logfile_RS_073.log', filemode="w", level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('RS_073 logger')

# RS-73 Aboveground Live Woody Biomass Density

# Import metadata sheet
metadata = pd.read_excel(dirs.metadata_dir, sheet_name="AGOL_properties")
metadata = metadata.set_index("Layer ID")

rs_layers = ["RS_073"]
gdb_name = metadata.at[rs_layers[0], "GDB"] + ".gdb"
gdb_dir = os.path.join(dirs.proj_dir, gdb_name)

# Specify the number of tiles covering the AOI
n_tiles = 2

logger.info(f"Starting layer: {rs_layers[0]}")
start_processing = time.time()
outname = f"{rs_layers[0]}_{dirs.clip_boundary_name}"

# Overwrite layer
arcpy.env.workspace = gdb_dir
if arcpy.Exists(outname):
    arcpy.Delete_management(outname)
    logger.info(f"Existing layer deleted: {rs_layers[0]}")

if n_tiles == 1:

    raw = arcpy.Raster(
            r"C:\Users\DominicH\Desktop\ALWBD\mg_per_ha\10N_030E.tif"
    )

    arcpy.env.workspace = gdb_dir
    arcpy.Clip_management(in_raster=raw, out_raster=os.path.join(gdb_dir, outname),
                          in_template_dataset=os.path.join(os.path.join(dirs.proj_dir,
                                                                        "Boundaries.gdb", dirs.clip_boundary_name)),
                          clipping_geometry="ClippingGeometry",
                          nodata_value="nan", maintain_clipping_extent="NO_MAINTAIN_EXTENT")
elif n_tiles > 1:

    raw1 = arcpy.Raster(
        r"C:\Users\DominicH\Desktop\ALWBD\mg_per_ha\10N_030E.tif")
    raw2 = arcpy.Raster(
        r"C:\Users\DominicH\Desktop\ALWBD\mg_per_ha\00N_030E.tif")
    # Add more raw layers if necessary and then adapt code below

    arcpy.Clip_management(in_raster=raw1, out_raster=os.path.join(gdb_dir, "temp1"),
                          in_template_dataset=os.path.join(os.path.join(dirs.proj_dir,
                                                                        "Boundaries.gdb", dirs.clip_boundary_name)),
                          clipping_geometry="ClippingGeometry",
                          nodata_value="nan", maintain_clipping_extent="NO_MAINTAIN_EXTENT")

    arcpy.Clip_management(in_raster=raw2, out_raster=os.path.join(gdb_dir, "temp2"),
                          in_template_dataset=os.path.join(os.path.join(dirs.proj_dir,
                                                                        "Boundaries.gdb", dirs.clip_boundary_name)),
                          clipping_geometry="ClippingGeometry",
                          nodata_value="nan", maintain_clipping_extent="NO_MAINTAIN_EXTENT")

    arcpy.env.workspace = gdb_dir
    arcpy.MosaicToNewRaster_management(input_rasters=["temp1", "temp2"],
                                       output_location=gdb_dir,
                                       raster_dataset_name_with_extension=outname,
                                       number_of_bands=1)

    arcpy.Delete_management(in_data=["temp1", "temp2"])

# Copy to API folder
arcpy.env.workspace = gdb_dir
api_file_name = os.path.join(dirs.api_input_dir, re.sub(".gdb", "", gdb_name), outname + ".tif")
if os.path.exists(api_file_name):
    os.remove(api_file_name)
arcpy.CopyRaster_management(in_raster=outname, out_rasterdataset=api_file_name)

# Rename the band to match layer id (can't do this when layer is in GDB)
rast = arcpy.Raster(api_file_name)
rast.renameBand(1, "temp")
rast.renameBand(1, outname)

end_processing = time.time()
logger.info(f"Layer completed: {rs_layers[0]}")
logger.info(f"Total processing time for {rs_layers[0]} (minutes): {str((end_processing - start_processing) / 60)}")


