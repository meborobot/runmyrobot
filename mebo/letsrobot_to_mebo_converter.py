from mebo_commands import MeboCommands
from letsrobot_commands import LetsrobotCommands
from letsrobot_to_mebo_lookup import letsrobot_to_mebo_lookup

class LetsRobotToMeboConverter:
    messageCount = 0

    def _new_cmd(self):
        result = "!" + self._to_base64(self.messageCount & 63)
        self.messageCount += 1
        return result

    @staticmethod
    def _to_base64(val):
        return "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"[val & 63]

    @staticmethod
    def _encode_base64(val, chars_count):
        result = ""
        for i in range(0, chars_count):
            result += LetsRobotToMeboConverter._to_base64(val >> (i * 6))
        return result

    @staticmethod
    def _encode_speed(speed):
        return LetsRobotToMeboConverter._encode_base64(speed, 2)

    def _command_string(self, cmd, para):
        MeboCmd = MeboCommands 
        enc_spd = self._encode_speed 
        new_cmd = self._new_cmd 
 
        if cmd == MeboCmd.READERS:                 return "READERS=?"
        elif cmd == MeboCmd.FACTORY:               return "P" 
        elif cmd == MeboCmd.BAT:                   return "BAT=?"
 
        elif cmd == MeboCmd.WHEEL_LEFT_FORWARD:    return new_cmd() + "F" + enc_spd(para)
        elif cmd == MeboCmd.WHEEL_LEFT_BACKWARD:   return new_cmd() + "F" + enc_spd(-para)
        elif cmd == MeboCmd.WHEEL_RIGHT_FORWARD:   return new_cmd() + "E" + enc_spd(para)
        elif cmd == MeboCmd.WHEEL_RIGHT_BACKWARD:  return new_cmd() + "E" + enc_spd(-para)
        elif cmd == MeboCmd.WHEEL_BOTH_STOP:       return new_cmd() + "B"
 
        elif cmd == MeboCmd.ARM_UP:                return new_cmd() + "G" + enc_spd(para)
        elif cmd == MeboCmd.ARM_DOWN:              return new_cmd() + "G" + enc_spd(-para)
        elif cmd == MeboCmd.ARM_POSITION:          return new_cmd() + "K" + enc_spd(para)
        elif cmd == MeboCmd.ARM_STOP:              return new_cmd() + "CEAA"
        elif cmd == MeboCmd.ARM_QUERY:             return "ARM=?"
 
        elif cmd == MeboCmd.WRIST_UD_UP:           return new_cmd() + "H" + enc_spd(para)
        elif cmd == MeboCmd.WRIST_UD_DOWN:         return new_cmd() + "H" + enc_spd(-para)
        elif cmd == MeboCmd.WRIST_UD_POSITION:     return new_cmd() + "L" + enc_spd(para)
        elif cmd == MeboCmd.WRIST_UD_STOP:         return new_cmd() + "CIAA"
        elif cmd == MeboCmd.WRIST_UD_QUERY:        return "WRIST_UD=?"
 
        elif cmd == MeboCmd.WRIST_ROTATE_LEFT:     return new_cmd() + "I" + enc_spd(para)
        elif cmd == MeboCmd.WRIST_ROTATE_RIGHT:    return new_cmd() + "I" + enc_spd(-para)
        elif cmd == MeboCmd.WRIST_ROTATE_POSITION: return new_cmd() + "M" + enc_spd(para)
        elif cmd == MeboCmd.WRIST_ROTATE_STOP:     return new_cmd() + "CQAA"
        elif cmd == MeboCmd.WRIST_ROTATE_QUERY:    return "WRIST_ROTATE=?"

        elif cmd == MeboCmd.CLAW_POSITION:         return new_cmd() + "N" + enc_spd(para)
        elif cmd == MeboCmd.CLAW_STOP:             return new_cmd() + "CgAA"
        elif cmd == MeboCmd.CLAW_QUERY:            return "CLAW=?"

        elif cmd == MeboCmd.CAL_ARM:               return new_cmd() + "DE"
        elif cmd == MeboCmd.CAL_WRIST_UD:          return new_cmd() + "DI"
        elif cmd == MeboCmd.CAL_WRIST_ROTATE:      return new_cmd() + "DQ"
        elif cmd == MeboCmd.CAL_CLAW:              return new_cmd() + "Dg"
        elif cmd == MeboCmd.CAL_ALL:               return new_cmd() + "D_"

        elif cmd == MeboCmd.VERSION_QUERY:         return "VER=?"
        elif cmd == MeboCmd.REBOOT_CMD:            return new_cmd() + "DE"
        elif cmd == MeboCmd.JOINT_SPEED:           return ""

        elif cmd == MeboCmd.SET_REG:               return ""
        elif cmd == MeboCmd.QUERY_REG:             return "REG" + str(para / 100 % 10) + str(para / 10 % 10) + str(para % 10) + "=?"
        elif cmd == MeboCmd.SAVE_REG:              return "REG=FLUSH"
                    
        elif cmd == MeboCmd.WHEEL_LEFT_SPEED:      return new_cmd() + "F" + enc_spd(para)
        elif cmd == MeboCmd.WHEEL_RIGHT_SPEED:     return new_cmd() + "E" + enc_spd(para)

        elif cmd == MeboCmd.QUERY_EVENT:           return "*"
        else:                                      return ""

    def _generate_single_command(self, number, command, parameter):
        cmd_str = self._command_string(command, parameter)
        return "command" + str(number) + "=mebolink_message_send(" + cmd_str + ")"

    def generate_message(self, *commands):
        query = "?"
        for i, command in enumerate(commands):
            query += self._generate_single_command(i + 1, command["command"], command["parameter"])
            if i < len(commands) - 1:
                query += "&"
        return query

    def _lr_to_mebo_command(self, cmd, param):

        if type(cmd) is str:
            cmd = LetsrobotCommands(cmd)

        mebo_commands = letsrobot_to_mebo_lookup[cmd]
        command_list = []
        for command in mebo_commands:
            command_list.append({
                "command": command,
                "parameter": param
            })
        
        return command_list

    def convert(self, *lr_commands):
        commands = []
        for lr_command in lr_commands:
            commands.extend(self._lr_to_mebo_command(lr_command["command"], lr_command["parameter"]))
        return self.generate_message(*commands)