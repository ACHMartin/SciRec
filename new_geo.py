# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 16:21:04 2023

@author: andrievskaia
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

### open model only with useful variables
geo = xr.open_dataset(r'N:/Partage_interne/Daria/CROCO1000_201009.nc', 
                      drop_variables = ['AKs','AKt','AKv','bostr','diff3d','radsw','rho','s_rho','s_w','salt','shfx','shfx_lat',
                                        'shfx_rlw','shfx_sen','sustr','svstr','zeta','temp'])
geo = geo[['u', 'v', 'uwnd', 'vwnd']]#, 'nav_lat_rho', 'nav_lat_u', 'nav_lat_v','nav_lon_rho','nav_lon_u','nav_lon_v']]


# ### drop dimensions we don't need
# geo = geo.drop_dims(['s_', ])

### subset time
geo = geo.sel(time_counter="2010-09-01T18:00:00.000000000")


### Ouessant coordinates and a tile 100x100km with centre in Ouessant
latitude = 48.4666667 # 48° 28′ N
longitude = -5.1 #  5° 06′ O
r_earth = 6378000.0
dy, dx = 50000, 50000
new_lat_right  = latitude  + (dy / r_earth) * (180 / np.pi)
new_lon_right = longitude + (dx / r_earth) * (180 / np.pi) / np.cos(latitude * np.pi/180)
new_lat_left  = latitude  - (dy / r_earth) * (180 / np.pi)
new_lon_left = longitude - (dx / r_earth) * (180 / np.pi) / np.cos(latitude * np.pi/180)


### subset aof
geo_short = geo.isel(x_u=slice(168,268), y_u=slice(509,609), x_v=slice(168,268), y_v=slice(509,609))

### compute geo inputs
# cvel = np.sqrt(geo_short.u**2 + geo_short.v**2)
# wspd = np.sqrt(geo_short.uwnd**2 + geo_short.vwnd**2)
# cdir = np.abs(180/np.pi*np.arctan2(geo_short.v,geo_short.u))
# wdir = np.abs(180/np.pi*np.arctan2(geo_short.vwnd,geo_short.uwnd))

### add new variables to netcdf 
# geo_short=geo_short.assign(current_velocity= cvel, current_direction=cdir, wind_speed=wspd, wind_direction=wdir)
# geo_short=geo_short.assign(current_velocity=(['y_u', 'x_u', 'y_v', 'x_v'], cvel, {'units':'meter second-1'}),# 'long_name':'current velocity'}), 
#                            current_direction=(cdir, {'units':'degrees', 'long_name':'current direction'}), 
#                            wind_speed=(wspd, {'units':'meter second-1', 'long_name':'wind velocity'}), 
#                            wind_direction=(wdir, {'units':'degrees', 'long_name':'wind direction'}))
### save netcdf
geo.to_netcdf('N:/Partage_interne/Daria/CROCO1000_201009_one.nc')
geo_short.to_netcdf('N:/Partage_interne/Daria/CROCO1000_201009_extr.nc')



#### Other area
lat_up, lat_down = 48.65, 47.65 # 48.65, 47.76
lon_left, lon_right = -7.35, -6.35 # -7.46, -6.13

### subset aof
geo_short = geo.isel(x_u=slice(40,140), y_u=slice(480,580), x_v=slice(40,140), y_v=slice(480,580))

### save netcdf
geo_short.to_netcdf('N:/1407-FE_SeaStar_SciRec/REALISATION/Technique/scirec_data/CROCO1000_201009_area.nc')

