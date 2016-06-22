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
    """

from datetime import datetime, timedelta
import re
from PowerReading import PowerReading
from PowerStats import PowerStats
from Utilities import num
import csv
import os


class Generator:
    """ class describing a Generator """
    _generator = {}
    _running_stat = PowerStats()
    _output = []
    _myreadings = []
    _mystats = []
    _reading_count = 0
    _sample_reading_count = 0
    _time_of_first_sample_in_set = datetime.strptime("06:00:00", "%H:%M:%S")

    def get_is_ready_to_read(self):
        """ returns whether the generator is ready to read """
        if self.get_time_output_last():  # TODO
            ready = True
        else:
            ready = False
        return ready

    def do_reading(self):
        """ makes generator fetch a reading """
        reading = PowerReading()
        reading.create_reading()
        self._myreadings.append(reading)
        self._onestat.caclulate_stats(reading)

    def get_stats(self):
        return self._mystats

    def get_readings(self):
        return self._myreadings

    def get_number_of_readings(self):
        """ get number of readings generator has taken """
        return self._reading_count

    def get_output(self):
        """ returns the running stat which is basically the 'output' for uploading """
        return self._output

    def set_time_daily_upload(self, time_daily_upload):
        """ sets the daily data upload time for the generator """
        self._generator['time_daily_upload'] = time_daily_upload

    def set_path_to_device(self, path_to_device):
        """ sets the path to the serial data device """
        self._generator['path_to_device'] = path_to_device

    def set_path_to_data(self, path_to_data):
        """ sets the path to the serial data file """
        self._generator['path_to_data'] = path_to_data

    def get_path_to_data(self):
        """ gets the path to the data"""
        return self._generator['path_to_data']

    def set_data_start_time(self, data_start_time):
        """ sets the start time of data read from a file """
        self._generator['data_start_time'] = data_start_time

    def get_data_start_time(self):
        """ gets the start time of data read from a file """
        return self._generator['data_start_time']

    def set_power_min(self, power_min):
        """ sets the minimum power """
        self._generator['power_min'] = power_min

    def set_power_max(self, power_max):
        """ sets the maximum power """
        self._generator['power_max'] = power_max

    def set_time_sample_period(self, time_sample_period):
        """ sets sampling period """
        self._generator['time_sample_period'] = time_sample_period

    def get_time_sample_period(self):
        """ gets sampling period """
        return self._generator['time_sample_period']

    def get_is_reading_from_file(self):
        """ returns true if we are reading from file """
        return self._generator['path_to_data'] != ""

    def set_file_date(self, file_date):
        """ date for data if not contained withing filename """
        self._generator['file_date'] = file_date

    def get_file_date(self):
        """ date for data if not contained withing filename """
        return self._generator['file_date']

    def get_readings_daily(self):
        """ returns daily readings """
        return self._generator['readings_daily']

    def is_comment(self, line):
        return line.startswith('#')

    # Kind of sily wrapper
    def is_whitespace(self, line):
        return line.isspace()

    def import_readings(self):
        # TODO implement reading from directory
        if self.get_is_reading_from_file():
            my_list = {}
            input_path = self.get_path_to_data()
            if os.path.isdir(input_path):
                search_path = os.walk(input_path)
            elif os.path.isfile(input_path):
                search_path = os.path.normpath(input_path)
            else:
                raise Exception("Invalid data file or directory").with_traceback()

            for root, dirs, files in search_path:
                for name in files:
                    try:
                        fin = open(os.path.join(root, name), 'rt')
                        print(fin.name)
                        # setting filedate from command line overrides reading it from filename
                        if self.get_file_date() == datetime.min:
                            d = re.search("([0-9]{4}\-[0-9]{2}\-[0-9]{2})", fin.name)
                            print(d.group(0))
                            if d.group(0):
                                self.set_file_date(datetime.strptime(d.group(0), "%Y-%m-%d"))
                            else:
                                print("no date found in filename")

                        data_reader = csv.reader(
                            (line for line in fin if not line.startswith('#') and not line.isspace()),
                            delimiter=' ')
                        for row in data_reader:
                            i = 0
                            for x in row:
                                if x != '':
                                    # print(i,'=',x)
                                    my_list[i] = x
                                    i += 1
                            my_reading = PowerReading()
                            onestat = PowerStats()
                            # if date is not min (i.e it has been explicitly set or read from filename
                            if self.get_file_date() != datetime.min:

                                # set placeholder value in reading to timedate plus run time
                                rtd = datetime.strptime(my_list[1], "%H:%M:%S")
                                # rtd read from file is of the form 01:36:10
                                dst = self.get_data_start_time()
                                fd = self.get_file_date() + timedelta(hours=dst.hour, minutes=dst.minute,
                                                                      seconds=dst.second)
                                timeofreading = fd + timedelta(hours=rtd.hour, minutes=rtd.minute, seconds=rtd.second)

                            else:
                                # otherwise use value already in file
                                timeofreading = my_list[0].strftime("%H.%M.%S")

                            # Since we're reading from file, time sample period is current time - last reading time (1st in set)
                            time_sample_period = timeofreading - self._time_of_first_sample_in_set

                            onestat.set_time_sample_period(time_sample_period)
                            self._running_stat.set_time_sample_period(time_sample_period)

                            _add_to_stack = False
                            # so we can only upload data in bulk with minute resolution
                            if timeofreading.minute != self._time_of_first_sample_in_set.minute:
                                self._time_of_first_sample_in_set = timeofreading
                                self._sample_reading_count = 0
                                _add_to_stack = True

                            my_reading.set_placeholder(timeofreading.strftime("%H.%M.%S"))
                            my_reading.set_run_time_daily(
                                datetime.strptime(my_list[1], "%H:%M:%S"))
                            my_reading.set_operating_state(my_list[2])
                            my_reading.set_generator_voltage(num(my_list[3]))
                            my_reading.set_generator_current(num(my_list[4]))
                            my_reading.set_generator_power(num(my_list[5]))
                            my_reading.set_line_voltage(num(my_list[6]))
                            my_reading.set_line_current_feed_in(num(my_list[7]))
                            my_reading.set_line_power_feed_in(num(my_list[8]))
                            my_reading.set_generator_temperature(num(my_list[9]))
                            self._reading_count += 1
                            self._sample_reading_count += 1
                            self._myreadings.append(my_reading)
                            self._running_stat.set_total_reading_count(self._reading_count)
                            self._running_stat.set_sample_reading_count(self._sample_reading_count)
                            self._running_stat.caclulate_stats(my_reading, self.get_file_date())
                            self._output.append(self._running_stat)
                            if _add_to_stack:
                                onestat.set_total_voltage(self._running_stat.get_total_voltage())
                                onestat.set_total_current(self._running_stat.get_total_current())
                                onestat.set_total_power(self._running_stat.get_total_power())
                                onestat.set_total_energy(self._running_stat.get_total_energy())
                                onestat.set_total_temperature(self._running_stat.get_total_temperature())
                                onestat.set_total_reading_count(self._reading_count)
                                onestat.set_sample_reading_count(self._sample_reading_count)
                                onestat.caclulate_stats(my_reading, self.get_file_date())
                                self._mystats.append(onestat)
                                _add_to_stack = False

                    finally:
                        if 'fin' in locals():
                            fin.close()

    def get_time_output_last(self):
        """ returns time of last output """
        return self._generator['time_output_last']

    def set_time_sunrise(self, time_sunrise):
        """ sets sunrise time """
        self._generator['time_sunrise'] = time_sunrise

    def clear_generator(self):
        """ clears generator """
        self._generator['path_to_device'] = ''
        self._generator['path_to_file'] = ''
        self._generator['path_to_dir'] = ''
        self._generator['power_min'] = 0.0
        self._generator['power_max'] = 0.0
        self._generator['time_sample_period'] = timedelta(hours=0, minutes=0, seconds=10)
        self._generator['time_daily_upload'] = datetime.min
        self._generator['is_reading_from_file'] = False
        self._generator['readings_daily'] = 0
        self._generator['time_output_last'] = datetime.min
        self._generator['reading_is_full_day'] = False
        self._generator['time_reading'] = datetime.min
        self._generator['time_sunrise'] = datetime.min
        self._generator['data_start_time'] = datetime.min
        self._generator['file_date'] = datetime.min
        self._reading_count = 0
        self._sample_reading_count = 0
        del self._myreadings[:]
        del self._mystats[:]
        self._running_stat.clear_stats()

    def print_stats(self):
        """ prints stats for generator to console"""
        print(" There are %i stats", len(self._mystats))
        for i in range(len(self._mystats)):
            mystat = self._mystats[i]
            mystat.print_stats()

    def print_readings(self):
        """ prints readings for generator to console """
        print(" There are %i readings", len(self._myreadings))
        for i in range(len(self._myreadings)):
            myreading = self._myreadings[i]
            myreading.print_reading()

    def __init__(self):
        """ class initialiser """
        self.clear_generator()
