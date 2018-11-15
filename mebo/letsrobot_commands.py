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

    O = "O"
    C = "C"

    S1 = "S1"
    S2 = "S2"
    S3 = "S3"
    
