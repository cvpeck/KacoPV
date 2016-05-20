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
    # Supplied with limited tested for others to tailor to their own needs
    #
    # This software in any form is covered by the following Open Source BSD license
    #
    # Copyright 2013-2014, Ian Hutt
    # All rights reserved.
    #
    # Redistribution and use in source and binary forms, with or without
    # modification, are permitted provided that the following conditions are met:
    #
    # 1. Redistributions of source code must retain the above copyright notice,
    # this list of conditions and the following disclaimer.
    #
    # 2. Redistributions in binary form must reproduce the above copyright notice,
    # this list of conditions and the following disclaimer in the documentation
    # and/or other materials provided with the distribution.
    #
    # THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS
    # AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
    # THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
    # PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER
    # OR CONTRIBUTORS BE LIABLE FOR
    # ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY OR CONSEQUENTIAL DAMAGES
    # (INCLUDING, BUT NOT LIMITE
    # TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
    # OR PROFITS; OR BUSINESS INTERRUPTION)
    # HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
    # STRICT LIABILITY, OR TORT (INCLUDING
    # NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
    # EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
    #
    """

class DataService:
    """ class containing data service """

    def clear_data_service(self):
        """ clears this data service data """
        self._data_service['host_url'] = ""
        self._data_service['host_uri_status'] = ""
        self._data_service['host_uri_output'] = ""
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


