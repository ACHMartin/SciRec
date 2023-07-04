import xarray as xr
import numpy as np
import seastar

### INPUTS
along = np.arange(0, 100)
across = np.arange(0,11)

#wdir_v = np.arange(0, 360, 5)
#wspd_v = 5 * np.ones_like(wdir_v)
#cvel_v = 0.6 * np.ones_like(wdir_v)
#cdir_v = 150 * np.ones_like(wdir_v)

wspd_v = np.array([2,3,4,5,6,7,8,10,12,15,18,21])
wdir_v = 0 * np.ones_like(wspd_v)
cvel_v = 0.6 * np.ones_like(wspd_v)
cdir_v = 150 * np.ones_like(wspd_v)


### END inputs

for ii, wdir in enumerate(wdir_v):
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
 
    geo = seastar.utils.tools.EarthRelativeSpeedDir2all(geo)

    geo_file_str = 'geo_{nb_across:03d}x{nb_along:03d}_'.format(nb_across=len(across),
                                                                nb_along=len(along))\
                + 'W{wspd:03.0f}_{wdir:03.0f}_C{cvel:03.1f}_{cdir:03.0f}.nc'.format(
                        wspd=wspd, wdir=wdir, cvel=cvel, cdir=cdir )
    geo.to_netcdf(path=geo_file_str)

