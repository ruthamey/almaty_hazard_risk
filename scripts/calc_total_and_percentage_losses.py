#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 16:08:31 2019

@author: earrame
"""

import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure


# set up some names of stuff
Scenarios = ['Verny', 'Chilik', 'Chon Kemin', 'City splay', 'Northern splay 45', 'Talgar', 'Kazakh platform']
scenarios = ['verny_1887', 'chilik_1889', 'chon_kemin_1911', 'city_splay', 'northern_splay', 'talgar', 'deep_EQ_kazakhplatform']
#scenarios = ['northern_splay']
scenarios_short = ['V', 'C', 'CK', 'CS', 'NS', 'T', 'KP']
districts = ['almaly', 'alatau', 'auezov', 'bostandyk', 'jetysu', 'medeusouth', 'medeunorth', 'nauryzbay', 'turksib']
Districts = ['Almaly', 'Alatau', 'Auezov', 'Bostandyk', 'Jetysu', 'Medeu South', 'Medeu North', 'Nauryzbay', 'Turksib']
#dataDir = "/nfs/a285/homes/earrame/openquake/almaty_scenarios/"
dataDir = "./../openquake/almaty_scenarios/"
colnames = ['rlz_id', 'loss_type', 'unit', 'mean', 'stddev']

# make empty dataframes
percentageoccupantsDf = pd.DataFrame(columns = scenarios, index=districts)
percentagemoniesDf = pd.DataFrame(columns = scenarios, index=districts)
percentagebuildingsDf = pd.DataFrame(columns = scenarios, index=districts)
exposurepointtotalDf = pd.DataFrame(0, columns = scenarios, index=['occupants', 'structural', 'damage'])

# load totals dataframe
#totalsDf = pd.read_csv('/nfs/a285/homes/earrame/qgis/almaty_districts_exposurepoints/district_totals.csv')
totalsDf = pd.read_csv('./../qgis/almaty_districts_exposurepoints/district_totals.csv')

#for measurement in ['occupants', 'structural', 'dmg']:
for measurement in ['occupants', 'structural', 'damage']:
    
    figure(num=None, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
    plt.rcParams.update({'font.size': 24})
    markersize=18
    errorbarsize=25
    linewidthsize=5
    edgesize=5

    myx= 1
    
    for scenario in scenarios:
    
        if measurement in ['occupants', 'structural', 'damage']:
            # Work out the calculation ID (because each one is unique from openquake)
            if scenario in ['chon_kemin_1911']:
                #temp = glob.glob(dataDir + scenario + "/one_fault/outputs_loss/agglosses_*.csv") # one fault
                temp = glob.glob(dataDir + scenario + "/two_fault/outputs_loss/agglosses_*.csv") # two fault
                #temp = glob.glob(dataDir + scenario + "/complex_fault/outputs_loss/agglosses_*.csv") # two fault
            elif scenario in ['northern_splay']:
                temp = glob.glob(dataDir + scenario + "/just45degrees/outputs_loss/agglosses_*.csv") # 45 degree
                #temp = glob.glob(dataDir + scenario + "/rampflat_ish_just_abrahamson/outputs_loss/agglosses_*.csv") # ramp flat
            else:
                temp = glob.glob(dataDir + scenario + "/outputs_loss/agglosses_*.csv")
            tempfile = temp[0]
            if scenario in ['chon_kemin_1911']:
                file = tempfile[len(dataDir)+len(scenario)+34 :] # one or two faults
                #file = tempfile[len(dataDir)+len(scenario)+38 :] # complex faults
            elif scenario in ['northern_splay']:
                file = tempfile[len(dataDir)+len(scenario)+38 :] # 45 degree
                #file = tempfile[len(dataDir)+len(scenario)+53 :] # rampflat
            else:
                file = tempfile[len(dataDir)+len(scenario)+24 :]
            calcId = file[0: -4]
    
            # Load the file
            if scenario in ['chon_kemin_1911']:
                #dataDf = pd.read_csv(dataDir + scenario + "/one_fault/outputs_loss/agglosses_" + calcId + ".csv", skiprows=[0]) # one faults
                dataDf = pd.read_csv(dataDir + scenario + "/two_fault/outputs_loss/agglosses_" + calcId + ".csv", skiprows=[0]) # two faults
                #dataDf = pd.read_csv(dataDir + scenario + "/complex_fault/outputs_loss/agglosses_" + calcId + ".csv", skiprows=[0]) # complex faults
            elif scenario in ['northern_splay']:
                dataDf = pd.read_csv(dataDir + scenario + "/just45degrees/outputs_loss/agglosses_" + calcId + ".csv", skiprows=[0]) # 45 degrees
                #dataDf = pd.read_csv(dataDir + scenario + "/rampflat_ish_just_abrahamson/outputs_loss/agglosses_" + calcId + ".csv", skiprows=[0]) # rampflat
            else:
                dataDf = pd.read_csv(dataDir + scenario + "/outputs_loss/agglosses_" + calcId + ".csv", skiprows=[0])
            dataDf['mean'] = pd.to_numeric(dataDf['mean'], errors='coerce')
            dataDf['stddev'] = pd.to_numeric(dataDf['stddev'], errors='coerce')
        
            # Calculate means of the 3 GMPEs and propagate errors with the standard deviations
            meancalc = dataDf.groupby('loss_type')['mean'].mean()           #Here we groupby the 'loss_type' column, we then access the 'mean' column and call mean on it
            stddevcalc = np.sqrt(np.sum(np.square(dataDf.loc[dataDf['loss_type'] == measurement, 'stddev'])))
            # this is just the standard deviations#
            #dataDf.loc[dataDf['loss_type'] == 'occupants', 'stddev']
        

            ## load occupant loss per district. load stats on number of people per district. calculate percentage.
            for district in districts:
                
                # load csv file with the openquake results for that district
                #districtdata = pd.read_csv("/nfs/a285/homes/earrame/openquake/almaty_scenarios/districts_with_openquakeresults/" + district + "_district_openquakeresults.csv")
                districtdata = pd.read_csv("./../openquake/almaty_scenarios/districts_with_openquakeresults/" + district + "_district_openquakeresults.csv")
                
                if measurement in ['occupants']:
                    #districtdata = pd.read_csv("/nfs/a285/homes/earrame/openquake/almaty_scenarios/districts_with_openquakeresults/" + district + "_district_openquakeresults.csv")
                    if scenario in ['verny_1887']:
                        variablename = 'SUM_VOCCUP'
                    if scenario in ['chilik_1889']:
                        variablename = 'SUM_COCCUP'
                    if scenario in ['chon_kemin_1911']:
                        #variablename = 'SUM_CK1OCC' # one fault
                        variablename = 'SUM_CK2OCC' # two fault
                        #variablename = 'SUM_CKCOCC' # complex fault
                    if scenario in ['city_splay']:
                        variablename = 'SUM_SPOCCU'
                    if scenario in ['deep_EQ_kazakhplatform']:
                        variablename = 'SUM_KPOCCU'
                    if scenario in ['northern_splay']:
                        variablename = 'SUM_N45OCC' # 45 degree
                        #variablename = 'SUM_NRFOCC' # ramp flat
                    if scenario in ['talgar']:
                        variablename = 'SUM_TOCCUP'
                    thing = districtdata[variablename] / totalsDf.loc[1,district] * 100
                    percentageoccupantsDf.loc[district,scenario] = thing[0] # calculate percentage, put in percentage occupants
                    
                    ### load district totals to calculate percentage (and check adds up) ###
                    # check against openquake output totals
                    addnextdistrict = exposurepointtotalDf.loc[measurement, scenario] + districtdata[variablename]
                    exposurepointtotalDf.loc[measurement, scenario] = addnextdistrict[0]
                    
                if measurement in ['structural']:
                    #districtdata = pd.read_csv("/nfs/a285/homes/earrame/openquake/almaty_scenarios/districts_with_openquakeresults/" + district + "_district_openquakeresults.csv")
                    if scenario in ['verny_1887']:
                        variablename = 'SUM_VSTRUC'
                    if scenario in ['chilik_1889']:
                        variablename = 'SUM_CSTRUC'
                    if scenario in ['chon_kemin_1911']:
                        #variablename = 'SUM_CK1STR' # one fault
                        variablename = 'SUM_CK2STR' # two fault
                        #variablename = 'SUM_CKCSTR' # complex faultlts
                    if scenario in ['city_splay']:
                        variablename = 'SUM_SPSTRU'
                    if scenario in ['deep_EQ_kazakhplatform']:
                        variablename = 'SUM_KPSTRU'
                    if scenario in ['northern_splay']:
                        variablename = 'SUM_N45STR' # 45 degree
                        #variablename = 'SUM_NRFSTR' # ramp flat
                    if scenario in ['talgar']:
                        variablename = 'SUM_TSTRUC'
                    thing = districtdata[variablename] / totalsDf.loc[2,district] * 100
                    percentagemoniesDf.loc[district,scenario] = thing[0] # calculate percentage, put in percentage monies
                    
                    ### load district totals to calculate percentage (and check adds up) ###
                    # check against openquake output totals
                    addnextdistrict = exposurepointtotalDf.loc[measurement, scenario] + districtdata[variablename]
                    exposurepointtotalDf.loc[measurement, scenario] = addnextdistrict[0]
                    
                if measurement in ['damage']:
                    #districtdata = pd.read_csv("/nfs/a285/homes/earrame/openquake/almaty_scenarios/districts_with_openquakeresults/" + district + "_district_openquakeresults.csv")
                    if scenario in ['verny_1887']:
                        variablename = 'SUM_VCOMPL'
                    if scenario in ['chilik_1889']:
                        variablename = 'SUM_CCOMPL'
                    if scenario in ['chon_kemin_1911']:
                        #variablename = 'SUM_CK1COM' # one fault
                        variablename = 'SUM_CK2COM' # two fault
                        #variablename = 'SUM_CKCCOM' # complex faults
                    if scenario in ['city_splay']:
                        variablename = 'SUM_SPCOMP'
                    if scenario in ['deep_EQ_kazakhplatform']:
                        variablename = 'SUM_KPCOMP'
                    if scenario in ['northern_splay']:
                        variablename = 'SUM_N45COM' # 45 degree
                        #variablename = 'SUM_NRFCOM' # ramp flat
                    if scenario in ['talgar']:
                        variablename = 'SUM_TCOMPL'
                    thing = districtdata[variablename] / totalsDf.loc[0,district] * 100
                    percentagebuildingsDf.loc[district,scenario] = thing[0] # calculate percentage, put in percentage monies
                    
                    ### load district totals to calculate percentage (and check adds up) ###
                    # check against openquake output totals
                    addnextdistrict = exposurepointtotalDf.loc[measurement, scenario] + districtdata[variablename]
                    exposurepointtotalDf.loc[measurement, scenario] = addnextdistrict[0] 

#        if measurement in ['dmg']:
#            # Work out the file name
#            if scenario in ['chon_kemin_1911']:
#                temp = glob.glob(dataDir + scenario + "/two_fault/outputs_damage/dmg_by_event_*.csv")
#            else:
#                temp = glob.glob(dataDir + scenario + "/outputs_damage/dmg_by_event_*.csv")
#            tempfile = temp[0]
#            if scenario in ['chon_kemin_1911']:
#                file = tempfile[len(dataDir)+len(scenario)+39 :]
#            else:
#                file = tempfile[len(dataDir)+len(scenario)+29 :]
#            calcId = file[0: -4]
#            
#            # Load the file
#            if scenario in ['chon_kemin_1911']:
#                dataDf = pd.read_csv(dataDir + scenario + "/two_fault/outputs_damage/dmg_by_event_" + calcId + ".csv")
#            else:
#                dataDf = pd.read_csv(dataDir + scenario + "/outputs_damage/dmg_by_event_" + calcId + ".csv")
#    
#            # Calculate mean of realisations and standard deviations
#            meancalc = dataDf['structural~complete'].mean()
#            stddevcalc = np.std(dataDf['structural~complete'])
    #%%
    
#        # Plot
#        if measurement in ['occupants']:
#            #plt.errorbar(x=myx, y = dataDf.loc[0, 'mean'], yerr=dataDf.loc[0, 'stddev'], ms=markersize, fmt='o', color='red', mec='black', mew=linewidthsize, capsize=errorbarsize, elinewidth=linewidthsize, capthick=edgesize)
#            plt.errorbar(x=myx, y=meancalc.iloc[0], yerr=stddevcalc, ms=markersize, fmt='o', color='red', mec='black', mew=linewidthsize, capsize=errorbarsize, elinewidth=linewidthsize, capthick=edgesize)
#            plt.axis(ymin=0, ymax=8500) 
#            #plt.ylabel("Fatalities")
#            
#        if measurement in ['structural']:
#            #plt.errorbar(x=myx, y = dataDf.loc[1, 'mean'], yerr=dataDf.loc[1, 'stddev'], ms=markersize, fmt='o', color='green', mec='black', mew=linewidthsize, capsize=errorbarsize, elinewidth=linewidthsize, capthick=edgesize)
#            plt.errorbar(x=myx, y=meancalc.iloc[1], yerr=stddevcalc, ms=markersize, fmt='o', color='green', mec='black', mew=linewidthsize, capsize=errorbarsize, elinewidth=linewidthsize, capthick=edgesize)
#            plt.axis(ymin=0, ymax=8e9)
#            #plt.ylabel("Structral Loss (USD)")
#            #plt.yaxis.tick_right()
#            #plt.yaxis.set_label_position("right")
#        if measurement in ['dmg']:
#            plt.errorbar(x=myx, y=meancalc, yerr=stddevcalc, ms=markersize, fmt='o', color='blue', mec='black', mew=linewidthsize, capsize=errorbarsize, elinewidth=linewidthsize, capthick=edgesize)
#  
#        # Add one on so they don't plot on top of each other 
#        myx = myx+1
#        
#    # Label axes
#    plt.xticks([1, 2,3,4,5,6,7], scenarios_short)
#    # Save
#    plt.savefig(('/nfs/a285/homes/earrame/figures/almaty_damage_loss_maps/' + measurement + '_totals.png'), bbox_inches='tight')