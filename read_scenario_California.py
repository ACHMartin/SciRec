import scipy.io as spio
import numpy as np
import pickle
from matplotlib import pyplot as plt
from drama import constants as cnst
from drama import utils as drtls
from scipy import ndimage
import os
from typing import Tuple, Optional

#  to ignore the warnings by nan
import warnings

warnings.simplefilter(action="ignore", category=RuntimeWarning)


def read_scenario_California(matfile: str, smp_out: Optional[float] = None,
                             rot_angle: Optional[float] = 0
                             ) -> Tuple[dict, float]:
    """
    Read tsc and wind from mat file (in Claudia Pasquero's format)
    :param matfile:
    :return: dic
    """
    scn = spio.loadmat(matfile)
    # crop data to get same dimension for both u and v
    scn['u'] = scn['u'][:, 0:-1]
    scn['su'] = scn['su'][:, 0:-1]
    scn['oclon_u'] = scn['oclon_u'][:, 0:-1]
    scn['oclat_u'] = scn['oclat_u'][:, 0:-1]

    scn['v'] = scn['v'][0:-1, :]
    scn['sv'] = scn['sv'][0:-1, :]

    tsc_v = np.zeros(scn['u'].shape + (2,))
    wind_v = np.zeros_like(tsc_v)

    tsc_v[:, :, 0] = scn['u']
    tsc_v[:, :, 1] = scn['v']

    # convert wind stress to wind speed with Cd=1e-3, air_density = 1.22 kg/m^3
    ind = scn['su'] < 0
    scn['su'][ind] = -scn['su'][ind]
    wind_v[:, :, 0] = np.sqrt(scn['su'] / 1.22e-3)
    wind_v[:, :, 0][ind] = -wind_v[:, :, 0][ind]
    ind = scn['sv'] < 0
    scn['sv'][ind] = -scn['sv'][ind]
    wind_v[:, :, 1] = np.sqrt(scn['sv'] / 1.22e-3)
    wind_v[:, :, 1][ind] = -wind_v[:, :, 1][ind]
    cos_lat = np.cos(np.radians(scn['oclat_u'][0, 0]))
    dx = np.sqrt((np.radians(scn['oclon_u'][0, 1] - scn['oclon_u'][0, 0]) * cos_lat * cnst.r_earth) ** 2
                 + (np.radians(scn['oclat_u'][0, 1] - scn['oclat_u'][0, 0]) * cnst.r_earth) ** 2)
    dy = np.sqrt((np.radians(scn['oclon_u'][1, 0] - scn['oclon_u'][0, 0]) * cos_lat * cnst.r_earth) ** 2 + (
                np.radians(scn['oclat_u'][1, 0] - scn['oclat_u'][0, 0]) * cnst.r_earth) ** 2)
    # print(dx)
    # print(dy)
    lon = scn['oclon_u']
    lat = scn['oclat_u']
    sst = scn['sst']
    if smp_out is None:
        smp_out = dx
    else:
        # Resample
        nxo = int(np.floor(tsc_v.shape[1] * dx / smp_out))
        nyo = int(np.floor(tsc_v.shape[0] * dy / smp_out))
        xo = np.arange(nxo) * smp_out / dx
        yo = np.arange(nyo) * smp_out / dy
        wind_v = drtls.linresample(drtls.linresample(wind_v, xo, axis=1, extrapolate=True),
                                   yo, axis=0, extrapolate=True)
        tsc_v = drtls.linresample(drtls.linresample(tsc_v, xo, axis=1, extrapolate=True),
                                  yo, axis=0, extrapolate=True)
        sst = drtls.linresample(drtls.linresample(sst, xo, axis=1, extrapolate=True),
                                yo, axis=0, extrapolate=True)
        lon = drtls.linresample(drtls.linresample(lon, xo, axis=1, extrapolate=True),
                                yo, axis=0, extrapolate=True)
        lat = drtls.linresample(drtls.linresample(lat, xo, axis=1, extrapolate=True),
                                yo, axis=0, extrapolate=True)
    wind_v = np.transpose(wind_v, axes=[1, 0, 2])
    tsc_v = np.transpose(tsc_v, axes=[1, 0, 2])
    sst = np.transpose(sst)
    lat = np.transpose(lat)
    lon = np.transpose(lon)
    if rot_angle != 0:
        wind_v[np.isnan(wind_v)] = 0
        tsc_v[np.isnan(tsc_v)] = 0
        sst[np.isnan(sst)] = 25
        wind_v = np.stack([ndimage.rotate(wind_v[:, :, 0], rot_angle),
                           ndimage.rotate(wind_v[:, :, 1], rot_angle)], axis=-1)
        tsc_v = np.stack([ndimage.rotate(tsc_v[:, :, 0], rot_angle),
                          ndimage.rotate(tsc_v[:, :, 1], rot_angle)], axis=-1)
        sst = ndimage.rotate(sst, rot_angle)
        lat = ndimage.rotate(lat, rot_angle)
        lon = ndimage.rotate(lon, rot_angle)
        rot_m = np.array([[np.cos(np.radians(rot_angle)), np.sin(np.radians(rot_angle))],
                          [-np.sin(np.radians(rot_angle)), np.cos(np.radians(rot_angle))]])
        wind_v = np.einsum("lk,ijk->ijl", rot_m, wind_v)
        tsc_v = np.einsum("lk,ijk->ijl", rot_m, tsc_v)
    dic_out = {'tsc': tsc_v, 'wnd': wind_v, 'sst': sst,
               'lon': lon, 'lat': lat, 'grid_spacing': smp_out, 'x': xo,
               'y': yo}
    return dic_out, smp_out


if __name__ == '__main__':
    main_dir = "/mnt/data/Harmony/California/"
    pardir = os.path.join(main_dir, 'PAR')
    datadir = './'
    # scn_file = 'sample_sfc_velocity_wind.mat
    scn_file = 'ocean_lionel.mat'
    dic_out, dx = read_scenario_California(os.path.join(main_dir, scn_file),
                                           smp_out=1e3, rot_angle=-10)
    sst = dic_out['sst']
    wind = dic_out['wnd']
    tsc = dic_out['tsc']
    dic_out['dx'] = dx
    with open(os.path.join(datadir, 'California.pyo'), 'wb') as f:
        pickle.dump(dic_out, f)
