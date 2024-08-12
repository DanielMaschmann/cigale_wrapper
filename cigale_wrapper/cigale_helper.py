"""
Here we gather all the helper functions we need for the Cigale wrapper
"""
import numpy as np
import astropy.units as u


class CigaleHelper:
    """
    collection of function to organize cigale access
    """
    @staticmethod
    def get_hst_filter_name(band, instrument, err=False):
        """
        Getting the correct HST filter name associated with HST observations
        Parameters
        ----------
        band : str
        instrument : str
        err : bool
        Returns
        -------
        filter_name : str
        """
        filter_name = 'hst.'
        if instrument == 'uvis':
            filter_name += 'wfc3.'
        elif instrument == 'acs':
            filter_name += 'wfc.'
        else:
            raise KeyError('instrument musst be uvis or acs')
        filter_name += band
        if err:
            filter_name += 'err'
        return filter_name

    @staticmethod
    def get_jwst_filter_name(band, instrument, err=False):
        """
        Getting the correct HST filter name associated with JWST observations
        Parameters
        ----------
        band : str
        instrument : str
        err: bool
        Returns
        -------
        filter_name : str
        """
        filter_name = 'jwst.'
        assert instrument in ['nircam', 'miri']
        filter_name += instrument + '.'
        filter_name += band
        if err:
            filter_name += 'err'
        return filter_name

    @staticmethod
    def replace_params_in_file(param_dict, file_name='pcigale.ini'):
        """
        function to replace specific model configurations in pcigale ini files
        Parameters
        ----------
        param_dict : dict
        file_name : str
        """
        with open(file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        print(param_dict.keys())
        for key in param_dict.keys():
            print('key ', key)
            line_index = [i for i in range(len(lines)) if lines[i].startswith(key)]
            prefix = ''
            if not line_index:
                line_index = [i for i in range(len(lines)) if lines[i].startswith('  ' + key)]
                prefix = '  '
            if not line_index:
                line_index = [i for i in range(len(lines)) if lines[i].startswith('    ' + key)]
                prefix = '    '
            if len(line_index) > 1:
                raise KeyError('There is apparently more than one line beginning with <<', key, '>>')
            if isinstance(param_dict[key], (str, bool, int, float)):
                new_line = prefix + key + ' = ' + str(param_dict[key]) + '\n'
            elif isinstance(param_dict[key], list):
                new_line = prefix + key + ' = '
                for obj in param_dict[key]:
                    new_line += str(obj) + ', '
            else:
                raise KeyError('The given parameters mus be of type str, bool, int, float or a list of these types')
            # check if there is no , at the end
            if new_line[-2:] == ', ':
                new_line = new_line[:-2]

            print('new_line ', new_line)
            lines[line_index[0]] = new_line
        with open(file_name, 'w', encoding='utf-8') as file:
            file.writelines(lines)

    @staticmethod
    def create_output_band_list_str(output_band_dict):
        """
        Function to create a cigale string list for filter names
        Parameters
        ----------
        output_band_dict : dict
        """
        output_band_list_str = []
        if output_band_dict is not None:
            if 'hst' in output_band_dict.keys():
                for band in output_band_dict['hst']['acs']:
                    output_band_list_str.append(CigaleHelper.get_hst_filter_name(band=band, instrument='acs'))
                for band in output_band_dict['hst']['uvis']:
                    output_band_list_str.append(CigaleHelper.get_hst_filter_name(band=band, instrument='uvis'))
            if 'jwst' in output_band_dict.keys():
                for band in output_band_dict['jwst']['nircam']:
                    output_band_list_str.append(CigaleHelper.get_jwst_filter_name(band=band,  instrument='nircam'))
                for band in output_band_dict['jwst']['miri']:
                    output_band_list_str.append(CigaleHelper.get_jwst_filter_name(band=band,  instrument='miri'))
        return output_band_list_str

    @staticmethod
    def create_int_age_list_log_spacing(start=1, stop=13.7e3, n_steps=100):
        """
        Function to create a cigale string list for filter names
        Parameters
        ----------
        start : int or float
        stop : int or float
        n_steps : int

        Returns
        -------
        age_sequence : ``np.ndarray``

        """
        return list(np.array(np.unique(np.rint(np.logspace(np.log10(start), np.log10(stop), n_steps))), dtype=int))

    @staticmethod
    def compute_sim_band_flux_rescaled(model_table, mstar_scale, dist_scale, band='hst.wfc3.F555W'):

        sim_flux = np.array(model_table[band])
        sim_dist = np.array(model_table['universe.luminosity_distance']) * u.m
        sim_mstar = np.array(model_table['stellar.m_star']) * u.M_sun

        mass_scale_factor = (mstar_scale * u.M_sun) / sim_mstar
        dist_scale_factor = sim_dist ** 2 / (((dist_scale * u.Mpc).to(u.m))**2)

        return sim_flux * mass_scale_factor * dist_scale_factor


