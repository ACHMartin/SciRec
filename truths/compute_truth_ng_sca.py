import os
import pathlib
import xarray as xr
import numpy as np
from typing import Optional
import seastar
# from seastar.utils.tools import dotdict
import sys
sys.path.append(os.path.dirname(os.path.abspath(__name__))) # add parent directory
import instruments.create_inst_from_OHB as inst
import geo.create_geo_ng_sca as geofunc

def compute_truth(inst: xr.Dataset, geo: xr.Dataset, gmf: dict, 
                  write_nc: Optional[bool]=False, 
                  main_path: Optional[str]='.'):
    '''
    '''

    # check across are the same size
    if not inst.across.size == geo.across.size:
        raise Exception('across shall be equals between inst and geo')
    if not inst.across.equals(geo.across):
        geo['across'] = inst.across

    truth = seastar.performance.scene_generation.truth_fct(geo, inst, gmf)

    uncertainty_in = xr.Dataset()
    uncertainty_in['Kp'] = inst['uncerty_Kp']
    uncertainty_in['RSV'] = inst['uncerty_RSV']
    [uncerty, noise] = seastar.performance.scene_generation.uncertainty_fct(
                            truth,
                            uncertainty_in
                        )

    file_str = 'truth_' + inst.attrs['filename'] \
        + '_' + geo.attrs['filename'] + '.nc'
    truth.attrs['filename'] = file_str[:-3]
    truth.attrs['history'] = 'inst: ' + inst.attrs['filename'] \
                        + '; geo: ' + geo.attrs['filename'] \
                        + '; nrcs gmf: ' + truth.attrs['gmf_nrcs'] \
                        + '; dop gmf: ' +  truth.attrs['gmf_doppler']
    if write_nc:
        path = os.path.join(main_path, 'truth')
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        file_path = os.path.join(path, file_str)
        truth.to_netcdf(path=file_path)

    return(truth, noise)

def compute_level1(truth: xr.Dataset, noise: xr.Dataset, write_nc=False, main_path='.'):
    '''
    '''    

    level1 = seastar.performance.scene_generation.noise_generation(truth, noise)
    level1['noise_Sigma0'] = noise['Sigma0']
    level1['noise_RSV'] = noise['RSV']

    file_str = 'level1_' + truth.attrs['filename'][6:] + '.nc'
    level1.attrs['filename'] = file_str[:-3]
    level1.attrs['history'] = 'truth: ' + truth.attrs['filename'] + '; ' + truth.attrs['history']
    if write_nc:
        path = os.path.join(main_path, 'level1')
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        file_path = os.path.join(path, file_str)
        level1.to_netcdf(path=file_path)
    
    return(level1)

if '__main__' == __name__:
    ngscat_path = os.path.join(os.sep,'PROJETS',
                           '1474-FE_Ocean_Scatterometer_NG',
                          'REALISATION','Technique')
    
    salong = 10
    sacross = 10
    
    # create env conditions
    my_env = dict({
        'ERWSpd': 5,
        'ERWDir':0,
        'CVel': 0,
        'CDir': 0
        })
    env = geofunc.compute_constant_geo(my_env, size_along=salong, size_across=sacross)
    
    # create simple instrument
    ohb_inst_path = os.path.join(ngscat_path, 'DATA','instrument','OHB-geometry_v20250409')
    name = 'conical_configuration_1-1__1.9rpm'
    fpath = os.path.join(ohb_inst_path, name, name + '.nc')
    si = inst.create_OHB_simple_inst(fpath, size_across=sacross)

    # create truth
    gmf={
        'nrcs': {'name': 'nscat4ds'},
        'doppler': {'name': 'mouche12'},
    }
    [truth, noise] = compute_truth(si, env, gmf)
    level1 = compute_level1(truth, noise)
