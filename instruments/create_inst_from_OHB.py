import os
import pathlib
import xarray as xr
import numpy as np

def create_OHB_simple_inst(fpath: str, value_along=0, size_across=11, write_nc=False, main_path='.'):
    '''
    inst_ds: xr.Dataset with the following fields: [CentralFreq; IncidenceAngleImage (along, across, look)
    LookAzimuthImage (along, across, look), uncerty_Kp (along, across, look) uncerty_RSV (along, across, look)]
    '''

    inst_ds = xr.open_dataset(fpath)
    inst_ds.attrs['filepath'] = fpath
    inst_ds.attrs['filename'] = os.path.basename(fpath)[:-3]
    inst_ds = inst_ds.set_coords('CentralFreq') 

    index_across = list(np.floor(np.linspace(0,inst_ds.across.size-1,size_across)).astype(int))
    # select only one value along, and a limited amount of values across
    simple_inst = inst_ds.sel(along=value_along, method='nearest').isel(across=index_across)

    simple_inst = simple_inst.rename({
        'look':'Antenna', 
        'LookAzimuthImage':'AntennaAzimuthImage'
        })

    if 'Polarization' not in simple_inst.data_vars:
        simple_inst['Polarization'] = (
            simple_inst.IncidenceAngleImage.dims,
            np.full(simple_inst.IncidenceAngleImage.shape, 'VV')
        )

    inst_file_str = f"inst_{simple_inst.across.size:03d}_{inst_ds.attrs['filename']}.nc"
    if 'filename' in simple_inst.attrs:
        simple_inst.attrs['history'] = simple_inst.attrs['filename']
        simple_inst.attrs['filename'] = inst_file_str[-3]
    if write_nc:
        inst_path = os.path.join(main_path, 'inst')
        pathlib.Path(inst_path).mkdir(parents=True, exist_ok=True)
        inst_file_path = os.path.join(inst_path, inst_file_str)
        simple_inst.to_netcdf(path=inst_file_path)

    return(simple_inst)

if '__main__' == __name__:
    input_dir = '/PROJETS/1474-FE_Ocean_Scatterometer_NG/REALISATION/Technique/DATA/instrument/OHB-geometry_v20250409'
    sacross = 10
    name = 'conical_configuration_1-1__1.9rpm'
    fpath = os.path.join(input_dir, name, name + '.nc')
    si = create_OHB_simple_inst(fpath, size_across=sacross)


