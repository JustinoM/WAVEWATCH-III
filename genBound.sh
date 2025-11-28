#!/bin/bash

# Justino justino@icm.csic.es
# WW3 tools
# Checks where CATSEA.mask has a "2" and generates lat lon boundary 
# line to be inserted in ww3_grid.nml to generate nested data
#

NAME="CATSEA"
if [ -z $2 ]; then 
	echo "Usage: $0 [Output for ww3_grid=1 output standard=0] [folder where "${NAME}".mask, "${NAME}"_y.inp and "${NAME}"_x.inp are located] [suffix for the names _4 etc]"	
	exit
fi


typeou=$1
folder=$2
if [ ! -z $3 ]; then
	suffix=$3
else
	suffix=""
fi

mask="${folder}/${NAME}${suffix}.mask"
fx="${folder}/${NAME}_x${suffix}.inp"
fy="${folder}/${NAME}_y${suffix}.inp"

# copy lat and lon corresponding to "2" in the mask
awk 'FNR==NR { for (i=1; i<NF+1;i++){ A[NR,i]=$i;}; next } { for (i=1; i<NF+1;i++){if (A[FNR,i]=="2") {printf "%+.8f\n", $i}}}' ${mask} ${fy} > /tmp/y$$
awk 'FNR==NR { for (i=1; i<NF+1;i++){ A[NR,i]=$i;}; next } { for (i=1; i<NF+1;i++){if (A[FNR,i]=="2") {printf " %+.8f\n", $i}}}' ${mask} ${fx} > /tmp/x$$

# Drop "corner" point... For CATSEA is the lower y and max x
miny=$(cat /tmp/y$$ | awk -v min=999 '{if ($1<min) {min=$1}} END{print min}')
maxx=$(cat /tmp/x$$ | awk -v max=-999 '{if ($1>max) {max=$1}} END{print max}')
corner=" $maxx $miny"

# tac -> reverse the files
paste /tmp/x$$ /tmp/y$$ | sed 's|\t| |g' > /tmp/c$$ # | grep -v "$corner" |tac > /tmp/c$$
rm /tmp/x$$ /tmp/y$$

if ((typeou==1)); then 
	cat /tmp/c$$ | awk -v p=0 'function abs(x){return ((x < 0.0) ? -x : x)}{
	xinc[p]=$1-xant
	yinc[p]=$2-yant
	px[p]=$1
	py[p]=$2
	xant=$1
	yant=$2
	p=p+1
	lin=1
	} END { 
	sx=0; sy=0; i0=0; sx=0; sy=0;
	# First point determines direction
	if (abs(xinc[1])<1e-12) {
		sx=1
	}
	if (abs(yinc[1])<1e-12) {
		sy=1
	}
	for (i=1;i<p;i++){
		if ((sx>0)&&(sy>0)){
			if (i0==p-1){
				print "OUTBND_LINE("lin") ="px[i0]*1.0,py[i0]*1.0,0,0,1  # Isolated point at the end
			} else {
				print "OUTBND_LINE("lin") ="px[i0]*1.0,py[i0]*1.0,xinc[i0+1]*1.0,yinc[i0+1]*1.0,2
			}
			i=i+1
			i0=i+1
			lin=lin+1
		} else {
			if (sx>0){
				if (abs(yinc[i]-yinc[i+1])<1e-12){
					sx=sx+1
				} else {
					print "OUTBND_LINE("lin") ="px[i0]*1.0,py[i0]*1.0,xinc[i0+1]*1.0,yinc[i0+1]*1.0,sx+1
					i0=i+1
					sx=0
					if (abs(xinc[i+1])<1e-12) {
						sx=1
					}
					if (abs(yinc[1])<1e-12) {
						sy=1
					}
					lin=lin+1
				}
			} 
			if (sy>0){
				if (abs(xinc[i]-xinc[i+1])<1e-12){
					sy=sy+1
				} else {
					print "OUTBND_LINE("lin") ="px[i0]*1.0,py[i0]*1.0,xinc[i0+1]*1.0,yinc[i0+1]*1.0,sy+1
					i0=i+1
					sy=0
					if (abs(xinc[i+1])<1e-12) {
						sx=1
					}
					if (abs(yinc[1])<1e-12) {
						sy=1
					}
					lin=lin+1
				}
			}
		}
	}
}'

	rm /tmp/c$$
	exit
fi


lines=$(cat /tmp/c$$ | wc -l)
zeros=$(echo "" | awk  -v d=$lines -v i=0 '{a= d/1; while (a>1) {i=i+1; a=d/10^i} print i}')
cad="\'BOUND_%0${zeros}d\'\n"
touch /tmp/cc$$
for ((i=1;i<=$lines;i++)); do
	printf "${cad}" $i >> /tmp/cc$$
done
paste /tmp/c$$ /tmp/cc$$ | sed 's|\t| |g'

rm /tmp/c$$ /tmp/cc$$
