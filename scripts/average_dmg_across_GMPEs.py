# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 09:43:14 2018

@author: ekhuss

Adapted by RMJA

18/10/19 Updated for openquake version 3.7 (which uses an annoying header)


"""

import glob
import pandas as pd
import numpy as np


# -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

# EDIT THIS AND ONLY THIS
# % # % # % # % # % # %
scenario_to_calculate = 'all'
# choices = ['CK1'], ['CK2'], ['CKC'], ['V'], ['SP'], ['KP'], ['T'], ['NSP45'], ['NSPrf'], 'all'
# % # % # % # % # % # %
# don't edit anything else please

# -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

if scenario_to_calculate in ['all']:
    scenario_to_calculate = ['CK1', 'CK2', 'CKC', 'C', 'V', 'SP', 'KP', 'T', 'NSP45', 'NSPrf']

for scenario in scenario_to_calculate:
    
    if scenario in ['CK1']:
         dataDir="/nfs/a285/homes/earrame/openquake/almaty_scenarios/chon_kemin_1911/one_fault/"
         outputname = "chonkemin1f"
    if scenario in ['CK2']:
         dataDir="/nfs/a285/homes/earrame/openquake/almaty_scenarios/chon_kemin_1911/two_fault/"
         outputname = "chonkemin2f"     
    if scenario in ['CKC']:   
         dataDir="/nfs/a285/homes/earrame/openquake/almaty_scenarios/chon_kemin_1911/complex_fault/"
         outputname = "chonkemincomplexf"
    if scenario in ['V']: 
         dataDir="/nfs/a285/homes/earrame/openquake/almaty_scenarios/verny_1887/"
         outputname = "verny"  
    if scenario in ['C']: 
         dataDir="/nfs/a285/homes/earrame/openquake/almaty_scenarios/chilik_1889/"
         outputname = "chilik" 
    if scenario in ['SP']:  
         dataDir="/nfs/a285/homes/earrame/openquake/almaty_scenarios/city_splay/"
         outputname = "citysplay"
    if scenario in ['KP']:  
         dataDir="/nfs/a285/homes/earrame/openquake/almaty_scenarios/deep_EQ_kazakhplatform/"
         outputname = "kazakhplatform"
    if scenario in ['T']:  
         dataDir="/nfs/a285/homes/earrame/openquake/almaty_scenarios/talgar/"
         outputname = "talgar"
    if scenario in ['NSP45']:  
         dataDir="/nfs/a285/homes/earrame/openquake/almaty_scenarios/northern_splay/just45degrees/"
         outputname = "northernsplay45"
    if scenario in ['NSPrf']:
         dataDir="/nfs/a285/homes/earrame/openquake/almaty_scenarios/northern_splay/rampflat_ish_just_abrahamson/"
         outputname = "northernsplayRF"
    

    for calculation in ['loss', 'dmg']:
    
        # Work out the calculation ID
        if calculation in ["dmg"]:
            temp = glob.glob(dataDir + "/outputs_damage/dmg_by_asset-rlz-*.csv")
            tempfile = temp[0]
            file = tempfile[len(dataDir)+37 :]
        if calculation in ["loss"]:
            temp = glob.glob(dataDir + "/outputs_loss/losses_by_asset-rlz-*.csv")
            tempfile = temp[0]
            file = tempfile[len(dataDir)+38 :]
        calcId = file[0: -4]
        
        # Load in the data. all have 3 realisations except for kazakh platform (KP) and northern rampflat with only 1      
        if calculation in ["dmg"]:
            rl0 = pd.read_csv(dataDir + "/outputs_damage/dmg_by_asset-rlz-000_" + calcId + ".csv", skiprows=0)
            if scenario in ['CK1', 'CK2', 'CKC', 'V', 'C', 'SP', 'T', 'NSP45']:
                rl1 = pd.read_csv(dataDir + "/outputs_damage/dmg_by_asset-rlz-001_" + calcId + ".csv", skiprows=0)
                rl2 = pd.read_csv(dataDir + "/outputs_damage/dmg_by_asset-rlz-002_" + calcId + ".csv", skiprows=0)
            colNames = ['COST_PER_AREA_USD', 'ID_0', 'ID_1', 'ID_2', 'ISO', 'NAME_0', 'NAME_1', 'NAME_2', 'OCCUPANCY','taxonomy','Lon','Lat','No','NoSTD','Slight','SlightSTD','Mod','ModSTD','Ext','ExtSTD','Col','ColSTD']
        if calculation in ["loss"]:
            rl0 = pd.read_csv(dataDir + "/outputs_loss/losses_by_asset-rlz-000_" + calcId + ".csv", skiprows=[0])
            if scenario in ['CK1', 'CK2', 'CKC', 'V', 'C', 'SP', 'T', 'NSP45']:
                rl1 = pd.read_csv(dataDir + "/outputs_loss/losses_by_asset-rlz-001_" + calcId + ".csv", skiprows=[0])
                rl2 = pd.read_csv(dataDir + "/outputs_loss/losses_by_asset-rlz-002_" + calcId + ".csv", skiprows=[0])
            colNames = ['COST_PER_AREA_USD', 'ID_0', 'ID_1', 'ID_2', 'ISO', 'NAME_0', 'NAME_1', 'NAME_2', 'OCCUPANCY','taxonomy','Lon','Lat','occupants_mean', 'occupants_std', 'structural_mean', 'structural_std']
        
        outDf = pd.DataFrame(columns = colNames)
        meanDf = pd.DataFrame(columns = colNames)
        
        # Add the known columns to the output df
        #outDf['ref'] = rl0['asset_ref'] they removed this in oq version 3.7
        outDf['taxonomy'] = rl0['taxonomy']
        outDf['Lon'] = rl0['lon']
        outDf['Lat'] = rl0['lat']
        outDf['COST_PER_AREA_USD'] = rl0['COST_PER_AREA_USD']
        outDf['ID_0'] = rl0['ID_0']
        outDf['ID_1'] = rl0['ID_1']
        outDf['ID_2'] = rl0['ID_2']
        outDf['ISO'] = rl0['ISO']
        outDf['NAME_0'] = rl0['NAME_0']
        outDf['NAME_1'] = rl0['NAME_1']
        outDf['NAME_2'] = rl0['NAME_2']
        outDf['OCCUPANCY'] = rl0['OCCUPANCY']
        
        # Calculate mean across the other columns
        #df = pd.concat([rl0, rl1, rl2]).groupby(level=0).mean()
        if scenario in ['CK1', 'CK2', 'CKC', 'V', 'C', 'SP', 'T', 'NSP45']:
            meandf = pd.concat([rl0, rl1, rl2]).groupby(level=0).mean()
        if scenario in ['KP', 'NSPrf']:
            meandf = rl0
        #df = pd.concat([rl0]).groupby(level=0).mean()
        
        #def calc_rlz_std( rlz0, rlz1, rlz2, stdvariable ):
        #   "calculate the standard deviation of each point for three realisations, using propagation of errors"
        #   std_of_rlzs = np.divide(np.sqrt(np.square(rlz0[stdvariable]) + np.square(rlz1[stdvariable]) + np.square(rlz2[stdvariable])), 3)
        #   return [std_of_rlzs]
        #
        #test = pd.DataFrame()
        #test['testytest'] = calc_rlz_std( rl0, rl1, rl2, 'structural~no_damage_stdv')
        
        # Add the mean columns to the output df
        if calculation in ["dmg"]:
            outDf['No'] = meandf['structural~no_damage_mean']
            #outDf['NoSTD'] = calc_rlz_std( rl0, rl1, rl2, 'structural~no_damage_stdv')
            outDf['Slight'] = meandf['structural~slight_mean']
            #outDf['SlightSTD'] = calc_rlz_std( rl0, rl1, rl2, 'structural~slight_stdv')
            outDf['Mod'] = meandf['structural~moderate_mean']
            #outDf['ModSTD'] = calc_rlz_std( rl0, rl1, rl2, 'structural~moderate_stdv')
            outDf['Ext'] = meandf['structural~extensive_mean']
            #outDf['ExtSTD'] = calc_rlz_std( rl0, rl1, rl2, 'structural~extensive_stdv')
            outDf['Col'] = meandf['structural~complete_mean']
            #outDf['ColSTD'] = calc_rlz_std( rl0, rl1, rl2, 'structural~complete_stdv')
            if scenario in ['CK1', 'CK2', 'CKC', 'V', 'C', 'SP', 'T', 'NSP45']:
                outDf['NoSTD'] = np.divide(np.sqrt(np.square(rl0['structural~no_damage_stdv']) + np.square(rl1['structural~no_damage_stdv']) + np.square(rl2['structural~no_damage_stdv'])),3)
                outDf['SlightSTD'] = np.divide(np.sqrt(np.square(rl0['structural~slight_stdv']) + np.square(rl1['structural~slight_stdv']) + np.square(rl2['structural~slight_stdv'])),3)
                outDf['ModSTD'] = np.divide(np.sqrt(np.square(rl0['structural~moderate_stdv']) + np.square(rl1['structural~moderate_stdv']) + np.square(rl2['structural~moderate_stdv'])),3)
                outDf['ExtSTD'] = np.divide(np.sqrt(np.square(rl0['structural~extensive_stdv']) + np.square(rl1['structural~extensive_stdv']) + np.square(rl2['structural~extensive_stdv'])),3)
                outDf['ColSTD'] = np.divide(np.sqrt(np.square(rl0['structural~complete_stdv']) + np.square(rl1['structural~complete_stdv']) + np.square(rl2['structural~complete_stdv'])),3)
            if scenario in ['KP', 'NSPrf']:
                outDf['NoSTD'] = rl0['structural~no_damage_stdv']
                outDf['SlightSTD'] = rl0['structural~slight_stdv']
                outDf['ModSTD'] = rl0['structural~moderate_stdv']
                outDf['ExtSTD'] = rl0['structural~extensive_stdv']
                outDf['ColSTD'] = rl0['structural~complete_stdv']
        if calculation in ["loss"]:
            outDf['occupants_mean'] = meandf['occupants~mean']
            #outDf['occupants_std'] = calc_rlz_std( rl0, rl1, rl2, 'occupants~stddev')
            outDf['structural_mean'] = meandf['structural~mean']
            #outDf['structural_std'] = calc_rlz_std( rl0, rl1, rl2, 'structural~stddev')
            if scenario in ['CK1', 'CK2', 'CKC', 'V', 'C', 'SP', 'T', 'NSP45']:
                outDf['occupants_std'] = np.divide(np.sqrt(np.square(rl0['occupants~stddev']) + np.square(rl1['occupants~stddev']) + np.square(rl2['occupants~stddev'])),3)
                outDf['structural_std'] = np.divide(np.sqrt(np.square(rl0['structural~stddev']) + np.square(rl1['structural~stddev']) + np.square(rl2['structural~stddev'])),3)
            if scenario in ['KP', 'NSPrf']:
                outDf['occupants_std'] = rl0['occupants~stddev']
                outDf['structural_std'] = rl0['structural~stddev']

        # Output results
        if calculation in ["dmg"]:
            outfile = dataDir + "/outputs_damage/calculated_mean_" + calculation + "_" + outputname + ".csv"
        if calculation in ["loss"]:
            outfile = dataDir + "/outputs_loss/calculated_mean_" + calculation + "_" + outputname + ".csv"
        outDf.to_csv(outfile, mode = 'w', index=False)
