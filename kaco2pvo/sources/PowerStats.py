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

from datetime import datetime

class PowerStats:
    """ class containing power statistics data """

    _stats = {}  # dictionary to store stats
    _reading_count = 0  # number of readings
    _time_sample_period = 0  # time sample period

    def get_stats(self):
        """ returns stats """
        return self._stats

    def caclulate_stats(self, power_reading):
        """ forces recalculation of stats """
        self._stats['generated_total'] += power_reading.get_generator_power()
        self._stats['amps_total'] += power_reading.get_generator_current()
        self._stats['volts_total'] += power_reading.get_generator_voltage()
        if self._stats['generated_peak'] < power_reading.get_generator_power():
            self._stats['generated_peak'] = power_reading.get_generator_power()
            self._stats['time_peak'] = datetime.now()
        if self._stats['temperature_max'] < power_reading.get_generator_temperature():
            self._stats['temperature_max'] = power_reading.get_generator_temperature()
        if self._stats['temperature_min'] > power_reading.get_generator_temperature():
            self._stats['temperature_min'] = power_reading.get_generator_temperature()
        self._stats['output_last'] = datetime.now()
        self._stats['generated_average'] = self._stats['generated_total'] / self._reading_count
        self._stats['current_average'] = self._stats['amps_total'] / self._reading_count
        self._stats['voltage_average'] = self._stats['volts_total'] / self._reading_count
        # If we don't have a full days readings, assume we get 12 hrs of the average reading
        self._stats['incomplete_average_generated_daily'] = (self._stats['generated_total'] / self._reading_count) * 12
        self._stats['energy_daily'] += power_reading.get_generator_power() * self.get_time_sample_period()

        # TODO reading from file does not have valid timestamps

    def print_stats(self):
        """ prints stats for generator to console """
        print('number of readings   = ', self.get_reading_count())
        print('generated total      = ', self._stats['generated_total'])
        print('last status          = ', self._stats['status_last'])
        print('amps total           = ', self._stats['amps_total'])
        print('volts total          = ', self._stats['volts_total'])
        print('energy daily         = ', self._stats['energy_daily'])
        print('incomplete_average_generated_daily       = ', self._stats['incomplete_average_generated_daily'])
        print('output last          = ', self._stats['output_last'])
        print('generated peak       = ', self._stats['generated_peak'])
        print('time peak            = ', self._stats['time_peak'])
        print('reading is full day  = ', self._stats['reading_is_full_day'])
        print('temperature max      = ', self._stats['temperature_max'])
        print('temperature min      = ', self._stats['temperature_min'])
        print('generated average    = ', self._stats['generated_average'])
        print('current average      = ', self._stats['current_average'])
        print('voltage average      = ', self._stats['voltage_average'])
        print('reading time         = ', self._stats['reading_time'])

    def create_stats(self):
        """ creates stats dictionary """
        self._stats = {}
        return self._stats

    def set_reading_count(self, count):
        """ sets reading count"""
        self._reading_count = count

    def get_reading_count(self):
        """ gets reading count"""
        return self._reading_count

    def set_time_sample_period(self, time_sample_period):
        """ set timesample period """
        self._time_sample_period = time_sample_period

    def get_time_sample_period(self):
        """ get time sample period """
        return self._time_sample_period

    def clear_stats(self):
        """ clears stats """
        self._stats['generated_total'] = 0.0
        self._stats['status_last'] = 0
        self._stats['amps_total'] = 0.0
        self._stats['volts_total'] = 0.0
        self._stats['energy_daily'] = 0.0
        self._stats['generated_daily'] = 0.0
        self._stats['incomplete_average_generated_daily'] = 0
        self._stats['output_last'] = datetime.min
        self._stats['generated_peak'] = 0.0
        self._stats['time_peak'] = datetime.min
        self._stats['reading_is_full_day'] = False
        self._stats['temperature_max'] = -254
        self._stats['temperature_min'] = 255
        self._stats['generated_average'] = 0.0
        self._stats['current_average'] = 0.0
        self._stats['voltage_average'] = 0.0
        self._stats['reading_time'] = datetime.min
        self.set_reading_count(0)

    def __init__(self):
        """ class initialiser """
        self._stats = self.create_stats()
        self.clear_stats()
