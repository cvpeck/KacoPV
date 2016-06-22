#!/usr/bin/env python
""" @package docstring
    Documentation for this module

    Process to take serial data from Kaco inverter and upload
    to pvoutput.org
    # Upload from Kaco Powador serial output to pvoutput.org live feed
    #
    #
    # To be run on RaspberryPi Python3 (IDLE3) using Prolific USB/Serial cable
    # To download required serial library from terminal prompt:
    #
    # sudo apt-get install python3-serial
    #

    """
from datetime import datetime, timedelta
import time

import sys
import urllib, urllib.parse
import http.client
from enum import Enum
import math


class Mode(Enum):
    output = 1
    status = 2
    output_batch = 3
    status_batch = 4


class DataService:
    """ class containing data service """

    _data_service = {}
    _mode = Mode.output
    _params_list = []

    def clear_data_service(self):
        """ clears this data service data """
        self._data_service['host_url'] = ""
        self._data_service['host_uri_status'] = ""
        self._data_service['host_uri_output'] = ""
        self._data_service['host_batch_uri_status'] = ""
        self._data_service['host_batch_uri_output'] = ""
        self._data_service['client_key'] = ""
        self._data_service['client_system_id'] = ""
        self._data_service['host_status_interval'] = timedelta(hours=0, minutes=5, seconds=0)
        self._data_service['is_ready_to_upload'] = False
        self._data_service['time_last_upload'] = datetime.min
        self._data_service['mode'] = Mode.output
        self._data_service['testing'] = True
        self._data_service['max_batch_status_size'] = 0
        self._data_service['max_batch_output_size'] = 0
        self._data_service['max_batch_status_age'] = 0
        self._data_service['max_batch_output_age'] = 0

    def create_data_service(self):
        """ creates reding dictionary """
        self._data_service = {}
        return self._data_service

    def set_max_batch_status_size(self, max):
        """ Sets the maximum number of status samples that can be uploaded in batch mode """
        self._data_service['max_batch_status_size'] = max

    def set_max_batch_output_size(self, max):
        """ Sets the maximum number of output samples that can be uploaded in batch mode """
        self._data_service['max_batch_output_size'] = max

    def set_max_batch_status_age(self, max):
        """ Sets the maximum age of status samples that can be uploaded in batch mode """
        self._data_service['max_batch_status_age'] = max

    def set_max_batch_output_age(self, max):
        """ Sets the maximum age of output samples that can be uploaded in batch mode """
        self._data_service['max_batch_output_age'] = max

    def get_max_batch_status_size(self):
        """ Gets the maximum number of status samples that can be uploaded in batch mode """
        return self._data_service['max_batch_status_size']

    def get_max_batch_output_size(self):
        """ Gets the maximum number of output samples that can be uploaded in batch mode """
        return self._data_service['max_batch_output_size']

    def get_max_batch_status_age(self):
        """ Gets the maximum age of status samples that can be uploaded in batch mode """
        return self._data_service['max_batch_status_age']

    def get_max_batch_output_age(self):
        """ Gets the maximum age of output samples that can be uploaded in batch mode """
        return self._data_service['max_batch_output_age']


    def set_testing(self, testing):
        """ Turns off uploading """
        self._data_service['testing'] = testing

    def set_mode(self, mode):
        """ sets the operating mode of the data service """
        self._data_service['mode'] = mode

    def get_mode(self):
        """ gets the operating mode of the data service"""
        return self._data_service['mode']

    def set_host_url(self, host_url):
        """ sets the URL for the data service host """
        self._data_service['host_url'] = host_url

    def set_host_uri_output(self, host_uri_output):
        """ sets the URI for outputting data to on the host """
        self._data_service['host_uri_output'] = host_uri_output

    def set_host_uri_status(self, host_uri_status):
        """ sets the URI for outputting status to on the host """
        self._data_service['host_uri_status'] = host_uri_status

    def set_host_batch_uri_output(self, host_uri_batch_output):
        """ sets the URI for batch uploading data to on the host """
        self._data_service['host_uri_batch_output'] = host_uri_batch_output

    def set_host_batch_uri_status(self, host_batch_uri_status):
        """ sets the URI for batch uploading status to on the host """
        self._data_service['host_batch_uri_status'] = host_batch_uri_status

    def get_host_url(self):
        """ gets the URL for the data service host """
        return self._data_service['host_url']

    def get_host_uri_output(self):
        """ gets the URI for outputting data to on the host """
        return self._data_service['host_uri_output']

    def get_host_uri_status(self):
        """ gets the URI for outputting status to on the host """
        return self._data_service['host_uri_status']

    def get_host_batch_uri_output(self):
        """ gets the URI for batch uploading data to on the host """
        return self._data_service['host_uri_batch_output']

    def get_host_batch_uri_status(self):
        """ gets the URI for batch uploading status to on the host """
        return self._data_service['host_batch_uri_status']

    def set_client_key(self, client_key):
        """ Sets the client key """
        self._data_service['client_key'] = client_key

    def set_client_system_id(self, client_system_id):
        """ Sets the client system ID """
        self._data_service['client_system_id'] = client_system_id

    def set_host_status_interval(self, host_status_interval):
        """ Sets the host interval """
        self._data_service['host_status_interval'] = host_status_interval

    def get_host_status_interval(self):
        """ Gets the host interval """
        return self._data_service['host_status_interval']

    def set_host_time_last_upload(self, host_time_last_upload):
        """ Sets the last upload time """
        self._data_service['time_last_upload'] = host_time_last_upload

    def get_host_time_last_upload(self):
        """ Gets the last upload time """
        return self._data_service['host_time_last_upload']

    def get_is_ready_to_upload(self):
        """ returns whether the system data service is ready to upload """
        if datetime.now > self.get_host_time_last_upload() + self.get_host_status_interval():
            self._data_service['is_ready_to_upload'] = True
        else:
            self._data_service['is_ready_to_upload'] = False
        return self._data_service['is_ready_to_upload']

    def do_batch_status_upload(self, stats):
        """ Constructs batch of status data to upload  """
        """ This is the upload which occurs regularly as the data is being read"""
        self.set_mode(Mode.status_batch)
        print("there are count_stats - ", len(stats))
        for i in range(len(stats)):
            mystat = stats[i]
            if mystat.get_time_of_stat() + self.get_max_batch_status_age() > datetime.now():
                params = {
                    'd': mystat.get_time_of_stat().strftime('%Y%m%d'),
                    't': mystat.get_time_of_stat().strftime('%H:%M'),
                    'v1': int(mystat.get_average_energy_generated_this_sample_period()),
                    'v2': int(mystat.get_average_power_generated_this_sample_period()),
                    'v3': int(0),  # Energy used not currently implemented by KACO
                    'v4': int(0),  # Power used not currently implemented by KACO,
                    'v5': mystat.get_average_temperature_this_sample_period(),
                    'v6': mystat.get_average_voltage_this_sample_period(),
                    'c1': 0,
                    'n': 0}
                print("batch status uploaded params would be ", params)
                self._params_list.append(params)
            else:
                print("skipping too old data from ", mystat.get_time_of_stat())
        self.post()

    def do_batch_output_upload(self, output):
        """ Constructs batch of output data to upload  """
        """ This is the upload which occurs on a daily basis """
        # TODO - all of the below is just a copy of the batch status output at present
        self.set_mode(Mode.output_batch)
        print("there are count_output - ", len(output))
        for i in range(len(output)):
            myoutput = output[i]
            if myoutput.get_time_of_stat() + self.get_max_batch_output_age() < datetime.now():  # TODO changed > to < for testing
                params = {
                    'd': myoutput.get_time_of_stat().strftime('%Y%m%d'),
                    'g': myoutput.get_total_power(),
                    'e': int(0),  # exported not currently implemented # TODO
                    'pp': myoutput.get_max_power(),
                    'pt': myoutput.get_max_time(),
                    'cd': "Not Sure",  # TODO - look up weather
                    'tm': myoutput.get_min_temp(),
                    'tx': myoutput.get_max_temp(),
                    'cm': "",  # TODO comment field add EOD for end of day reading
                    'ip': int(0),  # TODO import peak
                    'io': int(0),  # TODO import off peak
                    'is': int(0),  # TODO import shoulder
                    'ih': int(0),  # TODO import high shoulder
                    'c': int(0)  # TODO consumption
                }
                print("batch output uploaded params would be ", params)
                self._params_list.append(params)
            else:
                print("skipping too old data from ", myoutput.get_time_of_stat())
        self.post()

    def do_status_upload(self, stats):
        """ Do the status upload """
        """ This is the upload which occurs regularly as the data is being read"""
        """ TODO """

        params = {'d': stats['reading_time'].strftime('%Y%m%d'),
                  't': stats['reading_time'].strftime('%H:%M'),
                  'v1': int(stats['energy_generated_this_sample_period']),
                  'v2': int(stats['power_generated_this_sample_period']),
                  'v3': int(stats['energy_used_this_sample-period']),
                  'v4': int(stats['power_used_this_sample_period']),
                  'v5': stats['temperature_average_this_sample_period'],
                  'v6': stats['voltage_average_this_sample_period'],
                  'c1': 0,
                  'n': 0}
        print("status uploaded params would be - d=%s t=%s ", params['d'])

    # def do_data_upload(self):
    #     """ Do the upload """
    #     """ TODO """
    # params = {'d': pvoDateOfOutput.strftime('%Y%m%d'),
    #           'g': pvoGenerated,
    #           'e': pvoExported,
    #           'pp': pvoPeakPower,
    #           'pt': pvoPeakTime.strftime('%H:%M'),
    #           'tm': pvoMinTemp,
    #           'tx': pvoMaxTemp,
    #           'ip': pvoImportPeak,
    #           'io': pvoImportOffPeak,
    #           'is': pvoImportShoulder,
    #           'ih': pvoImportHighShoulder,
    #           'c': pvoConsumption,
    #           'cm': 'EOD upload.'
    #                 + pvoComment}

    def post(self):
        """ Performs posting to pvoutput.org """
        if self.get_mode() == Mode['output']:
            uri = self.get_host_uri_output()
            post_size = 1
        elif self.get_mode() == Mode['output_batch']:
            uri = self.get_host_batch_uri_output()
            post_size = self.get_max_batch_output_size()
        elif self.get_mode() == Mode['status']:
            uri = self.get_host_uri_status()
            post_size = 1
        elif self.get_mode() == Mode['status_batch']:
            uri = self.get_host_batch_uri_status()
            post_size = self.get_max_batch_status_size()
        else:
            raise Exception("Invalid operating mode attempted").with_traceback()

                # LOGGER4.debug("Posting results - " + str(params))
        headers = {'X-Pvoutput-Apikey': self._data_service['client_key'],
                   'X-Pvoutput-SystemId': self._data_service['client_system_id'],
                   "Accept": "text/plain",
                   "Content-type": "application/x-www-form-urlencoded"}

        count = post_size
        while True:
            data = "data="
            params_slice = self._params_list[count - post_size:count]
            for params in params_slice:
                if self.get_mode() == (Mode['status'] or Mode['status_batch']):
                    data += str(params['d']) + "," \
                            + str(params['t']) + "," \
                            + str(params['v1']) + "," \
                            + str(params['v2']) + "," \
                            + str(params['v3']) + "," \
                            + str(params['v4']) + "," \
                            + str(params['v5']) + "," \
                            + str(params['v6']) + ";"
                elif self.get_mode() == (Mode['output'] or Mode['output_batch']):
                    data += str(params['d']) + "," \
                            + str(params['g']) + "," \
                            + str(params['e']) + "," \
                            + str(params['pp']) + "," \
                            + str(params['pt']) + "," \
                            + str(params['cd']) + "," \
                            + str(params['tm']) + "," \
                            + str(params['tx']) + "," \
                            + str(params['cm']) + "," \
                            + str(params['ip']) + "," \
                            + str(params['io']) + "," \
                            + str(params['is']) + "," \
                            + str(params['ih']) + "," \
                            + str(params['c']) + ";"
                else:
                    raise Exception("Invalid operating mode attempted").with_traceback()

            if not self._data_service['testing']:
                try:
                    conn = http.client.HTTPConnection(self.get_host_url())
                    #               conn.set_debuglevel(2) # debug purposes only
                    conn.request("POST", uri, urllib.parse.urlencode(data), headers)
                    response = conn.getresponse()
                    # LOGGER4.debug("Status" + str(response.status) + "   Reason:" +
                    #             str(response.reason) + "-" + str(response.read()))
                    sys.stdout.flush()
                    conn.close()
                    return response.status == 200

                except Exception as e:
                    # LOGGER4.error("Exception posting results\n" + str(e))
                    sys.stdout.flush()
                    return False
            else:
                # LOGGER4.debug("In testing mode - NOT posting results")
                print("data posted would have been ", data)
            count += post_size
            if len(params_slice) < post_size:
                break;

    def __init__(self):
        """ class initialiser """
        self._data_service = self.create_data_service()
        self.clear_data_service()
