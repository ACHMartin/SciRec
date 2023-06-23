import xarray as xr
import numpy as np
import seastar
import pathlib
import os
from typing import Optional

GMF_DEFAULT = {'nrcs': {'name': 'nscat4ds'}, 'doppler': {'name': 'mouche12'}, }

def compute_truth(main_dir: str, specs: dict, inst_file: str, region: str,
                  gmf: Optional[dict] = GMF_DEFAULT,
                  size_across: Optional[int] = 120,
                  size_along: Optional[int] = 150):
    inst_str = specs['instr_geometry']
    noise_str = specs["noise_str"]

    along_size = size_along
    region = 'California'
    ### END of inputs


    ## Geo
    ## Loading + calculation
    inst_path = os.path.join(main_dir, 'instruments', inst_file)
    inst = xr.open_dataset(inst_path)
    geo_path = os.path.join(main_dir, 'geo',
                            f'geo_{size_across}x{size_along}_{region}.nc')
    geo = xr.open_dataset(geo_path)



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

    lgmf = f'{gmf_nrcs[0]}{gmf_nrcs[-3:]}_{gmf_doppler[0]}{gmf_doppler[-2:]}'
    out_str = f'{inst_str}{size_along:03d}_{noise_str}_{region}_{lgmf}.nc'

    truth_path = os.path.join(main_dir, 'truths')
    pathlib.Path(truth_path).mkdir(parents=True, exist_ok=True)
    truth_file_str = os.path.join(truth_path, f'truth_{out_str}')
    truth.to_netcdf(path=truth_file_str)

    level1.attrs['inst'] = inst_path
    level1.attrs['geo'] = geo_path
    level1.attrs['truth'] = os.path.join(main_dir, 'truths', truth_file_str)

    level1_path = os.path.join(main_dir, 'level1s')
    pathlib.Path(level1_path).mkdir(parents=True, exist_ok=True)
    level1_file_str = os.path.join(level1_path, f'level1_{out_str}')
    level1.to_netcdf(path=level1_file_str)


if '__main__' == __name__:
    main_dir = '../'
    specs = {
             'instr_geometry': inst_str,
             }
    specs["noise_str"] = 'SNKp03RSV07_MVNKp04RSVnan'
    inst_file = 'lg_inst_3base_3AC20_35_120x_SNKp03RSV07_MVNKp04RSVnan.nc'
    compute_truth(main_dir, specs, inst_file, 'California', gmf=GMF_DEFAULT,
                  size_across=120, size_along=150)
