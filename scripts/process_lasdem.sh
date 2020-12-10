#! /bin/tcsh

# Script to process a DEM using LAStools (http://lastools.org)
#  
# This script:
# 	- converts las file into laz
# 	- converts laz file into UTM coordinates
#	- tiles laz file and then sorts tiles
#	- classified ground, removes noise
#	- creates digital terrain model (DTM)
#	- creates digital surface model (DSM)
#	- creates a png and kml file
#
# For info see my google docs: https://docs.google.com/document/d/1D_HOKtUrl-m4Wy9qNot842LaCggtvYOJYCBv9xwViKw

set file = $1
set utmzone = $2
set resolution = $3

#utmzone = 43north or 43n

#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%
#%#%#%#%#%#%#%#%#%#%#%   Pre-processing   #%#%#%#%#%#%#%#%#%#%#%#%#%#%
#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%

#% rename as raw
mv $file.las ${file}_raw.las

#%#%#%#%#% Convert las file to laz #%#%#%#%#%
las2las -v -i ${file}_raw.las -olaz -o ${file}_raw.laz

#%#%#%#%#% Convert long/lat to UTM #%#%#%#%#%
las2las -v -i ${file}_raw.laz -o ${file}_raw_utm.laz -longlat -target_utm $utmzone -elevation_meter -target_elevation_meter


#%#%#%#%#% Split las file into small enough las files for lastools free to work #%#%#%#%#%
# Tile - create small and buffered tiles
mkdir tiles_raw
lastile.exe -v -i ${file}_raw_utm.laz -tile_size 750 -buffer 50 -flag_as_withheld -epsg 32643 -odir tiles_raw -o ${file}.laz
echo "Note that EPSG:32643 (Almaty and Bishkek) is hard-wired in... should probably fix this"

# Sort tiles - rearranges the points into a more coherent spatial order
#mkdir tiles_sorted
#lassort.exe -v -i tiles_raw/${file}*.laz -odix _sorted -odir tiles_sorted -olaz -cores 12

#%#%#%#%#% Make a png and kml of the initial point cloud #%#%#%#%#%
# this is quick but will insert black line
lasgrid.exe -v -elevation -meter -wgs84 -false -opng -i ${file}_raw_utm.laz

# find min and max of main file, to use for all the splits
lasinfo -i ${file}_raw_utm.laz -otxt -o ${file}_raw_info.txt
set minheight = `grep "min x y z" ${file}_raw_info.txt | awk '{ print $7}'`
set maxheight = `grep "max x y z" ${file}_raw_info.txt | awk '{ print $7}'`
## output as kmls and pngs
mkdir rawdem


#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%
#%#%#%##%#%#%   temporarily classify ground  #%#%#%#%#%#%#%#%#%%#%
#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%

# Use lasthin to find highest points per 3.5m cell, classify as 8 (all other points = 0)
mkdir tiles_thinned
lasthin.exe -v -i tiles_raw/${file}*.laz -step 3.5 -highest -classify_as 8 -odir tiles_thinned -olaz -cores 12

# Run lasnoise only on the points with classification code 8. Set isolated points as 7.
#mkdir tiles_isolated
#lasnoise.exe -v -i tiles_thinned/${file}*.laz -ignore_class 0 -step_xy $resolution -step_z 0.1 -isolated 4 -classify_as 7 -odir tiles_isolated -olaz -cores 12

# Run lasground on only the surviving points (class 8). Sets classification of points as either ground (2) or non ground (1). (Ignore class 0 and 7)
mkdir temp_ground
lasground.exe -v -i tiles_thinned/${file}*.laz -not_airborne -city -ultra_fine -ignore_class 0 7 -odir temp_ground -olaz -cores 12

#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%
#%#%#%##%#%#%   Remove noise below ground  #%#%#%#%#%#%#%#%#%%#%
#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%

# Run lasheight to classify everything 0.2m below the ground as noise (7) and all others as unclassified
mkdir tiles_denoised
lasheight.exe -i temp_ground/${file}*.laz -do_not_store_in_user_data -classify_below -0.05 7 -classify_above -0.05 1 -odir tiles_denoised -olaz -cores 12
#-odix _denoised

#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%
#%#%#%##%#%#%   Create DTM - always ignore noise (class 7)   #%#%#%#%#%#%#%#%#%%#%
#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%

# Use lasthin to classify the LOWEST non-noise point per 'step' sized cell (ignoring class 7, which is noise)
mkdir thinned_lowest
lasthin.exe -i tiles_denoised/${file}*.laz -ignore_class 7 -step $resolution -lowest -classify_as 8 -odir thinned_lowest -olaz -cores 4

# Considering only lowest points, classify points as ground and non ground (ignoring class 7 (noise) and class 1 (non ground))
mkdir ground
lasground.exe -i thinned_lowest/${file}*.laz -ignore_class 1 7 -city -ultra_fine -bulge 0.1 -odir ground -olaz -cores 12


#%#%#%##%#%#%   Make and output useful things for DTM   #%#%#%#%#%#%#%#%#%%#%

# Make the final DTM and output it in laz, tif and hillshade.tif
mkdir dtm_tiles
# laz tiles
las2dem.exe -i ground/${file}*.laz -keep_class 2 -step $resolution -use_tile_bb -odir dtm_tiles -olaz -o ${file}_dtm.laz -cores 12
#las2las.exe -i dtm_tiles/*.laz -odir dtm_tiles -odix _longlat -olaz -utm $utmzone -target_longlat
# tif tiles
las2dem.exe -i ground/${file}*.laz -keep_class 2 -step $resolution -use_tile_bb -odir dtm_tiles -otif -o ${file}_dtm.tif -cores 12
#gdalwarp dtm_tiles/*.tif -t_srs "+proj=longlat +datum=WGS84 +zone=43 +hemisphere=north"
#las2dem.exe -i dtm_tiles/*_longlat.laz -step $resolution -use_tile_bb -odir dtm_tiles -otif -o ${file}_dtm_longlat.tif -cores 12
# Merge tif tiles
mkdir dtm
gdal_merge.py -v dtm_tiles/${file}*.tif -o dtm/${file}_dtm_merged.tif
#gdalwarp dtm_tiles/${file}*.tif -t_srs "WGS84 +proj=utm +zone=43 +hemisphere=north" dtm_tiles/${file}_dtm_longlat.tif
# tif hillshade tiles
las2dem.exe -i ground/${file}*.laz -keep_class 2 -step $resolution -hillshade -use_tile_bb -odir dtm_tiles -otif -odix _hillshade_dtm -cores 12 
# Merge tif tiles
gdal_merge.py -v dtm_tiles/${file}*_hillshade_dtm.tif -o dtm/${file}_hillshade_dtm_merged.tif


# Convert to grd for gmt
gdal_translate -of GMT dtm/${file}_dtm_merged.tif dtm/${file}_dtm_merged.grd

# Merge tiles
lasmerge.exe -i dtm_tiles/${file}*.laz -o ${file}_dtm_utm.laz -odir dtm

# Make a png and kml of merged .las  ---- SORT ciTHIS OUT to make separate ones and merge
#blast2dem.exe -i dtm/${file}.laz -merged -keep_class 2 -step $resolution -hillshade -o ${file}_dtm_hillshaded.png -odir dtm
# one with black lines for quickcheck - THIS WORKS I THINK BUT I COMMENTED IT OUT
#blast2dem.exe -i dtm/${file}_dtm_utm.laz -merged -step $resolution -hillshade -o ${file}_dtm_hillshaded.png -odir dtm
#lasgrid.exe -v -elevation -meter -wgs84 -false -set_min_max $minheight $maxheight -opng -i dtm/${file}_dtm_utm.laz -o ${file}_dtm.png -odir dtm
lasgrid.exe -v -elevation -meter -wgs84 -false -set_min_max $minheight $maxheight -opng -i dtm/${file}_dtm_utm.laz  -odir dtm
# separate for science
# tiff tiles
mkdir dtm/${file}_kml_tiles
#blast2dem.exe -i dtm_tiles/*.laz -step $resolution -o ${file}_dtm.png -odir dtm/kml
lasgrid.exe -v -i ground/${file}*.laz -keep_class 2 -elevation -meter -wgs84 -false -set_min_max $minheight $maxheight -odix _dtm -opng -odir dtm/${file}_kml_tiles
# hillshade tiles
mkdir dtm/${file}_kmlhillshade_tiles
#blast2dem.exe -i ground/${file}*.laz -keep_class 2 -step $resolution -hillshade -odix _dsm_hillshaded -opng -odir dtm/${file}_kmlhillshade_tiles
#- THIS WORKS I THINK BUT I COMMENTED IT OUT

#%#%#%#%#%  and merge the kmls - somehow ? %#%#%#%#% 
#mkdir outputdir
#mv *.kml ./outputdir/
#cd outputdir
#zip output.kmz *
#mv output.kmz ..
#cd ..

# Convert back to longlat
las2las.exe -i dtm/${file}_dtm_utm.laz -odir dtm -o ${file}_dtm_lonlat.laz -utm $utmzone -target_longlat

# Output tiles as txt
las2txt.exe -i dtm/${file}_dtm_lonlat.laz -odir dtm -odir dtm -o ${file}_dtm_lonlat.txt -parse xyz


#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%
#%#%#%##%#%#%   Create DSM    #%#%#%#%#%#%#%#%#%%#%
#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%

# Use lasthin to classify the HIGHEST non-noise point per 'step' sized cell as class 8 (ignoring class 7, which is noise)
mkdir thinned_highest
lasthin.exe -i tiles_denoised/${file}*.laz -ignore_class 7 -step $resolution -highest -classify_as 8 -odir thinned_highest -olaz -cores 4

# no need to use lasground again - we don't care which points are ground or not. we want all of the highest ones.



#%#%#%##%#%#%   Make and output useful things for DSM   #%#%#%#%#%#%#%#%#%%#%


# Make the final DSM and output it in laz, tif and hillshade.tif
mkdir dsm_tiles
# laz tiles
las2dem.exe -i thinned_highest/${file}*.laz -keep_class 8 -step $resolution -use_tile_bb -odir dsm_tiles -olaz -odix _dsm -cores 4

# Merge tiles
mkdir dsm
lasmerge.exe -i dsm_tiles/${file}*.laz -odir dsm -o ${file}_dsm_utm.laz

# Convert las back to longlat
las2las.exe -i dsm/${file}_dsm_utm.laz -odir dsm -o ${file}_dsm_lonlat.laz -utm $utmzone -target_longlat

# tif tiles
las2dem.exe -i thinned_highest/${file}*.laz -keep_class 8 -step $resolution -use_tile_bb -odir dsm_tiles -otif -o ${file}_dsm.tif -cores 12

# Merge tif tiles
gdal_merge.py -v dsm_tiles/${file}*.tif -o dsm/${file}_dsm_merged.tif
# tif hillshade tiles
#las2dem.exe -i dsm_tiles/${file}*.laz -step $resolution -hillshade -use_tile_bb -odir dsm_tiles -otif -odix _hillshade_dsm -cores 12 
las2dem.exe -i thinned_highest/${file}*.laz -keep_class 8 -step $resolution -hillshade -use_tile_bb -odir dsm_tiles -otif -odix _hillshade_dsm -cores 12
# Merge hillshade tif tiles
gdal_merge.py -v dsm_tiles/${file}*_hillshade_dsm.tif -o dsm/${file}_hillshade_dsm_merged.tif

# Merge tifs
gdal_merge.py dsm_tiles/*.tif -o dsm/${file}_dsm_merged.tif
gdalwarp dsm/${file}_dsm_merged.tif -t_srs "WGS84 +proj=utm +zone=43 +hemisphere=north" dsm/${file}_dsm_merged_longlat.tif

# Convert to grd for gmt
gdal_translate -of GMT dsm/${file}_dsm_merged_longlat.tif dsm/${file}_dsm_merged.grd


# Make a png and kml
# one with black lines for quickcheck#- THIS WORKS I THINK BUT I COMMENTED IT OUT
#blast2dem.exe -i dsm/${file}_dsm_utm.laz -merged -hillshade -step $resolution -odir dsm -o ${file}_dsm_hillshaded.png
#lasgrid.exe -v -elevation -meter -wgs84 -false -set_min_max $minheight $maxheight -opng -i dsm/${file}_dsm_utm.laz -o ${file}_dsm.png -odir dsm
lasgrid.exe -v -i dsm/${file}_dsm_utm.laz -elevation -meter -wgs84 -false -set_min_max $minheight $maxheight -opng -odix _dsm -odir dsm
# separate for science
mkdir dsm/${file}_kml_tiles
lasgrid.exe -v -i thinned_highest/${file}*.laz -keep_class 8  -elevation -meter -wgs84 -false -set_min_max $minheight $maxheight -odix _dsm -opng -odir dsm/${file}_kml_tiles
mkdir dsm/${file}_kmlhillshade_tiles
#blast2dem.exe -i thinned_highest/${file}*.laz -keep_class 8  -step $resolution -hillshade -odix _dsm_hillshaded -opng -odir dsm/${file}_kmlhillshade_tiles
#- THIS WORKS I THINK BUT I COMMENTED IT OUT

#%#%#%#%#%  and merge the kmls - somehow ? %#%#%#%#% 
#mkdir outputdir
#mv *.kml ./outputdir/
#cd outputdir
#zip output.kmz *
#mv output.kmz ..
#cd ..


# Output tiles as txt
las2txt.exe -i dsm/${file}_dsm_lonlat.laz -odir dsm -o ${file}_dsm_lonlat.txt
#las2txt.exe -i dsm/${file}_dsm_lonlat.laz -odir dsm -o ${file}_dsm_lonlat.txt -parse xyz


#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%
#%#%#%##%#%#%   Tidy intermediates    #%#%#%#%#%#%#%#%#%%#%
#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%#%
rm -rf dsm_tiles
rm -rf dtm_tiles
rm -rf ground
rm -rf rawdem
rm -rf temp_ground
rm -rf thinned_highest
rm -rf thinned_lowest
rm -rf tiles_denoised
rm -rf tiles_isolated
rm -rf tiles_raw
rm -rf tiles_sorted
rm -rf tiles_thinned

echo Ta da!
