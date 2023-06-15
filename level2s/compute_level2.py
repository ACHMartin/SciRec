import sys
sys.path.append("/gpfs/USERS/andrievskaia/SeaSTAR/seastar_project")


import xarray as xr
import numpy as np
import seastar
from seastar.utils.tools import dotdict
import time

### INPUTS
## Instrument
# inst_file = 'inst_3sq29_3AC19_39_011x_SNKp03RSV05_MVNKp04RSV40.nc'
#inst_file = 'inst_2sq22_2AC15_35_011x_SNKp03RSV05.nc'
# inst_file = 'inst_4base_4AC15_35_011x_SNKp03RSV05_MVNKp04RSV20_MHNKp04RSV20.nc'
# inst_file = 'inst_4base_4AC15_29_003x_SNKp03RSV05_MVNKp04RSV20_MHNKp04RSV20.nc'
# inst_file = 'inst_4base_4AC15_29_003x_SNKp03RSV05_MVNKp04RSV20_MHNKp04RSV20_n.nc'
# inst_file = 'inst_3base_3AC15_35_011x_SNKp03RSV05_MVNKp05RSV40.nc'
# inst_file = 'inst_3base_3AC15_36_100x_SNKp03RSV05_MVNKp05RSV40.nc'
# inst_file = 'inst_3base_3AC15_36_011x_SNKp03RSV07_MVNKp04RSVnan.nc'
inst_file = 'inst_3base_3AC15_36_100x_SNKp03RSV07_MVNKp04RSVnan.nc'
inst_str = inst_file[8:13]
inst_path = '../instruments/' + inst_file

gmf={
    'nrcs': {'name': 'nscat4ds'},
    'doppler': {'name': 'mouche12'},
}

across_size=int(inst_file[20:23])
along_size=100

## Geo
wdir_v = np.arange(0, 360, 15)
wspd_v = 5 * np.ones_like(wdir_v)
cvel_v = 0.6 * np.ones_like(wdir_v)
cdir_v = 0 * np.ones_like(wdir_v)

gmf_nrcs = gmf['nrcs']['name'].upper()
gmf_doppler = gmf['doppler']['name'].upper()
## Iteration
ii = 0

wdir = 270
# for ii, wdir in enumerate(wdir_v):
wspd = wspd_v[ii]
cvel = cvel_v[ii]
cdir = cdir_v[ii]

out_str = inst_file[5:24] + '{nb_along:03d}_'.format(nb_along=along_size)\
            + inst_file[25:-3] \
            + '_W{wspd:03.0f}_{wdir:03.0f}_C{cvel:03.1f}_{cdir:03.0f}'.format(
                wspd=wspd, wdir=wdir,
                cvel=cvel, cdir=cdir) \
            + '_{}_{}.nc'.format(gmf_nrcs[0]+gmf_nrcs[-3:],
                    gmf_doppler[0]+gmf_doppler[-2:])

level1_str = 'level1_' + out_str
level1_path = '../level1s/' + level1_str

# path_l1 = 'H:/SeaSTAR/20230418_SciReC_simu/level1s'
# level1 = xr.open_dataset(path_l1 + '/'+ level1_str)

level1 = xr.open_dataset(level1_path).load()

noise = xr.Dataset()
noise['Sigma0'] = level1['noise_Sigma0']
noise['RSV'] = level1['noise_RSV']

truth_str = 'truth_' + out_str
truth_path = '../truths/' + truth_str
truth = xr.open_dataset(truth_path)
truth = truth.load()

if __name__ == '__main__':
    start_time = time.perf_counter()

    lmout = seastar.retrieval.level2.run_find_minima(level1, noise, gmf)
    lmout.attrs = level1.attrs
    lmout.attrs['level1'] = level1_path

    level2_file_str = 'level2_' + out_str
    lmout.to_netcdf(path=level2_file_str)

    # # ambiguity = {'name': 'closest_truth', 'truth': truth, 'method': 'current'}
    # # ambiguity = {'name': 'sort_by_cost', 'truth': truth, 'method': 'current'}
    # ambiguity = {'name': 'closest_truth', 'truth': truth, 'method': 'wind'}
    # sol = seastar.retrieval.ambiguity_removal.solve_ambiguity(lmout, ambiguity)
    # level2 = seastar.retrieval.level2.sol2level2(sol)
    #
    # out_str_sol = inst_file[5:24] + '{nb_along:03d}_'.format(nb_along=along_size) \
    #           + inst_file[25:-3] \
    #           + '_W{wspd:03.0f}_{wdir:03.0f}_C{cvel:03.1f}_{cdir:03.0f}'.format(
    #     wspd=wspd, wdir=wdir,
    #     cvel=cvel, cdir=cdir) \
    #           + '_{}_{}_sol.nc'.format(gmf_nrcs[0] + gmf_nrcs[-3:],
    #                                gmf_doppler[0] + gmf_doppler[-2:])
    # level2_file_str_sol = 'level2_' + out_str_sol
    # level2.to_netcdf(path=level2_file_str_sol)