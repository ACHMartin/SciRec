import sys
sys.path.append("/gpfs/PROJETS/1407-FE_SeaStar_SciRec/REALISATION/Technique/seastar_project")
import xarray as xr
import numpy as np
import seastar

### INPUTS
across_length = 100
along_length = 100
across = np.arange(0, across_length)
along = np.arange(0, along_length)

# flag to choose between geo from constant values or from model
geo_flag = 'model' # 'const' 'model'
# path to geo if it is taken from model
path_to_geo = 'N:/1407-FE_SeaStar_SciRec/REALISATION/Technique/scirec_data/CROCO1000_201009_area.nc'

# Geo
if geo_flag == 'const':
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
    geo_file_str = r'geo_{nb_across:03d}x{nb_along:03d}_'.format(nb_across=len(across),
                                                                 nb_along=len(along)) \
                   + 'W{wspd:03.0f}_{wdir:03.0f}_C{cvel:03.1f}_{cdir:03.0f}.nc'.format(
        wspd=wspd, wdir=wdir, cvel=cvel, cdir=cdir)
else:
    # new geo from CROCO model
    geo_short = xr.open_dataset(path_to_geo)

    lon = geo_short.nav_lon_u.values[0]
    lat = []
    for i in range(len(geo_short.nav_lat_u.values)):
        lat.append(geo_short.nav_lat_u.values[i][0])
    lat = np.array(lat)

    wspd, wdir = seastar.utils.tools.windUV2SpeedDir(geo_short.uwnd, geo_short.vwnd)
    cvel, cdir = seastar.utils.tools.currentUV2VelDir(geo_short.u, geo_short.v)

    wspd = wspd.sel(x_v=1, y_v=1, drop=True)[:across_length, :along_length]
    wdir = wdir[:across_length, :along_length, 1, 1]
    cvel = cvel.sel(x_v=1, y_v=1, s_rho=0, drop=True)[:across_length, :along_length]
    cdir = cdir[0, :across_length, :along_length, 1, 1]

    geo = xr.Dataset(
        data_vars=dict(
            # EarthRelativeWindSpeed=(['latitude', 'longitude'], wspd.values),
            # EarthRelativeWindDirection=(['latitude', 'longitude'], wdir),
            # CurrentVelocity=(['latitude', 'longitude'], cvel.values),
            # CurrentDirection=(['latitude', 'longitude'], cdir),
            # across=(['latitude', 'longitude'], np.array(range(0,100,1))*np.ones((100, 100))),
            # along=(['latitude', 'longitude'], (np.array(range(0,100,1))*np.ones((100, 100))).transpose()),
            EarthRelativeWindSpeed=(['across', 'along'], wspd.values),
            EarthRelativeWindDirection=(['across', 'along'], wdir),
            CurrentVelocity=(['across', 'along'], cvel.values),
            CurrentDirection=(['across', 'along'], cdir),
            # latitude=(['across', 'along'], geo_short.nav_lat_u.values),
            # longitude=(['across', 'along'], geo_short.nav_lon_u.values),
        ),
        coords=dict(
            across=across,
            along=along,
            latitude=(['across', 'along'], geo_short.nav_lat_u.values),
            longitude=(['across', 'along'], geo_short.nav_lon_u.values),
        )
    )
    geo_file_str = r'geo_model_area_{nb_across:03d}x{nb_along:03d}.nc'.format(nb_across=len(across),nb_along=len(along))

geo = seastar.utils.tools.EarthRelativeSpeedDir2all(geo)
geo.to_netcdf(path=geo_file_str)


