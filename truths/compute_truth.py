import xarray as xr
import numpy as np
import seastar
from seastar.utils.tools import dotdict

### INPUTS
## Instrument
#inst_file = 'inst_3sq29_3AC19_39_011x_SNKp03RSV05_MVNKp04RSV40.nc'
#inst_file = 'inst_2sq22_2AC15_35_011x_SNKp03RSV05.nc'
inst_file = 'inst_3base_3AC15_35_011x_SNKp03RSV07_MVNKp04RSVnan.nc'
inst_str = inst_file[5:10]
inst_path = '../instruments/' + inst_file

gmf={
    'nrcs': {'name': 'nscat4ds'},
    'doppler': {'name': 'mouche12'},
}

across_size = int(inst_file[20:23])
along_size=100

### END of inputs


## Geo
#wdir_v = np.arange(0, 360, 15)
#wspd_v = 5 * np.ones_like(wdir_v)
#cvel_v = 0.6 * np.ones_like(wdir_v)
#cdir_v = 150 * np.ones_like(wdir_v)
wspd_v = np.array([2,3,4,5,6,7,8,10,12,15,18,21])
wdir_v = 225 * np.ones_like(wspd_v)
cvel_v = 0.6 * np.ones_like(wspd_v)
cdir_v = 150 * np.ones_like(wspd_v)



## Loading + calculation
inst = xr.open_dataset(inst_path)

for ii, wdir in enumerate(wdir_v):
    wspd = wspd_v[ii]
    cvel = cvel_v[ii]
    cdir = cdir_v[ii]
    geo_path = '../geo/' \
            + 'geo_{nb_across:03d}x{nb_along:03d}_'.format(
                nb_across=across_size, nb_along=along_size)\
            + 'W{wspd:03.0f}_{wdir:03.0f}_C{cvel:03.1f}_{cdir:03.0f}.nc'.format(
                wspd=wspd, wdir=wdir, cvel=cvel, cdir=cdir)
    geo = xr.open_dataset(geo_path)



    # check across and along are the same size
    if not inst.across.equals(geo.across):
        geo['across'] = inst.across

    #geo['WindSpeed'] = geo['OceanSurfaceWindSpeed'] # TODO -> to be remove but
    # geo['WindDirection'] = geo['OceanSurfaceWindDirection']
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

