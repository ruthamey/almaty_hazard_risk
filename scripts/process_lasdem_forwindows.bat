rem ! /bin/tcsh

rem Script to process a DEM using LAStools (http://lastools.org)
rem  
rem This script:
rem 	- converts las file into laz
rem 	- converts laz file into UTM coordinates
rem	- classified ground, removes noise
rem	- creates digital terrain model (DTM)
rem	- creates digital surface model (DSM)
rem	- creates a png and kml file
rem
rem For info see my google docs: https://docs.google.com/document/d/1D_HOKtUrl-m4Wy9qNot842LaCggtvYOJYCBv9xwViKw

SET file=spot_almaty_original_terrain_0_0
SET utmzone=43n
SET resolution=1.5
SET laspath=C:\software\LAStools\bin\

rem %#%#%#%#%#%#%#%#%#%#%   Pre-processing   #%#%#%#%#%#%#%#%#%#%#%#%#%#%
rem % Rename the .las file as _raw.las
copy %file%.las %file%_raw.las

rem %#%#%#%#% Convert las file to laz #%#%#%#%#%
%laspath%las2las -v -i %file%_raw.las -olaz -o %file%_raw.laz

rem %#%#%#%#% Convert long/lat to UTM #%#%#%#%#%
%laspath%las2las -v -i %file%_raw.laz -o %file%_raw_utm.laz -longlat -target_utm %utmzone% -elevation_meter -target_elevation_meter

rem %#%#%#%#% Make a png and kml of the initial point cloud #%#%#%#%#%
%laspath%lasgrid.exe -v -elevation -meter -wgs84 -false -opng -i %file%_raw.laz

rem find min and max of main file, to use for all the splits
rem lasinfo -i ${file}_raw_utm.laz -otxt -o ${file}_raw_info.txt
rem set minheight = `grep "min x y z" ${file}_raw_info.txt | awk '{ print $7}'`
rem set maxheight = `grep "max x y z" ${file}_raw_info.txt | awk '{ print $7}'`
rem # output as kmls and pngs
rem mkdir rawdem

rem %#%#%##%#%#%   Temporarily classify ground  #%#%#%#%#%#%#%#%#%%#%
rem Use lasthin to find highest points per 3.5m cell, classify as 8 (all other points = 0)
rem choosing percentile https://rapidlasso.com/category/median-ground/ 
%laspath%lasthin.exe -v -i %file%_raw_utm.laz -step 3.5 -highest -classify_as 8 -olaz -o %file%_raw_utm_lasthin.laz

rem Run lasnoise only on the points with classification code 8. Set isolated points as 7.
rem mkdir tiles_isolated
rem lasnoise.exe -v -i tiles_thinned/${file}*.laz -ignore_class 0 -step_xy $resolution -step_z 0.1 -isolated 4 -classify_as 7 -odir tiles_isolated -olaz -cores 12

rem Run lasground on only the surviving points (class 8). Sets classification of points as either ground (2) or non ground (1). (Ignore class 0 and 7)
rem %laspath%lasground.exe -v -i %file%_raw_utm_lasthin.laz -not_airborne -city -ultra_fine -ignore_class 0 7 -olaz -o %file%_raw_utm_lasthin_lasground.laz
rem lasground is limited to about 30 - 40 million
mkdir tiles
%laspath%lasindex -i %file%_raw_utm_lasthin.laz -cores 4
%laspath%lastile -i %file%_raw_utm_lasthin.laz -merged -o tiles -odir tiles -tile_size 2000 -buffer 50 -olaz -cores 4
mkdir tilesground
%laspath%lasground.exe -v -i tiles\*.laz -not_airborne -city -ultra_fine -ignore_class 0 7 -olaz -odir tilesground  -cores 4

rem %#%#%##%#%#%   Remove noise below ground  #%#%#%#%#%#%#%#%#%%#%
rem Run lasheight to classify everything 0.2m below the ground as noise (7) and all others as unclassified
mkdir tilesgroundnonoise
%laspath%lasheight.exe -i tilesground\*.laz -do_not_store_in_user_data -classify_below -0.05 7 -classify_above -0.05 1 -olaz -odir tilesgroundnonoise  -cores 4


rem %#%#%##%#%#%   Create DTM - always ignore noise (class 7)   #%#%#%#%#%#%#%#%#%%#%
rem Use lasthin to classify the LOWEST non-noise point per 'step' sized cell (ignoring class 7, which is noise)
mkdir tilesgroundnonoiselowest
%laspath%lasthin.exe -i tilesgroundnonoise\*.laz -ignore_class 7 -step %resolution% -lowest -classify_as 8 -odir tilesgroundnonoiselowest  -cores 4


rem Considering only lowest points, classify points as ground and non ground (ignoring class 7 (noise) and class 1 (non ground))
mkdir tilesgroundnonoiselowestclassified
%laspath%lasground.exe -i tilesgroundnonoiselowest\*.las -ignore_class 1 7 -city -ultra_fine -bulge 0.1 -odir tilesgroundnonoiselowestclassified -olaz  -cores 4

rem Remove buffers 
%laspath%lastile -i tilesgroundnonoiselowestclassified\*.laz -remove_buffer -odix _nobuffer -odir tilesgroundnonoiselowestclassified -olaz -cores 4

rem %#%#%##%#%#%  Make the final DTM and output it in laz, tif and hillshade.tif %#%#%##%#%#% 
mkdir dtm
%laspath%blast2dem.exe -i tilesgroundnonoiselowestclassified\*_nobuffer.laz -merged -keep_class 2 -step %resolution% -olaz -o %file%_dtm_utm.laz -odir dtm
rem Output DTM tif
rem %laspath%blast2dem.exe -i %file%_ground.laz -keep_class 2 -step %resolution% -otif -o %file%_dtm_utm.tif -odir dtm
%laspath%blast2dem.exe -i dtm\%file%_dtm_utm.laz -step %resolution% -otif -o %file%_dtm_utm.tif -odir dtm 
rem Output DTM hillshade tif
rem %laspath%blast2dem.exe -i %file%_ground.laz -keep_class 2 -step %resolution% -hillshade -otif -o %file%_dtm_hillshade_utm.tif -odir dtm
%laspath%blast2dem.exe -i dtm\%file%_dtm_utm.laz -step %resolution% -hillshade -otif -o %file%_dtm_hillshade_utm.tif -odir dtm
rem Output DTM png and kml
%laspath%lasgrid.exe -v -elevation -meter -wgs84 -false -step %resolution% -o %file%_dtm.png -opng -i dtm\%file%_dtm_utm.laz -odir dtm
rem Output DTM hillshade png and kml
rem %laspath%blast2dem.exe -i %file%_ground.laz -o %file%_dtm_hillshade.png -keep_class 2 -step %resolution% -hillshade -opng -odir dtm
%laspath%blast2dem.exe -i dtm\%file%_dtm_utm.laz -o %file%_dtm_hillshade.png -step %resolution% -hillshade -opng -odir dtm
rem Convert to grd for gmt
rem gdal_translate -of GMT dtm/${file}_dtm_merged.tif dtm/${file}_dtm_merged.grd
rem Convert back to longlat
%laspath%las2las.exe -i dtm\%file%_dtm_utm.laz -o %file%_dtm_lonlat.laz -utm %utmzone% -target_longlat -odir dtm
rem Output tiles as txt
%laspath%las2txt.exe -i dtm\%file%_dtm_lonlat.laz -o %file%_dtm_lonlat.txt -parse xyz -odir dtm



rem %#%#%##%#%#%   Create DSM    #%#%#%#%#%#%#%#%#%%#%
rem Use lasthin to classify the HIGHEST non-noise point per 'step' sized cell as class 8 (ignoring class 7, which is noise)
mkdir tileshighest
%laspath%lasthin.exe -i tilesgroundnonoise\*.laz -odir tileshighest -ignore_class 7 -step %resolution% -highest -classify_as 8 -olaz -cores 4

rem no need to use lasground again - we don't care which points are ground or not. we want all of the highest ones.

rem Remove buffer
%laspath%lastile -i tileshighest\*.laz -remove_buffer -odix _nobuffer -odir tileshighest -olaz -cores 4

rem Make the final DSM and output it in laz, tif and hillshade.tif
mkdir dsm
%laspath%blast2dem.exe -i tileshighest\*_nobuffer.laz -merged -o %file%_dsm_utm.laz -keep_class 8 -step %resolution% -olaz -odir dsm

rem Convert las back to longlat
%laspath%las2las.exe -i dsm\%file%_dsm_utm.laz -o %file%_dsm_lonlat.laz -utm %utmzone% -target_longlat -odir dsm

rem Output DSM tif
rem %laspath%blast2dem.exe -i %file%_highest.laz -keep_class 8 -step %resolution% -otif -o %file%_dsm.tif -odir dsm
%laspath%blast2dem.exe -i dsm\%file%_dsm_utm.laz -step %resolution% -otif -o %file%_dsm.tif -odir dsm
rem Output DSM hillshade tif
rem %laspath%blast2dem.exe -i %file%_highest.laz -keep_class 8 -step %resolution% -hillshade -otif -o %file%_dsm_hillshade.tif -odir dsm
%laspath%blast2dem.exe -i dsm\%file%_dsm_utm.laz -step %resolution% -hillshade -otif -o %file%_dsm_hillshade.tif -odir dsm
rem Output DSM png and kml
%laspath%lasgrid.exe -v -i dsm\%file%_dsm_utm.laz -step %resolution% -elevation -meter -wgs84 -false -opng -odir dsm -o %file%_dsm.png
rem Output DSM hillshade png and kml
rem %laspath%blast2dem.exe -i %file%_highest.laz -keep_class 8 -o %file%_dsm_hillshade.png  -step %resolution% -hillshade -opng -odir dsm
%laspath%blast2dem.exe -i dsm\%file%_dsm_utm.laz -o %file%_dsm_hillshade.png  -step %resolution% -hillshade -opng -odir dsm
rem Convert back to lonlat
%laspath%las2las.exe -i dsm\%file%_dsm_utm.laz -o %file%_dsm_lonlat.laz -utm %utmzone% -target_longlat -odir dsm
rem Output as txt
%laspath%las2txt.exe -i dsm\%file%_dsm_lonlat.laz -o %file%_dsm_lonlat.txt -odir dsm
rem las2txt.exe -i dsm/${file}_dsm_lonlat.laz -odir dsm -o ${file}_dsm_lonlat.txt -parse xyz


rem %#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%
rem %#%#%##%#%#%   Tidy intermediates    #%#%#%#%#%#%#%#%#%%#%
rem %#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%
del %file%_raw.las
del %file%_raw.laz
del %file%_raw_utm_lasthin.laz
del /f tilesground
del /f tilesgroundnonoise
del /f tilesgroundnonoiselowest
del /f tilesgroundnonoiselowestclassified
del /f tileshighest
rem del %file%_raw_utm_lasthin_lasground.laz
rem del %file%_raw_utm_lasthin_lasground_lasheight.laz
rem del %file%_raw_utm_lowest.laz
rem del %file%_ground.laz
rem del %file%_highest.laz

del dtm\%file%_dtm_utm.kml
del dtm\%file%_dtm_hillshade_utm.kml

echo Ta da!
