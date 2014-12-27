#!/usr/bin/env python3

# Upload from Kaco Powador serial output to pvoutput.org live feed
#
#
# To be run on RaspberryPi Python3 (IDLE3) using Prolific based USB/Serial cable supplied with EcoEye
# To download required serial library from terminal prompt:
#
# sudo apt-get install python3-serial
#
# Supplied with limited tested for others to tailor to their own needs
#
# This software in any form is covered by the following Open Source BSD license:
#
# Copyright © 2013-2014, Ian Hutt
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, are permitted provided
# that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and
# the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and
# the following disclaimer in the documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

from datetime import datetime
import socket, time, serial, http.client, urllib, urllib.parse, sys, xml.etree.ElementTree as ET

# Import requirements for logging
import logging
import auxiliary_module


# Setup logging
# set up logging to file
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='/var/log/solar/kaco2pv.log',
                    filemode='w')
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

# Now, we can log to the root logger, or any other logger. First the root...
logging.info('Jackdaws love my big sphinx of quartz.')

# Now, define a couple of other loggers which might represent areas in your
# application:

#general logging
logger1 = logging.getLogger('kaco2pv.general')
#logging info for daily output
logger2 = logging.getLogger('kaco2pv.dailyreadings')
#logging info for regular output
logger3 = logger.getLogger('kaco2pv.readings')
#logging info for posting
logger4 = logger.getLogger('kaco2pv.posting')
#logging info for inverter
logger5 = logger.getLogger('kaco2pv.inverter')

# Example log usage
logger1.debug('Quick zephyrs blow, vexing daft Jim.')
logger1.info('How quickly daft jumping zebras vex.')
logger2.warning('Jail zesty vixen who grabbed pay from quack.')
logger2.error('The five boxing wizards jump quickly.')


logger1.info("pvs2pvo - (c) Ian Hutt 2014")
logger1.info("modified by Chris Peck for Kaco Inverters")
logger1.info("Startup ", time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))

pvs_device = "/dev/ttyUSB0"                             # May need changing
pvs_min_pvp = 7.5                                       # PV generation values (W) less than this will be set to 0
pvs_max_pvp = 6000.0                                    # PV generation values greater than this will be set to this

pvo_host= "pvoutput.org"
pvo_statusuri= "/service/r2/addstatus.jsp"
pvo_outputuri= "/service/r2/addoutput.jsp"


pvo_key = "7ed8a297d387d3887dbd8059c5d8544382a4a12b" 
pvo_systemid = "24657"                                  # Your PVoutput system ID here
pvo_statusInterval = 5                                  # How often in minutes to update PVoutput 
sampleTime = 10/3600					# Time in hours of updates from Kaco unit (normally 10 seconds)

pvDailyUploadTimeHour = 23 
pvDailyUploadTimeMin = 45

localOnlyTesting = False # True for local only, False turns on pvoutput upload

totalUse = 0.0
totalGen = 0.0
totalAmps = 0.0
totalVolts = 0.0
totalReadings = 0
lastStatus = time.localtime()

dailyUse = 0.0
dailyGen = 0.0
dailyEnergy = 0.0
minTemp = 100
maxTemp = -100
dailyReadings = 0
lastOutput = time.localtime()
lastOutput = time.gmtime(0) # set last daily summary output to epoch ie never
peakGen  = 0.0
peakTime = time.localtime()
sunriseHour = 9 # latest time after which it is decided that there aren't a full days readings
fullDaysReadings = False

def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

class powerReading:
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
        return self._timeOfReading
    
    def generatedPower(self):
        return self._generatorPower
    
    def temperature(self):
        return self._unitTemperature

    def generatedVoltage(self):
        return self._generatorVoltage 

    def generatedCurrent(self):
        return self._generatorCurrent
    
    def __init__(self, timeOfReading, dailyRunTime, operatingState, generatorVoltage, generatorCurrent, generatorPower, lineVoltage, lineCurrentFeedIn, powerFeedIn, unitTemperature):
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

def post( uri, params ):
    if (localOnlyTesting != True):
        try:
                logger4.debug("Posting results - ",params)
                headers = {'X-Pvoutput-Apikey' : pvo_key,
                           'X-Pvoutput-SystemId' : pvo_systemid,
                            "Accept" : "text/plain",
                            "Content-type": "application/x-www-form-urlencoded"}
                conn = http.client.HTTPConnection(pvo_host)
#               conn.set_debuglevel(2) # debug purposes only
                conn.request("POST", uri, urllib.parse.urlencode(params), headers)
                response = conn.getresponse()
                logger4.debug("Status", response.status, "   Reason:", response.reason, "-", response.read())
                sys.stdout.flush()
                conn.close()
       	        return response.status == 200
        except Exception as e:
                logger4.error("Exception posting results\n", e)
       	        sys.stdout.flush()
                return False
    else:
        logger4.debug("In testing mode - NOT posting results")
        return True
        

def postPVstatus(timeOfReading, energyGen, powerGen, energyUse, powerUse, temp, volts):
        params = {'d' : time.strftime('%Y%m%d',timeOfReading),
           't' : time.strftime('%H:%M', timeOfReading),
           'v1' : energyGen,
           'v2' : powerGen,
           'v3' : energyUse,  # for later use if required
           'v4' : powerUse,
           'v5' : temp,       
           'v6' : volts,
           'c1' : 0,
           'n' : 0}
                  
        logger4.debug("Params:", params)
        # POST the data
        return post(pvo_statusuri, params)

def postPVoutput(dateOfOutput, generated, exported, peakPower, peakTime, condition, minTemp, maxTemp, importPeak, importOffPeak, importShoulder, importHighShoulder, consumption, comment):
        params = {'d' : time.strftime('%Y%m%d',dateOfOutput),
            'g'  : generated,
            'e'  : exported,
            'pp' : peakPower,
            'pt' : time.strftime('%H:%M', peakTime ),
            # 'cd' : condition,
            # pvoutput automatically obtains weather data to find conditions
            'tm' : minTemp,
            'tx' : maxTemp,
	    'ip' : importPeak,
            'io' : importOffPeak,
            'is' : importShoulder,
	    'ih' : importHighShoulder,
            'c'  : consumption,
            'cm': 'EOD upload. Readings since ' + time.strftime('%d/%m/%Y %H:%M:%S', startTime) + comment}
        logger4.debug("Params:", params)
        # POST the data
        return post(pvo_outputuri, params)

def addReading(power):
    gen = power.generatedPower()
    volts = power.generatedVoltage()
    temperature = power.temperature()
    amps = power.generatedCurrent()
    timeNow = time.localtime()
    comment = ""
    global totalGen, totalReadings, lastStatus, totalAmps, totalVolts
    totalGen += gen
    totalAmps += amps
    totalVolts += volts
    totalReadings += 1
    global sampleTime, dailyEnergy, dailyGen, dailyReadings, lastOutput, peakGen, peakTime, fullDaysReadings, maxTemp, minTemp
    dailyGen += gen
    dailyEnergy += (gen*sampleTime)
    dailyReadings += 1
    logger3.info(power.timeOfReading().strftime('%Y-%m-%d %H:%M:%S'), "Gen:", gen, "W ", dailyEnergy, "Wh ", volts,"V ", amps,"A")
    if (gen > peakGen):
        peakGen = int(gen)
        peakTime = timeNow
    if(temperature > maxTemp):
        maxTemp=(temperature)
    if(temperature < minTemp):
        minTemp = temperature
    if (timeNow.tm_min % pvo_statusInterval == 0) & (lastStatus.tm_min != timeNow.tm_min):
        # You may wish to modify the simplistic averaging for something
        # more sophisticated like weighted average or kalman
        avgGen = float(totalGen / totalReadings)
        avgVoltage = float(totalVolts / totalReadings)
        avgCurrent = float(totalAmps / totalReadings)
        logger3.info("Time to output status. avgGen:", avgGen, "W ", avgVoltage, "V ", avgCurrent,"A")
        if postPVstatus(timeNow, dailyEnergy, avgGen, 0, 0,  temperature, avgVoltage):
            lastStatus = timeNow
            totalUse = 0.0
            totalGen = 0.0
            totalAmps = 0.0
            totalVolts = 0.0
            totalReadings = 0
            logger3.info("Status update sucessfully sent to PVoutput")
        else:
            lastStatus = timeNow
            logger3,error(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),"Failed to post status to pvoutput")
        sys.stdout.flush()
    logger2.debug("Debugging daily sumary")
    logger2.debug("timeNow.tm_hour = ",timeNow.tm_hour)
    logger2.debug("timeNow.tm_min = ",timeNow.tm_min)
    logger2.debug("timeNow.tm_day = ",timeNow.tm_mday)
    logger2.debug ("lastOutput.tm_mday = ",lastOutput.tm_mday)
    if (timeNow.tm_hour >= pvDailyUploadTimeHour) and (timeNow.tm_min >= pvDailyUploadTimeMin) and (lastOutput.tm_mday != timeNow.tm_mday):
        daysGen = int((dailyGen / dailyReadings) * 24.0)
        logger2.info("Time to output EOD. DaysGen:", daysGen, "W")
        if not fullDaysReadings:
            logger2.info(" Incomplete days readings.")
            comment = " Incomplete readings for days"
        if postPVoutput(timeNow, daysGen, 0, peakGen, peakTime, 'Not Sure', minTemp, maxTemp, 0, 0, 0, 0, 0, comment):
            lastOutput = timeNow
            dailyUse = 0
            dailyGen = 0
            dailyReadings = 0
            peakGen  = 0
            peakTime = timeNow
            minTemp = 100
            maxTemp = -100
            dailyEnergy = 0.0
            logger2.info("EOD Output sucessfully sent to PVoutput")
        else:
            logger2.error(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),"Failed to post daily output to pvoutput")
        fullDaysReadings = True
    sys.stdout.flush()

def processReading(reading):
    logger5.debug("Reading data", reading)
    readings = reading.split()
    placeHolder = readings[0]
    logger5.debug("placeHolder = ",placeHolder)
    dailyRunTime = readings[1]
    logger5.debug("dailyRunTime = ",dailyRunTime)
    operatingState = readings[2]
    logger5.debug("operatingState = ",operatingState)
    generatorVoltage = num(readings[3])
    logger5.debug("generatorVoltage = ",generatorVoltage)
    generatorCurrent = num(readings[4])
    logger5.debug("generatorCurrent = ",generatorCurrent)
    generatorPower = num(readings[5])
    logger5.debug("generatorPower = ",generatorPower)
    lineVoltage = num(readings[6])
    loggger5.debug("lineVoltage = ",lineVoltage)
    lineCurrentFeedIn = num(readings[7])
    logger5.debug("lineCurrentFeedIn = ",lineCurrentFeedIn)
    powerFeedIn = num(readings[8])
    logger5.debug("powerFeedIn = ",powerFeedIn)
    unitTemperature = num(readings[9])
    logger5.debug("unitTemperature = ",unitTemperature)
    logger5.debug("Processing data")
    if (generatorPower < pvs_min_pvp):
        generatorPower = 0
    elif (generatorPower > pvs_max_pvp):
        generatorPower = pvs_max_pvp

    reading = powerReading(datetime.utcnow(), dailyRunTime, operatingState, generatorVoltage, generatorCurrent, generatorPower, lineVoltage, lineCurrentFeedIn, powerFeedIn,unitTemperature) 
    addReading(reading)
        
try:
    logger5.info("Opening PV inverter serial port on ", pvs_device )
    com=serial.Serial(pvs_device, baudrate=9600, bytesize=8, parity='N', stopbits=1, xonxoff=0, timeout=5.0)
    com.open()

    if com.isOpen():
        com.flush
        logger5.info("PV inverter connection opened")
    else:
        logger5.error("Unable to open connection to PV inverter")

    logger5.info("Processing PV inverter data")

    startTime = time.localtime()
    fullDaysReadings = startTime.tm_hour < sunriseHour
    
    sys.stdout.flush()
    buffer = ''
    while com.isOpen():
        try:
            buffer += com.read(max(1,com.inWaiting())).decode('utf-8', "replace")
        except Exception as ex:
            logger5.error("Exception reading from PV inverter. Terminating\n", ex)
            logger5.error("Check that another process is not using device")
            com.close()
            sys.stdout.flush()    
        if '\r' in buffer:
            readings = buffer.split('\r')
            buffer=readings.pop()
            for reading in readings:
                processReading(reading)

    com.close()
except Exception as e:
    logger1.error("Exception processing PV inverter data. Terminating\n", e)
    sys.stdout.flush()


logger1.info("Bye")
sys.stdout.flush()

