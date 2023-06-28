# -*- coding: utf-8 -*-
"""
Created on Wed May 31 10:39:29 2023

@author: andrievskaia
"""
import numpy as np
import math
import xarray as xr
import matplotlib.pyplot as plt

#####
##### Plot retreived current and wind
#####
level2 = xr.open_dataset(r'N:\1407-FE_SeaStar_SciRec\REALISATION\Technique\SciRec\level2s\level2_model_3base_3AC20_36_100x100_SNKp03RSV07_MVNKp04RSVnan_N4DS_M12_sol_closest_truth_current.nc')
# closest_truth_current, sort_by_cost_current, closest_truth_wind
cmap_dict = {'CurrentVelocity': 'plasma', 'CurrentDirection': 'hsv', 
             'WindSpeed': 'viridis', 'WindDirection': 'twilight', 'cost': 'viridis'}

skipx, skipy = 5, 5
X,Y = np.meshgrid(level2.across,level2.along)
plt.rcParams.update({'font.size':40})

###
fig1 = plt.figure(figsize=(50,40))
level2.CurrentVelocity.plot(
    x='across',
    y='along',
    cmap=cmap_dict['CurrentVelocity']
)
q = plt.quiver(
    X[::skipy,::skipx],
    Y[::skipy,::skipx],
    level2.CurrentU[::skipy,::skipx],
    level2.CurrentV[::skipy,::skipx],
    angles='uv',
    # scale=20,
)
# plt.quiverkey(q, 1.03, 0.97, 0.5, r'$2 \frac{m}{s}$', labelpos='N')
plt.title('Ambiguity method: closest_truth to current')
# plt.title('Ambiguity method: sort_by_cost')
# plt.title('Ambiguity method: closest_truth to wind')


###
fig2 = plt.figure(figsize=(50,40))
level2.WindSpeed.plot(
    x='across',
    y='along',
    cmap=cmap_dict['WindSpeed']
)
plt.quiver(
    X[::skipy,::skipx],
    Y[::skipy,::skipx],
    level2.WindU[::skipy,::skipx],
    level2.WindV[::skipy,::skipx],
    angles='uv',
)
plt.title('Ambiguity method: closest_truth to current')
# plt.title('Ambiguity method: sort_by_cost')
# plt.title('Ambiguity method: closest_truth to wind')


###
fig3 = plt.figure(figsize=(50,40))
im = level2.cost.plot(x='across', vmax=4)
# cbar = fig3.colorbar(im).cmap.set_over('red')
im.cmap.set_over('red')
plt.title('Ambiguity method: closest_truth to current')
# plt.title('Ambiguity method: sort_by_cost')
# plt.title('Ambiguity method: closest_truth to wind')


#####
##### Plot input current and wind
#####
geo = xr.open_dataset(r'N:\1407-FE_SeaStar_SciRec\REALISATION\Technique\SciRec\geo\geo_model_100x100.nc')
x,y = np.meshgrid(geo.across,geo.along)

###
fig12 = plt.figure(figsize=(50,40))
geo.CurrentVelocity.plot(
    x='across',
    y='along',
    cmap=cmap_dict['CurrentVelocity']
)
plt.quiver(
    x[::skipy,::skipx],
    y[::skipy,::skipx],
    geo.CurrentU[::skipy,::skipx],
    geo.CurrentV[::skipy,::skipx],
    angles='uv',
)
plt.title('Input Current', fontsize = 40)


###
fig22 = plt.figure(figsize=(50,40))
geo.EarthRelativeWindSpeed.plot(
    x='across',
    y='along',
    cmap=cmap_dict['WindSpeed']
)
plt.quiver(
    x[::skipy,::skipx],
    y[::skipy,::skipx],
    geo.EarthRelativeWindU[::skipy,::skipx],
    geo.EarthRelativeWindV[::skipy,::skipx],
    angles='uv',
)
plt.title('Input Wind', fontsize = 40)


#####
##### Plot difference between input and retreived current and wind
#####
l = level2.assign_coords(across = geo.across)
diff_current_vel = np.sqrt((l.CurrentU-geo.CurrentU)**2 + (l.CurrentV-geo.CurrentV)**2)
diff_wind_vel = np.sqrt((l.WindU-geo.EarthRelativeWindU)**2 + (l.WindV-geo.EarthRelativeWindV)**2)
new_cur_u = np.abs(l.CurrentU-geo.CurrentU)
new_cur_v = np.abs(l.CurrentV-geo.CurrentV)
new_win_u = np.abs(l.WindU-geo.EarthRelativeWindU)
new_win_v = np.abs(l.WindV-geo.EarthRelativeWindV)

l['diff_current_vel'] = diff_current_vel
l['diff_wind_vel'] = diff_wind_vel
l['new_cur_u'] = np.abs(l.CurrentU-geo.CurrentU)
l['new_cur_v'] = np.abs(l.CurrentV-geo.CurrentV)
l['new_win_u'] = np.abs(l.WindU-geo.EarthRelativeWindU)
l['new_win_v'] = np.abs(l.WindV-geo.EarthRelativeWindV)

###
fig13 = plt.figure(figsize=(50,40))
l.diff_current_vel.plot(
    x='across',
    y='along',
    cmap=cmap_dict['CurrentVelocity']
)
plt.quiver(
    x[::skipy,::skipx],
    y[::skipy,::skipx],
    l.new_cur_u[::skipy,::skipx],
    l.new_cur_v[::skipy,::skipx],
    angles='uv',
)
plt.title('Current difference', fontsize = 40)


###
fig23 = plt.figure(figsize=(50,40))
l.diff_wind_vel.plot(
    x='across',
    y='along',
    cmap=cmap_dict['WindSpeed']
)
plt.quiver(
    x[::skipy,::skipx],
    y[::skipy,::skipx],
    l.new_win_u[::skipy,::skipx],
    l.new_win_v[::skipy,::skipx],
    angles='uv',
)
plt.title('Wind difference', fontsize = 40)


