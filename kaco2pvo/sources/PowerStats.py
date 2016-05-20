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

class PowerStats:
    """ class containing power statistics data """

    def get_stats(self):
        """ returns stats """
        return self._stats

    def caclulate_stats(self, power_reading):
        """ forces recalculation of stats """
        self._stats['generated_total'] += power_reading['generated_power']
        self._stats['amps_total'] += power_reading['generator_current']
        self._stats['volts_total'] += power_reading['generator_voltage']
        if self._stats['generated_peak'] < power_reading['generated_peak']:
            self._stats['generated_peak'] = power_reading['generated_peak']
            self._stats['time_peak'] = power_reading['time_peak']
        if self._stats['temperature_max'] < power_reading['generator_temperature']:
            self._stats['temperature_max'] = power_reading['generator_temperature']
        if self._stats['temperature_min'] > power_reading['generator_temperature']:
            self._stats['temperature_min'] = power_reading['generator_temperature']


        # TODO
        self._stats['energy_daily'] = 0.0
        self._stats['generated_daily'] = 0.0
        self._stats['readings_daily'] = 0.0
        self._stats['output_last'] = datetime.min
        self._stats['generated_average'] = 0.0
        self._stats['current_average'] = 0.0
        self._stats['voltage_average'] = 0.0



    def create_stats(self):
        """ creates stats dictionary """
        self._stats = {}
        return self._stats

    def clear_stats(self):
        """ clears stats """
        self._stats['generated_total'] = 0.0
        self._stats['status_last'] = 0
        self._stats['amps_total'] = 0.0
        self._stats['volts_total'] = 0.0
        self._stats['energy_daily'] = 0.0
        self._stats['generated_daily'] = 0.0
        self._stats['readings_daily'] = 0
        self._stats['output_last'] = datetime.min
        self._stats['generated_peak'] = 0.0
        self._stats['time_peak'] = datetime.min
        self._stats['reading_is_full_day'] = False
        self._stats['temperature_max'] = 0.0
        self._stats['temperature_min'] = 0.0
        self._stats['generated_average'] = 0.0
        self._stats['current_average'] = 0.0
        self._stats['voltage_average'] = 0.0
        self._stats['reading_time'] = datetime.min

    def __init__(self):
        """ class initialiser """
        self._stats = self.create_stats()
        self.clear_stats()