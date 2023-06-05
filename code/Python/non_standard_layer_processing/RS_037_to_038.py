import agol_dirs as dirs
import arcpy
import os
import re
import pandas as pd

# RS_037 GHS-SMOD and RS_038 GHS-BUILT S

# Note that processing of RS_038 will take some time because of the fine resolution

# Import metadata sheet
metadata = pd.read_excel(dirs.metadata_dir, sheet_name="AGOL_properties")
metadata = metadata.set_index("Layer ID")

rs_layers = ["RS_037", "RS_038"]
gdb_name = metadata.at[rs_layers[0], "GDB"] + ".gdb"
gdb_dir = os.path.join(dirs.proj_dir, gdb_name)

for i in rs_layers:

    outname = f"{i}_{dirs.clip_boundary_name}"

    if i == "RS_037":
        raw1 = arcpy.Raster(r"C:\Users\DominicH\Desktop\GHS\GHS_SMOD_E2020_GLOBE_R2022A_54009_1000_V1_0_R9_C22.tif")
        raw2 = arcpy.Raster(r"C:\Users\DominicH\Desktop\GHS\GHS_SMOD_E2020_GLOBE_R2022A_54009_1000_V1_0_R10_C22.tif")
    elif i == "RS_038":
        raw1 = arcpy.Raster(r"C:\Users\DominicH\Desktop\GHS\GHS_BUILT_S_E2018_GLOBE_R2022A_54009_10_V1_0_R9_C22.tif")
        raw2 = arcpy.Raster(r"C:\Users\DominicH\Desktop\GHS\GHS_BUILT_S_E2018_GLOBE_R2022A_54009_10_V1_0_R10_C22.tif")

    arcpy.Clip_management(in_raster=raw1, out_raster=os.path.join(gdb_dir, "temp1"),
                          in_template_dataset=os.path.join(os.path.join(dirs.proj_dir,
                                                                        "Boundaries.gdb", dirs.clip_boundary_name)),
                          clipping_geometry="ClippingGeometry",
                          nodata_value=0, maintain_clipping_extent="NO_MAINTAIN_EXTENT")

    arcpy.Clip_management(in_raster=raw2, out_raster=os.path.join(gdb_dir, "temp2"),
                          in_template_dataset=os.path.join(os.path.join(dirs.proj_dir,
                                                                        "Boundaries.gdb", dirs.clip_boundary_name)),
                          clipping_geometry="ClippingGeometry",
                          nodata_value=0, maintain_clipping_extent="NO_MAINTAIN_EXTENT")

    arcpy.env.workspace = gdb_dir
    arcpy.MosaicToNewRaster_management(input_rasters=["temp1", "temp2"],
                                       output_location=gdb_dir,
                                       raster_dataset_name_with_extension=outname,
                                       number_of_bands=1)

    arcpy.Delete_management(in_data=["temp1", "temp2"])

    # Copy to API folder
    api_file_name = os.path.join(dirs.api_input_dir, re.sub(".gdb", "", gdb_name), outname + ".tif")
    if os.path.exists(api_file_name):
        os.remove(api_file_name)
    arcpy.CopyRaster_management(in_raster=outname, out_rasterdataset=api_file_name)

############
# outname = f"{rs_layer}_{dirs.clip_boundary_name}"
#
#
# GHS_BUILT_S_E2018_GLOBE_R2022A_54009_10_V1_0_R9_C22.tif
#
# ghs_raw1 = arcpy.Raster(r"C:\Users\DominicH\Desktop\GHS\GHS_SMOD_E2020_GLOBE_R2022A_54009_1000_V1_0_R9_C22.tif")
# ghs_raw2 = arcpy.Raster(r"C:\Users\DominicH\Desktop\GHS\GHS_SMOD_E2020_GLOBE_R2022A_54009_1000_V1_0_R10_C22.tif")
#
# arcpy.MosaicToNewRaster_management(input_rasters=[ghs_raw1, ghs_raw2],
#                                    output_location=gdb_dir,
#                                    raster_dataset_name_with_extension="ghs_merge",
#                                    number_of_bands=1)
#
# arcpy.env.workspace = gdb_dir
# arcpy.Clip_management(in_raster="ghs_merge", out_raster=os.path.join(gdb_dir, outname),
#                       in_template_dataset=os.path.join(os.path.join(dirs.proj_dir,
#                                                                     "Boundaries.gdb", dirs.clip_boundary_name)),
#                       clipping_geometry="ClippingGeometry",
#                       nodata_value=0, maintain_clipping_extent="NO_MAINTAIN_EXTENT")
#
# arcpy.Delete_management(in_data="ghs_merge")
#
# # Add color map
# # arcpy.AddColormap_management(in_raster=os.path.join(gdb_dir, outname),
# #                              in_template_raster=None,
# #                              input_CLR_file=r"C:\Users\DominicH\Desktop\GHS"
# #                                             r"\GHS_SMOD_E2020_GLOBE_R2022A_54009_1000_V1_0_R9_C22.clr")
#
#
# # Copy to API
# api_file_name = os.path.join(dirs.api_input_dir, re.sub(".gdb", "", gdb_name), outname + ".tif")
# if os.path.exists(api_file_name):
#     os.remove(api_file_name)
# arcpy.CopyRaster_management(in_raster=outname, out_rasterdataset=api_file_name)
