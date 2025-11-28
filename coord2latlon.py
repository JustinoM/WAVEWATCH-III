#!/usr/bin/env python3

# Justino justino@icm.csic.es
# WW3 tools 
# Convert output of clickline to lat/lon data and formats it to WW3 matlab object to be used by create_obstr.m
#
# Input parameters:
#	1.- netcdf corresponding to the Hires croco grid
#	2.- variable corresponding to latitude (lat_rho)
#	3.- variable corresponding to longitude (lon_rho)
#	4.- file created using clickline.py (coordinates.dat)
#	5.- output mat filename to be used by create_obstr.m



import netCDF4 as nc
import numpy as np
from scipy.io import savemat
from numpy.core.records import fromarrays
import sys


def main():

	def finish_boundary(boundx,boundy,i):
		west=min(boundx)
		east=max(boundx)
		south=min(boundy)
		north=max(boundy)
		n=len(boundx)
		bx=np.zeros((n,1),dtype=np.float64)
		by=np.zeros((n,1),dtype=np.float64)
	
		bx[:,0]=np.asarray(boundx, dtype=np.float64)
		by[:,0]=np.asarray(boundy, dtype=np.float64)
	
	
		boundaries[i]['n']=n
		boundaries[i]['level']=1
		boundaries[i]['west']=west
		boundaries[i]['east']=east
		boundaries[i]['north']=north
		boundaries[i]['south']=south
		boundaries[i]['x']=bx
		boundaries[i]['y']=by
	
	if len(sys.argv) < 5:		
		sys.exit("See notes in the code: Usage "+sys.argv[0]+" CROCO_GRID lat_rho lon_rho coordinates.dat output.mat")
		
	# Nombre del archivo NetCDF y la variable que queremos leer
	archivo_netcdf = sys.argv[1]	 
	variablelat_netcdf = sys.argv[2]	
	variablelon_netcdf = sys.argv[3]	
	
	# Option 2 each coast in a separate file. This is and old option (ALLINONE=False)
	# fichero_coordenadas=["c1.txt", "c2.txt", "c3.txt", "c4.txt", "c5.txt", "c6.txt", "c7.txt", "c8.txt", "c9.txt", "c10.txt", "c11.txt", "c12.txt"]
	fichero_coordenadas=[sys.argv[4]]
	ficheromat=sys.argv[5]
	
	
	NB=len(fichero_coordenadas)
	ALLINONE=False
	if NB==1: # In this case all the coasts could be saved in the same file
		with open(fichero_coordenadas[0], "r") as f:
			for line in f:
				d=line.strip().split(',')
				try:
					x=int(d[0])
				except:
					NB=NB+1
					ALLINONE=True
		NB=NB-1
	
					
	# Abrir el archivo NetCDF y leer la variable
	print ("Reading "+archivo_netcdf)
	ds = nc.Dataset(archivo_netcdf)
	lat= ds.variables[variablelat_netcdf ][:]  # Leer toda la variable
	lon= ds.variables[variablelon_netcdf ][:]  # Leer toda la variable
	
	boundtype = np.dtype({'names': ['n', 'level', 'west','east','south','north','x','y'], 
               'formats': [np.int32, np.int32, np.float64, np.float64, np.float64, np.float64, object,object]})
	boundaries = np.zeros((NB,), dtype=boundtype)
	
	
	if ALLINONE==False:
		for i in range(0,NB):
			
			boundx=[]
			boundy=[]
		
			with open(fichero_coordenadas[i], "r") as f:	
				print ("Reading "+fichero_coordenadas[i])
				for line in f:
					data=line.strip().split(',')
					x=int(data[0])
					y=int(data[1])
					boundx.append(lon[y,x])
					boundy.append(lat[y,x])
			
			finish_boundary(boundx,boundy,i)
	else:
		boundx=[]
		boundy=[]
		i=0
		with open(fichero_coordenadas[0], "r") as f:	
			print ("Reading "+fichero_coordenadas[0])
			for line in f:
				data=line.strip().split(',')
				try:
					x=int(data[0])
					y=int(data[1])
					boundx.append(lon[y,x])
					boundy.append(lat[y,x])
				except:
					
					finish_boundary(boundx,boundy,i)
					i=i+1
					boundx=[]
					boundy=[]
					print ("The coast "+str(i)+" has been read")
	
	savemat(ficheromat,{"bound": boundaries})
	print (ficheromat+" has been created")
	
	
if __name__ == "__main__":
	main()