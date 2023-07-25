# -*- coding: utf-8 -*-
"""
Created on Wed May 31 10:39:29 2023

@author: andrievskaia
"""
import numpy as np
import math
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


#####
##### Plot retreived current and wind
#####
level2 = xr.open_dataset(r'N:\1407-FE_SeaStar_SciRec\REALISATION\Technique\SciRec\level2s\level2_model_3base_3AC20_36_100x100_SNKp03RSV07_MVNKp04RSVnan_N4DS_M12_sol_closest_truth_wind.nc')
# closest_truth_current, sort_by_cost_current, closest_truth_wind
level2['flag'] = level2.cost > 4

cmap_dict = {'CurrentVelocity': 'plasma', 'CurrentDirection': 'hsv', 
             'WindSpeed': 'viridis', 'WindDirection': 'twilight', 'cost': 'viridis'}

map_proj = ccrs.Mercator()
skipx, skipy = 5, 5
X,Y = np.meshgrid(level2.longitude,level2.latitude)
plt.rcParams.update({'font.size':40})

###
fig1 = plt.figure(figsize=(50,40))
ax = fig1.add_subplot(1,1,1, projection=map_proj, frameon=True)
gl = ax.gridlines(draw_labels=True)
level2.CurrentVelocity.where(~level2.flag).plot(
    x='longitude',
    y='latitude',
    cmap='turbo',
    vmin=0,
    vmax=1.2,
    transform=ccrs.PlateCarree(),
)

# plt.quiver(
#     X[::skipy,::skipx],
#     Y[::skipy,::skipx],
#     level2.CurrentU[::skipy,::skipx],
#     level2.CurrentV[::skipy,::skipx],
#     angles='uv',
#     # scale=20,
# )
level2.where(~level2.flag).plot.quiver(
        x='longitude',
        y='latitude',
        u='CurrentU',
        v='CurrentV',
        # linewidth=1,
        # arrowsize = 1,
        # density=5,
        # color='k',
        angles='uv',
        transform=ccrs.PlateCarree(),
    )
ax.coastlines(resolution='10m', color='black', linewidth=1)
ax.add_feature(cfeature.GSHHSFeature(scale='full',facecolor='white'), linewidth=1.5)
# plt.quiverkey(q, 1.03, 0.97, 0.5, r'$2 \frac{m}{s}$', labelpos='N')
# plt.title('Ambiguity method: closest_truth to current', fontsize = 60)
# plt.title('Ambiguity method: sort_by_cost', fontsize = 60)
plt.title('Ambiguity method: closest_truth to wind', fontsize = 60)




###
fig2 = plt.figure(figsize=(50,40))
ax = fig2.add_subplot(1,1,1, projection=map_proj, frameon=True)
gl = ax.gridlines(draw_labels=True)
level2.WindSpeed.where(~level2.flag).plot(
    x='longitude',
    y='latitude',
    cmap='viridis',# !!! TO DO: chnage cmap
    vmin=5,
    vmax=12,
    transform=ccrs.PlateCarree(),
)
# plt.quiver(
#     X[::skipy,::skipx],
#     Y[::skipy,::skipx],
#     level2.WindU[::skipy,::skipx],
#     level2.WindV[::skipy,::skipx],
#     angles='uv',
# )
level2.where(~level2.flag).plot.quiver(
        x='longitude',
        y='latitude',
        u='WindU',
        v='WindV',
        angles='uv',
        transform=ccrs.PlateCarree(),
)
ax.coastlines(resolution='10m', color='black', linewidth=1)
ax.add_feature(cfeature.GSHHSFeature(scale='full',facecolor='white'), linewidth=1.5)
# plt.title('Ambiguity method: closest_truth to current',  fontsize = 60)
# plt.title('Ambiguity method: sort_by_cost',  fontsize = 60)
plt.title('Ambiguity method: closest_truth to wind',  fontsize = 60)


###
fig3 = plt.figure(figsize=(50,40))
im = level2.cost.plot(x='across', vmax=4)
# cbar = fig3.colorbar(im).cmap.set_over('red')
im.cmap.set_over('red')
# plt.title('Ambiguity method: closest_truth to current')
# plt.title('Ambiguity method: sort_by_cost')
plt.title('Ambiguity method: closest_truth to wind')


#%%
#####
##### Plot input current and wind
#####
# geo = xr.open_dataset(r'N:\1407-FE_SeaStar_SciRec\REALISATION\Technique\SciRec\geo\geo_model_coord_100x100.nc')
geo = xr.open_dataset(r'N:\1407-FE_SeaStar_SciRec\REALISATION\Technique\SciRec\geo\geo_model_area_100x100.nc')
x,y = np.meshgrid(geo.longitude, geo.latitude)

###
cLon, cLat = -5.1, 48.5
cmin, cmax = geo.CurrentVelocity.min(), geo.CurrentVelocity.max()
min_lat, max_lat = geo.latitude.values[0][0], geo.latitude.values[-1][0]
min_lon, max_lon = geo.longitude.values[0][0], geo.longitude.values[0][-1]
img_extent_deg = [min_lon, max_lon, min_lat, max_lat]
map_proj = ccrs.Mercator()

fig12 = plt.figure(figsize=(50,40))
ax = fig12.add_subplot(1,1,1, projection=map_proj, frameon=True)
gl = ax.gridlines(draw_labels=True)                                # add the longitude / latitude lines
# ax.set_extent(img_extent_deg, crs=ccrs.PlateCarree())
geo.CurrentVelocity.plot(
    x='longitude',
    y='latitude',
    cmap='turbo',
    vmin=0,
    vmax=0.7,
    transform=ccrs.PlateCarree(),
)
geo.plot.quiver(
        x='longitude',
        y='latitude',
        u='CurrentU',
        v='CurrentV',
        angles='uv',
        transform=ccrs.PlateCarree(),
)
# ax.quiver(
#     x[::skipy,::skipx],
#     y[::skipy,::skipx],
#     geo.CurrentU[::skipy,::skipx],
#     geo.CurrentV[::skipy,::skipx],
#     angles='uv',
#     transform=map_proj,
# )
ax.coastlines(resolution='10m', color='black', linewidth=1)
ax.add_feature(cfeature.GSHHSFeature(scale='full',facecolor='white'), linewidth=1.5)
plt.title('Input Current', fontsize = 60)


###
fig22 = plt.figure(figsize=(50,40))
ax = fig22.add_subplot(1,1,1, projection=map_proj, frameon=True)
gl = ax.gridlines(draw_labels=True)     
geo.EarthRelativeWindSpeed.plot(
    x='longitude',
    y='latitude',
    cmap='viridis', # !!! TO DO: chnage cmap
    vmin=5,
    vmax=9,
    transform=ccrs.PlateCarree(),
)
geo.plot.quiver(
        x='longitude',
        y='latitude',
        u='EarthRelativeWindU',
        v='EarthRelativeWindV',
        angles='uv',
        transform=ccrs.PlateCarree(),
)
# plt.quiver(
#     x[::skipy,::skipx],
#     y[::skipy,::skipx],
#     geo.EarthRelativeWindU[::skipy,::skipx],
#     geo.EarthRelativeWindV[::skipy,::skipx],
#     angles='uv',
# )
ax.coastlines(resolution='10m', color='black', linewidth=1)
ax.add_feature(cfeature.GSHHSFeature(scale='full',facecolor='white'), linewidth=1.5)
plt.title('Input Wind', fontsize = 60)

#%%
#####
##### Plot difference between input and retreived current and wind
#####
level2 = xr.open_dataset(r'N:\1407-FE_SeaStar_SciRec\REALISATION\Technique\SciRec\level2s\level2_model_3base_3AC20_36_100x100_SNKp03RSV07_MVNKp04RSVnan_N4DS_M12_sol_closest_truth_current.nc')
# closest_truth_current, sort_by_cost_current, closest_truth_wind
geo = xr.open_dataset(r'N:\1407-FE_SeaStar_SciRec\REALISATION\Technique\SciRec\geo\geo_model_100x100.nc')
level2['flag'] = level2.cost > 4
l = level2.assign_coords(across = geo.across)
diff_current_vel = np.sqrt((l.CurrentU-geo.CurrentU)**2 + (l.CurrentV-geo.CurrentV)**2)
diff_wind_vel = np.sqrt((l.WindU-geo.EarthRelativeWindU)**2 + (l.WindV-geo.EarthRelativeWindV)**2)

l['diff_current_vel'] = diff_current_vel
l['diff_wind_vel'] = diff_wind_vel
l['new_cur_u'] = l.CurrentU-geo.CurrentU
l['new_cur_v'] = l.CurrentV-geo.CurrentV
l['new_win_u'] = l.WindU-geo.EarthRelativeWindU
l['new_win_v'] = l.WindV-geo.EarthRelativeWindV

###
fig13 = plt.figure(figsize=(50,40))
ax = fig13.add_subplot(1,1,1, projection=map_proj, frameon=True)
gl = ax.gridlines(draw_labels=True) 

l.diff_current_vel.where(~l.flag).plot(
    x='longitude',
    y='latitude',
    cmap='turbo',
    vmin=0,
    vmax=2.5,
    transform=ccrs.PlateCarree(),
)
l.where(~l.flag).plot.quiver(
        x='longitude',
        y='latitude',
        u='new_cur_u',
        v='new_cur_v',
        angles='uv',
        transform=ccrs.PlateCarree(),
)
# plt.quiver(
#     x[::skipy,::skipx],
#     y[::skipy,::skipx],
#     l.new_cur_u[::skipy,::skipx],
#     l.new_cur_v[::skipy,::skipx],
#     angles='uv',
# )
ax.coastlines(resolution='10m', color='black', linewidth=1)
ax.add_feature(cfeature.GSHHSFeature(scale='full',facecolor='white'), linewidth=1.5)
plt.title('Current difference: closest_truth to current', fontsize = 60)
# plt.title('Current difference: sort_by_cost', fontsize = 60)
# plt.title('Current difference: closest_truth to wind', fontsize = 60)


###
fig23 = plt.figure(figsize=(50,40))
ax = fig23.add_subplot(1,1,1, projection=map_proj, frameon=True)
gl = ax.gridlines(draw_labels=True) 
l.diff_wind_vel.where(~l.flag).plot(
    x='longitude',
    y='latitude',
    cmap='viridis',
    vmin=0,
    vmax=10,
    transform=ccrs.PlateCarree(),
)
l.where(~l.flag).plot.quiver(
        x='longitude',
        y='latitude',
        u='new_win_u',
        v='new_win_v',
        angles='uv',
        transform=ccrs.PlateCarree(),
)
# plt.quiver(
#     x[::skipy,::skipx],
#     y[::skipy,::skipx],
#     l.new_win_u[::skipy,::skipx],
#     l.new_win_v[::skipy,::skipx],
#     angles='uv',
# )
ax.coastlines(resolution='10m', color='black', linewidth=1)
ax.add_feature(cfeature.GSHHSFeature(scale='full',facecolor='white'), linewidth=1.5)
plt.title('Wind difference: closest_truth to current', fontsize = 60)
# plt.title('Wind difference: sort_by_cost', fontsize = 60)
# plt.title('Wind difference: closest_truth to wind', fontsize = 60)


#%% Plot RSV and sigma0
level1 = xr.open_dataset(r'N:\1407-FE_SeaStar_SciRec\REALISATION\Technique\SciRec\level1s\level1_model_3base_3AC20_36_100x100_SNKp03RSV07_MVNKp04RSVnan_N4DS_M12.nc')

map_proj = ccrs.Mercator()
plt.rcParams.update({'font.size':40})

level1['Sigma0_dB'] = 10 * np.log10(level1.Sigma0)

### plot Sigma0
for antenna in level1.Antenna.data:
    fig14 = plt.figure(figsize=(50,40))
    ax = fig14.add_subplot(1,1,1, projection=map_proj, frameon=True)
    gl = ax.gridlines(draw_labels=True)
    level1.Sigma0_dB.sel(Antenna=antenna).plot(
        x='longitude',
        y='latitude',
        cmap='gist_gray',
        vmin=-0,
        vmax=-20,
        transform=ccrs.PlateCarree(),
    )
    ax.coastlines(resolution='10m', color='black', linewidth=1)
    ax.add_feature(cfeature.GSHHSFeature(scale='full',facecolor='white'), linewidth=1.5)
    plt.title('Sigma0, Antenna {name}'.format(name=antenna), fontsize = 60)


### plot RSV 
for antenna in level1.Antenna.data:
    fig24 = plt.figure(figsize=(50,40))
    ax = fig24.add_subplot(1,1,1, projection=map_proj, frameon=True)
    gl = ax.gridlines(draw_labels=True)
    level1.RSV.sel(Antenna=antenna).plot(
        x='longitude',
        y='latitude',
        cmap='RdBu_r',# !!! TO DO: chnage cmap
        vmin=0.5,
        vmax=-1.5,
        transform=ccrs.PlateCarree(),
    )
    ax.coastlines(resolution='10m', color='black', linewidth=1)
    ax.add_feature(cfeature.GSHHSFeature(scale='full',facecolor='white'), linewidth=1.5)
    plt.title('RSV, Antenna {name}'.format(name=antenna),  fontsize = 60)


#%% RMSE
level2 = xr.open_dataset(r'N:\1407-FE_SeaStar_SciRec\REALISATION\Technique\SciRec\level2s\level2_model_area_3base_3AC20_36_100x100_SNKp03RSV07_MVNKp04RSVnan_N4DS_M12_sol_closest_truth_current.nc')
# closest_truth_current, sort_by_cost_current, closest_truth_wind
geo = xr.open_dataset(r'N:\1407-FE_SeaStar_SciRec\REALISATION\Technique\SciRec\geo\geo_model_area_100x100.nc')
level2 = level2.rename({'WindSpeed': 'EarthRelativeWindSpeed', 'WindDirection': 'EarthRelativeWindDirection'})
level2= level2.assign_coords(across = geo.across)
err = level2 - geo
err['flag'] = level2.cost > 4

rmse_cur_vel = np.sqrt((err['CurrentVelocity'].where(~err.flag)**2).mean(dim=['along', 'across']))
rmse_wind_vel = np.sqrt((err['EarthRelativeWindSpeed'].where(~err.flag)**2).mean(dim='along'))

print(rmse_cur_vel)
print(rmse_wind_vel)

from scipy.stats import circmean, circstd
# rmse for the circular variables
cmean_tmp = np.mod(err.where(~err.flag),360).reduce(circmean, dim=['along', 'across'], low=0, high=360, nan_policy='omit')
cmean = (np.mod((cmean_tmp-180),360)-180) # centre around 0
cstd = np.mod(err.where(~err.flag),360).reduce(circstd, dim=['along', 'across'], low=0, high=360, nan_policy='omit')
crmse = np.sqrt(cmean**2 + cstd**2)
print(crmse)


