"""
Cigale model wrapper main script
"""
import os
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.io import fits
import astropy.constants as const

from astropy.table import Table
from cigale_wrapper import cigale_helper
from phangs_data_access import helper_func


class CigaleModelWrapper:
    """
    This class is made to wrap around the CIGALE SED fitting software.
    Here two modes are of major important: 1) simulating SED models 2) fitting SEd models to observations
    """
    def __init__(self):

        # attributes to load cigale results
        self.model_table = None
        self.model_table_dict = None

    @staticmethod
    def run_sim_cigale_model(sed_module_conf_dict, n_cores=1, output_band_dict=None, save_sed=False,
                             delete_old_models=True):
        """
        Function to simulate CIGALE models
        Parameters
        ----------
        sed_module_conf_dict : dict
        n_cores : int
        output_band_dict : dict
        save_sed : bool
        delete_old_models : bool

        """
        # get all the sed modules
        sed_module_list = list(sed_module_conf_dict.keys())
        cigale_init_params = {
            'sed_modules': sed_module_list,
            'analysis_method': 'savefluxes',
            'cores': n_cores,
        }
        # initiate pcigale
        os.system('pcigale init')
        # set initial parameters
        cigale_helper.CigaleHelper.replace_params_in_file(param_dict=cigale_init_params)
        # configurate pcigale
        os.system('pcigale genconf')
        # set module configurations
        for module_str in sed_module_conf_dict.keys():
            print(module_str)
            cigale_helper.CigaleHelper.replace_params_in_file(param_dict=sed_module_conf_dict[module_str])

        output_band_list_str = cigale_helper.CigaleHelper.create_output_band_list_str(output_band_dict=output_band_dict)
        analysis_params = {'bands': output_band_list_str, 'save_sed': save_sed}
        cigale_helper.CigaleHelper.replace_params_in_file(param_dict=analysis_params)

        # run pcigale
        os.system('pcigale run')
        # delete old models
        if delete_old_models:
            os.system('rm -rf *_out')

    @staticmethod
    def sim_cigale_model_params(sed_module_conf_dict, sed_param_list, output_band_dict, n_cores=1,
                                data_output_path='', file_name=None, save_output=True,
                                delete_old_models=True):
        """
        Function to simulate CIGALE models for a specific set of parameters and access the output
        Parameters
        ----------
        sed_module_conf_dict : dict
        sed_param_list : list
        output_band_dict : dict
        n_cores : int
        data_output_path : str
        file_name : str
        save_output : bool
        delete_old_models : bool

        Return
        ------
        model_table : ``astropy.table.Table``
        """
        # simulate_data
        CigaleModelWrapper.run_sim_cigale_model(sed_module_conf_dict=sed_module_conf_dict, n_cores=n_cores,
                                                output_band_dict=output_band_dict, delete_old_models=delete_old_models)
        # load cigale output
        model_table = CigaleModelWrapper.load_cigale_model_params(sed_param_list=sed_param_list,
                                                                  output_band_dict=output_band_dict)
        # save table if wanted
        if save_output & (file_name is not None):
            file_path = helper_func.FileTools.verify_suffix(file_name=Path(data_output_path) / file_name, suffix='fits')
            if not os.path.isdir(Path(data_output_path)):
                os.makedirs(Path(data_output_path))
            model_table.write(file_path, overwrite=True)

        return model_table

    @staticmethod
    def load_cigale_model_params(sed_param_list, output_band_dict, model_block_file_name='out/models-block-0.fits'):
        """
        load cigale model blocks output and return only needed columns
        Parameters
        ----------
        sed_param_list : list
        output_band_dict : dict
        model_block_file_name : str

        Return
        ------
        model_table : ``astropy.table.Table``
        """
        # get model table with all columns which are wanted
        model_table = Table.read(model_block_file_name)
        param_list = cigale_helper.CigaleHelper.create_output_band_list_str(output_band_dict=output_band_dict)
        param_list += sed_param_list
        return model_table[param_list]

    @staticmethod
    def quick_access_sim_cigale_model_params(sed_module_conf_dict, sed_param_list, output_band_dict, n_cores=1,
                                             data_output_path='', file_name=None, save_output=True,
                                             delete_old_models=True, re_sim=False):
        """
        Function to quickly access CIGALE model simulation based on a given file name.
        Parameters
        ----------
        sed_module_conf_dict : dict
        sed_param_list : list
        output_band_dict : dict
        n_cores : int
        data_output_path : str
        file_name : str
        save_output : bool
        delete_old_models : bool
        re_sim : bool

        Return
        ------
        model_table : ``astropy.table.Table``
        """
        file_path = helper_func.FileTools.verify_suffix(file_name=Path(data_output_path) / file_name, suffix='fits')
        if (not os.path.isfile(file_path)) | re_sim:
            return CigaleModelWrapper.sim_cigale_model_params(sed_module_conf_dict=sed_module_conf_dict,
                                                              sed_param_list=sed_param_list,
                                                              output_band_dict=output_band_dict, n_cores=n_cores,
                                                              data_output_path=data_output_path, file_name=file_name,
                                                              save_output=save_output,
                                                              delete_old_models=delete_old_models)
        else:
            return Table.read(file_path)

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # !!!!!!! TO DO: add option to fit data points with CIGALE !!!!!!!
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def create_cigale_flux_file(self, file_path, band_list, aperture_dict_list, snr=3, name_list=None,
                                redshift_list=None, dist_list=None):

        if isinstance(aperture_dict_list, dict):
            aperture_dict_list = [aperture_dict_list]

        if name_list is None:
            name_list = np.arange(start=0,  stop=len(aperture_dict_list)+1)
        if redshift_list is None:
            redshift_list = [0.0] * len(aperture_dict_list)
        if dist_list is None:
            dist_list = [self.dist_dict[self.target_name]['dist']] * len(aperture_dict_list)

        name_list = np.array(name_list, dtype=str)
        redshift_list = np.array(redshift_list)
        dist_list = np.array(dist_list)


        # create flux file
        flux_file = open(file_path, "w")
        # add header for all variables
        band_name_list = self.compute_cigale_band_name_list(band_list=band_list)
        flux_file.writelines("# id             redshift  distance   ")
        for band_name in band_name_list:
            flux_file.writelines(band_name + "   ")
            flux_file.writelines(band_name + "_err" + "   ")
        flux_file.writelines(" \n")

        # fill flux file
        for name, redshift, dist, aperture_dict in zip(name_list, redshift_list, dist_list, aperture_dict_list):
            flux_file.writelines(" %s   %f   %f  " % (name, redshift, dist))
            flux_list, flux_err_list = self.compute_cigale_flux_list(band_list=band_list, aperture_dict=aperture_dict,
                                                                     snr=snr)
            for flux, flux_err in zip(flux_list, flux_err_list):
                flux_file.writelines("%.15f   " % flux)
                flux_file.writelines("%.15f   " % flux_err)
            flux_file.writelines(" \n")

        flux_file.close()




