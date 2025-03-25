#!/bin/bash
# LRO WAC Mono Level 1 processing of a single raw image (.IMG)
# Execute this file by typing: ./lrowac1.sh image_name=M119415370ME clon=67.23 clat=28.46 resolution=64.42046980734709 newmaptemplate=true

# Initialize default values for the variables
image_name=""
clon=""
clat=""
resolution=""
newmaptemplate=false  # default to false

base_dir="/home/james/MyFolder/code/GIT/ai4space_labelling_studio"

# Parse the command-line arguments
for arg in "$@"
do
  case $arg in
    image_name=*) image_name="${arg#*=}" ;;
    clon=*) clon="${arg#*=}" ;;
    clat=*) clat="${arg#*=}" ;;
    resolution=*) resolution="${arg#*=}" ;;
    projection=*) projection="${arg#*=}" ;;
    newmaptemplate=*) newmaptemplate="${arg#*=}" ;;
    *) echo "Invalid argument: $arg" ;;
  esac
done

# Check if mandatory variables are set
if [[ -z "$image_name" || -z "$clon" || -z "$clat" || -z "$resolution" ]]; then
  echo "Error: Missing required arguments (image_name, clon, clat, resolution)"
  exit 1
fi

echo "Processing image $image_name with clon=$clon, clat=$clat, resolution=$resolution"
echo "New map template: $newmaptemplate"

# Convert raw image (.IMG) to ISIS cube format (.cub)
lrowac2isis from=${base_dir}/input/${image_name}.IMG to=${base_dir}/temp/${image_name}.cub

# Initialize SPICE kernels for geometric data
spiceinit from=${base_dir}/temp/${image_name}.vis.even.cub web=true url=https://astrogeology.usgs.gov/apis/ale/v0.9.1/spiceserver/
spiceinit from=${base_dir}/temp/${image_name}.vis.odd.cub web=true url=https://astrogeology.usgs.gov/apis/ale/v0.9.1/spiceserver/

# # Apply radiometric calibration
lrowaccal from=${base_dir}/temp/${image_name}.vis.even.cub to=${base_dir}/temp/${image_name}_even_cal.cub
lrowaccal from=${base_dir}/temp/${image_name}.vis.odd.cub to=${base_dir}/temp/${image_name}_odd_cal.cub

# Apply photometric correction
photomet from=${base_dir}/temp/${image_name}.vis.even.cub to=${base_dir}/temp/${image_name}_even_cal_phot.cub frompvl=$ISISROOT/appdata/templates/photometry/moon_clementine_uvvis_a.pvl
photomet from=${base_dir}/temp/${image_name}.vis.odd.cub to=${base_dir}/temp/${image_name}_odd_cal_phot.cub frompvl=$ISISROOT/appdata/templates/photometry/moon_clementine_uvvis_a.pvl

# Check if newmaptemplate is true, then run maptemplate mercator*, transversemercator*, orthographic*, polarstereographic*, simplecylindrical, equirectangular*, lambertconformal, lambertazimuthalequalarea*, obliquecylindrical, pointperspective, robinson
if [ "$newmaptemplate" = true ]; then
  echo "Generating a new map template with clon=$clon, clat=$clat, resolution=$resolution."
  maptemplate map=${base_dir}/temp/${image_name} projection=$projection clon=$clon clat=$clat targopt=user targetname=moon resopt=mpp resolution=$resolution 
else
  echo "Skipping map template generation."
fi

# Map project the calibrated and photometrically corrected cubes
cam2map from=${base_dir}/temp/${image_name}_even_cal_phot.cub map=${base_dir}/temp/${image_name}.map to=${base_dir}/temp/${image_name}_even_cal_phot_map.cub pixres=map
cam2map from=${base_dir}/temp/${image_name}_odd_cal_phot.cub map=${base_dir}/temp/${image_name}.map to=${base_dir}/temp/${image_name}_odd_cal_phot_map.cub pixres=map

# Combine the even and odd images into a single output cube
echo ${base_dir}/temp/${image_name}_even_cal_phot_map.cub > ${base_dir}/temp/${image_name}_list.txt
echo ${base_dir}/temp/${image_name}_odd_cal_phot_map.cub >> ${base_dir}/temp/${image_name}_list.txt

noseam fromlist=${base_dir}/temp/${image_name}_list.txt to=${base_dir}/temp/${image_name}.cub samples=333 lines=333

echo "Processing of $image_name completed."

# make a directory for the output
mkdir -p ${base_dir}/output/${image_name} 

isis2std from=${base_dir}/temp/${image_name}.cub to=${base_dir}/output/${image_name}/${image_name}.png

# Move to the output folder
mv ${base_dir}/temp/${image_name}.cub ${base_dir}/output/${image_name}/${image_name}.cub
mv ${base_dir}/input/${image_name}.IMG ${base_dir}/output/${image_name}/${image_name}.IMG

# Clean up temporary files from temp folder
rm ${base_dir}/temp/${image_name}*
rm ${base_dir}/output/${image_name}/${image_name}.pgw

