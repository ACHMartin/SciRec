import sys
sys.path.append("/gpfs/USERS/andrievskaia/SeaSTAR/seastar_project")

import xarray as xr
import numpy as np
import seastar

### INPUTS
along = np.arange(0, 100) #9
across = np.arange(0, 100) #11

wdir_v = np.arange(0, 360, 5)
wspd_v = 5 * np.ones_like(wdir_v)
cvel_v = 0.6 * np.ones_like(wdir_v)
cdir_v = 0 * np.ones_like(wdir_v)

ii = 0
# for ii, wdir in enumerate(wdir_v):
wdir = 270
wspd = wspd_v[ii]
cvel = cvel_v[ii]
cdir = cdir_v[ii]
geo = xr.Dataset(
        data_vars=dict(
            EarthRelativeWindSpeed=(['across', 'along'],
                np.full([across.size, along.size], wspd)),
            EarthRelativeWindDirection=(['across', 'along'],
                np.full([across.size, along.size], wdir)),
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

#[geo['CurrentU'], geo['CurrentV']] = \
    #seastar.utils.tools.currentVelDir2UV(
        #geo['CurrentVelocity'],
        #geo['CurrentDirection']
    #)
#[geo['EarthRelativeWindU'], geo['EarthRelativeWindV']] = \
    #seastar.utils.tools.windSpeedDir2UV(
        #geo['EarthRelativeWindSpeed'],
        #geo['EarthRelativeWindDirection']
    #)
geo = seastar.utils.tools.EarthRelativeSpeedDir2all(geo)

geo_file_str = r'geo_{nb_across:03d}x{nb_along:03d}_'.format(nb_across=len(across),
                                                            nb_along=len(along))\
            + 'W{wspd:03.0f}_{wdir:03.0f}_C{cvel:03.1f}_{cdir:03.0f}.nc'.format(
                    wspd=wspd, wdir=wdir, cvel=cvel, cdir=cdir )
geo.to_netcdf(path=geo_file_str)

