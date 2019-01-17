from enum import Enum, unique 

@unique
class LetsrobotCommands(Enum):
    F = "F"
    B = "B"
    L = "L"
    R = "R"
    
    AU = "AU"
    AD = "AD"
    WU = "WU"
    WD = "WD"
    RL = "RL"
    RR = "RR"

    OI = "OI"
    CI = "CI"

    O = "O"
    C = "C"

    LON = "LON"
    LOFF = "LOFF"
    
