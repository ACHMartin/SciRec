import sys
sys.path.append("/gpfs/PROJETS/1407-FE_SeaStar_SciRec/REALISATION/Technique/seastar_project")


import xarray as xr
import numpy as np
import seastar
from seastar.utils.tools import dotdict

### INPUTS
## Instrument
inst_file = 'inst_3base_3AC20_36_011x_SNKp03RSV07_MVNKp04RSVnan.nc'
inst_str = inst_file[5:10]
inst_path = '../instruments/' + inst_file

across_size = int(inst_file[20:23])
along_size=9

gmf_model = 'yurovsky19' #'mouche12' 'yurovsky19'
gmf={
    'nrcs': {'name': 'nscat4ds'},
    'doppler': {'name': gmf_model},
}

## Geo
wdir_v = np.arange(0, 360, 15)
wspd_v = 5 * np.ones_like(wdir_v)
cvel_v = 0.6 * np.ones_like(wdir_v)
cdir_v = 0 * np.ones_like(wdir_v)
wdir = 270

## Loading + calculation
inst = xr.open_dataset(inst_path)

ii = 0
# for ii, wdir in enumerate(wdir_v):
wspd = wspd_v[ii]
cvel = cvel_v[ii]
cdir = cdir_v[ii]
geo_path = '../geo/' \
        + 'geo_{nb_across:03d}x{nb_along:03d}_'.format(
            nb_across=across_size, nb_along=along_size)\
        + 'W{wspd:03.0f}_{wdir:03.0f}_C{cvel:03.1f}_{cdir:03.0f}.nc'.format(
            wspd=wspd, wdir=wdir, cvel=cvel, cdir=cdir)

geo = xr.open_dataset(geo_path)
# geo = geo.copy(deep=True)

# check across and along are the same size
if not inst.across.equals(geo.across):
    geo['across'] = inst.across

geo['WindSpeed'] = geo['OceanSurfaceWindSpeed'] # TODO -> to be remove but
# need to adapt function below
geo['WindDirection'] = geo['OceanSurfaceWindDirection']
truth = seastar.performance.scene_generation.truth_fct(geo, inst, gmf)

truth.attrs['inst'] = inst_path
truth.attrs['geo'] = geo_path

uncertainty_in = xr.Dataset()
uncertainty_in['Kp'] = inst['uncerty_Kp']
uncertainty_in['RSV'] = inst['uncerty_RSV']
[uncerty, noise] = seastar.performance.scene_generation.uncertainty_fct(
                        truth,
                        uncertainty_in
                    )

level1 = seastar.performance.scene_generation.noise_generation(truth, noise)
level1['noise_Sigma0'] = noise['Sigma0']
level1['noise_RSV'] = noise['RSV']

gmf_nrcs = gmf['nrcs']['name'].upper()
gmf_doppler = gmf['doppler']['name'].upper()

out_str = inst_file[5:24] + '{nb_along:03d}_'.format(nb_along=along_size)\
        + inst_file[25:-3] \
        + '_W{wspd:03.0f}_{wdir:03.0f}_C{cvel:03.1f}_{cdir:03.0f}'.format(
            wspd=wspd, wdir=wdir,
            cvel=cvel, cdir=cdir) \
        + '_{}_{}.nc'.format(gmf_nrcs[0]+gmf_nrcs[-3:],
                gmf_doppler[0]+gmf_doppler[-2:])

truth_file_str = 'truth_' + out_str
truth.to_netcdf(path=truth_file_str)

level1.attrs['inst'] = inst_path
level1.attrs['geo'] = geo_path
level1.attrs['truth'] = '../truths/' + truth_file_str

level1_file_str = '../level1s/level1_' + out_str
level1.to_netcdf(path=level1_file_str)

