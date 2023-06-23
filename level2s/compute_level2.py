import sys
sys.path.append("/gpfs/PROJETS/1407-FE_SeaStar_SciRec/REALISATION/Technique/seastar_project")
import xarray as xr
import numpy as np
import seastar
import time

### INPUTS
## Instrument
inst_file = 'inst_3base_3AC20_36_100x_SNKp03RSV07_MVNKp04RSVnan.nc'
inst_str = inst_file[8:13]
inst_path = '../instruments/' + inst_file

## Scene size
across_size = int(inst_file[20:23])
along_size = 100

## gmf
gmf_model = 'mouche12' # 'yurovsky19' 'mouche12'
gmf={
    'nrcs': {'name': 'nscat4ds'},
    'doppler': {'name': gmf_model},
}

## Geo
# flag to choose between geo from constant values or from model
geo_flag = 'model' # 'const' 'model'


### Loading + calculation
gmf_nrcs = gmf['nrcs']['name'].upper()
gmf_doppler = gmf['doppler']['name'].upper()

## Geo
if geo_flag == 'const':
    wdir_v = np.arange(0, 360, 15)
    wspd_v = 5 * np.ones_like(wdir_v)
    cvel_v = 0.6 * np.ones_like(wdir_v)
    cdir_v = 0 * np.ones_like(wdir_v)
    wdir = 270

    ## Iteration
    ii = 0
    # for ii, wdir in enumerate(wdir_v):
    wspd = wspd_v[ii]
    cvel = cvel_v[ii]
    cdir = cdir_v[ii]

    out_str = inst_file[5:24] + '{nb_along:03d}_'.format(nb_along=along_size) \
              + inst_file[25:-3] \
              + '_W{wspd:03.0f}_{wdir:03.0f}_C{cvel:03.1f}_{cdir:03.0f}'.format(
        wspd=wspd, wdir=wdir,
        cvel=cvel, cdir=cdir) \
              + '_{}_{}.nc'.format(gmf_nrcs[0] + gmf_nrcs[-3:],
                                   gmf_doppler[0] + gmf_doppler[-2:])
    level1_str = 'level1_' + out_str
    truth_str = 'truth_' + out_str
else:
    out_str = inst_file[5:24] + '{nb_along:03d}_'.format(nb_along=along_size) \
              + inst_file[25:-3] + '_{}_{}.nc'.format(gmf_nrcs[0] + gmf_nrcs[-3:],
                                                      gmf_doppler[0] + gmf_doppler[-2:])
    level1_str = 'level1_model_' + out_str
    truth_str = 'truth_model_' + out_str

level1_path = '../level1s/' + level1_str
level1 = xr.open_dataset(level1_path).load()

noise = xr.Dataset()
noise['Sigma0'] = level1['noise_Sigma0']
noise['RSV'] = level1['noise_RSV']

truth_path = '../truths/' + truth_str
truth = xr.open_dataset(truth_path)
truth = truth.load()

if __name__ == '__main__':
    start_time = time.perf_counter()

    lmout = seastar.retrieval.level2.run_find_minima(level1, noise, gmf)
    lmout.attrs = level1.attrs
    lmout.attrs['level1'] = level1_path

    if geo_flag == 'const':
        level2_file_str = 'level2_' + out_str
    else:
        level2_file_str = 'level2_model_' + out_str
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