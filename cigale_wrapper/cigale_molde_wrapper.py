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
import pickle
from scipy.constants import c as speed_of_light_mps
import itertools

from astropy.table import Table, vstack
from cigale_wrapper import CigaleHelper
from werkzeugkiste import helper_func


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
        CigaleHelper.replace_params_in_file(param_dict=cigale_init_params)
        # configurate pcigale
        os.system('pcigale genconf')

        # set module configurations
        for module_str in sed_module_conf_dict.keys():
            print(module_str)
            CigaleHelper.replace_params_in_file(param_dict=sed_module_conf_dict[module_str])

        output_band_list_str = CigaleHelper.create_output_band_list_str(output_band_dict=output_band_dict)
        analysis_params = {'bands': output_band_list_str, 'save_sed': save_sed}
        CigaleHelper.replace_params_in_file(param_dict=analysis_params)

        # run pcigale
        os.system('pcigale run')
        # delete old models
        if delete_old_models:
            os.system('rm -rf *_out')

    @staticmethod
    def sim_cigale_model(sed_module_conf_dict, sed_param_list, output_band_dict, n_cores=1,
                         data_output_path='', file_name=None,

                         save_output_param_table=True, save_output_sed=True,
                         delete_old_models=True,
                         obj_mstar_msun=1, obj_dist_mpc=1

                         ):
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
        save_output_param_table : bool
        save_output_sed : bool
        delete_old_models : bool

        Return
        ------
        model_table : ``astropy.table.Table``
        """
        # simulate_data
        CigaleModelWrapper.run_sim_cigale_model(sed_module_conf_dict=sed_module_conf_dict, n_cores=n_cores,
                                                output_band_dict=output_band_dict, delete_old_models=delete_old_models,
                                                save_sed=save_output_sed,
                                                )
        # load cigale param table
        model_table = CigaleModelWrapper.get_cigale_model_param_table(sed_param_list=sed_param_list,
                                                                      output_band_dict=output_band_dict,
                                                                      obj_mstar_msun=obj_mstar_msun,
                                                                      obj_dist_mpc=obj_dist_mpc)
        # load cigale seds
        if save_output_sed:
            model_sed_dict = CigaleModelWrapper.get_sim_cigale_model_sed_dict(model_param_table=model_table,
                                                                          obj_mstar_msun=obj_mstar_msun,
                                                                           obj_dist_mpc=obj_dist_mpc)
        else:
            model_sed_dict = None

        # save param table if wanted
        if save_output_param_table & (file_name is not None):
            file_path_model_param_table = CigaleModelWrapper.get_file_path_names(
            data_output_path=data_output_path, file_name=file_name, file_type='param_table', suffix='fits')
            if not os.path.isdir(Path(data_output_path)): os.makedirs(Path(data_output_path))
            model_table.write(file_path_model_param_table, overwrite=True)

        # save sed dict if wanted
        if save_output_sed & (file_name is not None) & (model_sed_dict is not None):
            file_path_sed_dict = CigaleModelWrapper.get_file_path_names(
            data_output_path=data_output_path, file_name=file_name, file_type='sed_dict', suffix='pickle')
            if not os.path.isdir(Path(data_output_path)): os.makedirs(Path(data_output_path))
            with open(file_path_sed_dict, 'wb') as pickle_file:
                pickle.dump(model_sed_dict, pickle_file)

        return model_table, model_sed_dict

    @staticmethod
    def get_cigale_model_param_table(sed_param_list, output_band_dict, model_block_file_name='out/models-block-0.fits',
                                     rescale_bands=True,
                                     obj_mstar_msun=1, obj_dist_mpc=1):
        """
        load cigale model blocks output and return only needed columns
        Parameters
        ----------
        sed_param_list : list
        output_band_dict : dict
        model_block_file_name : str
        rescale_bands : bool
        obj_mstar_msun : float
        obj_dist_mpc : float

        Return
        ------
        model_table : ``astropy.table.Table``
        """
        # load the model block table
        model_block_table = Table.read(model_block_file_name)
        # get all the parameters needed
        band_list = CigaleHelper.create_output_band_list_str(output_band_dict=output_band_dict)
        # get only those parameters and bands needed
        model_table = model_block_table[sed_param_list]

        # only rescale if a stellar module is present
        if rescale_bands:
            if 'stellar.m_star' in list(model_table.keys()):
                flux_rescale_fact = CigaleModelWrapper.get_cigale_band_flux_rescale_fact(
                    model_table=model_block_table, obj_mstar_msun=obj_mstar_msun, obj_dist_mpc=obj_dist_mpc)
                # add al band model fluxes and rescale them to mass and distance
                for band in band_list:
                    model_table.add_column(model_block_table[band] * flux_rescale_fact, name=band, index=-1)
            else:
                for band in band_list:
                    model_table.add_column(model_block_table[band], name=band, index=-1)
        return model_table

    @staticmethod
    def get_sim_cigale_model_sed_dict(model_param_table, obj_mstar_msun, obj_dist_mpc):
        """
        load cigale model blocks output and return only needed columns
        Parameters
        ----------


        Return
        ------
        model_table : ``astropy.table.Table``
        """
        # get model table with all columns which are wanted
        #
        sed_dict = {}
        for sed_idx in range(len(model_param_table)):
            model_sim_mass = np.array(model_param_table['stellar.m_star'][sed_idx]) * u.M_sun
            wave_nm, flux_mjy = CigaleModelWrapper.load_sim_cigale_model_sed(
                obj_mstar_msun=obj_mstar_msun, obj_dist_mpc=obj_dist_mpc, model_sed_name='out/%i_best_model.fits' % sed_idx,
            model_sim_mass=model_sim_mass)
            wave_mu = wave_nm.to(u.um)
            sed_dict.update({sed_idx: {'wave_mu': wave_mu, 'flux_mjy': flux_mjy}})
        return sed_dict

    @staticmethod
    def get_file_path_names(data_output_path, file_name, file_type='param_table', suffix='fits'):
        """
        Fuction to return the file path of the model parameter table or the sed dict
        Parameters
        ----------
        data_output_path : str
        file_name : str
        file_type : str

        Return
        ------
        file_path : ``pathlib.Path``
        """
        assert file_type in ['param_table', 'sed_dict', 'fit_summary_dict']

        return (
            helper_func.FileTools.verify_suffix(file_name=Path(data_output_path) / (file_name + '_' + file_type),
                                                suffix=suffix))

    @staticmethod
    def quick_access_sim_cigale_model(sed_module_conf_dict, sed_param_list, output_band_dict,
                                      n_cores=1, data_output_path='', file_name=None,
                                                               obj_mstar_msun=1, obj_dist_mpc=1,

                                      compute_sed=False,
                                      save_output_param_table=True, save_output_sed=False,

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
        save_output_param_table : bool
        save_output_sed : bool
        delete_old_models : bool
        re_sim : bool

        Return
        ------
        model_table : ``astropy.table.Table``
        """
        file_path_model_param_table = CigaleModelWrapper.get_file_path_names(
            data_output_path=data_output_path, file_name=file_name, file_type='param_table', suffix='fits')
        file_path_sed_dict = CigaleModelWrapper.get_file_path_names(
            data_output_path=data_output_path, file_name=file_name, file_type='sed_dict', suffix='pickle')

        print('file_path ', file_path_model_param_table)
        print('file_path ', file_path_sed_dict)

        if compute_sed:
            # check if files already exist
            if os.path.isfile(file_path_model_param_table) & os.path.isfile(file_path_sed_dict) & (not re_sim):
                # both files already exist
                model_param_table = Table.read(file_path_model_param_table)

                with open(file_path_sed_dict, 'rb') as file:
                    model_sed_dict = pickle.load(file)

            else:
                model_param_table, model_sed_dict = CigaleModelWrapper.sim_cigale_model(
                sed_module_conf_dict=sed_module_conf_dict, sed_param_list=sed_param_list,
                                                              output_band_dict=output_band_dict, n_cores=n_cores,
                                                              data_output_path=data_output_path, file_name=file_name,
                                                        save_output_param_table=save_output_param_table,
                                                        save_output_sed=save_output_sed,
                                                              delete_old_models=delete_old_models,
                obj_mstar_msun=obj_mstar_msun, obj_dist_mpc=obj_dist_mpc)
        else:
            # check if files already exist
            if os.path.isfile(file_path_model_param_table) & (not re_sim):
                # both files already exist
                model_param_table = Table.read(file_path_model_param_table)
                model_sed_dict = None
            else:
                model_param_table, model_sed_dict = CigaleModelWrapper.sim_cigale_model(
                sed_module_conf_dict=sed_module_conf_dict, sed_param_list=sed_param_list,
                                                              output_band_dict=output_band_dict, n_cores=n_cores,
                                                              data_output_path=data_output_path, file_name=file_name,
                                                        save_output_param_table=save_output_param_table,
                                                        save_output_sed=save_output_sed,
                                                              delete_old_models=delete_old_models,
                obj_mstar_msun=obj_mstar_msun, obj_dist_mpc=obj_dist_mpc)

        return model_param_table, model_sed_dict

    @staticmethod
    def load_sim_cigale_model_sed(obj_mstar_msun, obj_dist_mpc, model_sim_mass, model_sed_name='out/0_best_model.fits'):
        """
        load cigale model blocks output and return only needed columns
        Parameters
        ----------
        obj_mstar_msun : float
        obj_dist_mpc : float
        model_sed_name : str

        Return
        ------
        model_table : ``astropy.table.Table``
        """

        obj_dist_mpc *= u.Mpc
        obj_mstar_msun *= u.M_sun
        # read in the invidual model/sed
        mod = fits.open(model_sed_name)[1].data

        # get wavelengths in nanometer
        wave_nm = mod['wavelength'] * u.nm

        # frequencies of the wavelengths
        freq = (const.c.to(u.nm / u.s) / wave_nm).to(u.Hz)

        # get Luminosity in W / nm units
        L_WnmMsun = mod['L_lambda_total'] * u.W / u.nm

        # convert Luminosity to W/Msun
        L_WMsun = L_WnmMsun * wave_nm

        # scale the Luminosity to the chosen star cluster mass
        L_W = L_WMsun * obj_mstar_msun / model_sim_mass

        # convert distance from Mpc to meters
        distance_m = obj_dist_mpc.to(u.m)

        # convert luminsoity to Flux [W/m2]
        flux_Wm2 = L_W / (4 * np.pi * distance_m ** 2)

        # Convert that Flux to Flux density in Jy
        Fnu_Jy = (flux_Wm2 / freq).to(u.Jy)
        # convert to mJy
        Fnu_mJy = Fnu_Jy.to(u.mJy)

        return wave_nm, Fnu_mJy

    @staticmethod
    def get_cigale_band_flux_rescale_fact(model_table, obj_mstar_msun, obj_dist_mpc):

        sim_dist = np.array(model_table['universe.luminosity_distance']) * u.m
        sim_mstar = np.array(model_table['stellar.m_star']) * u.M_sun

        mass_scale_factor = (obj_mstar_msun * u.M_sun) / sim_mstar
        dist_scale_factor = sim_dist ** 2 / (((obj_dist_mpc * u.Mpc).to(u.m))**2)

        return mass_scale_factor * dist_scale_factor

    @staticmethod
    def create_cigale_flux_file(file_path, band_list, obs_list, instrument_list, flux_table, dist, snr=3, scale_lim=3,
                                name_list=None, redshift_list=None, return_flux_dict=True):


        n_rows = len(flux_table)

        if name_list is None:
            name_list = np.arange(start=0,  stop=len(flux_table)+1)
        if redshift_list is None:
            redshift_list = [0.0] * n_rows
        # if dist is just 1
        if (isinstance(dist, float) | isinstance(dist, int)) & (n_rows > 1):
            dist_list = [dist] * n_rows
        elif isinstance(dist, list) | isinstance(dist, np.ndarray):
            dist_list = dist
        else:
            dist_list = [dist]


        # get cigale band list
        cigale_band_name_list = CigaleHelper.get_filter_name_list(band_list=band_list, obs_list=obs_list,
                                                                                instrument_list=instrument_list,
                                                                                include_err=False)
        # create flux file
        flux_file = open(file_path, "w")
        # add header for all variables
        flux_file.writelines("# id             redshift  distance   ")
        for band_name in cigale_band_name_list:
            flux_file.writelines(band_name + "   ")
            flux_file.writelines(band_name + "_err" + "   ")
        flux_file.writelines(" \n")

        flux_dict = {}
        # fill flux file
        for row_idx, name, redshift, dist in zip(range(n_rows), name_list, redshift_list, dist_list):
            flux_dict.update({name: {
                'redshift': redshift,
                'dist': dist,
                'band_list': band_list,
                'obs_list': obs_list,
                'instrument_list': instrument_list,
            }})
            flux_file.writelines(" %s   %f   %f  " % (name, redshift, dist))

            for band_idx, band in enumerate(band_list):
                flux = flux_table[row_idx]['%s_flux' % band_list[band_idx]]
                flux_err = flux_table[row_idx]['%s_flux_err' % band_list[band_idx]]
                if flux > 0:
                    if (flux / flux_err) > snr:
                        flux_dict[name].update({'%s_flux' % band: flux, '%s_flux_err' % band: flux_err,
                                                 '%s_lim_flag' % band: False, '%s_neg_flux_flag' % band: False})
                        flux_file.writelines("%.15f   " % flux)
                        flux_file.writelines("%.15f   " % flux_err)
                    else:
                        flux_dict[name].update({'%s_flux' % band: flux * scale_lim, '%s_flux_err' % band: flux_err,
                                                '%s_lim_flag' % band: True, '%s_neg_flux_flag' % band: False})
                        flux_file.writelines("%.15f   " % (flux_err * scale_lim))
                        flux_file.writelines("%.15f   " % (-flux_err))
                else:
                    flux_dict[name].update({'%s_flux' % band: flux_err * scale_lim, '%s_flux_err' % band: flux_err,
                                             '%s_lim_flag' % band: True, '%s_neg_flux_flag' % band: True})
                    flux_file.writelines("%.15f   " % (flux_err * scale_lim))
                    flux_file.writelines("%.15f   " % (-flux_err))

            flux_file.writelines(" \n")

        flux_file.close()
        if return_flux_dict:
            return flux_dict

    @staticmethod
    def get_best_fit_cigale_model_param_table(sed_param_list, output_band_dict,
                                              model_block_file_name='out/results.fits'):
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

        # load the model block table
        model_block_table = Table.read(model_block_file_name)

        # get all the parameters needed
        band_list = CigaleHelper.create_output_band_list_str(output_band_dict=output_band_dict)

        sed_param_list_best_fit = ['best.' + item for item in sed_param_list]
        sed_param_list_bayes_fit = ['bayes.' + item for item in sed_param_list]
        sed_param_list_bayes_fit.remove('bayes.reduced_chi_square')
        sed_param_list_bayes_fit.remove('bayes.chi_square')

        model_table = model_block_table[['id'] + sed_param_list_best_fit + sed_param_list_bayes_fit]

        for band in band_list:
            model_table.add_column(model_block_table['best.' + band], name='best.' + band, index=-1)
            model_table.add_column(model_block_table['bayes.' + band], name='bayes.' + band, index=-1)

        return model_table

    @staticmethod
    def load_cigale_best_fit_sed(lum_dist_m, model_sed_name='out/0_best_model.fits'):
        """
        load cigale model blocks output and return only needed columns
        Parameters
        ----------
        lum_dist_m : float
        model_sed_name : str

        Return
        ------
        model_table : dict
        """

        sed = fits.open(model_sed_name)[1].data

        wave = sed['wavelength'] * u.nm
        best_fit_flux = sed['Fnu'] * u.mJy
        sed_dict = {'wave': wave, 'best_fit_flux': best_fit_flux}

        # add stellar continuum
        if 'stellar.young' in sed.names:
            # the stellar continuum is given in luminosity
            stellar_unattenuated_lum = (sed['stellar.young'] + sed['stellar.old']) * u.W / u.nm
            # the attenuation is additive to the unattenuated spectrum
            stellar_attenuation_lum = (sed['attenuation.stellar.young'] + sed['attenuation.stellar.old']) * u.W / u.nm
            # add absorption to the stellar spectrum
            if 'nebular.absorption_young' in sed.names:
                stellar_attenuation_lum += (sed['nebular.absorption_young'] +
                                            sed['nebular.absorption_old']) * u.W / u.nm
            conv_fact_lum2flux = wave**2 / (speed_of_light_mps * u.m / u.s) / (4.0 * np.pi * (lum_dist_m * u.m) ** 2)
            stellar_unattenuated_flux = (stellar_unattenuated_lum * conv_fact_lum2flux).to(u.mJy)
            stellar_attenuated_flux = ((stellar_unattenuated_lum + stellar_attenuation_lum) * conv_fact_lum2flux).to(u.mJy)
            sed_dict.update({
                'stellar_unattenuated_flux': stellar_unattenuated_flux,
                'stellar_attenuated_flux': stellar_attenuated_flux
            })

        if 'nebular.emission_young' in sed.names:
            # the stellar continuum is given in luminosity
            nebular_unattenuated_lum = (sed['nebular.emission_young'] + sed['nebular.emission_old']) * u.W / u.nm
            # the attenuation is additive to the unattenuated spectrum
            nebular_attenuation_lum = (sed['attenuation.nebular.emission_young'] +
                                       sed['attenuation.nebular.emission_old']) * u.W / u.nm
            conv_fact_lum2flux = wave**2 / (speed_of_light_mps * u.m / u.s) / (4.0 * np.pi * (lum_dist_m * u.m) ** 2)
            nebular_unattenuated_flux = (nebular_unattenuated_lum * conv_fact_lum2flux).to(u.mJy)
            nebular_attenuated_flux = ((nebular_unattenuated_lum + nebular_attenuation_lum) *
                                       conv_fact_lum2flux).to(u.mJy)
            sed_dict.update({
                'nebular_unattenuated_flux': nebular_unattenuated_flux,
                'nebular_attenuated_flux': nebular_attenuated_flux
            })



        if 'dust.Umin_Umin' in sed.names:
            # the stellar continuum is given in luminosity
            dust_lum = (sed['dust.Umin_Umin'] + sed['dust.Umin_Umax']) * u.W / u.nm
            # the attenuation is additive to the unattenuated spectrum
            conv_fact_lum2flux = wave**2 / (speed_of_light_mps * u.m / u.s) / (4.0 * np.pi * (lum_dist_m * u.m) ** 2)
            dust_flux = (dust_lum * conv_fact_lum2flux).to(u.mJy)
            sed_dict.update({
                'dust_flux': dust_flux,
            })



        # plt.plot(wave, best_fit_flux)
        # plt.plot(wave, stellar_unattenuated_flux)
        # plt.plot(wave, stellar_attenuated_flux)
        # plt.xscale('log')
        # plt.yscale('log')
        # plt.show()
        # exit()

        return sed_dict

    @staticmethod
    def get_cigale_best_fit_sed_dict(model_param_table):
        """
        load cigale model blocks output and return only needed columns
        Parameters
        ----------


        Return
        ------
        model_table : dict
        """
        # get model table with all columns which are wanted
        #
        sed_dict_all_fits = {}

        for sed_idx in range(len(model_param_table)):
            sed_dict = CigaleModelWrapper.load_cigale_best_fit_sed(
                lum_dist_m=model_param_table['best.universe.luminosity_distance'][sed_idx],
                model_sed_name='out/%i_best_model.fits' % sed_idx)

            sed_dict_all_fits.update({sed_idx: sed_dict})
        return sed_dict_all_fits

    @staticmethod
    def load_cigale_param_pdf(fit_name, param_comb_list):
        hdu_chi2_block = fits.open('out/%s_chi2-block-0.fits' % fit_name)
        chi2_value_grid = np.array(hdu_chi2_block[1].data, dtype=float)

        pdf_param_dict = {}
        for param_tuple in param_comb_list:
            print(param_tuple)
            hdu_param_1 = fits.open('out/%s_%s-block-0.fits' % (fit_name, param_tuple[0]))
            hdu_param_2 = fits.open('out/%s_%s-block-0.fits' % (fit_name, param_tuple[1]))
            param_grid_1 = np.array(hdu_param_1[1].data, dtype=float)
            param_grid_2 = np.array(hdu_param_2[1].data, dtype=float)

            unique_values_param_1 = np.unique(param_grid_1)
            unique_values_param_2 = np.unique(param_grid_2)

            # individual pdf distributions
            if param_tuple[0] not in pdf_param_dict:
                chi2_value_param_1 = np.zeros(len(unique_values_param_1)) * np.nan
                for idx_param_1 in range(len(unique_values_param_1)):
                    mask_selected_values = param_grid_1 == unique_values_param_1[idx_param_1]
                    chi2_value_param_1[idx_param_1] = np.nanmin(chi2_value_grid[mask_selected_values])
                pdf_param_dict.update({str(param_tuple[0]): chi2_value_param_1,
                                       '%s_values' % param_tuple[0]: unique_values_param_1})

            if param_tuple[1] not in pdf_param_dict:
                chi2_value_param_2 = np.zeros(len(unique_values_param_2)) * np.nan
                for idx_param_2 in range(len(unique_values_param_2)):
                    mask_selected_values = param_grid_2 == unique_values_param_2[idx_param_2]
                    chi2_value_param_2[idx_param_2] = np.nanmin(chi2_value_grid[mask_selected_values])
                pdf_param_dict.update({str(param_tuple[1]): chi2_value_param_2,
                                       '%s_values' % param_tuple[1]: unique_values_param_2})

            # combination of both params
            chi2_value_param_1_param_2 = np.zeros((len(unique_values_param_1), len(unique_values_param_2))) * np.nan
            for idx_param_1 in range(len(unique_values_param_1)):
                for idx_param_2 in range(len(unique_values_param_2)):
                    mask_selected_values = ((param_grid_1 == unique_values_param_1[idx_param_1]) &
                                            (param_grid_2 == unique_values_param_2[idx_param_2]))
                    # if sum(mask_selected_values) > 0:
                    chi2_value_param_1_param_2[idx_param_1, idx_param_2] = (
                        np.nanmin(chi2_value_grid[mask_selected_values]))
            pdf_param_dict.update({'%s_%s' % (param_tuple[0], param_tuple[1]): chi2_value_param_1_param_2})

        return pdf_param_dict

    @staticmethod
    def get_cigale_param_pdf_dict(model_param_table, param_comb_list):

        pdf_param_dict_all = {}
        for sed_idx in range(len(model_param_table)):
            pdf_param_dict = CigaleModelWrapper.load_cigale_param_pdf(fit_name=sed_idx, param_comb_list=param_comb_list)

            pdf_param_dict_all.update({sed_idx: pdf_param_dict})
        return pdf_param_dict_all

    @staticmethod
    def run_cigale_fit(sed_module_conf_dict, flux_file_name, output_band_dict, n_cores=1, save_best_sed=True,
                       delete_old_models=False, n_decimals_redshift=2, save_chi2='none'):
        """
        Function to simulate CIGALE models
        Parameters
        ----------
        sed_module_conf_dict : dict
        flux_file_name : str or pathlib.Path
        n_cores : int
        output_band_dict : dict
        save_best_sed : bool
        delete_old_models : bool
        n_decimals_redshift : int
        save_chi2 : str

        """
        # get all the sed modules
        sed_module_list = list(sed_module_conf_dict.keys())

        cigale_init_params = {
            'data_file': flux_file_name,
            'sed_modules': sed_module_list,
            'analysis_method': 'pdf_analysis',
            'cores': n_cores,
        }
        # initiate pcigale
        os.system('pcigale init')

        # set initial parameters
        CigaleHelper.replace_params_in_file(param_dict=cigale_init_params)


        # configurate pcigale
        os.system('pcigale genconf')

        # set module configurations
        for module_str in sed_module_conf_dict.keys():
            print(module_str)
            CigaleHelper.replace_params_in_file(param_dict=sed_module_conf_dict[module_str])

        output_band_list_str = CigaleHelper.create_output_band_list_str(output_band_dict=output_band_dict,
                                                                                      include_err=True)
        analysis_params = {'bands': output_band_list_str, 'save_best_sed': save_best_sed,
                           'lim_flag': 'noscaling', 'save_chi2': save_chi2}
        CigaleHelper.replace_params_in_file(param_dict=analysis_params)

        # We need to replace the redshift keyword with redshift_decimals in the analysis_params
        # this might chance in the future

        CigaleHelper.replace_redshift_digits_name_in_file(n_decimals_redshift=n_decimals_redshift)

        # run pcigale
        os.system('pcigale run')
        # delete old models
        if delete_old_models:
            os.system('rm -rf *_out')

    @staticmethod
    def fit_cigale_model2data(
            sed_module_conf_dict, flux_file_name, sed_param_list, output_band_dict, n_cores=1, save_best_sed=True,
            n_decimals_redshift=2, save_output_sed=True, save_param_correl=False, param_correl_list=None,

            delete_old_models=False):
        """
        Function to fit CIGALe models to observational data

        Parameters
        ----------
        sed_module_conf_dict : dict
        sed_param_list : list
        output_band_dict : dict
        n_cores : int
        save_output_sed : bool
        delete_old_models : bool

        Return
        ------
        model_table : ``astropy.table.Table``
        """
        if save_param_correl:
            save_chi2 = 'properties'
        else:
            save_chi2 = 'none'

        # fit data
        CigaleModelWrapper.run_cigale_fit(
            sed_module_conf_dict=sed_module_conf_dict, flux_file_name=flux_file_name, n_cores=n_cores,
            output_band_dict=output_band_dict, save_best_sed=save_best_sed, delete_old_models=delete_old_models,
            n_decimals_redshift=n_decimals_redshift, save_chi2=save_chi2)

        # load cigale param table
        model_table = CigaleModelWrapper.get_best_fit_cigale_model_param_table(sed_param_list=sed_param_list,
                                                                               output_band_dict=output_band_dict)

        fit_summary_dict = {
            'model_table': model_table,
            'sed_module_conf_dict': sed_module_conf_dict,
            'output_band_dict': output_band_dict,
        }
        # load cigale seds
        if save_output_sed:
            sed_dict_all_fits = CigaleModelWrapper.get_cigale_best_fit_sed_dict(model_param_table=model_table)
            fit_summary_dict.update({'sed_dict_all_fits': sed_dict_all_fits})

        # load chi2 values and create correlated maps
        if save_param_correl:
            if param_correl_list is None:
                param_correl_list = sed_param_list
            grid_param_values = param_correl_list.copy()
            grid_param_values.remove('chi_square')
            grid_param_values.remove('reduced_chi_square')
            grid_param_values.remove('stellar.m_star')
            if 'dust.umean' in grid_param_values:
                grid_param_values.remove('dust.umean')

            param_comb_list = list(itertools.combinations(grid_param_values, 2))
            pdf_param_dict_all = (
                CigaleModelWrapper.get_cigale_param_pdf_dict(model_param_table=model_table,
                                                             param_comb_list=param_comb_list))
            fit_summary_dict.update({'pdf_param_dict_all': pdf_param_dict_all})

        return fit_summary_dict

        # print(pdf_param_dict_all)
        #
        # plt.imshow(np.log10(pdf_param_dict_all[0]['attenuation.A550_sfh.age']), origin='lower',
        #            extent=(np.min(pdf_param_dict_all[0]['attenuation.A550_values']),
        #                    np.max(pdf_param_dict_all[0]['attenuation.A550_values']),
        #                    np.min(pdf_param_dict_all[0]['sfh.age_values']),
        #                    np.max(pdf_param_dict_all[0]['sfh.age_values'])),
        #            aspect='auto')
        #
        # plt.show()
        exit()


        # save param table if wanted
        if save_output_param_table & (file_name is not None):
            file_path_model_param_table = CigaleModelWrapper.get_file_path_names(
            data_output_path=data_output_path, file_name=file_name, file_type='param_table', suffix='fits')
            if not os.path.isdir(Path(data_output_path)): os.makedirs(Path(data_output_path))
            model_table.write(file_path_model_param_table, overwrite=True)

        # save sed dict if wanted
        if save_output_sed & (file_name is not None) & (model_sed_dict is not None):
            file_path_sed_dict = CigaleModelWrapper.get_file_path_names(
            data_output_path=data_output_path, file_name=file_name, file_type='sed_dict', suffix='pickle')
            if not os.path.isdir(Path(data_output_path)): os.makedirs(Path(data_output_path))
            with open(file_path_sed_dict, 'wb') as pickle_file:
                pickle.dump(model_sed_dict, pickle_file)

        return model_table, model_sed_dict

    @staticmethod
    def quick_access_fit_cigale_model2data(
            sed_module_conf_dict, flux_file_name, sed_param_list, output_band_dict, n_cores=1, save_best_sed=True,
            n_decimals_redshift=2, save_output_sed=False, save_param_correl=False, param_correl_list=None,
            data_output_path='', file_name=None, delete_old_models=True, re_sim=False):
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
        save_output_param_table : bool
        save_output_sed : bool
        delete_old_models : bool
        re_sim : bool

        Return
        ------
        model_table : ``astropy.table.Table``
        """

        file_path_fit_summary_dict = CigaleModelWrapper.get_file_path_names(
            data_output_path=data_output_path, file_name=file_name, file_type='fit_summary_dict', suffix='pickle')

        print('file_path_fit_summary_dict ', file_path_fit_summary_dict)

        if os.path.isfile(file_path_fit_summary_dict) & (not re_sim):
            with open(file_path_fit_summary_dict, 'rb') as file:
                fit_summary_dict = pickle.load(file)
        else:
            fit_summary_dict = CigaleModelWrapper.fit_cigale_model2data(
                sed_module_conf_dict=sed_module_conf_dict, flux_file_name=flux_file_name, sed_param_list=sed_param_list,
                output_band_dict=output_band_dict, n_cores=n_cores, save_best_sed=save_best_sed,
                n_decimals_redshift=n_decimals_redshift, save_output_sed=save_output_sed,
                save_param_correl=save_param_correl, param_correl_list=param_correl_list,
                delete_old_models=delete_old_models)

            with open(file_path_fit_summary_dict, 'wb') as pickle_file:
                pickle.dump(fit_summary_dict, pickle_file)

        return fit_summary_dict



