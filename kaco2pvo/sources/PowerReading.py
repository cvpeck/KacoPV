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

class PowerReading:
    """ class containing power reading """

    _reading = {}

    def get_stats(self):
        """ returns stats """
        return self

    def create_reading(self):
        """ creates reding dictionary """
        self._reading = {}
        return self._reading

    def print_reading(self):
        """ prints a reading to the console """
        print(self._reading)

    def set_placeholder(self, placeholder):
        """ set placeholder """
        self._reading['placeholder'] = placeholder

    def set_run_time_daily(self, run_time_daily):
        """ set run time daily """
        self._reading['run_time_daily'] = run_time_daily

    def set_operating_state(self, operating_state):
        """ set operating state """
        self._reading['operating_state'] = operating_state

    def set_generator_voltage(self, generator_voltage):
        """ set generator voltage """
        self._reading['generator_voltage'] = generator_voltage

    def set_generator_current(self, generator_current):
        """ set generator current """
        self._reading['generator_current'] = generator_current

    def set_generator_power(self, generator_power):
        """ set generator power """
        self._reading['generator_power'] = generator_power

    def set_line_voltage(self, line_voltage):
        """ set line voltage """
        self._reading['line_voltage'] = line_voltage

    def set_line_current_feed_in(self, line_current_feed_in):
        """ set line current feed in """
        self._reading['line_currrent_feed_in'] = line_current_feed_in

    def set_line_power_feed_in(self, line_power_feed_in):
        """ set line power feed in """
        self._reading['line_power_feed_in'] = line_power_feed_in

    def set_generator_temperature(self, generator_temperature):
        """ set generator temperature """
        self._reading['generator_temperature'] = generator_temperature

    def get_run_time_daily(self):
        """ get run time daily """
        return self._reading['run_time_daily']

    def get_operating_state(self):
        """ get generator state """
        return self._reading['operating_state']

    def get_generator_voltage(self):
        """ get generator voltage """
        return self._reading['generator_voltage']

    def get_generator_current(self):
        """ get generator current """
        return self._reading['generator_current']

    def get_generator_power(self):
        """ get generator power """
        return self._reading['generator_power']

    def get_line_voltage(self):
        """ get line voltage """
        return self._reading['line_voltage']

    def get_line_current_feed_in(self):
        """ get line current feed in """
        return self._reading['line_currrent_feed_in']

    def get_line_power_feed_in(self):
        """ get line power feed in """
        return self._reading['line_power_feed_in']

    def get_generator_temperature(self):
        """ get generator temperature """
        return self._reading['generator_temperature']




    def clear_reading(self):
        """ clears stats """
        self._reading['placeholder'] = '00.00.0000'
        self._reading['run_time_daily'] = datetime.min
        self._reading['operating_state'] = 0
        self._reading['generator_voltage'] = 0.0
        self._reading['generator_current'] = 0.0
        self._reading['generator_power'] = 0
        self._reading['line_voltage'] = 0.0
        self._reading['line_current_feed_in'] = 0.0
        self._reading['line_power_feed_in'] = 0
        self._reading['generator_temperature'] = 0

    def __init__(self):
        """ class initialiser """
        self._reading = self.create_reading()
        self.clear_reading()

