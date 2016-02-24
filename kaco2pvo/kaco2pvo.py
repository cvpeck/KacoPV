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


# Import utilities
import Utilities


# Import requirements for logging
import logging
import logging.handlers

LOG_BASEDIR = "/var/log/solar/"
LOG_FILENAME = LOG_BASEDIR + "kaco2pv.log"
LOG_READINGS_FILENAME = LOG_BASEDIR + "kaco2pv_readings.log"




Utilities.make_sure_path_exists(LOG_BASEDIR)

# Setup logging
# set up logging to file
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=LOG_FILENAME,
                    filemode='w')
# define a Handler which writes INFO messages or higher to the sys.stderr
CONSOLE = logging.StreamHandler()
CONSOLE.setLevel(logging.DEBUG) #was info
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

LOGGER1.info("pvs2pvo - (c) Ian Hutt 2014")
LOGGER1.info("modified by Chris Peck for Kaco Inverters")
LOGGER1.info("Startup")

# May need changing
# Device normally used on Raspberry pi
PVS_DEVICE = "/dev/ttyUSB0"
# Device used on Mac
# PVS_DEVICE = "/dev/cu.usbserial"
# PV generation values (W) less than this will be set to 0
PVS_MIN_PVP = 7.5
# PV generation values greater than this will be set to this
PVS_MAX_PVP = 6000.0

PVO_HOST = "pvoutput.org"
PVO_STATUS_URI = "/service/r2/addstatus.jsp"
PVO_OUTPUT_URI = "/service/r2/addoutput.jsp"


PVO_KEY = "7ed8a297d387d3887dbd8059c5d8544382a4a12b"
# Your PVoutput system ID here
PVO_SYSTEM_ID = "24657"
# How often in minutes to update PVoutput
PVO_STATUS_INTERVAL = 5
# Time in hours of updates from Kaco unit (normally 10 seconds)
SAMPLE_TIME = 10/3600

PV_DAILY_UPLOAD_TIME_HOUR = 23
PV_DAILY_UPLOAD_TIME_MIN = 45


TIME_NOW = datetime.now()
PV_DAILY_UPLOAD_TIME = TIME_NOW.replace(hour=PV_DAILY_UPLOAD_TIME_HOUR,
                                        minute=PV_DAILY_UPLOAD_TIME_MIN,
                                        second=0, microsecond=0)

# True for local only, False turns on pvoutput upload
LOCAL_ONLY_TESTING = False



from Generator import Generator
from PowerReading import PowerReading
from DataService import DataService

KACOGENERATOR = Generator()
MYREADING = PowerReading()
DATASERVICE = DataService()

DATASERVICE.set_host_url(PVO_HOST)
DATASERVICE.set_host_uri_status(PVO_STATUS_URI)
DATASERVICE.set_host_uri_output(PVO_OUTPUT_URI)



