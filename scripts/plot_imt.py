# -*- coding: utf-8 -*-
"""
Script to load gmf outputs from OpenQuake
Take the mean
Plot
Outputs

This is a nice script to give to people (based on an older, messier script)

RMJA written 2/10/19
RMJA updated so compatible with windows and linux with os.path.join 14/10/09

"""

##### IMPORT MODULES ####
import pandas as pd
import matplotlib.pyplot as plt
#import numpy as np
import glob
import os.path
#import sys

#directory=sys.argv[1]

######### Change 'directory' input here - put full path to directory with the outputs from openquake  #######
#%                                                                          #%
######### the outputs of this script (.csv file and .pdf file(s)) will be saved in the same directory #######
#########  IF USING WINDOWS NEED DOUBLE BACKWARDS SLASHES AND IGNORE 'C:'  #######
#########  e.g. "\\Users\\Ruth\\demo1" not "C:\Users\Ruth\demo1"  #######
#########  IF USING WINDOWS NEED DOUBLE BACKWARDS SLASHES AND IGNORE 'C:'  #######
#directory="/nfs/a285/homes/earrame/openquake/almaty_scenarios/northern_splay/just45degrees/outputs_hazard/"
directory="\\Users\\rutha\\OneDrive - University of Leeds\\ruth_postdoc\\openquake\\almaty_scenarios\\northern_splay\\outputs_hazard_uniformvs30_abrahamson\\"
######################################


# Don't edit anything below here

# WORK OUT CALCULATION ID (each is unique for openquake outputs)
filename = os.path.join(directory, "gmf-data*.csv")
temp = glob.glob(filename)
tempfile = temp[0]
file = tempfile[len(directory)+9 :]
calcId = file[0: -4]

######### SET UP FILENAMES #######
#sitecvs = outputDir + "/" + "sitemesh_" + calcId + ".csv" 
#datacvs = outputDir + "/" + "gmf-data_" + calcId + ".csv" 
sitecsvfile = "sitemesh_" + calcId + ".csv" 
sitecvs = os.path.join(directory, sitecsvfile)
datacvsfile = "gmf-data_" + calcId + ".csv"
datacvs = os.path.join(directory, datacvsfile)
#rupturexml = outputDir + "/" + rupture_filename + ".xml"


 ##### LOAD THE FILES USING PANDAS ####
sitelocations = pd.read_csv(sitecvs, delimiter=',')
data = pd.read_csv(datacvs, delimiter=',')
#imts = ['gmv_PGA', 'gmv_SA(0.1)']
imts = list(data.columns)[2:]

# create output dataframe
outDf = pd.DataFrame(columns = ['long', 'lat'])
outDf['long'] = sitelocations.lon
outDf['lat'] = sitelocations.lat

for imt in imts:
    
    # this is messy.  i don't want to talk about it.
    if imt in ['gmv_PGA']:
        imtname = 'PGA'
    if imt in ['gmv_SA(1.0)']:
        imtname = 'SA_1'
    if imt in ['gmv_SA(0.3)']:
        imtname = 'SA_0p3'
    if imt in ['gmv_SA(0.7)']:
        imtname = 'SA_0p7'
    if imt in ['gmv_SA(0.1)']:
        imtname = 'SA_0p1'
    
    ##### TAKE THE MEAN OF THE PGAs FOR EACH SITE ###
    imt_mean_persite = data.groupby('sid')[imt].mean() # group by site ID and then take the mean
    outDf[imt] = imt_mean_persite
    
    ##### PLOT ####
    plot = plt.scatter(sitelocations.lon, sitelocations.lat, s=None, c=imt_mean_persite)
    plt.xlabel('longitude')
    plt.ylabel('latitude')
    cbar= plt.colorbar(plot)
    
    if imt in ['gmv_PGA']:
        cbar.set_label("PGA (g)", labelpad=+1)
    if imt in ['gmv_SA(1.0)', 'gmv_SA(0.3)', 'gmv_SA(0.7)', 'gmv_SA(0.1)']:
        cbar.set_label("SA (m/sec/sec)", labelpad=+1)
    
    # PLOT FAULT #
    # havent really worked out how to do this... have to read nrml file
    #plt.scatter(76.945, 43.26, c='r', edgecolor='black')
    #plt.plot((77.2845437192546, 76.587629182654), (43.2490878288074, 43.0280220784148), color='r')

    ###### OUTPUT PLOTS #########
    figureoutput = os.path.join(directory, imtname)
    plt.tight_layout()
    plt.savefig(figureoutput + '.png', format='png')
    plt.show()
    
    
###### OUTPUT data in csv format #########
outfile = os.path.join(directory, "long_lat_IMT.csv")
outDf.to_csv(outfile, mode = 'w', index=False)
