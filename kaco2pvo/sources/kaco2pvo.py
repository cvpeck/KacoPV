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

# Import utilities
from Utilities import *

# Import requirements for logging
# import logging
import logging.handlers

from Generator import Generator
from PowerReading import PowerReading
from DataService import DataService
from PowerStats import PowerStats

import argparse

LOG_BASEDIR = "/var/log/solar/"
LOG_FILENAME = LOG_BASEDIR + "kaco2pv.log"
LOG_READINGS_FILENAME = LOG_BASEDIR + "kaco2pv_readings.log"

make_sure_path_exists(LOG_BASEDIR)

# Setup logging
# set up logging to file
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=LOG_FILENAME,
                    filemode='w')
# define a Handler which writes INFO messages or higher to the sys.stderr
CONSOLE = logging.StreamHandler()
CONSOLE.setLevel(logging.DEBUG)  # was info
# set a format which is simpler for console use
FORMATTER = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
CONSOLE.setFormatter(FORMATTER)
# add the handler to the root logger
logging.getLogger('').addHandler(CONSOLE)

# Now, we can log to the root logger, or any other logger. First the root...
# logging.info('Jackdaws love my big sphinx of quartz.')

# Now, define a couple of other loggers which might represent areas in your
# application:

# general logging
LOGGER1 = logging.getLogger('kaco2pv.general')
# logging info for daily output
LOGGER2 = logging.getLogger('kaco2pv.dailyreadings')
# logging info for regular output
LOGGER3 = logging.getLogger('kaco2pv.readings')
# logging info for posting
LOGGER4 = logging.getLogger('kaco2pv.posting')
# logging info for inverter
LOGGER5 = logging.getLogger('kaco2pv.inverter')

# Now logging specifically of the data received from the inverter

LOGGER6 = logging.getLogger('kaco2pv.raw')
PVDATA = logging.handlers.TimedRotatingFileHandler(LOG_READINGS_FILENAME,
                                                   when='midnight',
                                                   interval=1,
                                                   backupCount=14,
                                                   encoding=None,
                                                   delay=False,
                                                   utc=False)
PVDATA.setLevel(logging.INFO)
FORMATTER = logging.Formatter('%(message)s')
PVDATA.setFormatter(FORMATTER)
LOGGER6.addHandler(PVDATA)

# Example log usage
# LOGGER1.debug('Quick zephyrs blow, vexing daft Jim.')
# LOGGER1.info('How quickly daft jumping zebras vex.')
# LOGGER2.warning('Jail zesty vixen who grabbed pay from quack.')
# LOGGER2.error('The five boxing wizards jump quickly.')

# -f file -d directory -k key foreground daemon

LOGGER1.info("pvs2pvo - (c) Ian Hutt 2014")
LOGGER1.info("modified by Chris Peck for Kaco Inverters")
LOGGER1.info("Startup")

# TODO
PVS_DATA_INPUT_FILE = "../data/from_kaco/solar/kaco2pv_readings.log.2016-05-10"
PVS_DATA_INPUT_DIR = ""

DAEMON = False

# May need changing
# Device normally used on Raspberry pi
PVS_DEVICE = "/dev/ttyUSB0"
# Device used on Mac
# PVS_DEVICE = "/dev/cu.usbserial"
# PV generation values (W) less than this will be set to 0
PVS_MIN_PVP = 7.5
# PV generation values greater than this will be set to this
PVS_MAX_PVP = 6000.0

PVS_READING_FROM_FILE = False

PVO_HOST = "pvoutput.org"
PVO_STATUS_URI = "/service/r2/addstatus.jsp"
PVO_OUTPUT_URI = "/service/r2/addoutput.jsp"
PVO_STATUS_BATCH_URI = "/service/r2/addbatchstatus.jsp"
PVO_OUTPUT_BATCH_URI = "/service/r2/addbatchoutput.jsp"

PVO_KEY = "7ed8a297d387d3887dbd8059c5d8544382a4a12b"
# Your PVoutput system ID here
PVO_SYSTEM_ID = "24657"
# How often in minutes to update PVoutput
PVO_STATUS_INTERVAL = "00:05:00"
# Maximum number of batch statuses that can be uploaded in one go
PVO_MAX_BATCH_STATUS_SIZE = 30
# Maximum number of batch outputs that can be uploaded in one go
PVO_MAX_BATCH_OUTPUT_SIZE = 30
# Maximum age (days) of batch statuses that can be uploaded
PVO_MAX_BATCH_STATUS_AGE = 14
# Maximum age (days) of batch outputs that can be uploaded in one go
PVO_MAX_BATCH_OUTPUT_AGE = 14
# Time in hours of updates from Kaco unit (normally 10 seconds)
PVS_SAMPLE_TIME_DEFAULT = "00:00:10"
t = datetime.strptime(PVS_SAMPLE_TIME_DEFAULT, "%H:%M:%S")

PVS_SAMPLE_TIME = timedelta(hours=t.hour, minutes=t.minute,
                            seconds=t.second)

PVS_DAILY_UPLOAD_TIME = "23:45"

# latest time after which it is decided that there aren't a full days readings
PVS_SUNRISE = "09:00"
PVS_DATA_START_TIME = "06:00:00"

# default date for file data if not specified in filename
datemin = datetime.min
datenow = datetime.now()
PVS_FILE_DATE = datemin.strftime("%Y-%m-%d")

PVS_TIME_NOW = datenow.strftime("%Y%m%d")

PVS_OUTPUT_DIRECTORY = '/var/log/solar'

# create the top-level parser
parser = argparse.ArgumentParser(description='Process data from KacoPV system and upload to pvoutput.org')

# parser for pv service arguments - part of main, not sub parser
parser.add_argument('--pvoutput_key', action='store',
                    help='key for uploading to pvoutput.org')
parser.add_argument('--pvoutput_systemid', action='store',
                    help='systemid for uploading to pvoutput.org')
parser.add_argument('--pvoutput_host', action='store',
                    help='host for uploading data to',
                    default=PVO_HOST)
parser.add_argument('--pvstatus_uri', action='store',
                    help='uri for uploading status data to',
                    default=PVO_STATUS_URI)
parser.add_argument('--pvoutput_uri', action='store',
                    help='uri for uploading output data to',
                    default=PVO_OUTPUT_URI)
parser.add_argument('--pv_batch_status_uri', action='store',
                    help='uri for batch uploading status data to',
                    default=PVO_OUTPUT_BATCH_URI)
parser.add_argument('--pv_batch_output_uri', action='store',
                    help='uri for batch uploading output data to',
                    default=PVO_STATUS_BATCH_URI)
parser.add_argument('--pvoutput_status_interval', action='store',
                    help='interval for updating status with service provider (HH:MM:SS)',
                    default=PVO_STATUS_INTERVAL)
parser.add_argument('--latest_time', action='store',
                    help='latest time which panels should be generating by (HH:MM:SS)',
                    default=PVS_SUNRISE)
parser.add_argument('--pv_max_batch_status_size', action='store',
                    help='maximum number of batch statuses that can be uploaded in one go',
                    default=PVO_MAX_BATCH_STATUS_SIZE)
parser.add_argument('--pv_max_batch_output_size', action='store',
                    help='maximum number of batch outputs that can be uploaded in one go',
                    default=PVO_MAX_BATCH_OUTPUT_SIZE)
parser.add_argument('--pv_max_batch_status_age', action='store',
                    help='maximum age (days) of batch statuses that can be uploaded',
                    default=PVO_MAX_BATCH_STATUS_AGE)
parser.add_argument('--pv_max_batch_output_age', action='store',
                    help='maximum age (days) of batch outputs that can be uploaded',
                    default=PVO_MAX_BATCH_OUTPUT_AGE)

subparsers = parser.add_subparsers(help='help for subcommand', dest='subparser_name')

# create the parser for the "import" command
parser_a = subparsers.add_parser('import', help='import and upload data from existing file or directory')
group_a = parser_a.add_mutually_exclusive_group()
group_a.add_argument('--input_directory', nargs='?', action='store',
                     help='directory to read existing solar data from',
                     default='')
group_a.add_argument('--input_file', nargs='?', action='store',
                     help='individual file to upload solar data from',
                     default='')
parser_a.add_argument('--file_date', action='store',
                      help='date of file for data upload if not specified in filename %YYYY-%MM-%DD',
                      default=PVS_FILE_DATE)
parser_a.add_argument('--start_time', action='store',
                      help='start time of data to upload (HH:MM:SS)',
                      default=PVS_DATA_START_TIME)

# create the parser for the "capture" command
parser_b = subparsers.add_parser('capture', help='capture and upload data from an external device')
parser_b.add_argument('--output_directory', action='store',
                      help='destination for solar logs',
                      default=PVS_OUTPUT_DIRECTORY)
parser_b.add_argument('--daemon', action='store_true',
                      help='start backgroung monitoring of solar data',
                      required=False, default=False)
parser_b.add_argument('--device', action='store',
                      help='device for capturing serial data from',
                      default=PVS_DEVICE)
parser_b.add_argument('--sample_time', action='store',
                      help='sample time for device (HH:MM:SS)',
                      default=PVS_SAMPLE_TIME)

args = parser.parse_args()
print(args)

if args.subparser_name == 'import':
    if args.input_directory != '':
        PVS_DATA_INPUT_DIR = args.input_directory
    if args.input_file != '':
        PVS_DATA_INPUT_FILE = args.input_file
    if args.input_file or args.input_directory:
        PVS_READING_FROM_FILE = True
    if args.file_date:
        PVS_FILE_DATE = datetime.strptime(args.file_date, "%Y-%m-%d")
    if args.start_time:
        PVS_DATA_START_TIME = datetime.strptime(args.start_time, "%H:%M:%S")


if args.subparser_name == 'capture':
    if args.output_directory != '':
        PVS_OUTPUT_DIRECTORY = args.output_directory
    if args.daemon:
        DAEMON = args.daemon
    if args.device:
        PVS_DEVICE = args.device
    if args.sample_time:
        t = time.strptime(args.sample_time, "%H:%M:%S")
        PVS_SAMPLE_TIME = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)

if args.pvoutput_key:
    PVO_KEY = args.pvoutput_key
if args.pvoutput_systemid:
    PVO_SYSTEM_ID = args.pvoutput_systemid
if args.pvoutput_host:
    PVO_HOST = args.pvoutput_host
if args.pvoutput_status_interval:
    t = time.strptime(args.pvoutput_status_interval, "%H:%M:%S")
    PVO_STATUS_INTERVAL = timedelta(hours=t.tm_hour, minutes=t.tm_min, seconds=t.tm_sec)
if args.pvoutput_uri:
    PVO_OUTPUT_URI = args.pvoutput_uri
if args.pvstatus_uri:
    PVO_STATUS_URI = args.pvstatus_uri
if args.pv_batch_output_uri:
    PVO_OUTPUT_URI = args.pvoutput_uri
if args.pv_batch_status_uri:
    PVO_STATUS_URI = args.pvstatus_uri
if args.latest_time:
    PVS_SUNRISE = time.strptime(args.latest_time, "%H:%M:%S")
if args.pv_max_batch_output_age:
    PVO_MAX_BATCH_OUTPUT_AGE = args.pv_max_batch_output_age
if args.pv_max_batch_status_age:
    PVO_MAX_BATCH_STATUS_AGE = args.pv_max_batch_status_age
if args.pv_max_batch_output_size:
    PVO_MAX_BATCH_OUTPUT_SIZE = args.pv_max_batch_output_size
if args.pv_max_batch_status_size:
    PVO_MAX_BATCH_STATUS_SIZE = args.pv_max_batch_status_size

# Instantiate objects
MYKACOGENERATOR = Generator()
MYDATASERVICE = DataService()

# Configure data service
MYDATASERVICE.set_testing(True)
MYDATASERVICE.set_client_key(PVO_KEY)
MYDATASERVICE.set_client_system_id(PVO_SYSTEM_ID)
MYDATASERVICE.set_host_url(PVO_HOST)
MYDATASERVICE.set_host_uri_status(PVO_STATUS_URI)
MYDATASERVICE.set_host_uri_output(PVO_OUTPUT_URI)
MYDATASERVICE.set_host_status_interval(PVO_STATUS_INTERVAL)
MYDATASERVICE.set_max_batch_status_size(PVO_MAX_BATCH_STATUS_SIZE)
MYDATASERVICE.set_max_batch_output_size(PVO_MAX_BATCH_OUTPUT_SIZE)
MYDATASERVICE.set_max_batch_status_age(timedelta(days=PVO_MAX_BATCH_STATUS_AGE))
MYDATASERVICE.set_max_batch_output_age(timedelta(days=PVO_MAX_BATCH_OUTPUT_AGE))

# Configure generator
if PVS_DATA_INPUT_DIR:
    MYKACOGENERATOR.set_path_dir(PVS_DATA_INPUT_DIR)
if PVS_DATA_INPUT_FILE:
    MYKACOGENERATOR.set_path_file(PVS_DATA_INPUT_FILE)
MYKACOGENERATOR.set_path_device(PVS_DEVICE)
MYKACOGENERATOR.set_power_max(PVS_MAX_PVP)
MYKACOGENERATOR.set_power_min(PVS_MIN_PVP)
MYKACOGENERATOR.set_time_daily_upload(PVS_DAILY_UPLOAD_TIME)
MYKACOGENERATOR.set_time_sunrise(PVS_SUNRISE)
MYKACOGENERATOR.set_time_sample_period(PVS_SAMPLE_TIME)
MYKACOGENERATOR.set_is_reading_from_file(PVS_READING_FROM_FILE)
MYKACOGENERATOR.set_data_start_time(PVS_DATA_START_TIME)
MYKACOGENERATOR.set_file_date(PVS_FILE_DATE)
MYKACOGENERATOR.import_readings()
MYKACOGENERATOR.print_readings()
MYKACOGENERATOR.print_stats()

MYDATASERVICE.do_batch_status_upload(MYKACOGENERATOR.get_stats())
