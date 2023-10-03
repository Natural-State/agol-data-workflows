import agol_dirs as dirs
import arcpy
import os
import re
import pandas as pd
import glob

# RS_041 to RS_047 Gridded livestock

# Import metadata sheet
metadata = pd.read_excel(dirs.metadata_dir, sheet_name="AGOL_properties")
metadata = metadata.set_index("Layer ID")

layer_dict = {
    "6_Ct_2010_Aw": "RS_041",
    "5_Ct_2010_Da": "RS_042",
    "6_Gt_2010_Aw": "RS_043",
    "5_Gt_2010_Da": "RS_044",
    "6_Sh_2010_Aw": "RS_045",
    "5_Sh_2010_Da": "RS_046"
}

gdb_name = metadata.at["RS_041", "GDB"] + ".gdb"
glw_raw_dir = r"C:\Users\DominicH\Desktop\GLW"
gdb_dir = os.path.join(dirs.proj_dir, gdb_name)

# Search for tiffs and remove files containing Ps
glw_raw_files = glob.glob(os.path.join(glw_raw_dir, "*.tif"))
glw_raw_files = [file_path for file_path in glw_raw_files if "Ps" not in file_path]
pattern = r'\\(\w+)\.tif$'

# i = glw_raw_files[0]
for i in glw_raw_files:

    glw_name = re.search(pattern, i).group(1)
    outname = f"{layer_dict[glw_name]}_{dirs.clip_boundary_name}"

    # Overwrite layer
    arcpy.env.workspace = gdb_dir
    if arcpy.Exists(outname):
        arcpy.Delete_management(outname)

    arcpy.Clip_management(in_raster=i, out_raster=os.path.join(gdb_dir, outname),
                          in_template_dataset=os.path.join(os.path.join(dirs.proj_dir,
                                                                    "Boundaries.gdb", dirs.clip_boundary_name)),
                          clipping_geometry="ClippingGeometry",
                          nodata_value="nan", maintain_clipping_extent="NO_MAINTAIN_EXTENT")

arcpy.env.workspace = gdb_dir
gdb_layers = arcpy.ListRasters()
for z in gdb_layers:
    api_file_name = os.path.join(dirs.api_input_dir, re.sub(".gdb", "", gdb_name), z + ".tif")
    if os.path.exists(api_file_name):
        os.remove(api_file_name)
    arcpy.CopyRaster_management(in_raster=z, out_rasterdataset=api_file_name)
    # Rename the band to match layer id (can't do this when layer is in GDB)
    rast = arcpy.Raster(api_file_name)
    rast.renameBand(1, "temp")
    rast.renameBand(1, z)
