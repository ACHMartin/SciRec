import os
import pathlib
import xarray as xr
import numpy as np
from typing import Optional
import seastar
from seastar.utils.tools import dotdict
from datetime import date

def compute_level2(
        level1: xr.Dataset, gmf: dict, 
        write_nc: Optional[bool]=False, 
        main_path: Optional[str]='.'
        ):
    '''
    '''
    level1 = level1.load() # needed for multiprocessing

    noise = xr.Dataset()
    noise['Sigma0'] = level1['noise_Sigma0']
    noise['RSV'] = level1['noise_RSV']

    lmout = seastar.retrieval.level2.run_find_minima(level1, noise, gmf, serial=False)
    # lmout = seastar.retrieval.level2.run_find_minima(level1, noise, gmf)

    file_str = 'level2_' + level1.attrs['filename'][6:] + '.nc'
    lmout.attrs['filename'] = file_str[:-3]
    lmout.attrs['history'] = 'level1: ' + level1.attrs['filename'] + ';\n ' + level1.attrs['history']
    if write_nc:
        path = os.path.join(main_path, 'level2')
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        file_path = os.path.join(path, file_str)
        lmout.to_netcdf(path=file_path)

    return(lmout)

if __name__=='__main__':
    ngscat_path = os.path.join(os.sep,'PROJETS',
                           '1474-FE_Ocean_Scatterometer_NG',
                          'REALISATION','Technique')
    main_dir = os.path.join(ngscat_path, '202504_SciReC_simu')

    # level1_name = 'level1_inst_010_conical_configuration_1-1__1.9rpm_geo_010x010_W005_000_C0.0_000.nc'
    level1_name = 'level1_inst_100_conical_configuration_1-1__1.9rpm_geo_100x100_W005_000_C0.0_000.nc'
    fpath = os.path.join(main_dir, 'level1', level1_name)
    level1 = xr.open_dataset(fpath)

    gmf={
        'nrcs': {'name': 'nscat4ds'},
        'doppler': {'name': 'mouche12'},
    }

    level2 = compute_level2(level1, gmf, write_nc=True, main_path=main_dir)

    

