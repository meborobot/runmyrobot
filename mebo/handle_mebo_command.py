from mebo.letsrobot_to_mebo_converter import LetsRobotToMeboConverter
from mebo.letsrobot_commands import LetsrobotCommands
from mebo.mebo_commands import MeboCommands
from mebo.letsrobot_to_param_lookup import letsrobot_to_param_lookup
import mebo.mebo_constants as mebo_constants
import httplib, socket, time

converter = LetsRobotToMeboConverter()

mebo_calibrated = False
def calibrate_mebo():
    global mebo_calibrated

    if mebo_calibrated:
        return

    mebo_command = converter.generate_message({
        "command": MeboCommands.CAL_ALL,
        "parameter": 0
    })

    try:
        conn = httplib.HTTPConnection(mebo_constants.MEBO_IP_ADDRESSE)
        
        print "\nSTART - sending GET request to: " + str(mebo_constants.MEBO_IP_ADDRESSE) + "/ajax/command.json" + mebo_command + "\n"
        conn.request("GET","/ajax/command.json" + mebo_command)
        res = conn.getresponse()
        print(res.status, res.reason)
    
        mebo_calibrated = True
    except (httplib.HTTPException, socket.error) as ex:
        print "Error: %s" % ex

claw_position = mebo_constants.CLAW_CLOSE_POSITION
def handle_claw_increment(command):
    global claw_position

    if command == "OI":
        claw_position -= mebo_constants.CLAW_INCREMENT
    if command == "CI":
        claw_position += mebo_constants.CLAW_INCREMENT

    if claw_position > mebo_constants.CLAW_CLOSE_POSITION:
        claw_position = mebo_constants.CLAW_CLOSE_POSITION
    if claw_position < mebo_constants.CLAW_OPEN_POSITION:
        claw_position = mebo_constants.CLAW_OPEN_POSITION

    mebo_command = converter.convert({
        "command": command,
        "parameter": claw_position
    })

    try:
        conn = httplib.HTTPConnection(mebo_constants.MEBO_IP_ADDRESSE)
        
        print "\nSTART - sending GET request to: " + str(mebo_constants.MEBO_IP_ADDRESSE) + "/ajax/command.json" + mebo_command + "\n"
        conn.request("GET","/ajax/command.json" + mebo_command)
        res = conn.getresponse()
        print(res.status, res.reason)
    except (httplib.HTTPException, socket.error) as ex:
        print "Error: %s" % ex

def handle_speed(command, speed):
    command = command.encode('ascii','ignore')

    if command == "S":
        print "setting speed"
        letsrobot_to_param_lookup[LetsrobotCommands.F] = speed
        letsrobot_to_param_lookup[LetsrobotCommands.B] = speed
        return
    if command == "T":
        print "setting turning"
        letsrobot_to_param_lookup[LetsrobotCommands.L] = speed
        letsrobot_to_param_lookup[LetsrobotCommands.R] = speed
        return
    
    mebo_command = converter.convert({
        "command": command,
        "parameter": speed
    })

    mebo_command_stop = converter.convert({
        "command": "F",
        "parameter": 0
    }, {
        "command": "AU",
        "parameter": 0
    }, {
        "command": "WU",
        "parameter": 0
    }, {
        "command": "RL",
        "parameter": 0
    })

    try:
        conn = httplib.HTTPConnection(mebo_constants.MEBO_IP_ADDRESSE)
        
        print "\nSTART - sending GET request to: " + str(mebo_constants.MEBO_IP_ADDRESSE) + "/ajax/command.json" + mebo_command + "\n"
        conn.request("GET","/ajax/command.json" + mebo_command)
        res = conn.getresponse()
        print(res.status, res.reason)
    
        time.sleep(mebo_constants.COMMAND_DURATION)
    
        print "\nSTOP - sending GET request to: " + str(mebo_constants.MEBO_IP_ADDRESSE) + "/ajax/command.json" + mebo_command_stop + "\n"
        conn.request("GET","/ajax/command.json" + mebo_command_stop)
        res = conn.getresponse()
        print(res.status, res.reason)
    except (httplib.HTTPException, socket.error) as ex:
        print "Error: %s" % ex

def handle_mebo_command(command):
    command = command.encode('ascii','ignore')

    calibrate_mebo()
    
    if command == "stop":
        return
    if command == "SI":
        return
    if command == "SD":
        return
    if command == "TI":
        return
    if command == "TD":
        return
    if command == "OI" or command == "CI":
        handle_claw_increment(command)
        return

    mebo_command = converter.convert({
        "command": command,
        "parameter": letsrobot_to_param_lookup[LetsrobotCommands(command)]
    })

    mebo_command_stop = converter.convert({
        "command": "F",
        "parameter": 0
    }, {
        "command": "AU",
        "parameter": 0
    }, {
        "command": "WU",
        "parameter": 0
    }, {
        "command": "RL",
        "parameter": 0
    })

    try:
        conn = httplib.HTTPConnection(mebo_constants.MEBO_IP_ADDRESSE)
        
        print "\nSTART - sending GET request to: " + str(mebo_constants.MEBO_IP_ADDRESSE) + "/ajax/command.json" + mebo_command + "\n"
        conn.request("GET","/ajax/command.json" + mebo_command)
        res = conn.getresponse()
        print(res.status, res.reason)
    
        time.sleep(mebo_constants.COMMAND_DURATION)
    
        print "\nSTOP - sending GET request to: " + str(mebo_constants.MEBO_IP_ADDRESSE) + "/ajax/command.json" + mebo_command_stop + "\n"
        conn.request("GET","/ajax/command.json" + mebo_command_stop)
        res = conn.getresponse()
        print(res.status, res.reason)
    except (httplib.HTTPException, socket.error) as ex:
        print "Error: %s" % ex
