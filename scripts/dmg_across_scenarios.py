# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 09:43:14 2018

@author: ekhuss
"""

import pandas as pd


# EDIT THIS AND ONLY THIS
# % # % # % # % # % # %
dataDir = "/nfs/a285/homes/earrame/openquake/almaty_scenarios/"
outputname = "almaty"
# % # % # % # % # % # %
# don't edit anything else please


for calculation in ['dmg', 'loss']:


    #CK1 = chonkemin1f
    #CK2 = chonkemin2f
    #CKc = chonkemincomplex
    #V = verny
    #C = chilik
    
    scenarios = ['CK1', 'CK2', 'CKC', 'C', 'V', 'SP', 'KP', 'T', 'N45', 'Nrf']
    
    #colNames = ['ref','taxonomy','Lon','Lat','chonkemin1f','chonkemin2f','chonkemincomplexf','verny',
    #            'chilik']
    if calculation in ["dmg"]:
        colNames = ['taxonomy','Lon','Lat','CK1complete','CK1completeSTD','CK2complete','CK2completeSTD','CKCcomplete','CKCcompleteSTD', 'Vcomplete', 'VcompleteSTD', 'SPcomplete', 'SPcompleteSTD']
    if calculation in ["loss"]:
        colNames = ['taxonomy','Lon','Lat','CK1occupants','CK1occupantsSTD','CK1structural','CK1structuralSTD','CK2occupants','CK2occupantsSTD','CK2structural','CK2structuralSTD','CKCoccupants','CKCoccupantsSTD','CKCstructural','CKCstructuralSTD', 'Voccupants', 'VoccupantsSTD', 'Vstructural', 'VstructuralSTD', 'SPoccupants', 'SPoccupantsSTD', 'SPstructural', 'SPstructuralSTD']
    outDf = pd.DataFrame(columns = colNames)
    
    CK1 = pd.read_csv(dataDir + "chon_kemin_1911/one_fault/outputs_damage/calculated_mean_dmg_chonkemin1f.csv")
    
    # Add the known columns to the output df
    #outDf['ref'] = CK1['ref'] they removed this in oq version 3.7
    outDf['taxonomy'] = CK1['taxonomy']
    outDf['Lon'] = CK1['Lon']
    outDf['Lat'] = CK1['Lat']
    
    
    # Add the collapse counts to the output df
    if calculation in ["dmg"]:
        
        for scenario in scenarios:
            
            # load appropriate dataframe for current scenario
            if scenario in ['CK1']:
                scenariodf = pd.read_csv(dataDir + "chon_kemin_1911/one_fault/outputs_damage/calculated_mean_dmg_chonkemin1f.csv")
            if scenario in ['CK2']:
                scenariodf = pd.read_csv(dataDir + "chon_kemin_1911/two_fault/outputs_damage/calculated_mean_dmg_chonkemin2f.csv")
            if scenario in ['CKC']:
                scenariodf = pd.read_csv(dataDir + "chon_kemin_1911/complex_fault/outputs_damage/calculated_mean_dmg_chonkemincomplexf.csv")
            if scenario in ['V']:
                scenariodf = pd.read_csv(dataDir + "verny_1887/outputs_damage/calculated_mean_dmg_verny.csv")
            if scenario in ['C']:        
                scenariodf = pd.read_csv(dataDir + "chilik_1889/outputs_damage/calculated_mean_dmg_chilik.csv")
            if scenario in ['SP']:
                scenariodf = pd.read_csv(dataDir + "city_splay/outputs_damage/calculated_mean_dmg_citysplay.csv")
            if scenario in ['KP']:
                scenariodf = pd.read_csv(dataDir + "deep_EQ_kazakhplatform/outputs_damage/calculated_mean_dmg_kazakhplatform.csv")
            if scenario in ['T']:
                scenariodf = pd.read_csv(dataDir + "talgar/outputs_damage/calculated_mean_dmg_talgar.csv")
            if scenario in ['N45']:
                scenariodf = pd.read_csv(dataDir + "northern_splay/just45degrees/outputs_damage/calculated_mean_dmg_northernsplay45.csv")
            if scenario in ['Nrf']:
                scenariodf = pd.read_csv(dataDir + "northern_splay/rampflat_ish_just_abrahamson/outputs_damage/calculated_mean_dmg_northernsplayRF.csv")
            
            # update outdataframe with the info
            #complete
            outDf[scenario + 'complete'] = scenariodf['Col']
            outDf[scenario + 'completeSTD'] = scenariodf['ColSTD']
            #extensive
            outDf[scenario + 'ext'] = scenariodf['Ext']
            outDf[scenario + 'extSTD'] = scenariodf['ExtSTD']
            #moderate
            outDf[scenario + 'mod'] = scenariodf['Mod']
            outDf[scenario + 'modSTD'] = scenariodf['ModSTD']       
            #slight
            outDf[scenario + 'slight'] = scenariodf['Slight']
            outDf[scenario + 'slightSTD'] = scenariodf['SlightSTD']        
            #none
            outDf[scenario + 'no'] = scenariodf['No']
            outDf[scenario + 'noSTD'] = scenariodf['NoSTD']  
           
            del scenariodf
            
    if calculation in ["loss"]:
        
        for scenario in scenarios:
        
            
            # load appropriate dataframe for current scenario
            if scenario in ['CK1']:
                scenariodf = pd.read_csv(dataDir + "chon_kemin_1911/one_fault/outputs_loss/calculated_mean_loss_chonkemin1f.csv")
            if scenario in ['CK2']:
                scenariodf = pd.read_csv(dataDir + "chon_kemin_1911/two_fault/outputs_loss/calculated_mean_loss_chonkemin2f.csv")
            if scenario in ['CKC']:
                scenariodf = pd.read_csv(dataDir + "chon_kemin_1911/complex_fault/outputs_loss/calculated_mean_loss_chonkemincomplexf.csv")
            if scenario in ['V']:
                scenariodf = pd.read_csv(dataDir + "verny_1887/outputs_loss/calculated_mean_loss_verny.csv")
            if scenario in ['C']: 
                scenariodf = pd.read_csv(dataDir + "chilik_1889/outputs_loss/calculated_mean_loss_chilik.csv")
            if scenario in ['SP']:
                scenariodf = pd.read_csv(dataDir + "city_splay/outputs_loss/calculated_mean_loss_citysplay.csv")
            if scenario in ['KP']:
                scenariodf = pd.read_csv(dataDir + "deep_EQ_kazakhplatform/outputs_loss/calculated_mean_loss_kazakhplatform.csv")
            if scenario in ['T']:
                scenariodf = pd.read_csv(dataDir + "talgar/outputs_loss/calculated_mean_loss_talgar.csv")
            if scenario in ['N45']:
                scenariodf = pd.read_csv(dataDir + "northern_splay/just45degrees/outputs_loss/calculated_mean_loss_northernsplay45.csv")
            if scenario in ['Nrf']:
                scenariodf = pd.read_csv(dataDir + "northern_splay/rampflat_ish_just_abrahamson/outputs_loss/calculated_mean_loss_northernsplayRF.csv")
            
            # occupants
            outDf[scenario + 'occupants'] = scenariodf['occupants_mean']
            outDf[scenario + 'occupantsSTD'] = scenariodf['occupants_std']
            # structural loss
            outDf[scenario + 'structural'] = scenariodf['structural_mean']
            outDf[scenario + 'structuralSTD'] = scenariodf['structural_std']
        
            del scenariodf
    
    # Output results
    if calculation in ["dmg"]:
        outfile = dataDir + "dmg_all_" + outputname + ".csv"
    if calculation in ["loss"]:
        outfile = dataDir + "loss_all_" + outputname + ".csv"
    outDf.to_csv(outfile, mode = 'w', index=False)
    
    
    ### Calculate total damage for different building classes
    
    if calculation in ["dmg"]:
        df = outDf
    
        colNames = ['Building class','Vcomplete','Ccomplete','CK2complete', 'SPcomplete', 'NSPcomplete', 'Tcomplete', 'KPcomplete','Sum']
        outdf = pd.DataFrame(columns = colNames)
        #outdf['Building class'] = ['CR','MCF','MR','MUR','W','UNK','Total']
        outdf['Building class'] = ['Reinforced concrete','Confined masonry','Reinforced masonry','Unreinforced masonry','Wooden', 'Steel','Unknown/Insufficient information','Total']
        
        
        scenarios = ['Vcomplete','Ccomplete','CK2complete', 'SPcomplete', 'N45complete', 'Nrfcomplete', 'Tcomplete', 'KPcomplete' ]
        for scenario in scenarios:
            CRsum = int(df[(df['taxonomy'].str.contains('CR'))].sum()[scenario])
            MCFsum = int(df[(df['taxonomy'].str.contains('MCF'))].sum()[scenario])
            MRsum = int(df[(df['taxonomy'].str.contains('MR'))].sum()[scenario])
            MURsum = int(df[(df['taxonomy'].str.contains('MUR'))].sum()[scenario])
            Wsum1 = int(df[(df['taxonomy'].str.contains('WLI'))].sum()[scenario])
            Wsum2 = int(df[(df['taxonomy'].str.contains('W/LWAL'))].sum()[scenario])
            Wsum=Wsum1+Wsum2
            Ssum = int(df[(df['taxonomy'].str.contains('S/LFM'))].sum()[scenario])
            UNKsum = int(df[(df['taxonomy'].str.contains('UNK'))].sum()[scenario])
            
            sumall = int(df[df[scenario] > 1.0 ].sum()[scenario])
            outdf[scenario] = [CRsum, MCFsum, MRsum, MURsum, Wsum, Ssum, UNKsum, sumall]
    
        outdf['Sum'] = outdf.sum(axis=1)
    
        #output to a csv file
        outfile = dataDir + "/dmg_summaries_by_taxonomy_" + outputname + ".csv"
        outdf.to_csv(outfile, mode = 'w', index=False)
        
