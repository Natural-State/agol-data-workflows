import agol_dirs as dirs
import arcpy
import os
import re
import pandas as pd

# Import metadata sheet
metadata = pd.read_excel(dirs.metadata_dir, sheet_name="AGOL_properties")
metadata = metadata.set_index("Layer ID")

rs_layer = "RS_067"
gdb_name = metadata.at[rs_layer, "GDB"] + ".gdb"
gdb_dir = os.path.join(dirs.proj_dir, gdb_name)
outname = f"{rs_layer}_{dirs.clip_boundary_name}"
gedi_raw = r"C:\Users\DominicH\Desktop\GEDI_L3\GEDI03_rh100_mean_2019108_2021216_002_02.tif"

arcpy.env.workspace = gdb_dir
if arcpy.Exists(outname):
    arcpy.Delete_management(outname)

arcpy.Clip_management(in_raster=gedi_raw, out_raster=os.path.join(gdb_dir, outname),
                      in_template_dataset=os.path.join(os.path.join(dirs.proj_dir,
                                                                    "Boundaries.gdb", dirs.clip_boundary_name)),
                      clipping_geometry="ClippingGeometry",
                      nodata_value=0, maintain_clipping_extent="NO_MAINTAIN_EXTENT")

arcpy.env.workspace = gdb_dir

# Copy to API
api_file_name = os.path.join(dirs.api_input_dir, re.sub(".gdb", "", gdb_name), outname + ".tif")
arcpy.CopyRaster_management(in_raster=outname, out_rasterdataset=api_file_name)
