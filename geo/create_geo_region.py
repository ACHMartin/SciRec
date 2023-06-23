import xarray as xr
import numpy as np
import os
from typing import Optional
import seastar
import pathlib
import pickle


def compute_geo(main_dir: str, dic_m: dict, region: str,
                size_along: Optional[str] = 150,
                size_across: Optional[str] = 120):

    i0 = 300
    i1 = i0 + size_across
    j0 = 50
    j1 = j0 + size_along

    wdir = np.rad2deg(np.arctan(dic_m['wnd'][:, :, 1], dic_m['wnd'][:, :, 0]))
    wspd = np.sqrt(dic_m['wnd'][:, :, 1]**2 + dic_m['wnd'][:, :, 0]**2)
    wdir = wdir[i0:i1, j0:j1]
    wspd = wspd[i0:i1, j0:j1]

    cdir = np.rad2deg(np.arctan(dic_m['tsc'][:, :, 1], dic_m['tsc'][:, :, 0]))
    cvel = np.sqrt(dic_m['tsc'][:, :, 1]**2 + dic_m['tsc'][:, :, 0]**2)
    cdir = cdir[i0:i1, j0:j1]
    cvel = cvel[i0:i1, j0:j1]


    ### INPUTS
    along = np.arange(cdir.shape[1])
    across = np.arange(cdir.shape[0])

    print(along.shape, across.shape, wdir.shape, cvel.shape)
    geo = xr.Dataset(
            data_vars=dict(
                EarthRelativeWindSpeed=(['across', 'along'], wspd),
                EarthRelativeWindDirection=(['across', 'along'], wdir),
                CurrentVelocity=(['across','along'], cvel),
                CurrentDirection=(['across', 'along'], cdir),
                ),
            coords=dict(
                across=across,
                along=along,
                )
            )

    geo = seastar.utils.tools.EarthRelativeSpeedDir2all(geo)

    geo_file_str = f'geo_{across.size:03d}x{along.size:03d}_{region}.nc'
    geo_path = os.path.join(main_dir, 'geo')
    pathlib.Path(geo_path).mkdir(parents=True, exist_ok=True)
    geo.to_netcdf(path=os.path.join(geo_path, geo_file_str))

if '__main__' == __name__:
    input_dir = '/home/lgaultier/src/SciRec'
    region = 'California'
    salong = 150
    sacross = 120
    path_data = os.path.join(input_dir, f'{region}.pyo')
    with open(path_data, 'rb') as f:
         dic_m = pickle.load(f)

    compute_geo(input_dir, dic_m, region, size_along=salong, size_across=sacross)
