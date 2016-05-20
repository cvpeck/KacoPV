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

from datetime import datetime
#from PowerReading import PowerReading

class Generator:
    """ class describing a Generator """

    def get_is_ready_to_read(self):
        """ returns whether the generator is ready to read """
        return self

    def create_generator(self):
        """ creates the Generator dictionary """
        self._generator = {}
        self._myreadings = []
        self._mystats = []


    def set_time_daily_upload(self, time_daily_upload):
        """ sets the daily data upload time for the generator """
        self._generator['time_daily_upload'] = time_daily_upload

    def set_path_device(self, path_to_device):
        """ sets the path to the serial data device """
        self._generator['path_to_device'] = path_to_device

    def set_power_min(self, power_min):
        """ sets the minimum power """
        self._generator['power_min'] = power_min

    def set_power_max(self, power_max):
        """ sets the maximum power """
        self._generator['power_max'] = power_max

    def set_time_sample_period(self, time_sample_period):
        """ sets sampling period """
        self._generator['time_sample_period'] = time_sample_period

    def get_is_reading_from_file(self):
        """ returns true if we are reading from file """
        return self._generator['is_reading_from_file']

    def get_readings_daily(self):
        """ returns daily readings """
        return self._generator['readings_daily']

    def get_time_output_last(self):
        """ returns time of last output """
        return self._generator['time_output_last']

    def set_time_sunrise(self, time_sunrise):
        """ sets sunrise time """
        self._generator['time_sunrise'] = time_sunrise

    def clear_generator(self):
        """ clears generator """
        self._generator['path_to_device'] = ''
        self._generator['power_min'] = 0.0
        self._generator['power_max'] = 0.0
        self._generator['time_sample_period'] = datetime.min
        self._generator['time_daily_upload'] = datetime.min
        self._generator['is_reading_from_file'] = False
        self._generator['readings_daily'] = 0
        self._generator['time_output_last'] = datetime.min
        self._generator['reading_is_full_day'] = False
        self._generator['time_reading'] = datetime.min
        self._generator['time_sunrise'] = datetime.min

        del self._myreadings[:]
        del self._mystats[:]

    def __init__(self):
        """ class initialiser """
        self.create_generator()
        self.clear_generator()


