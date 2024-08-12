"""
This is the cigale config file. You should do your own and use this as an orientation
"""

standard_sed_modules_params = {
    'sfh2exp':
    {
        # e-folding time of the main stellar population model in Myr.
        'tau_main': [0.001],
        # e-folding time of the late starburst population model in Myr.
        'tau_burst': [0.001],
        # Mass fraction of the late burst population.
        'f_burst': [0.0],
        # Age of the main stellar population in the galaxy in Myr. The precision
        # is 1 Myr.
        'age': [1],
        # Age of the late burst in Myr. The precision is 1 Myr.
        'burst_age': [1],
        # Value of SFR at t = 0 in M_sun/yr.
        'sfr_0': [1.0],
        # Normalise the SFH to produce one solar mass.
        'normalise': [True]
    },
    'bc03':
    {
        # Initial mass function: 0 (Salpeter) or 1 (Chabrier).
        'imf': [1],
        # Metalicity. Possible values are: 0.0001, 0.0004, 0.004, 0.008, 0.02, 0.05.
        'metallicity': [0.02],
        # Age [Myr] of the separation between the young and the old star
        # populations. The default value in 10^7 years (10 Myr). Set to 0 not to
        # differentiate ages (only an old population).
        'separation_age': [10]
    },
    'nebular': {
        # Ionisation parameter. Possible values are: -4.0, -3.9, -3.8, -3.7,
        # -3.6, -3.5, -3.4, -3.3, -3.2, -3.1, -3.0, -2.9, -2.8, -2.7, -2.6,
        # -2.5, -2.4, -2.3, -2.2, -2.1, -2.0, -1.9, -1.8, -1.7, -1.6, -1.5,
        # -1.4, -1.3, -1.2, -1.1, -1.0.
        'logU': [-2.0],
        # Gas metallicity. Possible values are: 0.000, 0.0004, 0.001, 0.002,
        # 0.0025, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009, 0.011, 0.012,
        # 0.014, 0.016, 0.019, 0.020, 0.022, 0.025, 0.03, 0.033, 0.037, 0.041,
        # 0.046, 0.051.
        'zgas': [0.02],
        # Electron density. Possible values are: 10, 100, 1000.
        'ne': [100],
        # Fraction of Lyman continuum photons escaping the galaxy. Possible
        # values between 0 and 1.
        'f_esc': [0.5],
        # Fraction of Lyman continuum photons absorbed by dust. Possible values
        # between 0 and 1.
        'f_dust': [0.0],
        # Line width in km/s.
        'lines_width': [300.0],
        # Include nebular emission.
        'emission': [True],
    },
    'dustext':
    {
        # E(B-V), the colour excess.
        'E_BV': [0],
        # Ratio of total to selective extinction, A_V / E(B-V). The standard
        # value is 3.1 for MW using CCM89. For SMC and LMC using Pei92 the
        # values should be 2.93 and 3.16.
        'Rv': [3.1],
        # Extinction law to apply. The values are 0 for CCM, 1 for SMC, and 2
        # for LCM.
        'law': [0],
        # Filters for which the extinction will be computed and added to the SED
        # information dictionary. You can give several filter names separated by
        # a & (don't use commas).
        'filters': ['B_B90 & V_B90 & FUV']
    },
    'redshifting':
    {
        # Redshift of the objects. Leave empty to use the redshifts from the
        # input file.
        'redshift': [0.0]
    },
    'restframe_parameters':
    {
        # Observed and intrinsic UV slopes β and β₀ measured in the same way as
        # in Calzetti et al. (1994).
        'beta_calz94': [False],
        # Dn4000 break using the Balogh et al. (1999) definition.
        'Dn4000': [False],
        # IRX computed from the GALEX FUV filter and the dust luminosity.
        'IRX': [False],
        # Equivalent width of emission/absorption lines. This requires a label
        # for easier recognition in the output file followed by thethe
        # definition of the wavelength ranges of three bands: the blue sideband,
        # the line, and the red sideband. Each band is defined by two
        # wavelengths and the wavelengths are separated by '/'. For instance the
        # HδA is defined as (Worthey et al. 1997):
        # 404.160/407.975/408.350/412.225/412.805/416.100. Different lines can
        # be provided separated by &. By convention, absorption lines are
        # positive and emission lines are negative.
        'EW': ['HdeltaA/404.160/407.975/408.350/412.225/412.850/416.100 & '
               'Halpha/650.0/652.5/653.5/660.0/661.0/663.5 & '
               'Pashalpha/1304.119/1694.889/1844.528/1902.998/2770.355/3250.592'],
        # Filters for which the rest-frame luminosity will be computed. You can
        # give several filter names separated by a & (don't use commas).
        'luminosity_filters': ['FUV & V_B90'],
        # Rest-frame colours to be computed. You can give several colours
        # separated by a & (don't use commas).
        'colours_filters': ['FUV-NUV & NUV-r_prime'],
        }
}

standard_output_sed_param_list = [

    #'dust.luminosity',
    #'param.restframe_Lnu(FUV)',
    #'param.restframe_Lnu(V_B90)',
    #'sfh.integrated',
    #'sfh.sfr',
    #'sfh.sfr100Myrs',
    #'sfh.sfr10Myrs',
    #'stellar.lum',
    #'stellar.lum_ly',
    #'stellar.lum_ly_old',
    #'stellar.lum_ly_young',
    #'stellar.lum_old',
    #'stellar.lum_young',
    #'stellar.m_gas',
    #'stellar.m_gas_old',
    #'stellar.m_gas_young',
    'stellar.m_star',
    #'stellar.m_star_old',
    #'stellar.m_star_young',
    #'stellar.n_ly',
    #'stellar.n_ly_old',
    #'stellar.n_ly_young',
    #'attenuation.B_B90',
    'attenuation.E_BV',
    #'attenuation.FUV',
    #'attenuation.V_B90',
    #'nebular.f_dust',
    'nebular.f_esc',
    #'nebular.lines_width',
    'nebular.logU',
    'nebular.ne',
    'nebular.zgas',
    'param.EW(Halpha)',
    'param.EW(HdeltaA)',
    'param.EW(Pashalpha)',
    #'param.restframe_FUV-NUV',
    #'param.restframe_NUV-r_prime',
    'sfh.age',
    #'sfh.burst_age',
    #'sfh.f_burst',
    #'sfh.tau_burst',
    #'sfh.tau_main',
    #'stellar.age_m_star',
    #'stellar.beta0',
    #'stellar.imf',
    'stellar.metallicity',
    #'stellar.old_young_separation_age',
    #'universe.age',
    'universe.luminosity_distance',
    #'universe.redshift',

]

data_output_path = '/media/benutzer/Extreme Pro/data/cigale_model_sim_output'

standard_output_band_dict = {'hst': {'acs': ['F435W', 'F555W', 'F814W'],
                                     'uvis': ['F275W', 'F336W', 'F438W', 'F555W', 'F814W']},
                             'jwst': {'nircam': ['F200W', 'F300M', 'F335M', 'F360M'],
                                      'miri': ['F770W', 'F1000W', 'F1130W', 'F2100W']}}

