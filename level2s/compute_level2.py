import xarray as xr
import numpy as np
import seastar
from seastar.utils.tools import dotdict
from datetime import date

### INPUTS
## Instrument
#inst_file = 'inst_3sq29_3AC19_39_011x_SNKp03RSV05_MVNKp04RSV40.nc'
#inst_file = 'inst_2sq22_2AC15_35_011x_SNKp03RSV05.nc'
inst_file = 'inst_3base_3AC15_35_011x_SNKp03RSV07_MVNKp04RSVnan.nc'
inst_str = inst_file[5:10]
inst_path = '../instruments/' + inst_file

gmf={
    'nrcs': {'name': 'nscat4ds'},
    'doppler': {'name': 'mouche12'},
}

across_size=int(inst_file[20:23])
along_size=9 #100

### END for inputs


## Geo
#wdir_v = np.arange(0, 360, 15)
#wspd_v = 5 * np.ones_like(wdir_v)
#cvel_v = 0.6 * np.ones_like(wdir_v)
#cdir_v = 150 * np.ones_like(wdir_v)

wspd_v = np.array([2,3,4,5,6,7,8,10,12,15,18,21])
wdir_v = 0 * np.ones_like(wspd_v)
cvel_v = 0.6 * np.ones_like(wspd_v)
cdir_v = 150 * np.ones_like(wspd_v)


## Iteration
for ii, wdir in enumerate(wdir_v):
    #wdir = wdir_v[ii]
    wspd = wspd_v[ii]
    cvel = cvel_v[ii]
    cdir = cdir_v[ii]

    gmf_nrcs = gmf['nrcs']['name'].upper()
    gmf_doppler = gmf['doppler']['name'].upper()

    in_str = inst_file[5:24] + '{nb_along:03d}_'.format(nb_along=along_size)\
                + inst_file[25:-3] \
                + '_W{wspd:03.0f}_{wdir:03.0f}_C{cvel:03.1f}_{cdir:03.0f}'.format(
                    wspd=wspd, wdir=wdir,
                    cvel=cvel, cdir=cdir) \
                + '_{}_{}.nc'.format(gmf_nrcs[0]+gmf_nrcs[-3:],
                        gmf_doppler[0]+gmf_doppler[-2:])

    out_str_v = in_str[:-3] + '_v{today}.nc'.format(
                        today=date.today().strftime("%Y%m%d")
                        )

    level1_str = 'level1_' + in_str
    level1_path = '../level1s/' + level1_str

    level1 = xr.open_dataset(level1_path).load()

    noise = xr.Dataset()
    noise['Sigma0'] = level1['noise_Sigma0']
    noise['RSV'] = level1['noise_RSV']

    if __name__=='__main__':
        lmout = seastar.retrieval.level2.run_find_minima(level1, noise, gmf, serial=False)
        lmout.attrs = level1.attrs
        lmout.attrs['level1'] = level1_path

        level2_file_str = 'level2_' + out_str_v
        lmout.to_netcdf(path=level2_file_str)

