#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 17:46:39 2023

@author: quentin
"""
from rasterio.merge import merge
import rasterio as rio
import glob
import os


def merge_rasters(raster_files:str, outfile_path:str) -> None:
    raster_to_mosiac = []

    for p in raster_files:
        raster = rio.open(p)
        raster_to_mosiac.append(raster)

    mosaic, output = merge(raster_to_mosiac)

    output_meta = raster.meta.copy()
    output_meta.update(
        driver="GTiff",
        height=mosaic.shape[1],
        width=mosaic.shape[2],
        transform=output,
        bigtiff="YES",
        compress="lzw",
    )

    with rio.open(outfile_path, "w", **output_meta) as m:
        m.write(mosaic)
