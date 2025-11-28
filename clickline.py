#!/usr/bin/env python3

# Justino justino@icm.csic.es
# WW3 tools 
# Clic on map to define coast lines, polygons...as lines
#
# To generate the coordinates.dat file in the WW3 tools chain
#	1.- press "a"
#	2.- click anywhere on the map
#	3.- press "q"

# More options
# press c to create points -> c again stops create
# press d to delete points -> d again stops to create
# press i to include inter points -> press in the existing point and in the cell in which to insert the new point -> i again stops insert
# press s to close / save figure (data is saved on the fly in filedat)
# press t to hide/show ticks
# press g to hide/show grid
# press a to generate automatic path


import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import sys
from matplotlib import ticker

# Constants & globals
def constants():
	global archivo_netcdf,variable_netcdf,filedat
	archivo_netcdf= "MASK_GRID_CATSEA_NEWGRID.nc"	 # Cambia esto por tu archivo
	variable_netcdf = "mask_rho"
	filedat="coordinates.dat"
	################### No hace falta cambiar mas
	
	global SAVEP, DELP,INSE,LPOS,AUTO
	SAVEP=0
	DELP=0
	INSE=0
	AUTO=0
	LPOS=-1
	# Lista para almacenar las coords	
	global coords
	coords = []
	
	global ax,fig,scat
	scat=[]
	
	
# Manage clicks
def onclick(event):
	global ax,fig,scat,LPOS,AUTO,filedat
	color='red'
	ecolor='black'
	color_res='white'
	ecolor_res='white'
	color_first='yellow'
	ecolor_first='yellow'
	def savecoord(x,y):
		coords.append((x, y))
		print(f"Coordenada guardada: ({x}, {y})")
		with open(filedat, "a") as f:
			f.write(f"{x}, {y}\n")
				
	if event.button == 1:  # Botón izquierdo del ratón
		x, y = event.xdata, event.ydata
		if x is not None and y is not None:				
			x, y = int(x+0.5), int(y+0.5)
			if AUTO==1:
				ax.set_title("Wait")	
				fig.canvas.draw()
				# Find contours in the binary mask
				
				thres=1
				cs=plt.contour(variable_2d,[thres])
				# Check if get_paths() is not available (old version)
				if not hasattr(cs, 'get_paths'):
					# Old version: iterate over each layer (i=0, only one level)
					for i, collection in enumerate(cs.collections):
						# get each path in the layer (level)
						paths=collection.get_paths()
				else:
					paths=cs.collections[0].get_paths()
				
				ncontours=len(paths)
				
				for cont in range(0,ncontours):
					v = paths[cont].vertices
					xo = v[:, 0]
					yo = v[:, 1]
					#index=np.argwhere(xo==x)
					#indey=np.argwhere(yo==y)
					#if len(np.intersect1d(index,indey)) >0:
					resx=[]
					resy=[]
					for i in range(len(xo)):
						if i == 0 or (xo[i] != xo[i-1] or yo[i] != yo[i-1]): # delete consecutive repeated points
							resx.append(xo[i])
							resy.append(yo[i]) 
					
					for i in range(0,len(resx)):
						savecoord(int(resx[i]), int(resy[i]))
					with open(filedat, "a") as f:
						f.write(f"\n")	
				for art in list(ax.lines):
					art.remove()
					
				if len(coords)>1:					
					ax.plot(*zip(*coords),'r-')
				for (x,y) in coords:	
					scat.append(ax.scatter(x, y, color=color, s=50, edgecolors=ecolor))
				ax.set_title("")
			if SAVEP==1:
				savecoord(x,y)
					
				for art in list(ax.lines):
					art.remove()
					
				if len(coords)>1:					
					ax.plot(*zip(*coords),'r-')
				scat.append(ax.scatter(x, y, color=color, s=50, edgecolors=ecolor))	 # Circle
				
			if DELP==1:						
				if (x,y) in coords:
					# Remove last occurence of this point
					lastind = len(coords) - 1 - coords[::-1].index((x,y))					
					coords.reverse()
					coords.remove((x,y))
					coords.reverse()	
					for art in list(ax.lines):
						art.remove()
					if len(coords)>1:
						ax.plot(*zip(*coords),'r-')
					xy = np.delete(scat[lastind].get_offsets(), 0, axis=0)
					scat[lastind].set_offsets(xy)
					del scat[lastind]
											
					print(f"Coordenada eliminada: ({x}, {y})")
					with open(filedat, "r+") as f:
						f.seek(0)
						for (xp,yp) in coords:
							f.write(f"{xp}, {yp}\n")       
						f.truncate()	
						
			if INSE==1:				
				if LPOS > -1:
					scat[LPOS].set_color(color)
					scat[LPOS].set_edgecolors(ecolor)
					f = open(filedat,"r")
					linelist = f.readlines()
					f.close()
					linelist.insert(LPOS,f"{x}, {y}\n")	
					f = open(filedat, "w")
					f.seek(0)
					f.truncate()	
					for line in linelist:
						f.write(line)
					f.close()
 
					for art in list(ax.lines):
						art.remove()
					coords.insert(LPOS,(x,y))			
					ax.plot(*zip(*coords),'r-')
					
									
					scat.insert(LPOS,ax.scatter(x, y, color=color_res, s=50, edgecolors=ecolor_res))	 # Dibuja el círculo
					
				else:	
					if (x,y) in coords:
						LPOS = len(coords) - 1 - coords[::-1].index((x,y))
						scat[LPOS].set_color(color_res)
						scat[LPOS].set_edgecolors(ecolor_res)
			try:			
				scat[0].set_color(color_first)					
				scat[0].set_edgecolor(ecolor_first)
				fig.canvas.draw()  # Refresca la imagen
			except:
				pass


# Manage keys

def onkeypres(event):
	global SAVEP,DELP,INSE,LPOS,AUTO,fig,ax,coords,scat,filedat
	if event.key == 's':
		print("Coordenadas guardadas:", coords)
		plt.close()
	color='red'
	ecolor='black'
	if LPOS==0:
		color='yellow'
		ecolor='yellow'
	if event.key == 'c': # create points
		if SAVEP==0:
			ax.set_title("Create mode on")
			fig.canvas.draw()
			if LPOS>-1:
				scat[LPOS].set_color(color)
				scat[LPOS].set_edgecolors(ecolor)
				fig.canvas.draw()
			SAVEP=1
			INSE=0
			DELP=0
			LPOS=-1
		else:
			ax.set_title("Create mode off")
			fig.canvas.draw()
			SAVEP=0
	if event.key == 'd': # Erase points
		if DELP==0:
			ax.set_title("Delete mode on")
			if LPOS>-1:
				scat[LPOS].set_color(color)
				scat[LPOS].set_edgecolors(ecolor)
				fig.canvas.draw()
			SAVEP=0
			INSE=0
			DELP=1
			LPOS=-1
		else:
			ax.set_title("Delete mode off")			
			DELP=0
	if event.key == 'i':	 # click on posterior existing point
		if INSE==0:
			ax.set_title("Insert mode on")			
			SAVEP=0
			DELP=0
			INSE=1
			LPOS=-1
		else:
			ax.set_title("Delete mode off")			
			if LPOS>-1:
				scat[LPOS].set_color(color)
				scat[LPOS].set_edgecolors(ecolor)
				fig.canvas.draw()
			INSE=0
			LPOS=-1
	if event.key == 'r' or event.key =='a': # delete points
		if event.key=='a':
			ax.set_title("Corrdinates deleted. Automatic detection: Click in a point of the coast")
			
		SAVEP=0
		DELP=0
		INSE=0
		LPOS=-1
		# delete file
		f = open(filedat, "w")
		f.seek(0)
		f.truncate()
		
		# delete coordinates
		del coords
		coords=[]
		
		# delete lines
		for art in list(ax.lines):
			art.remove()
		
		# delete dots		
		for scatter in plt.gca().collections:
			scatter.remove()
		del scat
		scat=[]
		fig.canvas.draw()
		if event.key == 'a': # automatic coast
			AUTO=1
	if event.key == 'g': # show/hide grid
		# This code should not work...
		isVisible=ax.get_xgridlines()[1].get_visible()		
		ax.grid(visible=isVisible)		
		fig.canvas.draw()
	if event.key == 't': # show/hide ticks
		if ax.get_xticklabels() ==[]:	
			plt.tick_params(axis='both', which='both', bottom=True, top=False, left=True, right=False, labelleft=True,labelright=False, labelbottom=True, labeltop=False)
		else:
			plt.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelleft=False,labelright=False, labelbottom=False, labeltop=False)
		fig.canvas.draw()			
	
		
# MAIN	
def main():
	global ax,fig,variable_2d
	constants()
	
	
	# read
	ds = nc.Dataset(archivo_netcdf)
	variable_2d = ds.variables[variable_netcdf ][:]  # Leer toda la variable
	
	
	# Plot figure
	WIDTH_SIZE=np.shape(variable_2d)[1]
	HEIGHT_SIZE=np.shape(variable_2d)[0]
	fig, ax = plt.subplots()
	mpl.rcParams["keymap.back"] = ['left', 'backspace']	   
	textstr = '\n'.join((r't: show/hide ticks',
		r'g: show/hide grid',
		r'c: create new point',
		r'd: delete point',
		r'i: insert point',
		r'a: automatic coast',
		r'r: reset points',
		r's: save plot',
		r'q: quit'))
	props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
	plt.gcf().text(0.01, 0.99, textstr, fontsize=12, verticalalignment='top', bbox=props)

	
	major_ticksx = np.arange(-0.5, WIDTH_SIZE, 1)
	xlabels = np.arange(0, WIDTH_SIZE+1, 1)
	major_ticksy = np.arange(-0.50, HEIGHT_SIZE, 1)
	ylabels = np.arange(0, HEIGHT_SIZE+1, 1)
	ax.set_xticks(major_ticksx)
	ax.set_xticklabels(xlabels, rotation=0)
	
	ax.set_yticks(major_ticksy)
	ax.set_yticklabels(ylabels, rotation=0)
	plt.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelleft=False,labelright=False, labelbottom=False, labeltop=False)
	ax.grid(visible=False,which='both')
	
	cmap = ax.imshow(variable_2d, origin='lower', cmap='jet')
	plt.colorbar(cmap, ax=ax)
	
	# Charge points...
	try:
		with open(filedat, "r") as f:	
			
			for line in f:
				data=line.strip().split(',')
				x=int(data[0])
				y=int(data[1])
				coords.append((x, y))
			if len(coords)>1:					
				ax.plot(*zip(*coords),'r-')
			color='yellow'
			ecolor='yellow'
			for (x,y) in coords:	
				scat.append(ax.scatter(x, y, color=color, s=50, edgecolors=ecolor))
				color='red'
				ecolor='black'
				
	except:
		pass
	
	# Events capture
	fig.canvas.mpl_connect('button_press_event', onclick)	   
	fig.canvas.mpl_connect('key_press_event', onkeypres)
	
	plt.show()
if __name__ == "__main__":
	main()