from letsrobot_commands import LetsrobotCommands
from mebo_commands import MeboCommands

letsrobot_to_mebo_lookup = {
    LetsrobotCommands.F: [
        MeboCommands.WHEEL_LEFT_FORWARD,
        MeboCommands.WHEEL_RIGHT_FORWARD
    ],
    LetsrobotCommands.B: [
        MeboCommands.WHEEL_LEFT_BACKWARD,
        MeboCommands.WHEEL_RIGHT_BACKWARD
    ],
    LetsrobotCommands.L: [
        MeboCommands.WHEEL_LEFT_BACKWARD,
        MeboCommands.WHEEL_RIGHT_FORWARD
    ],
    LetsrobotCommands.R: [
        MeboCommands.WHEEL_LEFT_FORWARD,
        MeboCommands.WHEEL_RIGHT_BACKWARD
    ],
    LetsrobotCommands.LN: [
        MeboCommands.LIGHT_OFF
    ],
    LetsrobotCommands.LY: [
        MeboCommands.LIGHT_ON
    ],
    LetsrobotCommands.AU: [
        MeboCommands.ARM_UP
    ],
    LetsrobotCommands.AD: [
        MeboCommands.ARM_DOWN
    ],
    LetsrobotCommands.WU: [
        MeboCommands.WRIST_UD_UP
    ],
    LetsrobotCommands.WD: [
        MeboCommands.WRIST_UD_DOWN
    ],
    LetsrobotCommands.RL: [
        MeboCommands.WRIST_ROTATE_LEFT
    ],
    LetsrobotCommands.RR: [
        MeboCommands.WRIST_ROTATE_RIGHT
    ],
    LetsrobotCommands.O: [
        MeboCommands.CLAW_POSITION
    ],
    LetsrobotCommands.C: [
        MeboCommands.CLAW_POSITION
    ],
    LetsrobotCommands.OI: [
        MeboCommands.CLAW_POSITION
    ],
    LetsrobotCommands.CI: [
        MeboCommands.CLAW_POSITION
    ],
    LetsrobotCommands.S1: [
        MeboCommands.SET_TURNING_SPEED_1
    ],
    LetsrobotCommands.S2: [
        MeboCommands.SET_TURNING_SPEED_3
    ],
    LetsrobotCommands.S3: [
        MeboCommands.SET_TURNING_SPEED_3
    ]
}

