import agol_dirs as dirs
import arcpy
import os
import re
import pandas as pd

# Import metadata sheet
metadata = pd.read_excel(dirs.metadata_dir, sheet_name="AGOL_properties")
metadata = metadata.set_index("Layer ID")

rs_layer = "RS_075"
gdb_name = metadata.at[rs_layer, "GDB"] + ".gdb"
gdb_dir = os.path.join(dirs.proj_dir, gdb_name)
outname = f"{rs_layer}_{dirs.clip_boundary_name}"
gdd_raw = r"C:\Users\DominicH\Desktop\GEnS\var12.tif"

arcpy.env.workspace = gdb_dir
if arcpy.Exists(outname):
    arcpy.Delete_management(outname)

arcpy.Clip_management(in_raster=gdd_raw, out_raster=os.path.join(gdb_dir, outname),
                      in_template_dataset=os.path.join(os.path.join(dirs.proj_dir,
                                                                    "Boundaries.gdb", dirs.clip_boundary_name)),
                      clipping_geometry="ClippingGeometry",
                      nodata_value="nan", maintain_clipping_extent="NO_MAINTAIN_EXTENT")

# Copy to API
api_file_name = os.path.join(dirs.api_input_dir, re.sub(".gdb", "", gdb_name), outname + ".tif")
if os.path.exists(api_file_name):
    os.remove(api_file_name)
arcpy.CopyRaster_management(in_raster=outname, out_rasterdataset=api_file_name)

# Rename the band to match layer id (can't do this when layer is in GDB)
rast = arcpy.Raster(api_file_name)
rast.renameBand(1, "temp")
rast.renameBand(1, outname)
print(rast.bandNames)
