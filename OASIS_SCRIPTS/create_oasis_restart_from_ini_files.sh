#!/bin/bash -e

# Justino justino@icm.csic.es
# WW3 tools
# Generates a CROCO oasis restart file from initial conditions used for CROCO
#

#
# This a modified version of create_oasis_restart_from_preexisting_output_files.sh
#

####################                        #####################################
#################### Notes on original file #####################################
####################                        #####################################
## ----------------------------------------------------------------------------- #
## - Create restart file for oasis                                             - #
## - from pre-existing model file                                              - #
##                                                                             - #
## Mandatory inputs:                                                           - #
##  - the model file name (with full path)                                     - #
##  - the oasis restart file name (with full path)                             - #
##  - the model: wrf, croco, or ww3 cases are accepted                         - #
## Optional input:                                                             - #
##  - the grid levels: for croco: 0 for parent, 1 for child, etc               - #
##                     for wrf: examples: WRF_d01_EXT_d01 or WRF_d02_EXT_d01   - #
##                       domain 1 of WRF coupled with domain 1 of other model  - #
##                       domain 2 of WRF coupled with domain 1 of other model  - #
##                                                                             - #
## ----------------------------------------------------------------------------- #
#
# Further Information:   
# http://www.croco-ocean.org
#  
# This file is part of CROCOTOOLS
#
# CROCOTOOLS is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 2 of the License,
# or (at your option) any later version.
#
# CROCOTOOLS is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA  02111-1307  USA
#
# Copyright (c) 2018 S. Jullien
# swen.jullien@ifremer.fr
## ----------------------------------------------------------------------------- #

# ------------------------------------------------------------------------------ #
dir="$(dirname $0)"
if [[ ${dir:0:1} == "/" ]] ; then 
	SCRIPTDIR=${dir}
else 
	curdir=$(pwd)
	SCRIPTDIR=${curdir}/${dir}
fi
filein=$1
fileout=$2
fileangle=$3

# ------------------------------------------------------------------------------ #
echo '*******************************************************************'
echo 'START script create_oasis_restart_from_ini_files.sh'
echo '*******************************************************************'
echo ' '

# First check if inputs are ok
if [[ -z $filein ]] || [[ -z $fileout ]] || [[ -z $fileangle ]] ; then
    echo 'ERROR: inputs are not correctly specified.'
    echo '       this script needs 3 inputs:'
    echo '       - the croco initial conditions file (with full path)'
    echo '       - the output oasis restart file name (with full path)'
    echo '       - the croco file containing angle and mask_rho variables (for instance CROCO bathymetry file)'
    echo ' Exit...'
    echo ' '
    exit 1
fi 
# ------------------------------------------------------------------------------ #
if [ -f $fileout ]; then
 	echo "The file $fileout exists, please delete it before execute this script"
 	exit
fi

mydir=$(dirname "$fileout")
filetmp0=$mydir/rst_tmp0_$$.nc
filetmp=$mydir/rst_tmp_$$.nc

echo "Copying initial conditions file"
cp $filein $filetmp0

ncks -A -v angle,mask_rho $fileangle $filetmp0

varlist=(CROCO_EOCE${gridlevels} \
         CROCO_NOCE${gridlevels} \
         CROCO_SST${gridlevels} \
         CROCO_SSH${gridlevels})

dimtime=time
timerange=1


echo ' '
echo 'Varlist to proceed is '$varlist
echo '========================================================================='
lengthvar=${#varlist[@]}
for k in `seq 0 $(( ${lengthvar} - 1))` ; do

    var=${varlist[$k]}
    echo ' '
    echo '======================'
    echo 'Process '$var'...'
    echo '======================'

    # Extract or compute var
    echo '---> Extract or compute '$var
    ${SCRIPTDIR}/OASIS_SCRIPTS/WW3_tools_from_croco.sh $filetmp0 $filetmp $var $timerange 
    # Remove time dimension
    echo '---> Remove time dimension...'
    ncwa -O -a $dimtime $filetmp $filetmp
    ncrename -d .eta_v,eta_rho -d .xi_u,xi_rho $filetmp
    ncks -A -v $var $filetmp $fileout
    rm $filetmp
done # LOOP on varlist
# remove global attributes
ncatted -h -O -a ,global,d,, $fileout $fileout 

echo "Apply mask and defining missing values..."
# Extract dimensions
xi_rho=`ncdump -h $filetmp0 | grep "xi_rho = " | cut -d '=' -f2 | cut -d ';' -f1`
xi_rho=${xi_rho// /}
eta_rho=`ncdump -h $filetmp0 | grep "eta_rho = " | cut -d '=' -f2 | cut -d ';' -f1`
eta_rho=${eta_rho// /}

ncks -h -A -v mask_rho -d xi_rho,0,$((${xi_rho}-3)) -d eta_rho,0,$((${eta_rho}-3)) ${filetmp0} ${fileout}
ncap2 -h -O -S 'mask_ini.nco' ${fileout} ${filetmp}
ncks -h -O -x -v mask_rho ${filetmp} ${fileout}
ncatted -h -a _FillValue,,c,f,0.0 ${fileout}

echo "Deleting copy of initial conditions file and temporal file"
rm $filetmp0 ${filetmp}
    



echo $fileout" has been created"

