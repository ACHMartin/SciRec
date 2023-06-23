import xarray as xr
import numpy as np
import seastar
import pathlib
import pickle
import os
import geo.create_geo_region as geo
import instruments.create_instruments_full_swath as instr
import truths.compute_truth_region as truth
import level2s.compute_level2_region as level2


GMF_DEFAULT = {'nrcs': {'name': 'nscat4ds'}, 'doppler': {'name': 'mouche12'}, }

if '__main__' == __name__:
    main_dir = '/home/lgaultier/src/SciRec'
    region = 'California'
    salong = 150
    sacross = 120
    specs = {'central_frequency': 13.5 * 10**9,
             'instr_geometry': '3base',
             'min_inc': 20,
             'max_inc':35,
             'Kp_sqt': 0.03,  # 3% (Mater v2-v4 3%)
             'RSV_sqt': 0.07,  # 7cm/s (Mater v4 5cm/s but push to 7cm/s after D8 in April 2023
             'Kp_midV': 0.04,  # 4% (Mater v2-v4: 4%)
             'Kp_midH': 0.04,  # 4%
             'RSV_midV': np.nan,  #np.nan  # cm/s (Mater v3: 40cm/s; v4 None)
             'RSV_midH': np.nan  # cm/s (Mater v3: 40cm/s; v4 None)
             }



    path_data = os.path.join(main_dir, f'{region}.pyo')



    with open(path_data, 'rb') as f:
         dic_m = pickle.load(f)

    geo.compute_geo(main_dir, dic_m, region, size_along=salong,
                    size_across=sacross)
    basename = 'lginstr'
    instr.compute_instrument(main_dir, specs, basename, size_across=sacross)
    inst_file_str, specs =  instr.build_filename(specs, basename, sacross)

    truth.compute_truth(main_dir, specs, inst_file_str, region, gmf=GMF_DEFAULT,
                        size_along=salong, size_across=sacross)
    level2.compute_level2(main_dir, specs, region, gmf=GMF_DEFAULT,
                          size_along=salong, size_across=sacross)

