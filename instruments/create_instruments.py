import xarray as xr
import numpy as np
from scipy import interpolate

### INPUTS
across_length = 100
Kp_sqt = 0.03 # 3% (Mater v2-v4 3%)
RSV_sqt = 0.07 # 6cm/s (Mater v2-v4 5cm/s) !!!

Kp_midV = 0.04 # 4% (Mater v2-v4: 4%) !!!
Kp_midH = 0.05 # 4%
RSV_midV = np.nan # cm/s (Mater v3: 40cm/s; v4 None) 0.40 !!!
RSV_midH = 0.40 # cm/s (Mater v3: 40cm/s; v4 None)

## Frequency
central_frequency = 13.5 * 10**9 #Hz

# inst_str OPTIONS
# 2sq22: two beams with a squint of 22° at near range
# 4base: geometry of the proposal with 2 sqt + broadside VV + HH
# 3base: same as 4 base but without HH
# 3sq29: reduce squint compare to baseline but keeping same incidence angle for broadside
inst_str = '3base'

if inst_str == '2sq22':
    ## Geometry
    # boundary values
    inc_angle_broadside_propa = [20.0, 28.4, 33.4] # WARNING not consistent with the squint.
    inc_angle_sqt_propa = [31.5, 36.5, 40.0]
    sqt_ground_propa = [22.5, 18.0, 15.0] # defined from sat direction for Fore beam;
    across_distance_propa = [0, 90, 150]

    # Define interpolation range for broadside
    inc_angle_broadside = np.linspace(15, 35 + 1, across_length)

if inst_str[1:] == 'sq29':
    ## Geometry
    # boundary values
    inc_angle_broadside_propa = [28.1, 33.6, 38.1]
    inc_angle_sqt_propa = [31.5, 36.5, 40.0]
    sqt_ground_propa = [29.0, 25.4, 22.5] # defined from sat direction for Fore beam;
    across_distance_propa = [0, 90, 150]

    # Define interpolation range for broadside
    inc_angle_broadside = np.linspace(19, 40 + 1, across_length)

if inst_str[1:] == 'base':
    ## Geometry
    # boundary values
    inc_angle_broadside_propa = [20.0, 28.4, 33.4]
    inc_angle_sqt_propa = [31.5, 36.5, 40.0]
    sqt_ground_propa = [52.2, 45.0, 37.8] # defined from sat direction for Fore beam;
    across_distance_propa = [0, 90, 150]

    # Define interpolation range for broadside
    # inc_angle_broadside = np.arange(15, 35+1, 2) #2
    inc_angle_broadside = np.linspace(20, 35 + 1, across_length)

## Interpolation
# create interpolation function based on broadside inci angle
f_inc_sqt = interpolate.interp1d(
        inc_angle_broadside_propa, inc_angle_sqt_propa,
        fill_value='extrapolate')
f_squint_ground = interpolate.interp1d(
        inc_angle_broadside_propa, sqt_ground_propa,
        fill_value='extrapolate')
f_across = interpolate.interp1d(
        inc_angle_broadside_propa, across_distance_propa,
        fill_value='extrapolate')
# interpolation over defined broadside range
inc_angle_mid = inc_angle_broadside
inc_angle_sqt = f_inc_sqt(inc_angle_broadside)
squint_ground = f_squint_ground(inc_angle_broadside)
across = f_across(inc_angle_broadside)

# Build inst dataset
inst = xr.Dataset(
        coords=dict(
            CentralFreq=( [], central_frequency ),
            )
        )
inst.CentralFreq.attrs['units'] = 'Hz'

inst=inst.assign_coords(across=('across', across))
inst.across.attrs['units'] = 'km'

if inst_str[0:3] == '2sq': # 2 antennas only squint
    inst=inst.assign_coords(Antenna=('Antenna', ['Fore', 'Aft']))
    inst['IncidenceAngleImage']=(
            ['across','Antenna'],
            np.stack((
                inc_angle_sqt,
                inc_angle_sqt,
                ), axis=-1)
            )
    inst['AntennaAzimuthImage']=(
            ['across','Antenna'],
            np.stack((
                90-squint_ground,
                90+squint_ground,
                ), axis=-1)
            )
    inst['Polarization']=(
            ['across','Antenna'],
            np.stack((
                np.full([across.size,], 'VV'),
                np.full([across.size,], 'VV')
                ), axis=-1)
            )

    inst['uncerty_Kp'] = (
            ['Antenna'], [Kp_sqt, Kp_sqt]
            )
    inst['uncerty_RSV'] = (
            ['Antenna'], [RSV_sqt, RSV_sqt]
            )

if inst_str[0] == '3':
    inst=inst.assign_coords(Antenna=('Antenna', ['Fore', 'MidV', 'Aft']))
    inst['IncidenceAngleImage']=(
            ['across','Antenna'],
            np.stack((
                inc_angle_sqt,
                inc_angle_mid,
                inc_angle_sqt,
                ), axis=-1)
            )
    inst['AntennaAzimuthImage']=(
            ['across','Antenna'],
            np.stack((
                90-squint_ground,
                np.full([across.size], 90),
                90+squint_ground,
                ), axis=-1)
            )
    inst['Polarization']=(
            ['across','Antenna'],
            np.stack((
                np.full([across.size,], 'VV'),
                np.full([across.size,], 'VV'),
                np.full([across.size,], 'VV')
                ), axis=-1)
            )

    inst['uncerty_Kp'] = (
            ['Antenna'], [Kp_sqt, Kp_midV, Kp_sqt]
            )
    inst['uncerty_RSV'] = (
            ['Antenna'], [RSV_sqt, RSV_midV, RSV_sqt]
            )


if inst_str[0] == '4':
    inst=inst.assign_coords(Antenna=('Antenna', ['Fore', 'MidV', 'MidH', 'Aft']))
    inst['IncidenceAngleImage']=(
            ['across','Antenna'],
            np.stack((
                inc_angle_sqt,
                inc_angle_mid,
                inc_angle_mid,
                inc_angle_sqt,
                ), axis=-1)
            )
    inst['AntennaAzimuthImage']=(
            ['across','Antenna'],
            np.stack((
                90-squint_ground,
                np.full([across.size], 90),
                np.full([across.size], 90),
                90+squint_ground,
                ), axis=-1)
            )
    inst['Polarization']=(
            ['across','Antenna'],
            np.stack((
                np.full([across.size,], 'VV'),
                np.full([across.size,], 'VV'),
                np.full([across.size,], 'HH'),
                np.full([across.size,], 'VV')
                ), axis=-1)
            )

    inst['uncerty_Kp'] = (
            ['Antenna'], [Kp_sqt, Kp_midV, Kp_midH, Kp_sqt]
            )
    inst['uncerty_RSV'] = (
            ['Antenna'], [RSV_sqt, RSV_midV, RSV_midH, RSV_sqt]
            )



### SAVE as NetCDF
if inst_str[0] == '2':
    noise_str = 'SNKp{Kp_sqt:02.0f}RSV{RSV_sqt:02.0f}'.format(
            Kp_sqt=Kp_sqt*100, 
            RSV_sqt=RSV_sqt*100
            )
elif inst_str[0] == '3':
    noise_str = 'SNKp{Kp_sqt:02.0f}RSV{RSV_sqt:02.0f}'.format(
                    Kp_sqt=Kp_sqt*100, 
                    RSV_sqt=RSV_sqt*100
                )\
            + '_MVNKp{Kp_midV:02.0f}RSV{RSV_midV:02.0f}'.format(
                    Kp_midV=Kp_midV*100,
                    RSV_midV=RSV_midV*100
                )
elif inst_str[0] == '4':
    noise_str = 'SNKp{Kp_sqt:02.0f}RSV{RSV_sqt:02.0f}'.format(
                    Kp_sqt=Kp_sqt*100, 
                    RSV_sqt=RSV_sqt*100
                )\
            + '_MVNKp{Kp_midV:02.0f}RSV{RSV_midV:02.0f}'.format(
                    Kp_midV=Kp_midV*100,
                    RSV_midV=RSV_midV*100
                )\
            + '_MHNKp{Kp_midH:02.0f}RSV{RSV_midH:02.0f}'.format(
                    Kp_midH=Kp_midH*100,
                    RSV_midH=RSV_midH*100
                )

inst_file_str = 'inst_{inst_str}_{inst_str:.1}AC'.format(inst_str=inst_str) \
    + '{broadside_inci_near:02.0f}_{broadside_inci_far:02.0f}'.format(
            broadside_inci_near=inc_angle_broadside[0],
            broadside_inci_far=inc_angle_broadside[-1]
        )\
    + '_{across_nb_points:03d}x_{noise_str}.nc'.format(
            across_nb_points=len(inc_angle_broadside),
            noise_str=noise_str
        )

    #+ '_{across_nb_points:03d}x_SNKp{Kp:02.0f}RSV{RSV:02.0f}.nc'.format(across_nb_points=len(inc_angle_broadside),
                                                                #Kp=Kp_sqt*100,
                                                                #RSV=RSV_sqt*100)
inst.to_netcdf(path=inst_file_str)



