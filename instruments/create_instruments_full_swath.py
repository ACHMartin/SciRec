import xarray as xr
import numpy as np
from scipy import interpolate
import pathlib
import sys
import os
from typing import Optional

### INPUTS
def build_filename(specs: dict, basename: str, size_across: int) -> str:
    inst_str = specs['instr_geometry']
    noise_str = f'SNKp{specs["Kp_sqt"]*100:02.0f}RSV{specs["RSV_sqt"]*100:02.0f}'
    if int(inst_str[0]) >= 3:
        _tmp = f'MVNKp{specs["Kp_midV"]*100:02.0f}RSV{specs["RSV_midV"]*100:02.0f}'
        noise_str = f'{noise_str}_{_tmp}'
    if int(inst_str[0]) >= 4:
        _tmp = f'MHNKp{specs["Kp_midH"]*100:02.0f}RSV{specs["RSV_midH"]*100:02.0f}'
        noise_str = f'{noise_str}_{tmp}'
    sat = f'{inst_str[0]}AC'
    angle = f'{specs["min_inc"]:02d}_{specs["max_inc"]:02d}'
    size = f'{size_across}'
    inst_file_str = f'{basename}_{inst_str}_{sat}_{angle}_{size}_{noise_str}.nc'
    specs["noise_str"] = noise_str
    return inst_file_str, specs


def compute_instrument(main_dir: str, specs: dict, basename: str,
                       size_across: Optional[int] = 120):
    inst_str = specs['instr_geometry']
    if 'sq22' in inst_str:
        ## Geometry
        # boundary values
        inc_angle_broadside_propa = [20.0, 28.4, 33.4] # WARNING not consistent with the squint. 
        inc_angle_sqt_propa = [31.5, 36.5, 40.0]
        sqt_ground_propa = [22.5, 18.0, 15.0] # defined from sat direction for Fore beam;
        across_distance_propa = [0, 90, 150]

        # Define interpolation range for broadside
        inc_angle_broadside = np.linspace(15, 35, num=size_across)
        #inc_angle_broadside = np.arange(15, 35+1, 2)

    elif 'sq29' in inst_str:
        ## Geometry
        # boundary values
        inc_angle_broadside_propa = [28.1, 33.6, 38.1]
        inc_angle_sqt_propa = [31.5, 36.5, 40.0]
        sqt_ground_propa = [29.0, 25.4, 22.5] # defined from sat direction for Fore beam;
        across_distance_propa = [0, 90, 150]

        # Define interpolation range for broadside
        inc_angle_broadside = np.linspace(19, 40, num=size_across)
        #inc_angle_broadside = np.arange(19, 40+1, 2)

    elif 'base' in inst_str:
        ## Geometry
        # boundary values
        inc_angle_broadside_propa = [20.0, 28.4, 33.4]
        inc_angle_sqt_propa = [31.5, 36.5, 40.0]
        sqt_ground_propa = [52.2, 45.0, 37.8] # defined from sat direction for Fore beam;
        across_distance_propa = [0, 90, 150]

        # Define interpolation range for broadside
        #inc_angle_broadside = np.linspace(15, 35, num=size_across)
        inc_angle_broadside = np.linspace(specs['min_inc'], specs['max_inc'],
                                          num=size_across)
    else:
        print('Unkown instr configuration, choose between sq22, base, sq29')
        sys.exit(1)
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
                CentralFreq=( [], specs['central_frequency'] ),
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
                ['Antenna'], [specs['Kp_sqt'], specs['Kp_sqt']]
                )
        inst['uncerty_RSV'] = (
                ['Antenna'], [specs['RSV_sqt'], specs['RSV_sqt']]
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

        inst['uncerty_Kp'] = (['Antenna'],
                              [specs['Kp_sqt'], specs['Kp_midV'], specs['Kp_sqt']]
                )
        inst['uncerty_RSV'] = (
                ['Antenna'], [specs['RSV_sqt'],specs['RSV_midV'], specs['RSV_sqt']]
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
                ['Antenna'], [specs['Kp_sqt'], specs['Kp_midV'], spec['Kp_midH'], specs['Kp_sqt']]
                )
        inst['uncerty_RSV'] = (
                ['Antenna'], [specs['RSV_sqt'], specs['RSV_midV'], specs['RSV_midH'], specs['RSV_sqt']]
                )



    ### SAVE as NetCDF
    inst_file_str, specs = build_filename(specs, basename, size_across)
    inst_path = os.path.join(main_dir, 'instruments')
    pathlib.Path(inst_path).mkdir(parents=True, exist_ok=True)
    inst_file_str = os.path.join(inst_path, inst_file_str)
    inst.to_netcdf(path=inst_file_str)


if '__main__' == __name__:
    main_dir = '/home/lgaultier/src/SciRec'
    ## Frequency
    central_frequency = 13.5 * 10**9 #Hz
    size_across = 120
    # inst_str OPTIONS
    # 2sq22: two beams with a squint of 22° at near range
    # 4base: geometry of the proposal with 2 sqt + broadside VV + HH
    # 3base: same as 4 base but without HH
    # 3sq29: reduce squint compare to baseline but keeping same incidence angle for broadside
    inst_str = '3base'
    specs = {'central_frequency': central_frequency,
             'instr_geometry': inst_str,
             'min_inc': 20,
             'max_inc': 35,
             'Kp_sqt': 0.03,  # 3% (Mater v2-v4 3%)
             'RSV_sqt': 0.07,  # 7cm/s (Mater v4 5cm/s but push to 7cm/s after D8 in April 2023
             'Kp_midV': 0.04,  # 4% (Mater v2-v4: 4%)
             'Kp_midH': 0.04,  # 4%
             'RSV_midV': np.nan,  #np.nan  # cm/s (Mater v3: 40cm/s; v4 None)
             'RSV_midH': np.nan  # cm/s (Mater v3: 40cm/s; v4 None)
             }
    compute_instrument(main_dir, specs, 'lginstr', size_across=size_across)
