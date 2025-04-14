import os
import pathlib
import xarray as xr
import numpy as np
import seastar


def compute_constant_geo(main_path: str, dict_env: dict, size_along=100, size_across=11):
    '''
    dict_env being .ERWSpd, .ERWdir, .CVel, .CDir
    Earth Relative Wind Speed/Direction
    '''

    ### INPUTS
    along = np.arange(0, size_along)
    across = np.arange(0,size_across)

    ERWSpd = dict_env.ERWSpd
    ERWDir = dict_env.ERWDir
    cvel = dict_env.CVel
    cdir = dict_env.CDir

    geo = xr.Dataset(
        data_vars=dict(
            EarthRelativeWindSpeed=(['across', 'along'],
                np.full([across.size, along.size], ERWSpd)),
            EarthRelativeWindDirection=(['across', 'along'],
                np.full([across.size, along.size], ERWDir)),
            CurrentVelocity=(['across','along'],
                np.full([across.size, along.size], cvel)),
            CurrentDirection=(['across', 'along'],
                np.full([across.size, along.size], cdir)),
            ),
        coords=dict(
            across=across,
            along=along,
            )
        )
 
    geo = seastar.utils.tools.EarthRelativeSpeedDir2all(geo)

    geo_file_str = f'geo_{across.size:03d}x{along.size:03d}_'\
                + f'W{ERWSpd:03.0f}_{ERWDir:03.0f}_C{cvel:03.1f}_{cdir:03.0f}.nc'
    geo_path = os.path.join(main_path, 'geo')
    pathlib.Path(geo_path).mkdir(parents=True, exist_ok=True)
    geo_file_path = os.path.join(geo_path, geo_file_str)
    geo.to_netcdf(path=geo_file_path)

if '__main__' == __name__:
    output_dir = '/PROJETS/1474-FE_Ocean_Scatterometer_NG/REALISATION/Technique/202504_SciReC_simu'
    salong = 10
    sacross = 10
    my_env = dict({
        'ERWSpd': 5,
        'ERWDir':0,
        'CVel': 0,
        'CDir': 0
        })

    compute_geo(output_dir, my_env, size_along=salong, size_across=sacross)

