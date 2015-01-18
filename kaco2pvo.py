#!/usr/bin/env python
""" Process to take serial data from Kaco inverter and upload
 to pvoutput.org """
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

from datetime import datetime
import serial
import sys
import time

# Import requirements for logging
import logging
import logging.handlers

LOG_FILENAME = '/var/log/solar/kaco2pv.log'
LOG_READINGS_FILENAME = '/var/log/solar/kaco2pv_readings.log'


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

LOGGER6 = logging.getLogger('')
pvdata = logging.handlers.TimedRotatingFileHandler(LOG_READINGS_FILENAME,
                                                   when='midnight',
                                                   interval=1,
                                                   backupCount=14,
                                                   encoding=None,
                                                   delay=False,
                                                   utc=False)
pvdata.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
pvdata.setFormatter(formatter)
LOGGER6.addHandler(pvdata)

# Example log usage
# LOGGER1.debug('Quick zephyrs blow, vexing daft Jim.')
# LOGGER1.info('How quickly daft jumping zebras vex.')
# LOGGER2.warning('Jail zesty vixen who grabbed pay from quack.')
# LOGGER2.error('The five boxing wizards jump quickly.')

LOGGER1.info("pvs2pvo - (c) Ian Hutt 2014")
LOGGER1.info("modified by Chris Peck for Kaco Inverters")
LOGGER1.info("Startup")

# May need changing
PVS_DEVICE = "/dev/ttyUSB0"
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

_totalUse = 0.0
totalGen = 0.0
totalAmps = 0.0
totalVolts = 0.0
totalReadings = 0
lastStatus = datetime.min

dailyUse = 0.0
dailyGen = 0.0
dailyEnergy = 0.0
minTemp = 100
maxTemp = -100
dailyReadings = 0
lastOutput = datetime.min
# set last daily summary output to epoch ie never
peakGen = 0.0
peakTime = datetime.now()
# latest time after which it is decided that there aren't a full days readings
sunriseHour = 9
fullDaysReadings = False


def num(stringToConvert):
    """ returns an int or float from string """
    try:
        return int(stringToConvert)
    except ValueError:
        return float(stringToConvert)


class powerReading:
    """ class containing power reading data """
    _timeOfReading = datetime.min
    _dailyRunTime = 0
    _operatingState = 0
    _generatorVoltage = 0.0
    _generatorCurrent = 0.0
    _generatorPower = 0.0
    _lineVoltage = 0.0
    _lineCurrentFeedIn = 0.0
    _powerFeedIn = 0.0
    _unitTemperature = 0.0

    def timeOfReading(self):
        """ returns time of reading """
        return self._timeOfReading

    def generatedPower(self):
        """ returns generated power """
        return self._generatorPower

    def temperature(self):
        """ returns temperature """
        return self._unitTemperature

    def generatedVoltage(self):
        """ returns generated voltage """
        return self._generatorVoltage

    def generatedCurrent(self):
        """ returns generated current """
        return self._generatorCurrent

    def __init__(self, timeOfReading, dailyRunTime, operatingState,
                 generatorVoltage,
                 generatorCurrent,
                 generatorPower, lineVoltage, lineCurrentFeedIn,
                 powerFeedIn, unitTemperature):
        self._timeOfReading = timeOfReading
        self._dailyRunTime = dailyRunTime
        self._operatingState = operatingState
        self._generatorVoltage = generatorVoltage
        self._generatorCurrent = generatorCurrent
        self._generatorPower = generatorPower
        self._lineVoltage = lineVoltage
        self._lineCurrentFeedIn = lineCurrentFeedIn
        self._powerFeedIn = powerFeedIn
        self._unitTemperature = unitTemperature


def post(uri, params):
    """ Performs posting to pvoutput.org """
    if not LOCAL_ONLY_TESTING:
        try:
            LOGGER4.debug("Posting results - " + params)
            headers = {'X-Pvoutput-Apikey': PVO_KEY,
                       'X-Pvoutput-SystemId': PVO_SYSTEM_ID,
                       "Accept": "text/plain",
                       "Content-type": "application/x-www-form-urlencoded"}
            conn = http.client.HTTPConnection(PVO_HOST)
#               conn.set_debuglevel(2) # debug purposes only
            conn.request("POST", uri, urllib.parse.urlencode(params), headers)
            response = conn.getresponse()
            LOGGER4.debug("Status" + response.status + "   Reason:" +
                          response.reason + "-" + response.read())
            sys.stdout.flush()
            conn.close()
            return response.status == 200
        except Exception as e:
            LOGGER4.error("Exception posting results\n" + str(e))
            sys.stdout.flush()
            return False
    else:
        LOGGER4.debug("In testing mode - NOT posting results")
        return True


def postPVstatus(pvsTimeOfReading, pvsEnergyGen,
                 pvsPowerGen, pvsEnergyUse, pvsPowerUse, pvsTemp, pvsVolts):
    """ Create string and pass it to status posting """
    params = {'d': time.strftime('%Y%m%d', pvsTimeOfReading),
              't': time.strftime('%H:%M', pvsTimeOfReading),
              'v1': pvsEnergyGen,
              'v2': pvsPowerGen,
              'v3': pvsEnergyUse,  # for later use if required
              'v4': pvsPowerUse,
              'v5': pvsTemp,
              'v6': pvsVolts,
              'c1': 0,
              'n': 0}

    LOGGER4.debug("Params:" + params)
    # POST the data
    return post(PVO_STATUS_URI, params)


def postPVoutput(pvoDateOfOutput, pvoGenerated, pvoExported, pvoPeakPower,
                 pvoPeakTime,
                 pvoCondition, pvoMinTemp, pvoMaxTemp,
                 pvoImportPeak, pvoImportOffPeak, pvoImportShoulder,
                 pvoImportHighShoulder, pvoConsumption, pvoComment):
    """ Create string and pass it to post function """
    params = {'d': time.strftime('%Y%m%d', pvoDateOfOutput),
              'g': pvoGenerated,
              'e': pvoExported,
              'pp': pvoPeakPower,
              'pt': time.strftime('%H:%M', pvoPeakTime),
              'tm': pvoMinTemp,
              'tx': pvoMaxTemp,
              'ip': pvoImportPeak,
              'io': pvoImportOffPeak,
              'is': pvoImportShoulder,
              'ih': pvoImportHighShoulder,
              'c': pvoConsumption,
              'cm': 'EOD upload.'
                    + pvoComment}
    LOGGER4.debug("Params:" + params)
    return post(PVO_OUTPUT_URI, params)


def addReading(newPowerReading):
    """ Add a power reading """
    gen = newPowerReading.generatedPower()
    volts = newPowerReading.generatedVoltage()
    temperature = newPowerReading.temperature()
    amps = newPowerReading.generatedCurrent()
    # timeNow = time.localtime()
    timeNow = datetime.now()

    comment = ""
    global totalGen, totalReadings, lastStatus, totalAmps, totalVolts
    totalGen += gen
    totalAmps += amps
    totalVolts += volts
    totalReadings += 1
    global dailyEnergy, dailyGen, dailyReadings
    global lastOutput, peakGen, peakTime, fullDaysReadings, maxTemp, minTemp
    dailyGen += gen
    dailyEnergy += (gen*SAMPLE_TIME)
    dailyReadings += 1
    LOGGER3.info("Gen:" + str(gen) + "W " + str(dailyEnergy) + "Wh "
                 + str(volts) + "V " + str(amps) + "A")
    if gen > peakGen:
        peakGen = int(gen)
        peakTime = timeNow
    if temperature > maxTemp:
        maxTemp = temperature
    if temperature < minTemp:
        minTemp = temperature
    if (timeNow.minute % PVO_STATUS_INTERVAL == 0) & (lastStatus.minute != timeNow.minute):
        # You may wish to modify the simplistic averaging for something
        # more sophisticated like weighted average or kalman
        avgGen = float(totalGen / totalReadings)
        avgVoltage = float(totalVolts / totalReadings)
        avgCurrent = float(totalAmps / totalReadings)
        LOGGER3.info("Time to output status. avgGen:" +
                     str(avgGen) + "W " + str(avgVoltage) + "V " + str(avgCurrent) + "A")
        if postPVstatus(timeNow, dailyEnergy,
                        avgGen, 0, 0, temperature, avgVoltage):
            lastStatus = timeNow
            totalGen = 0.0
            totalAmps = 0.0
            totalVolts = 0.0
            totalReadings = 0
            LOGGER3.info("Status update sucessfully sent to PVoutput")
        else:
            lastStatus = timeNow
            LOGGER3.error(time.strftime('%Y-%m-%d %H:%M:%S',
                                        time.localtime()),
                          "Failed to post status to pvoutput")
        sys.stdout.flush()
    LOGGER2.debug("Debugging daily summary")
    LOGGER2.debug("timeNow.hour = " + str(timeNow.hour))
    LOGGER2.debug("timeNow.minute = " + str(timeNow.minute))
    LOGGER2.debug("timeNow.day = " + str(timeNow.day))
    LOGGER2.debug("lastOutput.day = " + str(lastOutput.day))
    if (timeNow > PV_DAILY_UPLOAD_TIME) and (timeNow.day > lastOutput.day):
        daysGen = int((dailyGen / dailyReadings) * 24.0)
        LOGGER2.info("Time to output EOD")
        LOGGER2.info("DaysGen:" + str(daysGen) + "W")
        if not fullDaysReadings:
            LOGGER2.info("Incomplete days readings.")
            comment = "Incomplete readings for days"
        if postPVoutput(timeNow, daysGen, 0, peakGen, peakTime, 'Not Sure',
                        minTemp, maxTemp, 0, 0, 0, 0, 0, comment):
            lastOutput = timeNow
            dailyGen = 0
            dailyReadings = 0
            peakGen = 0
            peakTime = timeNow
            minTemp = 100
            maxTemp = -100
            dailyEnergy = 0
            LOGGER2.info("EOD Output sucessfully sent to PVoutput")
        else:
            LOGGER2.error("Failed to post daily output to pvoutput")
        fullDaysReadings = True
    sys.stdout.flush()


def processReading(readingToProcess):
    """ Take string and process into component parts of reading """
    LOGGER6.info(readingToProcess)
    LOGGER5.debug("Reading data" + readingToProcess)
    myReadings = readingToProcess.split()
    placeHolder = myReadings[0]
    LOGGER5.debug("placeHolder = " + placeHolder)
    dailyRunTime = myReadings[1]
    LOGGER5.debug("dailyRunTime = " + str(dailyRunTime))
    operatingState = myReadings[2]
    LOGGER5.debug("operatingState = " + str(operatingState))
    generatorVoltage = num(myReadings[3])
    LOGGER5.debug("generatorVoltage = " + str(generatorVoltage))
    generatorCurrent = num(myReadings[4])
    LOGGER5.debug("generatorCurrent = " + str(generatorCurrent))
    generatorPower = num(myReadings[5])
    LOGGER5.debug("generatorPower = " + str(generatorPower))
    lineVoltage = num(myReadings[6])
    LOGGER5.debug("lineVoltage = " + str(lineVoltage))
    lineCurrentFeedIn = num(myReadings[7])
    LOGGER5.debug("lineCurrentFeedIn = " + str(lineCurrentFeedIn))
    powerFeedIn = num(myReadings[8])
    LOGGER5.debug("powerFeedIn = " + str(powerFeedIn))
    unitTemperature = num(myReadings[9])
    LOGGER5.debug("unitTemperature = " + str(unitTemperature))
    LOGGER5.debug("Processing data")
    if generatorPower < PVS_MIN_PVP:
        generatorPower = 0
    elif generatorPower > PVS_MAX_PVP:
        generatorPower = PVS_MAX_PVP

    newReading = powerReading(datetime.utcnow(), dailyRunTime, operatingState,
                              generatorVoltage, generatorCurrent,
                              generatorPower, lineVoltage, lineCurrentFeedIn,
                              powerFeedIn, unitTemperature)
    addReading(newReading)

try:
    LOGGER5.info("Opening PV inverter serial port on " + str(PVS_DEVICE))
    COM_PORT = serial.Serial(PVS_DEVICE, baudrate=9600, bytesize=8,
                             parity='N', stopbits=1, xonxoff=0, timeout=5.0)
    COM_PORT.open()

    if COM_PORT.isOpen():
        COM_PORT.flush()
        LOGGER5.info("PV inverter connection opened")
    else:
        LOGGER5.error("Unable to open connection to PV inverter")

    LOGGER5.info("Processing PV inverter data")

    START_TIME = datetime.now()
    if START_TIME.hour < sunriseHour:
        fullDaysReadings = False
        LOGGER5.info("Not a full days readings")
    else:
        fullDaysReadings = True
        LOGGER5.info("A full days readings")

    sys.stdout.flush()
    myBuffer = ''
    while COM_PORT.isOpen():
        try:
            myBuffer += COM_PORT.read(max(1, COM_PORT.inWaiting())).decode('utf-8', "replace")
        except Exception as ex:
            LOGGER5.error("Exception reading from PV inverter. Terminating\n" + str(ex))
            LOGGER5.error("Check that another process is not using device")
            COM_PORT.close()
            sys.stdout.flush()
        if '\r' in myBuffer:
            readings = myBuffer.split('\r')
            myBuffer = readings.pop()
            for newReading in readings:
                processReading(newReading)

    COM_PORT.close()
except Exception as e:
    LOGGER1.error("Exception processing PV inverter data. Terminating\n" + str(e))
    sys.stdout.flush()


LOGGER1.info("Bye")
sys.stdout.flush()
