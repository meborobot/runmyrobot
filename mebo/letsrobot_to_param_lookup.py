from mebo.letsrobot_commands import LetsrobotCommands
import mebo.mebo_constants as mebo_constants

letsrobot_to_param_lookup = {
    LetsrobotCommands.F: mebo_constants.MOVEMENT_SPEED,
    LetsrobotCommands.B: mebo_constants.MOVEMENT_SPEED,
    LetsrobotCommands.L: mebo_constants.TURNING_SPEED,
    LetsrobotCommands.R: mebo_constants.TURNING_SPEED,

    LetsrobotCommands.AU: mebo_constants.ARM_SPEED,
    LetsrobotCommands.AD: mebo_constants.ARM_SPEED,

    LetsrobotCommands.LY: mebo_constants.LIGHT_ON,
    LetsrobotCommands.LN: mebo_constants.LIGHT_OFF,

    LetsrobotCommands.WU: mebo_constants.WRIST_UD_SPEED,
    LetsrobotCommands.WD: mebo_constants.WRIST_UD_SPEED,

    LetsrobotCommands.RR: mebo_constants.WRIST_ROTATION_SPEED,
    LetsrobotCommands.RL: mebo_constants.WRIST_ROTATION_SPEED,

    LetsrobotCommands.O: mebo_constants.CLAW_OPEN_POSITION,
    LetsrobotCommands.C: mebo_constants.CLAW_CLOSE_POSITION,

    LetsrobotCommands.S1: mebo_constants.TURNINGSPEEDS1,
    LetsrobotCommands.S2: mebo_constants.TURNINGSPEEDS2,
    LetsrobotCommands.S3: mebo_constants.TURNINGSPEEDS3
}
