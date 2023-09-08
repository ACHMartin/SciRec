import sys
sys.path.append("/PROJETS/1407-FE_SeaStar_SciRec/REALISATION/Technique/seastar_project")
import xarray as xr
import numpy as np
import os
import seastar


fcroco = 'CROCO1000_20100918_IroiseSea_v20230907'
path_to_geo =
os.path.join('/','PROJETS','1407-FE_SeaStar_SciRec','REALISATION','Technique','SciRec','geo')
croco = xr.open_dataset(os.path.join(path_to_geo,fcroco + '.nc'))

across_length = 150
along_length = 150
across = np.arange(0, across_length)
along = np.arange(0, along_length)

geo = xr.Dataset(
   data_vars=dict(
      EarthRelativeWindU = (['across', 'along'], croco.uwnd.data),
      EarthRelativeWindV = (['across', 'along'], croco.vwnd.data),
      CurrentU = (['across', 'along'], croco.u.data),
      CurrentV = (['across', 'along'], croco.v.data),
   ),
   coords=dict(
      across=across,
      along=along,
      latitude=croco.nav_lat_u.data[:,0],
      longitude=croco.nav_lon_u.data[0,:],
   )
)
geo.attrs['croco_file'] = os.path.join(path_to_geo,fcroco +'.nc')
geo = seastar.utils.tools.EarthRelativeUV2all(geo)

geofname = 'geo_'+fcroco+r'_{nb_across:03d}x{nb_along:03d}.nc'.format(nb_across=len(across),nb_along=len(along))
geo.to_netcdf(path=os.path.join(path_to_geo,geofname))

