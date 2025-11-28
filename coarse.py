#!/usr/bin/env python3

# Justino justino@icm.csic.es
# WW3 tools 
# Generate a coarser grid for WW3 departing from CROCO grid.
# uses mean or median and puts the data corresponding to the boundary to
# have the same limit in open boundaries
# 
# Note: FOR CATSEA. You must delete/modify "parches" (below) in your seas 
#     Patches are for small islands that dissaper after decimation and thet I like to maintain
#

import xarray as xr
import numpy as np
import sys

#################### CHANGE INPUT VARS

# Original CROCO grid
original_croco_grid="MASK_GRID_CATSEA_NEWGRID.nc"

# prefix for the new files
name="CATSEA"

# decimation (4 means that only survive 1 of every 4 original points)
res=4

##################################################3
filemask=name+"_"+str(res)+".mask_nobound"
filemask2=name+"_"+str(res)+".mask"
fileh=name+"_"+str(res)+".bot"
filex=name+"_x_"+str(res)+".inp"
filey=name+"_y_"+str(res)+".inp"
lonlatmask=name+"_lonlat_"+str(res)+".dat"

mask=xr.open_dataset(original_croco_grid,engine='netcdf4')['mask_rho']
h=xr.open_dataset(original_croco_grid,engine='netcdf4')['h']
lat_rho=xr.open_dataset(original_croco_grid,engine='netcdf4')['lat_rho']
lon_rho=xr.open_dataset(original_croco_grid,engine='netcdf4')['lon_rho']

res_h=h.coarsen(xi_rho=res, boundary="pad").median().coarsen(eta_rho=res, boundary="pad").median()

res_h_first=h[0,:].coarsen(xi_rho=res, boundary="pad").median()
res_h_last=h[:,-1].coarsen(eta_rho=res, boundary="pad").median()


res_mask=mask.coarsen(xi_rho=res, boundary="pad").mean().coarsen(eta_rho=res, boundary="pad").mean()
res_mask.values[res_mask.values>0.5]=1
res_mask.values[res_mask.values<=0.5]=0

############
# Parches small islands that dissapear due to the coarse grid and that I like to maintain
############
res_mask.values[205,184]=0
res_mask.values[60,36]=0
res_mask.values[14,60]=0
res_mask.values[15,60]=0
res_mask.values[10,62]=0
res_mask.values[18,53]=0
res_mask.values[25,67]=0
res_mask.values[47,88]=0
res_mask.values[196,204]=0
############
# End parches
############

res_mask_first=mask[0,:].coarsen(xi_rho=res, boundary="pad").mean()
res_mask_first.values[res_mask_first.values>0.5]=1
res_mask_first.values[res_mask_first.values<=0.5]=0

res_mask_last=mask[:,-1].coarsen(eta_rho=res, boundary="pad").mean()
res_mask_last.values[res_mask_last.values>0.5]=1
res_mask_last.values[res_mask_last.values<=0.5]=0

res_lat=lat_rho.coarsen(xi_rho=res, boundary="pad").mean().coarsen(eta_rho=res, boundary="pad").mean()

res_lat_first=lat_rho[0,:].coarsen(xi_rho=res, boundary="pad").mean()
res_lat_last=lat_rho[:,-1].coarsen(eta_rho=res, boundary="pad").mean()

res_lon=lon_rho.coarsen(xi_rho=res, boundary="pad").mean().coarsen(eta_rho=res, boundary="pad").mean()

res_lon_first=lon_rho[0,:].coarsen(xi_rho=res, boundary="pad").mean()
res_lon_last=lon_rho[:,-1].coarsen(eta_rho=res, boundary="pad").mean()


# Check the last point for longitude and recompute it if the deltax is different
# (new grid is not congruent with the original one)
lastxdelta=res_lon_last-res_lon[:,-1]
lastxdelta2=res_lon[:,-1]-res_lon[:,-2]
for i in range(len(res_lon[:,-1])):
	if lastxdelta[i]!=lastxdelta2[i]:
		res_lon_last.values[i]=res_lon.values[i,-1]+lastxdelta2.values[i]
		
		
# The same but for the first point of the latitude but assuming a linear deltay (not constant)
firstydelta=res_lat[0,:]-res_lat_first
firstydelta2=res_lat[1,:]-res_lat[0,:]
firstydelta3=res_lat[2,:]-res_lat[1,:]
a=(firstydelta3-firstydelta2)/(res_lat[2,:]-res_lat[1,:])
b=firstydelta3-a*res_lat[2,:]
flin=a*res_lat[0,:]+b
for i in range(len(res_lat[0,:])):
	if firstydelta[i]!=flin[i]:
		res_lat_first.values[i]=res_lat.values[0,i]-flin.values[i]
		


print("Creating "+filemask)
with open(filemask, 'a') as f:
	f.seek(0)
	f.truncate()
	# First line (lower latitude and open boundary)
	
	stri=""
	for j in range(0,np.shape(res_mask)[1]):
		stri=stri+" "+str(int(res_mask_first.values[j]))+" "
	# New corner (copy of original value)
	stri=stri+" "+str(int(mask.values[0,-1]))+" "
	f.write(stri+"\n")
	
	# Rest of the domain
	for i in range(0,np.shape(res_mask)[0]):
		stri=""
		for j in range(0,np.shape(res_mask)[1]):       
			stri=stri+" "+str(int(res_mask.values[i,j]))+" "
		# Last column (higher longitude and open boundary)
		stri=stri+" "+str(int(res_mask_last.values[i]))+" "
		f.write(stri+"\n")

print("Creating "+filemask2)
with open(filemask2, 'a') as f:
	f.seek(0)
	f.truncate()
	# First line (lower latitude and open boundary)
	
	if res_mask_first.values[0]==1:
		stri=" 2 "
	else:
		stri=" "+str(int(res_mask_first.values[0]))+" "
	for j in range(1,np.shape(res_mask)[1]):
		if res_mask_first.values[j]==1:
			stri=stri+" 2 "
		else:
			stri=stri+" "+str(int(res_mask_first.values[j]))+" "
	# New corner (copy of original value)
	if mask.values[0,-1]==1:
		stri=stri+" 2 "
	else:
		stri=stri+" "+str(int(ask.values[0,-1]))+" "
	f.write(stri+"\n")
	
	# Rest of the domain
	for i in range(0,np.shape(res_mask)[0]):
		stri=""
		for j in range(0,np.shape(res_mask)[1]):
			#if (i==0 or j==np.shape(res_mask)[1]-1) and res_mask.values[i,j]==1:
			#	stri=stri+" 2 "
			#else:
			stri=stri+" "+str(int(res_mask.values[i,j]))+" "
		# Last column (higher longitude and open boundary)
		
		if (res_mask_last.values[i]==1):
			stri=stri+" 2 "
		else:
			stri=stri+" "+str(int(res_mask_last.values[i]))+" "
		
		f.write(stri+"\n")
		
print("Creating "+fileh)
with open(fileh, 'a') as f:
	f.seek(0)
	f.truncate()
	# First line (lower latitude and open boundary)
	
	stri=""
	for j in range(0,np.shape(res_h)[1]):
		stri=stri+"  "+str(-res_h_first.values[j])+" "
	# New corner (copy of original value)
	stri=stri+" "+str(-h.values[0,-1])+" "
	f.write(stri+"\n")
	
	# Rest of the domain
	for i in range(0,np.shape(res_h)[0]):
		stri=""
		for j in range(0,np.shape(res_h)[1]):       
			stri=stri+" "+str(-res_h.values[i,j])+" "
		# Last column (higher longitude and open boundary)
		stri=stri+" "+str(-res_h_last.values[i])+" "
		f.write(stri+"\n")
		
print("Creating "+filex)
with open(filex, 'a') as f:
	f.seek(0)
	f.truncate()
	# First line (lower latitude and open boundary)
	
	stri=""
	for j in range(0,np.shape(res_lon)[1]):
		stri=stri+" "+str(res_lon_first.values[j])+" "
	# New corner (copy of original value)
	stri=stri+" "+str(res_lon_last.values[0])+" "
	f.write(stri+"\n")
	
	# Rest of the domain
	for i in range(0,np.shape(res_lon)[0]):
		stri=""
		for j in range(0,np.shape(res_lon)[1]):       
			stri=stri+" "+str(res_lon.values[i,j])+" "
		# Last column (higher latitude and open boundary)
		stri=stri+" "+str(res_lon_last.values[i])+" "
		f.write(stri+"\n")
		
print("Creating "+filey)
with open(filey, 'a') as f:
	f.seek(0)
	f.truncate()
	# First line (lower latitude and open boundary)
	
	stri=""
	for j in range(0,np.shape(res_lat)[1]):
		stri=stri+" "+str(res_lat_first.values[j])+" "
	# New corner (copy of original value)
	stri=stri+" "+str(res_lat_first.values[0])+" "
	f.write(stri+"\n")
	
	# Rest of the domain
	for i in range(0,np.shape(res_lat)[0]):
		stri=""
		for j in range(0,np.shape(res_lat)[1]):       
			stri=stri+" "+str(res_lat.values[i,j])+" "
		# Last column (higher longitude and open boundary)
		stri=stri+" "+str(res_lat_last.values[i])+" "
		f.write(stri+"\n")		
		
print("Creating "+lonlatmask)
with open(lonlatmask, 'a') as f:
	f.seek(0)
	f.truncate()
	# First line (lower latitude and open boundary)
	
	stri=str(res_lon_first.values[0])+" "+str(res_lat_first.values[0])+" "+str(res_mask_first.values[0])
	f.write(stri+"\n")
	for j in range(1,np.shape(res_lat)[1]):
		stri=str(res_lon_first.values[j])+" "+str(res_lat_first.values[j])+" "+str(res_mask_first.values[j])
		f.write(stri+"\n")	
	# New corner (copy of original value)
	stri=str(lon_rho.values[0,-1])+" "+str(lat_rho.values[0,-1])+" "+str(mask.values[0,-1])
	f.write(stri+"\n")
	
	# Rest of the domain
	for i in range(0,np.shape(res_lat)[0]):		
		for j in range(0,np.shape(res_lat)[1]):       
			stri=str(res_lon.values[i,j])+" "+str(res_lat.values[i,j])+" "+str(res_mask.values[i,j])
			f.write(stri+"\n")	
		# Last column (higher longitude and open boundary)
		stri=str(res_lon_last.values[i])+" "+str(res_lat_last.values[i])+" "+str(res_mask_last.values[i])
		f.write(stri+"\n")	
			
