# -*- coding: utf-8 -*-
"""
Created on Wed May 31 10:39:29 2023

@author: andrievskaia
"""
import numpy as np
import math
import xarray as xr
import matplotlib.pyplot as plt

level2 = xr.open_dataset(r'N:\1407-FE_SeaStar_SciRec\REALISATION\Technique\SciRec\level2s\level2_model_3base_3AC20_36_011x009_SNKp03RSV07_MVNKp04RSVnan_N4DS_M12_sol_closest_truth_wind.nc').load()
# closest_truth_current, sort_by_cost_current, closest_truth_wind
cmap_dict = {'CurrentVelocity': 'plasma', 'CurrentDirection': 'hsv', 
             'WindSpeed': 'viridis', 'WindDirection': 'twilight', 'cost': 'viridis'}

plt.rcParams.update({'font.size': 40})

###
fig1 = plt.figure(figsize=(50,40))
level2.CurrentVelocity.plot(
    x='across',
    y='along',
    cmap=cmap_dict['CurrentVelocity']
)
level2.plot.quiver(
    x='across',
    y='along',
    u='CurrentU',
    v='CurrentV',
    angles='uv',
)
# plt.title('Ambiguity method: closest_truth to current', fontsize = 40)
# plt.title('Ambiguity method: sort_by_cost')
plt.title('Ambiguity method: closest_truth to wind')
plt.show()

###
fig2 = plt.figure(figsize=(50,40))
level2.WindSpeed.plot(
    x='across',
    y='along',
    cmap=cmap_dict['WindSpeed']
)
level2.plot.quiver(
    x='across',
    y='along',
    u='WindU',
    v='WindV',
    angles='uv',
)
# plt.title('Ambiguity method: closest_truth to current', fontsize = 40)
# plt.title('Ambiguity method: sort_by_cost')
plt.title('Ambiguity method: closest_truth to wind')
plt.show()

###
fig3 = plt.figure(figsize=(50,40))
im = level2.cost.plot(x='across', vmax=4)
# cbar = fig3.colorbar(im).cmap.set_over('red')
im.cmap.set_over('red')
# plt.title('Ambiguity method: closest_truth to current', fontsize = 40)
# plt.title('Ambiguity method: sort_by_cost')
plt.title('Ambiguity method: closest_truth to wind')
plt.show()






