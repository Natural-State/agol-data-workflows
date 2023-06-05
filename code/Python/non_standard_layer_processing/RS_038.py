# RS_038 GHS-BUILT S

local_dir = r"H:\My Drive\ArcPro projects"
boundaries_gdb_dir = os.path.join(local_dir, r"GEE export layers\Boundaries.gdb")
api_input_dir = os.path.join(local_dir, r"GEE export layers\api_input")
clip_boundary = "MKR_NS_buff_5km"
metadata = pd.read_excel(r"H:\My Drive\GIS layers catalog.xlsx", sheet_name="AGOL_properties")
metadata = metadata.set_index("Layer ID")

# Define which layers need to be processed
rs_layer = "RS_038"
gdb_name = metadata.at[rs_layer, "GDB"] + ".gdb"
gdb_dir = os.path.join(local_dir, r"GEE export layers", gdb_name)
outname = f"{rs_layer}_{clip_boundary}"
ghs_raw = os.path.join(local_dir, r"GEE export layers",
                       r"GHS_raw\GHS_BUILT_S_E2018_GLOBE_R2022A_54009_10_V1_0_R9_C22.tif")

arcpy.env.workspace = gdb_dir
arcpy.Clip_management(in_raster=ghs_raw, out_raster=os.path.join(gdb_dir, outname),
                      in_template_dataset=os.path.join(boundaries_gdb_dir, clip_boundary),
                      clipping_geometry="ClippingGeometry",
                      nodata_value=0, maintain_clipping_extent="NO_MAINTAIN_EXTENT")

# Copy to API
api_file_name = os.path.join(api_input_dir, re.sub(".gdb", "", gdb_name), outname + ".tif")
arcpy.CopyRaster_management(in_raster=outname, out_rasterdataset=api_file_name)
