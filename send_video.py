import urllib2
import subprocess
import shlex
import re
import os
import time
import platform
import json
import sys
import base64
import random
import datetime
import traceback
import robot_util
import thread
import copy
import argparse
import audio_util
import mebo.mebo_constants as mebo_constants

class DummyProcess:
    def poll(self):
        return None
    def __init__(self):
        self.pid = 123456789


parser = argparse.ArgumentParser(description='robot control')
parser.add_argument('camera_id')
parser.add_argument('--info-server', help="handles things such as rest API requests about ports, for example 1.1.1.1:8082", default='letsrobot.tv')
parser.add_argument('--info-server-protocol', default="https", help="either https or http")
parser.add_argument('--app-server-socketio-host', default="letsrobot.tv", help="wherever app is running")
parser.add_argument('--app-server-socketio-port', default=8022, help="typically use 8022 for prod, 8122 for dev, and 8125 for dev2")
parser.add_argument('--api-server', help="Server that robot will connect to listen for API update events", default='api.letsrobot.tv')
parser.add_argument('--xres', type=int, default=768)
parser.add_argument('--yres', type=int, default=432)
parser.add_argument('video_device_number', default=0, type=int)
parser.add_argument('--audio-device-number', default=1, type=int)
parser.add_argument('--audio-device-name')
parser.add_argument('--kbps', default=512, type=int)
parser.add_argument('--brightness', type=int, help='camera brightness')
parser.add_argument('--contrast', type=int, help='camera contrast')
parser.add_argument('--saturation', type=int, help='camera saturation')
parser.add_argument('--rotate180', default=False, type=bool, help='rotate image 180 degrees')
parser.add_argument('--env', default="prod")
parser.add_argument('--screen-capture', dest='screen_capture', action='store_true') # tells windows to pull from different camera, this should just be replaced with a video input device option
parser.set_defaults(screen_capture=False)
parser.add_argument('--no-mic', dest='mic_enabled', action='store_false')
parser.set_defaults(mic_enabled=True)
parser.add_argument('--no-camera', dest='camera_enabled', action='store_false')
parser.set_defaults(camera_enabled=True)
parser.add_argument('--dry-run', dest='dry_run', action='store_true')
parser.add_argument('--mic-channels', type=int, help='microphone channels, typically 1 or 2', default=1)
parser.add_argument('--audio-input-device', default='Microphone (HD Webcam C270)') # currently, this option is only used for windows screen capture
parser.add_argument('--stream-key', default='hello')
parser.add_argument('--mic-gain', default=80, type=int) #control sensitivity of microphone
parser.add_argument('--pipe-audio', dest='arecord', action='store_false')

commandArgs = parser.parse_args()
robotSettings = None
resolutionChanged = False
currentXres = None
currentYres = None
server = 'letsrobot.tv'
infoServer = commandArgs.info_server
apiServer = commandArgs.api_server

audioProcess = None
videoProcess = None

from socketIO_client import SocketIO, LoggingNamespace

# enable raspicam driver in case a raspicam is being used
os.system("sudo modprobe bcm2835-v4l2")

# --mic-gain microphone sensitivity
os.system("amixer -c %d cset numid=3 %d%%" % (commandArgs.audio_device_number, commandArgs.mic_gain))

#if commandArgs.env == "dev":
#    print "using dev port 8122"
#    port = 8122
#elif commandArgs.env == "dev2":
#    print "using dev port 8125"
#    port = 8125
#elif commandArgs.env == "prod":
#    print "using prod port 8022"
#    port = 8022
#else:
#    print "invalid environment"
#    sys.exit(0)


print "initializing socket io"
print "server:", server
#print "port:", port




infoServerProtocol = commandArgs.info_server_protocol

print "trying to connect to app server socket io", commandArgs.app_server_socketio_host, commandArgs.app_server_socketio_port
appServerSocketIO = SocketIO(commandArgs.app_server_socketio_host, commandArgs.app_server_socketio_port, LoggingNamespace)
print "finished initializing app server socket io"

def getVideoPort():

    url = '%s://%s/get_video_port/%s' % (infoServerProtocol, infoServer, commandArgs.camera_id)
    response = robot_util.getWithRetry(url)
    return json.loads(response)['mpeg_stream_port']



def getAudioPort():

    url = '%s://%s/get_audio_port/%s' % (infoServerProtocol, infoServer, commandArgs.camera_id)
    response = robot_util.getWithRetry(url)
    return json.loads(response)['audio_stream_port']


def getRobotID():

    url = '%s://%s/get_robot_id/%s' % (infoServerProtocol, infoServer, commandArgs.camera_id)
    response = robot_util.getWithRetry(url)
    return json.loads(response)['robot_id']

def getWebsocketRelayHost():
    url = '%s://%s/get_websocket_relay_host/%s' % (infoServerProtocol, infoServer, commandArgs.camera_id)
    response = robot_util.getWithRetry(url)
    return json.loads(response)

def getOnlineRobotSettings(robotID):
    url = 'https://%s/api/v1/robots/%s' % (apiServer, robotID)
    response = robot_util.getWithRetry(url)
    return json.loads(response)
        
def identifyRobotId():
    appServerSocketIO.emit('identify_robot_id', robotID);



def randomSleep():
    """A short wait is good for quick recovery, but sometimes a longer delay is needed or it will just keep trying and failing short intervals, like because the system thinks the port is still in use and every retry makes the system think it's still in use. So, this has a high likelihood of picking a short interval, but will pick a long one sometimes."""

    timeToWait = random.choice((0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 5))
    print "sleeping", timeToWait
    time.sleep(timeToWait)

def startVideoCaptureLinux():

    print "getting websocket relay host for video and audio"
    websocketRelayHost = getWebsocketRelayHost()

    print "websocket relay host for video and audio:", websocketRelayHost

    videoHost = websocketRelayHost['host']
    videoPort = getVideoPort()
    audioHost = websocketRelayHost['host']
    audioPort = getAudioPort()

    # Original
    videoCommandLine1 = '/usr/local/bin/ffmpeg -r 25 -i rtsp://stream:video@'+str(mebo_constants.MEBO_IP_ADDRESSE)+':554/media/stream2 {rotation_option} -f mpegts -codec:v mpeg1video -b:v {kbps}k -bf 0 -muxdelay 0.001 http://{video_host}:{video_port}/{stream_key}/640/480/'.format(video_device_number=robotSettings.video_device_number, rotation_option=rotationOption(), kbps=robotSettings.kbps, video_host=videoHost, video_port=videoPort, xres=robotSettings.xres, yres=robotSettings.yres, stream_key=robotSettings.stream_key)
    videoCommandLine2 = 'ffmpeg -r 25 -i rtsp://stream:video@'+str(mebo_constants.MEBO_IP_ADDRESSE)+':554/media/stream2  {rotation_option} -f mpegts -codec:v mpeg1video -b:v {kbps}k -bf 0 -muxdelay 0.001 http://{video_host}:{video_port}/{stream_key}/640/480/'.format(video_device_number=robotSettings.video_device_number, rotation_option=rotationOption(), kbps=robotSettings.kbps, video_host=videoHost, video_port=videoPort, xres=robotSettings.xres, yres=robotSettings.yres, stream_key=robotSettings.stream_key)

    ffmpegFound = 'ffmpeg -r 25 -i rtsp://stream:video@'+str(mebo_constants.MEBO_IP_ADDRESSE)+':554/media/stream2 \
-codec:v mpeg1video -an -f mpegts -b:v 1000k -bf 0 -muxdelay 0.001 http://{video_host}:{video_port}/{stream_key}/640/480/ \
-codec:a mp2 -vn -ar 44100 -ac 1 -f mpegts -b:a 32k -muxdelay 0.001 http://{audio_host}:{audio_port}/{stream_key2}/640/480/'.format(video_host=videoHost, video_port=videoPort, stream_key=robotSettings.stream_key, audio_host=audioHost, audio_port=audioPort, stream_key2=robotSettings.stream_key)

    ffmpegNotFound = '/usr/bin/ffmpeg -r 25 -i rtsp://stream:video@'+str(mebo_constants.MEBO_IP_ADDRESSE)+':554/media/stream2 \
-codec:v mpeg1video -an -f mpegts -b:v 1000k -bf 0 -muxdelay 0.001 http://{video_host}:{video_port}/{stream_key}/640/480/ \
-codec:a mp2 -vn -ar 44100 -ac 1 -f mpegts -b:a 32k -muxdelay 0.001 http://{audio_host}:{audio_port}/{stream_key2}/640/480/'.format(video_host=videoHost, video_port=videoPort, stream_key=robotSettings.stream_key, audio_host=audioHost, audio_port=audioPort, stream_key2=robotSettings.stream_key)

    try:
        subprocess.Popen("ffmpeg")
	print "ffmpeg found at ffmpeg"
	return subprocess.Popen(shlex.split(ffmpegFound))
    except:
        print "ffmpeg not found at ffmpeg"
        try:
            subprocess.Popen("/usr/local/bin/ffmpeg")
	    print "ffmpeg found at /usr/local/bin/ffmpeg"
	    return subprocess.Popen(shlex.split(ffmpegNotFound))
        except:
            print "ffmpeg not found at /usr/local/bin/ffmpeg"


def rotationOption():

    if robotSettings.rotate180:
        return "-vf transpose=2,transpose=2"
    else:
        return ""


def onCommandToRobot(*args):
    global robotID

    if len(args) > 0 and 'robot_id' in args[0] and args[0]['robot_id'] == robotID:
        commandMessage = args[0]
        print('command for this robot received:', commandMessage)
        command = commandMessage['command']

        if command == 'VIDOFF':
            print ('disabling camera capture process')
            print "args", args
            robotSettings.camera_enabled = False
            os.system("killall ffmpeg")

        if command == 'VIDON':
            if robotSettings.camera_enabled:
                print ('enabling camera capture process')
                print "args", args
                robotSettings.camera_enabled = True
        
        sys.stdout.flush()


def onConnection(*args):
    print 'connection:', args
    sys.stdout.flush()


def onRobotSettingsChanged(*args):
    print '---------------------------------------'
    print 'set message recieved:', args
    refreshFromOnlineSettings()
    


def killallFFMPEGIn30Seconds():
    time.sleep(30)
    os.system("killall ffmpeg")

    

#todo, this needs to work differently. likely the configuration will be json and pull in stuff from command line rather than the other way around.
def overrideSettings(commandArgs, onlineSettings):
    global resolutionChanged
    global currentXres
    global currentYres
    resolutionChanged = False
    c = copy.deepcopy(commandArgs)
    print "onlineSettings:", onlineSettings
    if 'mic_enabled' in onlineSettings:
        c.mic_enabled = onlineSettings['mic_enabled']
    if 'xres' in onlineSettings:
        if currentXres != onlineSettings['xres']:
            resolutionChanged = True
        c.xres = onlineSettings['xres']
        currentXres = onlineSettings['xres']
    if 'yres' in onlineSettings:
        if currentYres != onlineSettings['yres']:
            resolutionChanged = True
        c.yres = onlineSettings['yres']
        currentYres = onlineSettings['yres']
    print "onlineSettings['mic_enabled']:", onlineSettings['mic_enabled']
    return c


def refreshFromOnlineSettings():
    global robotSettings
    global resolutionChanged
    print "refreshing from online settings"
    onlineSettings = getOnlineRobotSettings(robotID)
    robotSettings = overrideSettings(commandArgs, onlineSettings)

    if not robotSettings.mic_enabled:
        print "KILLING**********************"

    if resolutionChanged:
        print "KILLING VIDEO DUE TO RESOLUTION CHANGE**********************"
        if videoProcess is not None:
            print "KILLING**********************"
            videoProcess.kill()

    else:
        print "NOT KILLING***********************"

def isMeboConnected():
    try:
        urllib2.urlopen('http://192.168.99.1/ajax/command.json', timeout=5)
        return True
    except urllib2.URLError as err:
        return False
    
def main():

    global robotID
    global audioProcess
    global videoProcess

    
    # overrides command line parameters using config file
    print "args on command line:", commandArgs


    robotID = getRobotID()
    identifyRobotId()

    print "robot id:", robotID

    refreshFromOnlineSettings()

    print "args after loading from server:", robotSettings
    
    appServerSocketIO.on('command_to_robot', onCommandToRobot)
    appServerSocketIO.on('connection', onConnection)
    appServerSocketIO.on('robot_settings_changed', onRobotSettingsChanged)






    sys.stdout.flush()

    
    if robotSettings.camera_enabled:
        if not commandArgs.dry_run:
            videoProcess = startVideoCaptureLinux()
        else:
            videoProcess = DummyProcess()


    numVideoRestarts = 0

    count = 0

    
    # loop forever and monitor status of ffmpeg processes
    while True:

        print "-----------------" + str(count) + "-----------------"
        
        appServerSocketIO.wait(seconds=1)


        # todo: note about the following ffmpeg_process_exists is not technically true, but need to update
        # server code to check for send_video_process_exists if you want to set it technically accurate
        # because the process doesn't always exist, like when the relay is not started yet.
        # send status to server

        if count % 5 == 0:
            if isMeboConnected() == True:
                print "Mebo online, sending video status..."
                appServerSocketIO.emit('send_video_status', {'send_video_process_exists': True,
                    'ffmpeg_process_exists': True,
                    'camera_id':commandArgs.camera_id})
            if isMeboConnected() == False:
                print "Mebo offline, not sending video status..."
        if numVideoRestarts > 100:
            time.sleep(20)
            os.system("sudo reboot")
        
        if count % 20 == 0:
            try:
                with os.fdopen(os.open('/tmp/send_video_summary.txt', os.O_WRONLY | os.O_CREAT, 0o777), 'w') as statusFile:
                    statusFile.write("time" + str(datetime.datetime.now()) + "\n")
                    statusFile.write("video process poll " + str(videoProcess.poll()) + " pid " + str(videoProcess.pid) + " restarts " + str(numVideoRestarts) + " \n")
                print "status file written"
                sys.stdout.flush()
            except:
                print "status file could not be written"
                traceback.print_exc()
                sys.stdout.flush()
                
        if (count % 60) == 0:
            identifyRobotId()
        
        if robotSettings.camera_enabled:
        
            print "video process poll", videoProcess.poll(), "pid", videoProcess.pid, "restarts", numVideoRestarts

            # restart video if needed
            if videoProcess.poll() != None:
                randomSleep()
                videoProcess = startVideoCaptureLinux()
                numVideoRestarts += 1
        else:
            print "video process poll: camera_enabled is false"

        
        count += 1

        
main()



