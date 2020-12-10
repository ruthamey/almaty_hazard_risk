#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 15:00:01 2019

@author: earrame
"""

import pandas as pd

# Sum of the buildings in Almaty

# Total in exposure model

regions = ['alatau','almaly','auezov', 'bostandyk', 'medeu', 'nauryzbay', 'turksib', 'jetysu']
df_total = pd.DataFrame(columns = regions)
df = pd.DataFrame(columns = regions)

for region in regions:
    districtdf = pd.read_csv("/nfs/a285/homes/earrame/qgis/almaty_districts_buildingsum/" + region + "_buildingsum.csv")
    df_total[region] = districtdf['sumBUILDIN']


#almaty = pd.read_csv("/nfs/a285/homes/earrame/openquake/exposure/Exposure_Res_almaty.csv")
#colNames = ['fid', 'LONGITUDE', 'LATITUDE', 'taxonomy', 'buildings', 'TOTAL_REPL_COST_USD', 'OCCUPANTS_PER_ASSET', 'ISO', 'NAME_0', 'ID_1', 'NAME_1', 'ID_2', 'OCCUPANCY','COST_PER_AREA_USD']


# NEED TO MAKE A DATAFRAME THAT HAS THE COLUMN HEADINGS EQUAL TO THE REGION IN REGIONS
#df['alatau'] = 
#df['almaly'] = 
#df['auezov'] =
#df['bostandyk'] =
#df['medeu'] =
#df['nauryzbay'] =
#df['turksib'] =
#df['jetysu'] =

colNames = ['Building class','alatau','almaly','auezov', 'bostandyk','medeu','nauryzbay','turksib','jetysu']
outdf = pd.DataFrame(columns = colNames)
outdf['Building class'] = ['Reinforced concrete','Confined masonry','Reinforced masonry','Unreinforced masonry','Wooden', 'Steel','Unknown/Insufficient information','Total buildings']
#outdf['District total'] = df_total
df = outdf

for region in regions:
    df = pd.read_csv("/nfs/a285/homes/earrame/qgis/almaty_districts_exposurepoints/" + region + "_exposure.csv")
    CRsum = int(df[(df['TAXONOMY'].str.contains('CR'))].sum()['BUILDINGS'])
    MCFsum = int(df[(df['TAXONOMY'].str.contains('MCF'))].sum()['BUILDINGS'])
    MRsum = int(df[(df['TAXONOMY'].str.contains('MR'))].sum()['BUILDINGS'])
    MURsum = int(df[(df['TAXONOMY'].str.contains('MUR'))].sum()['BUILDINGS'])
    Wsum1 = int(df[(df['TAXONOMY'].str.contains('WLI'))].sum()['BUILDINGS'])
    Wsum2 = int(df[(df['TAXONOMY'].str.contains('W/LWAL'))].sum()['BUILDINGS'])
    Wsum=Wsum1+Wsum2
    Ssum = int(df[(df['TAXONOMY'].str.contains('S/LFM'))].sum()['BUILDINGS'])
    UNKsum = int(df[(df['TAXONOMY'].str.contains('UNK'))].sum()['BUILDINGS'])   
    #sumall = int(df[df[region] > 1.0 ].sum()[region])
    
    #districtdftotal = pd.read_csv("/nfs/a285/homes/earrame/qgis/almaty_districts_buildingsum/" + region + "_buildingsum.csv")
    #total = districtdftotal['sumBUILDIN']
    total = CRsum + MCFsum + MRsum + MURsum + Wsum + Ssum + UNKsum

    #outdf[region] = [CRsum, MCFsum, MRsum, MURsum, Wsum, Ssum, UNKsum, total[0]]
    outdf[region] = [CRsum, MCFsum, MRsum, MURsum, Wsum, Ssum, UNKsum, total]

# check the sums with this
#outdf['almaly'][0:6].sum()

outfile = "/nfs/a285/homes/earrame/figures/almaty_buildings/districtsummary.csv"
outdf.to_csv(outfile, mode = 'w', index=False)


