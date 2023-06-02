import os

proj_dir = r"H:\My Drive\ArcPro projects\agol-data-workflows"
metadata_dir = r"H:\My Drive\ArcPro projects\agol-data-workflows\agol_layers_metadata.xlsx"
gee_dir = r"H:\My Drive\GEE_exports"
api_input_dir = os.path.join(proj_dir, r"api_input")
move_dir = os.path.join(gee_dir, "sent_to_gdb")
clip_boundary_name = "MKR_PACE"

