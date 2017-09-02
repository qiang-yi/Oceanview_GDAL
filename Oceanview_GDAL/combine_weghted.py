'''
Created on Feb 25, 2017

@author: Yi Qiang
'''
import time
import numpy as np
import math
import gdal
import numpy as np
from gdalconst import *
from osgeo import osr
import csv
from numpy import int16, float32, int32, float64

point_dir="D:/oceanview/obs_points/"
#dem_20k="D:/UH_work/other_data/dem_20k"
#output_dir="D:/UH_work/viewshed4/"
dist_dir="D:/oceanview/dist_obs_points/"

#dem_20k="D:/oceanview/LiDAR_dem/dsm_no50"
output_dir="D:/oceanview/viewshed_dsm_no25/"
origin_dem="D:/oceanview/LiDAR_dem/dsm_no25"

def GetGeoInfo(FileName):
    SourceDS = gdal.Open(FileName, GA_ReadOnly)
    NDV = SourceDS.GetRasterBand(1).GetNoDataValue()
    xsize = SourceDS.RasterXSize
    ysize = SourceDS.RasterYSize
    GeoT = SourceDS.GetGeoTransform()
    Projection = osr.SpatialReference()
    Projection.ImportFromWkt(SourceDS.GetProjectionRef())
    #DataType = SourceDS.GetRasterBand(1).DataType
    #DataType = gdal.GetDataTypeName(DataType)
    DataType=gdal.GDT_Float32
    return NDV, xsize, ysize, GeoT, Projection, DataType

def CreateGeoTiff(Name, Array, driver,NDV,xsize, ysize, GeoT, Projection, DataType):
    #DataType = gdal.GDT_Int32
    NewFileName = Name+'.tif'

    # Set up the dataset
    DataSet = driver.Create( NewFileName, xsize, ysize, 1, DataType )
    #Array[np.isnan(Array)] = NDV
            # the '1' is for band 1.
    DataSet.SetGeoTransform(GeoT)
    DataSet.SetProjection( Projection.ExportToWkt() )
    # Write the array
    DataSet.GetRasterBand(1).WriteArray( Array )
    DataSet.GetRasterBand(1).SetNoDataValue(NDV)
    return NewFileName

[NDV, xsize, ysize, GeoT, Projection, DataType]=GetGeoInfo(origin_dem)
driver = gdal.GetDriverByName('GTiff')

print ('processing weighted'+origin_dem)

#Load the first viewshed layer
dataset = gdal.Open(output_dir+'view0', GA_ReadOnly)
band = dataset.GetRasterBand(1)
total_viewshed=band.ReadAsArray().astype(float32)

#Load elevation layer
dataset = gdal.Open(origin_dem, GA_ReadOnly)
band = dataset.GetRasterBand(1)
elv=(band.ReadAsArray()/float(1000))

for fid in range(0,542):
    # Print x,y coordinates of each point feature

    start_time = time.time()
    
    #Load distance to point layer
    dist_fn=dist_dir+"dist_"+str(fid)
    dataset = gdal.Open(dist_fn, GA_ReadOnly)
    band = dataset.GetRasterBand(1)
    dist=(band.ReadAsArray()/float(1000))

    #Load viewshed layer
    dataset=gdal.Open(output_dir+"view"+str(fid), GA_ReadOnly)
    band = dataset.GetRasterBand(1)
    viewshed=band.ReadAsArray().astype(float32)
    
    
    #dist=float(pt_list[fid][2])
    
    #print(dist)
    #weight=(1/elv)*(1/(dist**2+1))*1000
    weight=1/(1+np.power((dist/elv),2))*(1/elv)*float(1000)
    weight=weight.astype(float32)
    #viewshed=(viewshed * weight).astype(int32)
    total_viewshed+=viewshed * weight
    
    #NewFileName=CreateGeoTiff(output_dir+"w_view"+str(fid), total_viewshed, driver, NDV,xsize, ysize, GeoT, Projection, DataType)

    print "processing time for "+str(fid)+"th point is "+ str(time.time()-start_time)

# Function to read the original file's projection:


driver = gdal.GetDriverByName('GTiff')
out_file=output_dir+"total_view"
NewFileName=CreateGeoTiff( out_file, total_viewshed, driver,NDV, xsize, ysize, GeoT, Projection, DataType)