import sys
sys.path.append("/gpfs/PROJETS/1407-FE_SeaStar_SciRec/REALISATION/Technique/seastar_project")
import xarray as xr
import numpy as np
import seastar
from seastar.utils.tools import dotdict

### INPUTS
## Instrument
inst_file = 'inst_3base_3AC20_33_150x_SNKp03RSV07_MVNKp04RSVnan.nc'
inst_str = inst_file[5:10]
inst_path = '../instruments/' + inst_file

geo_file = 'geo_CROCO1000_20100918_IroiseSea_v20230907_150x150.nc'
geo_path = '../geo/' + geo_file


across_size = int(inst_file[20:23])
along_size = 150

gmf_model = 'mouche12' #'mouche12' 'yurovsky19'
gmf={
    'nrcs': {'name': 'nscat4ds'},
    'doppler': {'name': gmf_model},
}

## Loading + calculation
inst = xr.open_dataset(inst_path)

gmf_nrcs = gmf['nrcs']['name'].upper()
gmf_doppler = gmf['doppler']['name'].upper()

## Geo
geo = xr.open_dataset(geo_path)

out_str = inst_file[5:24] + '{nb_along:03d}_'.format(nb_along=along_size) \
           + inst_file[25:-3] + '_{}_{}.nc'.format(gmf_nrcs[0] + gmf_nrcs[-3:],
                                gmf_doppler[0] + gmf_doppler[-2:])


truth = seastar.performance.scene_generation.truth_fct(geo, inst, gmf)

for key in geo.attrs: # copy attributes from geo
   truth.attrs[key] = geo.attrs[key]
for key in inst.attrs: # copy attributes from inst
   truth.attrs[key] = inst.attrs[key]
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

truth_file_str = 'truth_IS_' + out_str #TODO ->  _area for ocean part, nothing for iroise
truth.to_netcdf(path=truth_file_str)

level1.attrs['inst'] = inst_path
level1.attrs['geo'] = geo_path
level1.attrs['truth'] = '../truths/' + truth_file_str

level1_file_str = '../level1s/level1_IS_' + out_str #TODO ->  _area for ocean part, nothing for iroise
level1.to_netcdf(path=level1_file_str)

