"""
Plotting parameters for visualization
"""

param_display_name_dict = {

    'reduced_chi_square': {'param_display_str': r'$\chi^2$',
                                'decimals_display': 1,
                                'custom_unit': None},
    'stellar.m_star': {'param_display_str': r'M$_{*}$',
                            'decimals_display': None,
                            'custom_unit': None},
    'attenuation.A550': {'param_display_str': r'A$_{\rm V}$',
                              'decimals_display': 1,
                              'custom_unit': 'mag'},
    'sfh.age': {'param_display_str': 'Age',
                     'decimals_display': None,
                     'custom_unit': None},
    'stellar.metallicity': {'param_display_str': r'Z$_*$',
                     'decimals_display': 4,
                     'custom_unit': None},

    'nebular.f_esc': {'param_display_str': r'f$_{\rm esc}$',
                           'decimals_display': 1,
                     'custom_unit': None},
    'nebular.logU': {'param_display_str': 'log U',
                     'decimals_display': 1,
                     'custom_unit': None},
    'nebular.ne': {'param_display_str': r'n$_e$',
                     'decimals_display': 0,
                     'custom_unit': None},
    'nebular.zgas': {'param_display_str': r'Z$_{\rm gas}$',
                     'decimals_display': 4,
                     'custom_unit': None},
    'nebular.f_dust': {'param_display_str': r'f$_{\rm dust}$',
                           'decimals_display': 1,
                     'custom_unit': None},



    'dust.qpah': {'param_display_str': r'q$_{\rm pa}$',
                     'decimals_display': 3,
                     'custom_unit': None},
    'dust.umin': {'param_display_str': r'U$_{\rm min}$',
                     'decimals_display': 3,
                     'custom_unit': None},
    'dust.alpha': {'param_display_str': r'$\alpha$',
                     'decimals_display': 1,
                     'custom_unit': None},
    'dust.gamma': {'param_display_str': r'$\gamma$',
                     'decimals_display': 3,
                     'custom_unit': None}









}




standard_sed_fit_plot_param_dict = {
    # general parameters
    'font_size_label': 30,
    'font_size_large': 45,
    'sed_axis_label_loc': 2,

    'display_parameter_list': ['best.reduced_chi_square', 'best.stellar.m_star', 'best.attenuation.A550',
                               'best.sfh.age'],

    # obs data
    'obs_data_fmt': '.',
    'obs_data_marker_color': 'k',
    'obs_data_marker_size': 40,
    'obs_data_zorder': 11,
    'obs_data_err_bar_line_width': 4,
    'obs_data_label': 'Observed fluxes',
    # obs data lim
    'obs_data_lim_fmt': '.',
    'obs_data_lim_marker_color': 'gray',
    'obs_data_lim_marker_size': 40,
    'obs_data_lim_arrow_size': 25,
    'obs_data_lim_zorder': 11,
    'obs_data_lim_err_bar_line_width': 4,

    # obs data
    'model_data_marker_type': 'o',
    'model_data_marker_color': 'red',
    'model_data_marker_size': 150,
    'model_data_zorder': 12,
    'model_data_label': 'Model fluxes',

    # residuals
    'residuals_marker_type': 'P',
    'residuals_marker_color': 'k',
    'residuals_marker_size': 300,
    'residuals_zorder': 12,
    'residuals_label': '(Obs - Mod) / Obs',



    # best fitting model components
    'best_fit_color': 'k',
    'best_fit_line_style': '-',
    'best_fit_line_width': 4,
    'best_fit_label': 'Model spectrum',
    'best_fit_zorder': 10,

    'stellar_unattenuated_color': 'tab:blue',
    'stellar_unattenuated_line_style': '--',
    'stellar_unattenuated_line_width': 3,
    'stellar_unattenuated_label': 'Stellar unattenuated',
    'stellar_unattenuated_zorder': 9,

    'stellar_attenuated_color': 'tab:olive',
    'stellar_attenuated_line_style': '--',
    'stellar_attenuated_line_width': 3,
    'stellar_attenuated_label': 'Stellar attenuated',
    'stellar_attenuated_zorder': 9,

    'nebular_color': 'tab:green',
    'nebular_line_style': '-',
    'nebular_line_width': 3,
    'nebular_label': 'Nebular emission',
    'nebular_zorder': 9,

    'dust_color': 'tab:red',
    'dust_line_style': '-',
    'dust_line_width': 3,
    'dust_label': 'Dust',
    'dust_zorder': 9,

}





standard_sed_pdf_fit_plot_param_dict = {
    # general parameters
    'font_size_label': 55,
    'sed_axis_label_loc': 2,

    'display_parameter_list': ['best.reduced_chi_square', 'best.stellar.m_star', 'best.attenuation.A550',
                               'best.sfh.age'],

    # obs data
    'obs_data_fmt': '.',
    'obs_data_marker_color': 'k',
    'obs_data_marker_size': 40,
    'obs_data_zorder': 11,
    'obs_data_err_bar_line_width': 4,
    'obs_data_label': 'Observed fluxes',
    # obs data lim
    'obs_data_lim_fmt': '.',
    'obs_data_lim_marker_color': 'gray',
    'obs_data_lim_marker_size': 40,
    'obs_data_lim_arrow_size': 25,
    'obs_data_lim_zorder': 11,
    'obs_data_lim_err_bar_line_width': 4,

    # obs data
    'model_data_marker_type': 'o',
    'model_data_marker_color': 'red',
    'model_data_marker_size': 150,
    'model_data_zorder': 12,
    'model_data_label': 'Model fluxes',

    # residuals
    'residuals_marker_type': 'P',
    'residuals_marker_color': 'k',
    'residuals_marker_size': 300,
    'residuals_zorder': 12,
    'residuals_label': '(Obs - Mod) / Obs',



    # best fitting model components
    'best_fit_color': 'k',
    'best_fit_line_style': '-',
    'best_fit_line_width': 4,
    'best_fit_label': 'Model spectrum',
    'best_fit_zorder': 10,

    'stellar_unattenuated_color': 'tab:blue',
    'stellar_unattenuated_line_style': '--',
    'stellar_unattenuated_line_width': 3,
    'stellar_unattenuated_label': 'Stellar unattenuated',
    'stellar_unattenuated_zorder': 9,

    'stellar_attenuated_color': 'tab:olive',
    'stellar_attenuated_line_style': '--',
    'stellar_attenuated_line_width': 3,
    'stellar_attenuated_label': 'Stellar attenuated',
    'stellar_attenuated_zorder': 9,

    'nebular_color': 'tab:green',
    'nebular_line_style': '-',
    'nebular_line_width': 3,
    'nebular_label': 'Nebular emission',
    'nebular_zorder': 9,

    'dust_color': 'tab:red',
    'dust_line_style': '-',
    'dust_line_width': 3,
    'dust_label': 'Dust',
    'dust_zorder': 9,

}


