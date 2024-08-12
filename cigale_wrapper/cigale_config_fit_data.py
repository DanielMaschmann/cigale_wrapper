"""
This is the cigale config file. You should do your own and use this as an orientation
"""

cigale_init_params = {
    'data_file': '',
    'parameters_file': '',
    'sed_modules': ['sfh2exp', 'bc03', 'dustext', 'redshifting', 'restframe_parameters'],
    'analysis_method': 'savefluxes',
    'cores': 6,
}