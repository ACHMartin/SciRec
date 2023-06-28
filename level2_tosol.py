import sys
sys.path.append("/gpfs/PROJETS/1407-FE_SeaStar_SciRec/REALISATION/Technique/seastar_project")
import xarray as xr
import numpy as np
import seastar

inst_file = 'inst_3base_3AC20_36_100x_SNKp03RSV07_MVNKp04RSVnan.nc'
truth = xr.open_dataset(r'N:\1407-FE_SeaStar_SciRec\REALISATION\Technique\SciRec\truths\truth_model_3base_3AC20_36_100x100_SNKp03RSV07_MVNKp04RSVnan_N4DS_M12.nc').load()
lmout = xr.open_dataset(r'N:\1407-FE_SeaStar_SciRec\REALISATION\Technique\SciRec\level2s\level2_model_3base_3AC20_36_100x100_SNKp03RSV07_MVNKp04RSVnan_N4DS_M12.nc').load()

inst_str = inst_file[8:13]
across_size, along_size = 100, 100

# flag to choose between geo from constant values or from model
geo_flag = 'model' # 'const' 'model'

gmf_model = 'mouche12' # 'yurovsky19'
gmf={
    'nrcs': {'name': 'nscat4ds'},
    'doppler': {'name': gmf_model},
}
gmf_nrcs = gmf['nrcs']['name'].upper()
gmf_doppler = gmf['doppler']['name'].upper()

# ambiguity = {'name': 'closest_truth', 'truth': truth, 'method': 'current'}
ambiguity = {'name': 'sort_by_cost', 'truth': truth, 'method': 'current'}
# ambiguity = {'name': 'closest_truth', 'truth': truth, 'method': 'wind'}
sol = seastar.retrieval.ambiguity_removal.solve_ambiguity(lmout, ambiguity)
level2sol = seastar.retrieval.level2.sol2level2(sol)

if geo_flag == 'const':
    wdir ,wspd, cvel, cdir = 270, 5, 0.6, 0
    out_str_sol = inst_file[5:24] + '{nb_along:03d}_'.format(nb_along=along_size) \
              + inst_file[25:-3] \
              + '_W{wspd:03.0f}_{wdir:03.0f}_C{cvel:03.1f}_{cdir:03.0f}'.format(
        wspd=wspd, wdir=wdir,
        cvel=cvel, cdir=cdir) \
              + '_{}_{}_sol_{}_{}.nc'.format(gmf_nrcs[0] + gmf_nrcs[-3:],
                                   gmf_doppler[0] + gmf_doppler[-2:], ambiguity['name'], ambiguity['method'])
    level2_file_str_sol = '../SciRec/level2s/' + 'level2_' + out_str_sol
else:
    out_str_sol = inst_file[5:24] + '{nb_along:03d}_'.format(nb_along=along_size) \
              + inst_file[25:-3] + '_{}_{}_sol_{}_{}.nc'.format(gmf_nrcs[0] + gmf_nrcs[-3:],
                                   gmf_doppler[0] + gmf_doppler[-2:], ambiguity['name'], ambiguity['method'])
    level2_file_str_sol = '../SciRec/level2s/' + 'level2_model_' + out_str_sol


level2sol.to_netcdf(path=level2_file_str_sol)