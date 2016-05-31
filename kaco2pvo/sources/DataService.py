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

class DataService:
    """ class containing data service """

    def clear_data_service(self):
        """ clears this data service data """
        self._data_service['host_url'] = ""
        self._data_service['host_uri_status'] = ""
        self._data_service['host_uri_output'] = ""
        self._data_service['host_batch_uri_status'] = ""
        self._data_service['host_batch_uri_output'] = ""
        self._data_service['client_key'] = ""
        self._data_service['client_system_id'] = ""
        self._data_service['host_status_interval'] = ""
        self._data_service['is_ready_to_upload'] = False

    def create_data_service(self):
        """ creates reding dictionary """
        self._data_service = {}
        return self._data_service


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

    def set_client_key(self, client_key):
        """ Sets the client key """
        self._data_service['client_key'] = client_key

    def set_client_system_id(self, client_system_id):
        """ Sets the client system ID """
        self._data_service['client_system_id'] = client_system_id

    def set_host_status_interval(self, host_status_interval):
        """ Sets the host interval """
        self._data_service['host_status_interval'] = host_status_interval

    def get_is_ready_to_upload(self):
        """ returns whether the system data service is ready to upload """
        return self._data_service['is_ready_to_upload']

    def do_upload(self):
        """ Do the upload """
        """ TODO """

    def __init__(self):
        """ class initialiser """
        self._data_service = self.create_data_service()
        self.clear_data_service()


