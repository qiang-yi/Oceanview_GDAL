'''
Created on Mar 7, 2017

@author: Yi Qiang
'''
import fiona
from osgeo import gdal

with fiona.open('C:/Users/Yi Qiang/Documents/UH_work/oceanview/other_data/sample_point_20k.shp', 'r') as sample_pts:
    print sample_pts.schema.copy()