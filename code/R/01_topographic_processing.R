## ________________________________________________________________________

## Title:    Topographic indices
## Purpose:  Calculate TRI, TPI and roughness from an elevation layer
## Author:   Dominic Henry
## Date:     14/03/2023

## Notes: Code requires installation of {whitebox}.
##        {whitebox} will need to install a
##        whitebox tools exe - follow the prompts after loading.

# If running code for the first time use restore the R library from the renv.lock file
# renv::restore()

## Libraries
library(terra)
library(glue)
library(whitebox)
library(readxl)
library(tidyverse)
library(sf)

## ________________________________________________________________________

## Define boundary
boundary_select <-  "LLBN"

boundary <- vect(st_read("Boundaries.gdb", boundary_select)) %>%
 terra::project("epsg:4326")

# Read in metadata
md_path <- "C:/Users/DominicH/OneDrive - Natural State/Shared Documents - Data Science Division/General/AGOL/agol_layers_metadata_10-2023.xlsx"

metadata <- readxl::read_xlsx(md_path, sheet = "AGOL_properties") %>%
 janitor::clean_names()

elev_id <- metadata$layer_id[which(metadata$layer_name == "Elevation 90m")]
elevation <- rast(glue("H:/My Drive/GEE_exports/sent_to_gdb/{elev_id}_{boundary_select}.tif"))
crs(elevation) <- "epsg:4326"

elevation <- crop(elevation, boundary, mask = TRUE)
plot(elevation)

tri <- terra::terrain(elevation, v = "TRIriley", neighbors=8)
plot(tri)

tpi <- terra::terrain(elevation, v = "TPI", neighbors=8)
plot(tpi)

rough <- terra::terrain(elevation, v = "roughness", neighbors=8)
plot(rough)

# TWI ---------------------------------------------------------------------

# https://vt-hydroinformatics.github.io/rgeoraster.html#topographic-wetness-index

## Create "temporary_data" folder if it doesn't exist

if(dir.exists("temporary_topo_data")){
 print("Temporary data folder exists")
} else {
 dir.create("temporary_topo_data")
 print("Temporary data folder created")
}

terra::writeRaster(terra:::project(elevation, "ESRI:102022"),
                   "temporary_topo_data/dem.tif",
                   overwrite = TRUE)

# Breach
wbt_breach_depressions_least_cost(
 dem = "temporary_topo_data/dem.tif",
 output = "temporary_topo_data/dem_breached.tif",
 dist = 5,
 fill = TRUE)

# Flow accumulation
wbt_d8_flow_accumulation(input = "temporary_topo_data/dem_breached.tif",
                         output = "temporary_topo_data/flo_accum.tif")

# Slope
wbt_slope(dem = "temporary_topo_data/dem_breached.tif",
          output = "temporary_topo_data/dem_slope.tif",
          units = "degrees")

# TWI
wbt_wetness_index(sca = "temporary_topo_data/flo_accum.tif",
                  slope = "temporary_topo_data/dem_slope.tif",
                  output = "temporary_topo_data/TWI.tif")

twi <- terra::rast("temporary_topo_data/TWI.tif") |>
 terra::project("epsg:4326")
plot(twi)

# Write files to API input folder -----------------------------------------

names(tri) <- glue("RS_008_{boundary_select}")
names(tpi) <- glue("RS_009_{boundary_select}")
names(twi) <- glue("RS_010_{boundary_select}")
names(rough) <- glue("RS_011_{boundary_select}")

terra::writeRaster(tri, glue("api_input/Topography/RS_008_{boundary_select}.tif"),
                   overwrite = TRUE)
terra::writeRaster(tpi,glue("api_input/Topography/RS_009_{boundary_select}.tif"),
                   overwrite = TRUE)
terra::writeRaster(twi, glue("api_input/Topography/RS_010_{boundary_select}.tif"),
                   overwrite = TRUE)
terra::writeRaster(rough, glue("api_input/Topography/RS_011_{boundary_select}.tif"),
                   overwrite = TRUE)

# Delete temp topo folder -------------------------------------------------
unlink("temporary_topo_data", recursive = TRUE)
