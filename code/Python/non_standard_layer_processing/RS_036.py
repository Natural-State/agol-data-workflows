import agol_dirs as dirs
import arcpy
import os
import re
import pandas as pd

# RS_036 GHM

# Import metadata sheet
metadata = pd.read_excel(dirs.metadata_dir, sheet_name="AGOL_properties")
metadata = metadata.set_index("Layer ID")

rs_layer = "RS_036"
gdb_name = metadata.at[rs_layer, "GDB"] + ".gdb"
gdb_dir = os.path.join(dirs.proj_dir, gdb_name)
ghm_raw = r"C:\Users\DominicH\Desktop\GHM\gHMv1_300m_2017_static-0000046592-0000046592.tif"

arcpy.Clip_management(in_raster=ghm_raw, out_raster=os.path.join(gdb_dir, "gHMv1_300m_2017_static"),
                      in_template_dataset=os.path.join(os.path.join(dirs.proj_dir,
                                                                    "Boundaries.gdb", dirs.clip_boundary_name)),
                      clipping_geometry="ClippingGeometry",
                      nodata_value=0, maintain_clipping_extent="NO_MAINTAIN_EXTENT")

arcpy.env.workspace = gdb_dir

# Scale raster so values are between 0 and 1.
outname = f"{rs_layer}_{dirs.clip_boundary_name}"
arcpy.ListRasters()
ghm_ras = arcpy.sa.Raster('gHMv1_300m_2017_static')
new_ras = ghm_ras / 65536
arcpy.CopyRaster_management(in_raster=new_ras, out_rasterdataset=os.path.join(gdb_dir, outname))
arcpy.Delete_management('gHMv1_300m_2017_static')

# Copy to API
api_file_name = os.path.join(dirs.api_input_dir, re.sub(".gdb", "", gdb_name), outname + ".tif")
arcpy.CopyRaster_management(in_raster=outname, out_rasterdataset=api_file_name)