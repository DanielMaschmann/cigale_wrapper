"""
Here we gather all the helper functions we need for the Cigale wrapper
"""
import numpy as np
import astropy.units as u
from werkzeugkiste import helper_func
from obszugang import ObsTools


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
            filter_name += 'wfc3.uvis1.'
        elif instrument == 'acs':
            filter_name += 'acs.wfc.'
        else:
            raise KeyError('instrument musst be uvis or acs')
        filter_name += band
        if err:
            filter_name += '_err'
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
            filter_name += '_err'
        return filter_name

    @staticmethod
    def get_obs_fitler_name(band, obs, instrument, err=False):
        """
        Getting the correct Obs filter name
        Parameters
        ----------
        band : str
        obs : str
        instrument : str
        err: bool
        Returns
        -------
        filter_name : str
        """
        if obs == 'hst':
            return CigaleHelper.get_hst_filter_name(band=band, instrument=instrument, err=err)
        if obs == 'jwst':
            return CigaleHelper.get_jwst_filter_name(band=band, instrument=instrument, err=err)

    @staticmethod
    def get_filter_name_list(band_list, obs_list, instrument_list, include_err=False):

        filter_name_list = []
        for band, obs, instrument in zip(band_list, obs_list, instrument_list):
            if obs == 'hst':
                filter_name_list.append(CigaleHelper.get_hst_filter_name(band=band, instrument=instrument, err=False))
                if include_err:
                    filter_name_list.append(CigaleHelper.get_hst_filter_name(band=band, instrument=instrument, err=True))
            if obs == 'jwst':
                filter_name_list.append(CigaleHelper.get_jwst_filter_name(band=band, instrument=instrument, err=False))
                if include_err:
                    filter_name_list.append(CigaleHelper.get_jwst_filter_name(band=band, instrument=instrument, err=True))
        return filter_name_list

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

        # # print(lines)
        # # print(param_dict.keys())
        # exit()
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
            new_line += '\n'
            print('new_line ', new_line)
            lines[line_index[0]] = new_line
        with open(file_name, 'w', encoding='utf-8') as file:
            file.writelines(lines)

    @staticmethod
    def replace_redshift_digits_name_in_file(n_decimals_redshift, file_name='pcigale.ini'):
        """
        function to replace specific model configurations in pcigale ini files
        Parameters
        ----------
        n_decimals_redshift : int
        file_name : str
        """
        with open(file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        key = 'redshift'
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
        new_line = prefix + 'redshift_decimals' + ' = ' + str(n_decimals_redshift) + '\n'

        # check if there is no , at the end
        if new_line[-2:] == ', ':
            new_line = new_line[:-2]
        new_line += '\n'
        lines[line_index[0]] = new_line

        with open(file_name, 'w', encoding='utf-8') as file:
            file.writelines(lines)

    @staticmethod
    def create_output_band_list_str(output_band_dict, include_err=False):
        """
        Function to create a cigale string list for filter names
        Parameters
        ----------
        output_band_dict : dict
        """
        output_band_list_str = []
        if output_band_dict is not None:
            if 'hst' in output_band_dict.keys():
                if 'acs' in output_band_dict['hst'].keys():
                    for band in output_band_dict['hst']['acs']:
                        output_band_list_str.append(CigaleHelper.get_hst_filter_name(band=band, instrument='acs'))
                        if include_err:
                            output_band_list_str.append(CigaleHelper.get_hst_filter_name(band=band, instrument='acs') + '_err')

                if 'uvis' in output_band_dict['hst'].keys():
                    for band in output_band_dict['hst']['uvis']:
                        output_band_list_str.append(CigaleHelper.get_hst_filter_name(band=band, instrument='uvis'))
                        if include_err:
                            output_band_list_str.append(CigaleHelper.get_hst_filter_name(band=band, instrument='uvis') + '_err')
                if 'ir' in output_band_dict['hst'].keys():
                    for band in output_band_dict['hst']['ir']:
                        output_band_list_str.append(CigaleHelper.get_hst_filter_name(band=band, instrument='ir'))
                        if include_err:
                            output_band_list_str.append(CigaleHelper.get_hst_filter_name(band=band, instrument='ir') + '_err')
            if 'jwst' in output_band_dict.keys():
                if 'nircam' in output_band_dict['jwst'].keys():
                    for band in output_band_dict['jwst']['nircam']:
                        output_band_list_str.append(CigaleHelper.get_jwst_filter_name(band=band,  instrument='nircam'))
                        if include_err:
                            output_band_list_str.append(CigaleHelper.get_jwst_filter_name(band=band, instrument='nircam') + '_err')
                if 'miri' in output_band_dict['jwst'].keys():
                    for band in output_band_dict['jwst']['miri']:
                        output_band_list_str.append(CigaleHelper.get_jwst_filter_name(band=band,  instrument='miri'))
                        if include_err:
                            output_band_list_str.append(CigaleHelper.get_jwst_filter_name(band=band, instrument='miri') + '_err')
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


