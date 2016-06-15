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


class Mode(Enum):
    output = 1
    status = 2
    batchoutput = 3
    batchstatus = 4


class DataService:
    """ class containing data service """

    _data_service = {}
    _mode = Mode.output

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
        self._data_service['max_batch_status_samples'] = 0
        self._data_service['max_batch_data_samples'] = 0

    def create_data_service(self):
        """ creates reding dictionary """
        self._data_service = {}
        return self._data_service

    def set_max_batch_status_samples(self, max):
        """ Sets the maximum number of status samples that can be uploaded in batch mode """
        self._data_service['max_batch_status_samples'] = max

    def set_max_batch_data_samples(self, max):
        """ Sets the maximum number of data samples that can be uploaded in batch mode """
        self._data_service['max_batch_data_samples'] = max

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
        """ Do the upload """
        """ TODO """
        """ Do the batchstatus upload """
        """ This is the upload which occurs regularly as the data is being read"""
        # stats = generator.get_stats()
        # readings = generator.get_readings()

        # print("there are count_readings - ",len(readings))
        print("there are count_stats - ", len(stats))

        for i in range(len(stats)):
            mystat = stats[i]

            params = {
                'd': mystat.get_time_of_stat(),  # TODO Convert to correct date format yyyymmdd
                't': mystat.get_time_of_stat(),  # TODO Convert to correct time format hh:mm
                'v1': mystat.get_average_energy_generated_this_sample_period(),
                'v2': mystat.get_average_power_generated_this_sample_period(),
                'v3': 0,  # Energy used not currently implemented by KACO
                'v4': 0,  # Power used not currently implemented by KACO,
                'v5': mystat.get_average_temperature_this_sample_period(),
                'v6': mystat.get_average_voltage_this_sample_period(),
                'c1': 0,
                'n': 0}
            print("batch status uploaded params would be - ", params)

    def do_batch_data_upload(self):
        """ Do the upload """
        """ TODO """

    def do_status_upload(self, stats):
        """ Do the status upload """
        """ This is the uload which occurs regularly as the data is being read"""
        """ TODO """
        params = {'d': stats['reading_time'].strftime('%Y%m%d'),
                  't': stats['reading_time'].strftime('%H:%M'),
                  'v1': stats['energy_generated_this_sample_period'],
                  'v2': stats['power_generated_this_sample_period'],
                  'v3': stats['energy_used_this_sample-period'],
                  'v4': stats['power_used_this_sample_period'],
                  'v5': stats['temperature_average_this_sample_period'],
                  'v6': stats['voltage_average_this_sample_period'],
                  'c1': 0,
                  'n': 0}
        print("status uploaded params would be - ", params)

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

    def post(self, _params):
        """ Performs posting to pvoutput.org """
        if not self._data_service['testing']:
            try:
                if self.get_mode() == Mode['output']:
                    uri = self.get_host_uri_output()
                elif self.get_mode() == Mode['output_batch']:
                    uri = self.get_host_batch_uri_output()
                elif self.get_mode() == Mode['status']:
                    uri = self.get_host_uri_status()
                elif self.get_mode() == Mode['status_batch']:
                    uri = self.get_host_batch_uri_status()
                else:
                    raise Exception("Invalid operating mode attempted").with_traceback()

                # LOGGER4.debug("Posting results - " + str(params))
                headers = {'X-Pvoutput-Apikey': self._data_service['client_key'],
                           'X-Pvoutput-SystemId': self._data_service['client_system_id'],
                           "Accept": "text/plain",
                           "Content-type": "application/x-www-form-urlencoded"}
                conn = http.client.HTTPConnection(self.get_host_url())
                #               conn.set_debuglevel(2) # debug purposes only
                conn.request("POST", uri, urllib.parse.urlencode(_params), headers)
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
            return True

    def __init__(self):
        """ class initialiser """
        self._data_service = self.create_data_service()
        self.clear_data_service()
