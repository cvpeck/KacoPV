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

# Import utilities
from Utilities import *
from datetime import datetime, timedelta


class PowerStats:
    """ class containing power statistics data """

    _stats = {}  # dictionary to store stats
    _total_reading_count = 0  # number of readings
    _sample_reading_count = 0  # the number of readings taken in this sample period

    def get_stats(self):
        """ returns stats """
        return self._stats

    def caclulate_stats(self, power_reading, start_date):
        """ forces recalculation of stats """
        # Energy calculations
        # Generated
        time_sample_period = self.get_time_sample_period()
        time_sample_hours = convert_timedelta_to_hours(time_sample_period)

        string_time_of_reading = power_reading.get_placeholder()
        time_of_reading = datetime.strptime(string_time_of_reading, "%H.%M.%S")
        date_time_of_reading = datetime(year=start_date.year,
                                        month=start_date.month,
                                        day=start_date.day,
                                        hour=time_of_reading.hour,
                                        minute=time_of_reading.minute,
                                        second=time_of_reading.second)

        self._stats['time_of_stat'] = date_time_of_reading

        self._stats['energy_generated_this_sample_period'] += \
            power_reading.get_generator_power() * time_sample_hours
        self._stats['energy_generated_total'] += \
            power_reading.get_generator_power() * time_sample_hours
        self._stats['energy_generated_average'] = \
            self._stats['energy_generated_total'] / self.get_total_reading_count()
        self._stats['energy_generated_average_this_sample_period'] = \
            self._stats['energy_generated_this_sample_period'] / self.get_sample_reading_count()
        # Consumed
        # self._stats['energy_consumed_this_sample_period'] += \
        #     power_reading.get_generator_power() * time_sample_hours
        # self._stats['energy_consumed_total'] += \
        #     power_reading.get_generator_power() * time_sample_hours
        # self._stats['energy_consumed_average'] = \
        #     self._stats['energy_consumed_total'] / self.get_total_reading_count()
        # self._stats['energy_consumed_average_this_sample_period'] = \
        #     self._stats['energy_consumed_this_sample_period'] / self.get_sample_reading_count()

        # Power calculations
        # Generated
        if self._stats['power_generated_peak'] < power_reading.get_generator_power():
            self._stats['power_generated_peak'] = power_reading.get_generator_power()
            self._stats['time_peak'] = time_of_reading

        self._stats['power_generated_this_sample_period'] += power_reading.get_generator_power()
        self._stats['power_generated_total'] += power_reading.get_generator_power()
        self._stats['power_generated_average'] = self._stats['power_generated_total'] / self.get_total_reading_count()
        self._stats['power_generated_average_this_sample_period'] = \
            self._stats['power_generated_this_sample_period'] / self.get_sample_reading_count()
        # # Consumed
        # if self._stats['power_consumed_peak'] < power_reading.get_generator_consumed_power():
        #     self._stats['power_comsumed_peak'] = power_reading.get_generator_consumed_power()
        #     self._stats['time_peak'] = datetime.now()
        # self._stats['power_consumed_this_sample_period'] += power_reading.get_generator_consumed_power()
        # self._stats['power_consumed_total'] += power_reading.get_generator_consumed_power()
        # self._stats['power_consumed_average'] = self._stats['power_consumed_total'] / self.get_total_reading_count()
        # self._stats['power_consumed_average_this_sample_period'] = \
        #     self._stats['power_consumed_average_this_sample_period'] / self.get_sample_reading_count()

        # Voltage calculations
        self._stats['voltage_this_sample_period'] += power_reading.get_generator_voltage()
        self._stats['voltage_total'] += power_reading.get_generator_voltage()
        self._stats['voltage_average'] = self._stats['voltage_total'] / self.get_total_reading_count()
        self._stats['voltage_average_this_sample_period'] = self._stats['voltage_this_sample_period'] \
                                                            / self.get_sample_reading_count()

        # Current calculations
        self._stats['current_this_sample_period'] += power_reading.get_generator_current()
        self._stats['current_total'] += power_reading.get_generator_current()
        self._stats['current_average'] = self._stats['current_total'] \
                                         / self.get_total_reading_count()
        self._stats['current_average_this_sample_period'] = self._stats['current_this_sample_period'] \
                                                            / self.get_sample_reading_count()

        # Temperature calculations
        if self._stats['temperature_max'] < power_reading.get_generator_temperature():
            self._stats['temperature_max'] = power_reading.get_generator_temperature()
        if self._stats['temperature_min'] > power_reading.get_generator_temperature():
            self._stats['temperature_min'] = power_reading.get_generator_temperature()

        self._stats['temperature_this_sample_period'] += power_reading.get_generator_temperature()
        self._stats['temperature_total'] += power_reading.get_generator_temperature()
        self._stats['temperature_average'] = self._stats['temperature_total'] / self.get_total_reading_count()
        self._stats['temperature_average_this_sample_period'] = self._stats['temperature_this_sample_period'] \
                                                                / self.get_sample_reading_count()

    def print_stats(self):
        """ prints stats for generator to console """
        print(self._stats)

    def create_stats(self):
        """ creates stats dictionary """
        self._stats = {}
        return self._stats

    def set_total_voltage(self, voltage):
        """ sets total voltage"""
        self._stats['voltage_total'] = voltage

    def set_total_current(self, current):
        """ sets total current"""
        self._stats['current_total'] = current

    def set_total_power(self, power):
        """ sets total power"""
        self._stats['power_generated_total'] = power

    def set_total_energy(self, energy):
        """ sets total energy"""
        self._stats['energy_generated_total'] = energy

    def set_total_temperature(self, temperature):
        """ sets total temperature"""
        self._stats['temperature_total'] = temperature

    def get_total_voltage(self):
        """ gets total voltage"""
        return self._stats['voltage_total']

    def get_total_current(self):
        """ gets total current"""
        return self._stats['current_total']

    def get_total_power(self):
        """ gets total power"""
        return self._stats['power_generated_total']

    def get_total_energy(self):
        """ gets total energy"""
        return self._stats['energy_generated_total']

    def get_total_temperature(self):
        """ gets total temperature"""
        return self._stats['temperature_total']

    def get_time_of_stat(self):
        """ gets time of stat"""
        return self._stats['time_of_stat']

    def get_average_energy_generated_this_sample_period(self):
        """ gets average energy generated this sample period"""
        return self._stats['energy_generated_average_this_sample_period']

    def get_average_power_generated_this_sample_period(self):
        """ gets average power generated this sample period"""
        return self._stats['power_generated_average_this_sample_period']

    def get_average_voltage_this_sample_period(self):
        """ gets average voltage this sample period"""
        return self._stats['voltage_average_this_sample_period']

    def get_average_temperature_this_sample_period(self):
        """ gets average temeprature this sample period"""
        return self._stats['temperature_average_this_sample_period']

    def set_total_reading_count(self, count):
        """ sets reading count"""
        self._total_reading_count = count

    def get_total_reading_count(self):
        """ gets reading count"""
        return self._total_reading_count

    def set_sample_reading_count(self, count):
        """ sets reading count"""
        self._sample_reading_count = count

    def get_sample_reading_count(self):
        """ gets reading count"""
        return self._sample_reading_count

    def set_time_sample_period(self, time_sample_period):
        """ set timesample period """
        self._stats['time_sample_period'] = time_sample_period

    def get_time_sample_period(self):
        """ get time sample period """
        return self._stats['time_sample_period']

    def reset_sample_period(self):
        self.set_time_sample_period(timedelta(hours=0, minutes=0, seconds=0))
        self.set_sample_reading_count(0)
        self._stats['energy_generated_this_sample_period'] = 0
        self._stats['energy_generated_average_this_sample_period'] = 0
        self._stats['energy_consumed_average_this_sample_period'] = 0
        self._stats['energy_consumed_this_sample_period'] = 0
        self._stats['power_generated_this_sample_period'] = 0
        self._stats['power_generated_average_this_sample_period'] = 0
        self._stats['power_consumed_this_sample_period'] = 0
        self._stats['power_consumed_average_this_sample_period'] = 0
        self._stats['voltage_this_sample_period'] = 0
        self._stats['voltage_average_this_sample_period'] = 0
        self._stats['current_this_sample_period'] = 0
        self._stats['current_average_this_sample_period'] = 0
        self._stats['temperature_this_sample_period'] = 0
        self._stats['temperature_average_this_sample_period'] = 0

    def clear_stats(self):
        """ clears stats """
        self.set_total_reading_count(0)
        self._stats['energy_generated_total'] = 0
        self._stats['energy_generated_average'] = 0
        self._stats['energy_consumed_total'] = 0
        self._stats['energy_consumed_average'] = 0
        self._stats['power_generated_total'] = 0
        self._stats['power_generated_average'] = 0
        self._stats['power_generated_peak'] = 0
        self._stats['power_consumed_total'] = 0
        self._stats['power_consumed_average'] = 0
        self._stats['power_consumed_peak'] = 0
        self._stats['voltage_total'] = 0
        self._stats['voltage_average'] = 0
        self._stats['current_total'] = 0
        self._stats['current_average'] = 0
        self._stats['temperature_max'] = -254
        self._stats['temperature_min'] = 255
        self._stats['temperature_total'] = 0
        self._stats['temperature_average'] = 0
        self._stats['timeofstat'] = datetime.min


    def __init__(self):
        """ class initialiser """
        self._stats = self.create_stats()
        self.clear_stats()
        self.reset_sample_period()
