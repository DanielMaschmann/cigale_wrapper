"""
Here we gather all functionality to visualize cigale outputs
"""
import numpy as np
import math
import astropy.units as u
import itertools
import matplotlib.pyplot as plt
plt.rc('text', usetex=True)


from werkzeugkiste import helper_func
from obszugang import ObsTools
from malkasten import plotting_tools
from cigale_wrapper import cigale_plotting_params, CigaleHelper


class CigaleVisualizer:
    """
    collection of function to visualize CIGALE simulations and fits
    """

    @staticmethod
    def visualize_cigale_sed_fit(flux_dict, fit_summary_dict, fit_id_name=None, sed_fit_plot_param_dict=None,
                                 display_parameter_list=None):


        # create figure
        fig = plt.figure(figsize=(30, 15))

        ax_sed = fig.add_axes((0.06, 0.25, 0.935, 0.745))
        ax_sed_residuals = fig.add_axes((0.06, 0.05, 0.935, 0.195))

        if fit_id_name is None:
            fit_id_name = 0

        if sed_fit_plot_param_dict is None:
            sed_fit_plot_param_dict = cigale_plotting_params.standard_sed_fit_plot_param_dict

        if display_parameter_list is None:
            display_parameter_list = sed_fit_plot_param_dict['display_parameter_list']

        mask_model_table = fit_summary_dict['model_table']['id'] == fit_id_name

        # plot observational fluxes
        min_max_data_values = CigaleVisualizer.display_fluxes(
            ax=ax_sed, flux_dict=flux_dict[fit_id_name],
            model_table=fit_summary_dict['model_table'][mask_model_table],
            sed_fit_plot_param_dict=sed_fit_plot_param_dict,
            return_min_max_value=True, ax_residuals=ax_sed_residuals)

        # plot SED
        CigaleVisualizer.display_sed_fit(ax=ax_sed, sed_dict=fit_summary_dict['sed_dict_all_fits'][fit_id_name],
                                         sed_fit_plot_param_dict=sed_fit_plot_param_dict)

        CigaleVisualizer.arange_sed_plot(
            ax_sed=ax_sed, ax_sed_residuals=ax_sed_residuals, min_max_data_values=min_max_data_values,
            sed_dict=fit_summary_dict['sed_dict_all_fits'][fit_id_name],
            model_table=fit_summary_dict["model_table"][mask_model_table],
        display_parameter_list=display_parameter_list, sed_fit_plot_param_dict=sed_fit_plot_param_dict)

        return fig

    @staticmethod
    def visualize_cigale_sed_pdf_fit(flux_dict, fit_summary_dict, pdf_corr_list, fit_id_name=None,
                                     sed_fit_plot_param_dict=None,
                                     display_parameter_list=None):



        fig_size_individual = (2, 2)

        n_cols = 18
        if len(pdf_corr_list) > 5:
            n_cols = len(pdf_corr_list) * 4 + 2

        n_rows = 8 + 2 + 1 + (len(pdf_corr_list) - 1) * 4 + 2
        idx_row_corr_start = 11
        print('n_cols ', n_cols)
        print('n_rows ', n_rows)

        fig = plt.figure(figsize=(2*n_cols, 2*n_rows))
        # gs = fig.add_gridspec(ncols=n_cols, nrows=n_rows, left=0.01, bottom=0.01, right=0.99, top=0.99,
        #                       wspace=0.01, hspace=0.01)
        gs = fig.add_gridspec(ncols=n_cols, nrows=n_rows, left=0.08, bottom=0.08, right=0.99, top=0.99,
                                  wspace=0.1, hspace=0.1)
        ax_sed = fig.add_subplot(gs[:8, :])
        ax_sed_residuals = fig.add_subplot(gs[8:10, :])


        if fit_id_name is None:
            fit_id_name = 0

        if sed_fit_plot_param_dict is None:
            sed_fit_plot_param_dict = cigale_plotting_params.standard_sed_pdf_fit_plot_param_dict

        if display_parameter_list is None:
            display_parameter_list = sed_fit_plot_param_dict['display_parameter_list']

        mask_model_table = fit_summary_dict['model_table']['id'] == fit_id_name

        # plot observational fluxes
        min_max_data_values = CigaleVisualizer.display_fluxes(
            ax=ax_sed, flux_dict=flux_dict[fit_id_name],
            model_table=fit_summary_dict['model_table'][mask_model_table],
            sed_fit_plot_param_dict=sed_fit_plot_param_dict,
            return_min_max_value=True, ax_residuals=ax_sed_residuals)

        # plot SED
        CigaleVisualizer.display_sed_fit(ax=ax_sed, sed_dict=fit_summary_dict['sed_dict_all_fits'][fit_id_name],
                                         sed_fit_plot_param_dict=sed_fit_plot_param_dict)

        CigaleVisualizer.arange_sed_plot(
            ax_sed=ax_sed, ax_sed_residuals=ax_sed_residuals, min_max_data_values=min_max_data_values,
            sed_dict=fit_summary_dict['sed_dict_all_fits'][fit_id_name],
            model_table=fit_summary_dict["model_table"][mask_model_table],
        display_parameter_list=display_parameter_list, sed_fit_plot_param_dict=sed_fit_plot_param_dict)

        # plot pdf
        idx_col = 0
        idx_row = idx_row_corr_start
        max_likelihood_value = np.exp(-0.5 * fit_summary_dict['model_table'][mask_model_table]['best.reduced_chi_square'])
        print(fit_summary_dict['pdf_param_dict_all'][fit_id_name].keys())

        idx_col_param = 0
        idx_row_param = 1

        n_combinations = len(list(itertools.combinations(pdf_corr_list, 2)))

        plot_top_distribution = True

        # get norm and cmap
        cmap = 'Blues'
        norm = plotting_tools.ColorBarTools.compute_cbar_norm(vmin_vmax=(0.001, 1), log_scale=True)

        for pdf_combo_idx in range(n_combinations):
            print(idx_col_param, idx_row_param)

            param_1 = pdf_corr_list[idx_col_param]
            param_2 = pdf_corr_list[idx_row_param]
            print(pdf_combo_idx, param_1, param_2)
            values_param_1 = fit_summary_dict['pdf_param_dict_all'][fit_id_name][param_1 + '_values']
            values_param_2 = fit_summary_dict['pdf_param_dict_all'][fit_id_name][param_2 + '_values']
            # get likelyhood_data
            chi2_data_param_1 = fit_summary_dict['pdf_param_dict_all'][fit_id_name][param_1]
            chi2_data_param_2 = fit_summary_dict['pdf_param_dict_all'][fit_id_name][param_2]
            likelihood_ratio_data_param_1 = np.exp(-0.5 * chi2_data_param_1) / max_likelihood_value
            likelihood_ratio_data_param_2 = np.exp(-0.5 * chi2_data_param_2) / max_likelihood_value
            # get best and bays value
            best_value_1 = fit_summary_dict['model_table'][mask_model_table]['best.' + param_1]
            best_value_2 = fit_summary_dict['model_table'][mask_model_table]['best.' + param_2]
            bayes_value_1 = fit_summary_dict['model_table'][mask_model_table]['bayes.' + param_1]
            bayes_value_2 = fit_summary_dict['model_table'][mask_model_table]['bayes.' + param_2]



            if param_1 + '_' + param_2 in fit_summary_dict['pdf_param_dict_all'][fit_id_name].keys():
                chi2_data_corr = fit_summary_dict['pdf_param_dict_all'][fit_id_name][param_1 + '_' + param_2]
                likelihood_ratio_data_corr = (np.exp(-0.5 * chi2_data_corr) / max_likelihood_value).T
            else:
                chi2_data_corr = fit_summary_dict['pdf_param_dict_all'][fit_id_name][param_2 + '_' + param_1]
                likelihood_ratio_data_corr = np.exp(-0.5 * chi2_data_corr) / max_likelihood_value

            # add correlation axis
            ax_pdf_corr = fig.add_subplot(gs[idx_row+2: idx_row+6, idx_col:idx_col+4])


            # computing the extents
            # n_pixel_value_1 =
            pixel_width_value_1 = (np.max(values_param_1) - np.min(values_param_1)) / (len(values_param_1) - 1)
            pixel_width_value_2 = (np.max(values_param_2) - np.min(values_param_2)) / (len(values_param_2) - 1)
            min_value_1 = np.min(values_param_1) - pixel_width_value_1 / 2
            max_value_1 = np.max(values_param_1) + pixel_width_value_1 / 2
            min_value_2 = np.min(values_param_2) - pixel_width_value_2 / 2
            max_value_2 = np.max(values_param_2) + pixel_width_value_2 / 2

            ax_pdf_corr.imshow(likelihood_ratio_data_corr, origin='lower',
                               extent=(min_value_1, max_value_1, min_value_2, max_value_2),
                               aspect='auto',
                               cmap=cmap, norm=norm,)
            plotting_tools.AxisTools.frame2axis(ax=ax_pdf_corr, color='k', line_width=3)
            ax_pdf_corr.scatter(bayes_value_1, bayes_value_2, marker='P', color='red', s=1500)
            ax_pdf_corr.scatter(best_value_1, best_value_2, marker='X', color='k', s=1200)

            # add y axis?
            if idx_col_param == 0:
                ax_pdf_corr.set_ylabel(cigale_plotting_params.param_display_name_dict[param_2]['param_display_str'],
                                       fontsize=sed_fit_plot_param_dict['font_size_label'])
                ax_pdf_corr.tick_params(axis='y', which='both', width=5, length=15, direction='in', color='k',
                                        right=True, labelsize=sed_fit_plot_param_dict['font_size_label'])
            else:
                ax_pdf_corr.tick_params(axis='y', which='both', width=5, length=15, direction='in', color='k',
                                        right=True, labelsize=sed_fit_plot_param_dict['font_size_label'], labelleft=False)

            if plot_top_distribution:
                ax_pdf_param_1 = fig.add_subplot(gs[idx_row: idx_row+2, idx_col:idx_col+4])
                ax_pdf_param_1.step(values_param_1 + pixel_width_value_1/2, likelihood_ratio_data_param_1, where='pre', linewidth=3, color='k')
                ax_pdf_param_1.plot([values_param_1[0] - pixel_width_value_1/2, values_param_1[0] + pixel_width_value_1/2],
                                    [likelihood_ratio_data_param_1[0], likelihood_ratio_data_param_1[0]],
                                    linewidth=3, color='k')

                ax_pdf_param_1.set_yscale('log')


                ax_pdf_param_1.set_xlim(min_value_1, max_value_1)
                plotting_tools.AxisTools.frame2axis(ax=ax_pdf_param_1, color='k', line_width=3)
                ax_pdf_param_1.tick_params(axis='both', which='both', width=5, length=15, direction='in', color='k',
                                           right=True, top=True, labelsize=sed_fit_plot_param_dict['font_size_label'],
                                           labelleft=False, labelbottom=False)
                plot_top_distribution = False

            if pdf_combo_idx == (n_combinations - 1):

                ax_pdf_param_2 = fig.add_subplot(gs[idx_row+2: idx_row+6, idx_col+4:idx_col+6])
                ax_pdf_param_2.invert_yaxis()
                ax_pdf_param_2.step(likelihood_ratio_data_param_2, values_param_2 - pixel_width_value_2/2,
                                    where='pre', linewidth=3, color='k')
                # add last value
                ax_pdf_param_2.plot([likelihood_ratio_data_param_2[-1], likelihood_ratio_data_param_2[-1]],
                                    [values_param_2[-1] - pixel_width_value_2/2, values_param_2[-1] + pixel_width_value_2/2], linewidth=3, color='k')
                ax_pdf_param_2.set_xscale('log')

                ax_pdf_param_2.set_ylim(min_value_2, max_value_2)
                plotting_tools.AxisTools.frame2axis(ax=ax_pdf_param_2, color='k', line_width=3)
                ax_pdf_param_2.tick_params(axis='both', which='both', width=5, length=15, direction='in', color='k',
                                           right=True, top=True, labelsize=sed_fit_plot_param_dict['font_size_label'],
                                           labelleft=False, labelbottom=False)



            # ax_pdf_corr.imshow(pdf_data)
            idx_row += 4
            idx_row_param += 1
            # check if column is completed
            if idx_row >= (n_rows - 4):
                idx_col_param += 1
                idx_row_param = idx_col_param + 1
                idx_col += 4
                idx_row = idx_row_corr_start + idx_col
                ax_pdf_corr.set_xlabel(cigale_plotting_params.param_display_name_dict[param_1]['param_display_str'],
                                       fontsize=sed_fit_plot_param_dict['font_size_label'])
                ax_pdf_corr.tick_params(axis='x', which='both', width=5, length=15, direction='in', color='k',
                                        top=True, labelsize=sed_fit_plot_param_dict['font_size_label'])

                plot_top_distribution = True
            else:
                ax_pdf_corr.tick_params(axis='x', which='both', width=5, length=15, direction='in', color='k',
                                        top=True, labelsize=sed_fit_plot_param_dict['font_size_label'],
                                        labelbottom=False)


            # add legend and c bar
            ax_labels = fig.add_subplot(gs[idx_row_corr_start: idx_row_corr_start+4, 4:8])
            ax_labels.scatter([], [], marker='X', color='k', s=1200, label='Best fit')
            ax_labels.scatter([], [], marker='P', color='red', s=1500, label='Bayes fit')
            ax_labels.legend(frameon=False, fontsize=sed_fit_plot_param_dict['font_size_label'])
            ax_labels.axis('off')

            ax_cbar = fig.add_subplot(gs[idx_row_corr_start+1: idx_row_corr_start+2, 8:12])
            plotting_tools.ColorBarTools.create_cbar(ax_cbar=ax_cbar, cmap=cmap, norm=norm, cbar_label=r'L_{max} / L',
                                                     fontsize=sed_fit_plot_param_dict['font_size_label'],
                                                     ticks=None, labelpad=2, tick_width=2,
                    orientation='horizontal', top_lable=True, label_color='k',
                    extend='neither')


        return fig




    @staticmethod
    def arange_sed_plot(ax_sed, ax_sed_residuals, min_max_data_values, sed_dict, model_table, display_parameter_list,
                        sed_fit_plot_param_dict):

        # set limits and layout
        #
        # set the x limits
        min_wave_lim, max_wave_lim = plotting_tools.AxisTools.data2axis_lim(
            ax=ax_sed, min_value=min_max_data_values[0], max_value=min_max_data_values[1], log_axis=True,
            min_margin=0.02, max_margin=0.02, axis='x')
        plotting_tools.AxisTools.data2axis_lim(
            ax=ax_sed_residuals, min_value=min_max_data_values[0], max_value=min_max_data_values[1], log_axis=True,
            min_margin=0.02, max_margin=0.02, axis='x')

        ax_sed_residuals.plot([min_wave_lim, max_wave_lim], [0, 0],
                              linewidth=3, linestyle='--', color='darkgray')

        # get maximal and minimal value for flux
        min_flux_value, max_flux_value = CigaleVisualizer.get_min_max_flux_value_from_sed_fit(
            sed_dict=sed_dict, min_wave_lim=min_wave_lim,
            max_wave_lim=max_wave_lim, init_min_flux_value=min_max_data_values[2],
            init_max_flux_value=min_max_data_values[3], wave_unit=u.um)
        # set y-axis limits
        plotting_tools.AxisTools.data2axis_lim(ax=ax_sed, min_value=min_flux_value, max_value=max_flux_value,
                                               log_axis=True, min_margin=0.05, max_margin=0.05, axis='y')
        # axis scales
        ax_sed.set_xscale('log')
        ax_sed.set_yscale('log')
        ax_sed_residuals.set_xscale('log')

        # add textbox with parameter
        display_str = r'$\underline{\rm Fit-parameters}$'
        display_str += ' \n'
        for display_parameter in display_parameter_list:

            display_str += cigale_plotting_params.param_display_name_dict[display_parameter]['param_display_str'] + '='
            if isinstance(cigale_plotting_params.param_display_name_dict[display_parameter]['decimals_display'], int):
                display_str += f'{model_table["best." + display_parameter].value[0]:.{cigale_plotting_params.param_display_name_dict[display_parameter]["decimals_display"]}f}'
            else:
                if display_parameter == 'stellar.m_star':
                    display_str += plotting_tools.StrTools.mstar2label(mstar=model_table["best." + display_parameter].value[0], add_unit=True)
                elif display_parameter == 'sfh.age':
                    display_str += plotting_tools.StrTools.age2label(age=model_table["best." + display_parameter].value[0])
            if cigale_plotting_params.param_display_name_dict[display_parameter]['custom_unit'] is not None:
                display_str += (' ' + cigale_plotting_params.param_display_name_dict[display_parameter]['custom_unit'])

            display_str += ' \n'
        display_str = display_str[:-2]

        t = ax_sed.text(0.7, 0.05, display_str, horizontalalignment='left', verticalalignment='bottom',
                        transform=ax_sed.transAxes, fontsize=sed_fit_plot_param_dict['font_size_label'])
        t.set_bbox(dict(facecolor='grey', alpha=0.5, edgecolor='black', boxstyle='round,pad=1'))

        # legends
        ax_sed.legend(fontsize=sed_fit_plot_param_dict['font_size_label'], loc=sed_fit_plot_param_dict['sed_axis_label_loc'])
        ax_sed_residuals.legend(fontsize=sed_fit_plot_param_dict['font_size_label'])
        # frames
        plotting_tools.AxisTools.frame2axis(ax=ax_sed, color='k', line_width=3)
        plotting_tools.AxisTools.frame2axis(ax=ax_sed_residuals, color='k', line_width=3)
        # labels
        ax_sed.set_ylabel(r'Flux [mJy]', fontsize=sed_fit_plot_param_dict['font_size_label'])
        ax_sed_residuals.set_ylabel('Relative \n residuals', labelpad=-20,
                                    fontsize=sed_fit_plot_param_dict['font_size_label'])
        ax_sed_residuals.set_xlabel(r'Wavelength [$\mu$m]', fontsize=sed_fit_plot_param_dict['font_size_label'],
                                    labelpad=-10)

        # tick and tickla  bels
        list_major_xticks, list_major_str_xticks, list_minor_xticks, list_minor_str_xticks = (
            plotting_tools.AxisTools.get_log_tick_labels(min_value=min_wave_lim, max_value=max_wave_lim))

        ax_sed.set_xticks(list_major_xticks)
        ax_sed.set_xticks(list_minor_xticks, minor=True)

        ax_sed_residuals.set_xticks(list_major_xticks)
        ax_sed_residuals.set_xticklabels(list_major_str_xticks)
        ax_sed_residuals.set_xticks(list_minor_xticks, minor=True)
        ax_sed_residuals.set_xticklabels(list_minor_str_xticks, minor=True)

        ax_sed.tick_params(axis='both', which='major', width=5, length=15, direction='in', color='k', top=True, right=True,
                           labelsize=sed_fit_plot_param_dict['font_size_label'], labelbottom=False)
        ax_sed.tick_params(axis='both', which='minor', width=3, length=10, direction='in', color='k', top=True, right=True,
                           labelsize=sed_fit_plot_param_dict['font_size_label'], labelbottom=False)

        ax_sed_residuals.tick_params(axis='both', which='major', width=5, length=15, direction='in', color='k',
                                     top=True, right=True,
                           labelsize=sed_fit_plot_param_dict['font_size_label'])
        ax_sed_residuals.tick_params(axis='both', which='minor', width=3, length=10, direction='in', color='k',
                                     top=True, right=True,
                           labelsize=sed_fit_plot_param_dict['font_size_label'])

    @staticmethod
    def display_sed_fit(ax, sed_dict, sed_fit_plot_param_dict, wave_unit=u.um):

        wave = sed_dict['wave'].to(wave_unit)

        ax.plot(wave, sed_dict['best_fit_flux'],
                color=sed_fit_plot_param_dict['best_fit_color'],
                linestyle=sed_fit_plot_param_dict['best_fit_line_style'],
                linewidth=sed_fit_plot_param_dict['best_fit_line_width'],
                label=sed_fit_plot_param_dict['best_fit_label'],
                zorder=sed_fit_plot_param_dict['best_fit_zorder'])
        if 'stellar_unattenuated_flux' in sed_dict.keys():
            ax.plot(wave, sed_dict['stellar_unattenuated_flux'],
                    color=sed_fit_plot_param_dict['stellar_unattenuated_color'],
                    linestyle=sed_fit_plot_param_dict['stellar_unattenuated_line_style'],
                    linewidth=sed_fit_plot_param_dict['stellar_unattenuated_line_width'],
                    label=sed_fit_plot_param_dict['stellar_unattenuated_label'],
                    zorder=sed_fit_plot_param_dict['stellar_unattenuated_zorder'])
        if 'stellar_attenuated_flux' in sed_dict.keys():
            ax.plot(wave, sed_dict['stellar_attenuated_flux'],
                    color=sed_fit_plot_param_dict['stellar_attenuated_color'],
                    linestyle=sed_fit_plot_param_dict['stellar_attenuated_line_style'],
                    linewidth=sed_fit_plot_param_dict['stellar_attenuated_line_width'],
                    label=sed_fit_plot_param_dict['stellar_attenuated_label'],
                    zorder=sed_fit_plot_param_dict['stellar_attenuated_zorder'])
        if 'nebular_attenuated_flux' in sed_dict.keys():
            ax.plot(wave, sed_dict['nebular_attenuated_flux'],
                    color=sed_fit_plot_param_dict['nebular_color'],
                    linestyle=sed_fit_plot_param_dict['nebular_line_style'],
                    linewidth=sed_fit_plot_param_dict['nebular_line_width'],
                    label=sed_fit_plot_param_dict['nebular_label'],
                    zorder=sed_fit_plot_param_dict['nebular_zorder'])
        if 'dust_flux' in sed_dict.keys():
            ax.plot(wave, sed_dict['dust_flux'],
                    color=sed_fit_plot_param_dict['dust_color'],
                    linestyle=sed_fit_plot_param_dict['dust_line_style'],
                    linewidth=sed_fit_plot_param_dict['dust_line_width'],
                    label=sed_fit_plot_param_dict['dust_label'],
                    zorder=sed_fit_plot_param_dict['dust_zorder'])

    @staticmethod
    def get_min_max_flux_value_from_sed_fit(sed_dict, min_wave_lim, max_wave_lim, init_min_flux_value=None,
                                            init_max_flux_value=None, wave_unit=u.um):
        # get maximal and minimal value for flux
        mask_wave_lim = ((sed_dict['wave'].to(wave_unit).value > min_wave_lim) &
                         (sed_dict['wave'].to(wave_unit).value < max_wave_lim))
        # best fit
        if init_min_flux_value > np.nanmin(sed_dict['best_fit_flux'][mask_wave_lim]).value:
            init_min_flux_value = np.nanmin(sed_dict['best_fit_flux'][mask_wave_lim]).value
        if init_max_flux_value < np.nanmax(sed_dict['best_fit_flux'][mask_wave_lim]).value:
            init_max_flux_value = np.nanmax(sed_dict['best_fit_flux'][mask_wave_lim]).value

        if 'stellar_attenuated_flux' in sed_dict.keys():
            if init_min_flux_value > np.nanmin(sed_dict['stellar_attenuated_flux'][mask_wave_lim]).value:
                init_min_flux_value = np.nanmin(sed_dict['stellar_attenuated_flux'][mask_wave_lim]).value
            if init_max_flux_value < np.nanmax(sed_dict['stellar_attenuated_flux'][mask_wave_lim]).value:
                init_max_flux_value = np.nanmax(sed_dict['stellar_attenuated_flux'][mask_wave_lim]).value

        if 'stellar_unattenuated_flux' in sed_dict.keys():
            if init_min_flux_value > np.nanmin(sed_dict['stellar_unattenuated_flux'][mask_wave_lim]).value:
                init_min_flux_value = np.nanmin(sed_dict['stellar_unattenuated_flux'][mask_wave_lim]).value
            if init_max_flux_value < np.nanmax(sed_dict['stellar_unattenuated_flux'][mask_wave_lim]).value:
                init_max_flux_value = np.nanmax(sed_dict['stellar_unattenuated_flux'][mask_wave_lim]).value

        return init_min_flux_value, init_max_flux_value

    @staticmethod
    def display_fluxes(ax, flux_dict, model_table, sed_fit_plot_param_dict, return_min_max_value=True,
                       ax_residuals=None):
        # lists fro best min and max estimation
        min_wave_list = []
        max_wave_list = []
        obs_flux_list = []
        for band, obs, instrument in zip(flux_dict['band_list'], flux_dict['obs_list'], flux_dict['instrument_list']):
            # get band wavelength
            mean_wave = ObsTools.get_obs_telescope_wave(band=band, obs=obs, target=None, instrument=instrument,
                                                        wave_estimator='mean_wave', unit='mu')
            min_wave = ObsTools.get_obs_telescope_wave(band=band, obs=obs, target=None, instrument=instrument,
                                                        wave_estimator='min_wave', unit='mu')
            max_wave = ObsTools.get_obs_telescope_wave(band=band, obs=obs, target=None, instrument=instrument,
                                                        wave_estimator='max_wave', unit='mu')
            min_wave_list.append(min_wave)
            max_wave_list.append(max_wave)

            # get fluxes
            obs_flux = flux_dict['%s_flux' % band]
            obs_flux_err = flux_dict['%s_flux_err' % band]
            obs_flux_list.append(obs_flux)
            # modeled fluxes

            model_flux = model_table['best.' + CigaleHelper.get_obs_fitler_name(band=band, obs=obs, instrument=instrument)]
            obs_flux_list.append(float(model_flux.value))

            # display obs fluxes
            if flux_dict['%s_lim_flag' % band]:
                eb = ax.errorbar(mean_wave, obs_flux,
                                 xerr=[[mean_wave - min_wave], [max_wave - mean_wave]], yerr=obs_flux_err * 2,
                                 fmt=sed_fit_plot_param_dict['obs_data_lim_fmt'],
                                 color=sed_fit_plot_param_dict['obs_data_lim_marker_color'],
                                 ms=sed_fit_plot_param_dict['obs_data_lim_marker_size'],
                                 elinewidth=sed_fit_plot_param_dict['obs_data_lim_err_bar_line_width'],
                                 zorder=sed_fit_plot_param_dict['obs_data_lim_zorder'],
                                 uplims=True)
                eb.lines[1][0].set_markersize(sed_fit_plot_param_dict['obs_data_lim_arrow_size'])
            else:
                ax.errorbar(mean_wave, obs_flux, xerr=[[mean_wave - min_wave], [max_wave - mean_wave]], yerr=obs_flux_err,
                            fmt=sed_fit_plot_param_dict['obs_data_lim_fmt'],
                            color=sed_fit_plot_param_dict['obs_data_marker_color'],
                            ms=sed_fit_plot_param_dict['obs_data_marker_size'],
                            elinewidth=sed_fit_plot_param_dict['obs_data_err_bar_line_width'],
                            zorder=sed_fit_plot_param_dict['obs_data_zorder'])
                # add residuals
                if ax_residuals is not None:
                    ax_residuals.scatter(mean_wave, (obs_flux - model_flux) / obs_flux,
                                         s=sed_fit_plot_param_dict['residuals_marker_size'],
                                         color=sed_fit_plot_param_dict['residuals_marker_color'],
                                         marker=sed_fit_plot_param_dict['residuals_marker_type'],
                                         zorder=sed_fit_plot_param_dict['residuals_zorder'])

            # display modeled fluxes
            ax.scatter(mean_wave, model_flux,
                       s=sed_fit_plot_param_dict['model_data_marker_size'],
                       color=sed_fit_plot_param_dict['model_data_marker_color'],
                       marker=sed_fit_plot_param_dict['model_data_marker_type'],
                       zorder=sed_fit_plot_param_dict['model_data_zorder'])

        # add display labels
        ax.errorbar([], [], xerr=[], yerr=[],
                    fmt=sed_fit_plot_param_dict['obs_data_lim_fmt'],
                    color=sed_fit_plot_param_dict['obs_data_marker_color'],
                    ms=sed_fit_plot_param_dict['obs_data_marker_size'],
                    elinewidth=sed_fit_plot_param_dict['obs_data_err_bar_line_width'],
                    zorder=sed_fit_plot_param_dict['obs_data_zorder'],
                    label=sed_fit_plot_param_dict['obs_data_label'])

        ax.scatter([], [],
                   s=sed_fit_plot_param_dict['model_data_marker_size'],
                   color=sed_fit_plot_param_dict['model_data_marker_color'],
                   marker=sed_fit_plot_param_dict['model_data_marker_type'],
                   zorder=sed_fit_plot_param_dict['model_data_zorder'],
                   label=sed_fit_plot_param_dict['model_data_label'])
        if ax_residuals is not None:
            ax_residuals.scatter([], [],
                                 s=sed_fit_plot_param_dict['residuals_marker_size'],
                                 color=sed_fit_plot_param_dict['residuals_marker_color'],
                                 marker=sed_fit_plot_param_dict['residuals_marker_type'],
                                 zorder=sed_fit_plot_param_dict['residuals_zorder'],
                                 label=sed_fit_plot_param_dict['residuals_label'])

        if return_min_max_value:
            return (np.nanmin(min_wave_list), np.nanmax(max_wave_list), np.nanmin(obs_flux_list),
                    np.nanmax(obs_flux_list))


