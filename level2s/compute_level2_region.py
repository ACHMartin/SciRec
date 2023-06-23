import xarray as xr
import os
import numpy as np
import seastar
from datetime import date
from typing import Optional

GMF_DEFAULT = {'nrcs': {'name': 'nscat4ds'}, 'doppler': {'name': 'mouche12'}, } 


def compute_level2(main_dir: str, specs: dict, region: str,
                   gmf: Optional[dict] = GMF_DEFAULT,
                   size_across: Optional[int] = 120,
                   size_along: Optional[int] = 150):


    gmf={
        'nrcs': {'name': 'nscat4ds'},
        'doppler': {'name': 'mouche12'},
    }
    inst_str = specs['instr_geometry']

    gmf_nrcs = gmf['nrcs']['name'].upper()
    gmf_doppler = gmf['doppler']['name'].upper()
    lgmf = f'{gmf_nrcs[0]}{gmf_nrcs[-3:]}_{gmf_doppler[0]}{gmf_doppler[-2:]}'
    in_str = f'{inst_str}{size_along}_{specs["noise_str"]}_{region}_{lgmf}'

    out_str_v = f'{in_str}_v{date.today().strftime("%Y%m%d")}.nc'

    level1_str = f'level1_{in_str}.nc'
    level1_path = os.path.join(main_dir,'level1s', level1_str)

    level1 = xr.open_dataset(level1_path).load()

    noise = xr.Dataset()
    noise['Sigma0'] = level1['noise_Sigma0']
    noise['RSV'] = level1['noise_RSV']

    lmout = seastar.retrieval.level2.run_find_minima(level1, noise, gmf)
    lmout.attrs = level1.attrs
    lmout.attrs['level1'] = level1_path
    level2_path = os.path.join(main_dir, 'level2s')
    pathlib.Path(level2_path).mkdir(parents=True, exist_ok=True)
    level2_file_str = os.path.join(level2_path, f'level2_{out_str_v}')
    lmout.to_netcdf(path=level2_file_str)


if '__main__' == __name__:
    main_dir = '../'
    specs = {}

    specs['instr_geometry'] = '3base'
    specs["noise_str"] = 'SNKp03RSV07_MVNKp04RSVnan'
    compute_level2(main_dir, specs, 'California', gmf=GMF_DEFAULT,
                   size_across=120, size_along=150)
