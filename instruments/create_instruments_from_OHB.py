import os
import xarray as xr
import numpy as np
from scipy import interpolate

def create_OHB_simple_inst(fpath: str, value_along=0, size_across=11):
    '''
    inst_ds: xr.Dataset with the following fields: [CentralFreq; IncidenceAngleImage (along, across, look)
    LookAzimuthImage (along, across, look), uncerty_Kp (along, across, look) uncerty_RSV (along, across, look)]
    '''

    inst_ds = xr.open_dataset(fpath)
    inst_ds.attrs['filepath'] = fpath
    inst_ds.attrs['filename'] = os.path.basename(fpath)

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

    return(simple_inst)

if '__main__' == __name__:
    input_dir = '/PROJETS/1474-FE_Ocean_Scatterometer_NG/REALISATION/Technique/DATA/instrument/OHB-geometry_v20250409'
    sacross = 10
    name = 'conical_configuration_1-1__1.9rpm'
    fpath = os.path.join(input_dir, name, name + '.nc')
    si = create_OHB_simple_inst(fpath, size_across=sacross)


