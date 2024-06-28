from scripts.settings import *

@dataclass
class Drive_Settings:
    left: int
    right: int
    speed: int

class Drive_Dir(Enum):
    DRIVE_DIR_FORWARD = 0
    DRIVE_DIR_REVERSE = 1
    DRIVE_DIR_ROTATE_LEFT = 2
    DRIVE_DIR_ROTATE_RIGHT = 3
    DRIVE_DIR_ARCTURN_SHARP_LEFT = 4
    DRIVE_DIR_ARCTURN_SHARP_RIGHT = 5
    DRIVE_DIR_ARCTURN_MID_LEFT = 6
    DRIVE_DIR_ARCTURN_MID_RIGHT = 7
    DRIVE_DIR_ARCTURN_WIDE_LEFT = 8
    DRIVE_DIR_ARCTURN_WIDE_RIGHT = 9
    DRIVE_DIR_NONE = 10

class Drive_Speed(Enum):
    DRIVE_SPEED_SLOW: int = 0
    DRIVE_SPEED_MEDIUM: int = 1
    DRIVE_SPEED_FAST: int = 2
    DRIVE_SPEED_MAX: int = 3

all_drive_settings: list[list[Drive_Settings]] = [
    [Drive_Settings(0, 0, 1), Drive_Settings(0, 0, 2), Drive_Settings(0, 0, 6), Drive_Settings(0, 0, 6)], #forward
    [Drive_Settings(0, 0, -1), Drive_Settings(0, 0, -2), Drive_Settings(0, 0, -6), Drive_Settings(0, 0, -6)], #reverse
    [Drive_Settings(6, 0, 1), Drive_Settings(6, 0, 1), Drive_Settings(6, 0, 6), Drive_Settings(10, 0, 6)], #rotate left : 10 0 8
    [Drive_Settings(0, 6, 1), Drive_Settings(0, 6, 1), Drive_Settings(0, 6, 6), Drive_Settings(0, 10, 6)], #rotate right : 0 10 8
    [Drive_Settings(14, 0, 1), Drive_Settings(14, 0, 2), Drive_Settings(14, 0, 6), Drive_Settings(12, 0, 6)], # arcturn left
    [Drive_Settings(0, 14, 1), Drive_Settings(0, 14, 2), Drive_Settings(0, 14, 6), Drive_Settings(0, 12, 6)], # artcurn right
    [Drive_Settings(10, 0, 1), Drive_Settings(10, 0, 2), Drive_Settings(10, 0, 6), Drive_Settings(6, 0, 6)], # mid left 
    [Drive_Settings(0, 10, 1), Drive_Settings(0, 10, 2), Drive_Settings(0, 10, 6), Drive_Settings(0, 10, 6)], # mid right 
    [Drive_Settings(4, 0, 1), Drive_Settings(4, 0, 2), Drive_Settings(4, 0, 6), Drive_Settings(10, 0, 6)], # wide left
    [Drive_Settings(0, 4, 1), Drive_Settings(0, 4, 2), Drive_Settings(0, 4, 6), Drive_Settings(0, 10, 6)], # wide right 
]

def DRIVE_STOP(bot):
    bot.drive_setting.left = 0
    bot.drive_setting.right = 0
    bot.drive_setting.speed = 0

def drive_set(direction: Drive_Dir, speed: Drive_Speed, bot, all_drive_settings: list[list[Drive_Settings]] = all_drive_settings):
    direction_val, speed_val = get_int_val(direction, speed)
    #print(direction_val, speed_val, drive_setting_str(all_drive_settings_2[direction_val][speed_val], all_drive_settings_2))
    #print(bot.state_machine.state)
    left_speed: int = all_drive_settings[direction_val][speed_val].left
    right_speed: int = all_drive_settings[direction_val][speed_val].right
    drive_speed: int = all_drive_settings[direction_val][speed_val].speed
    bot.drive_setting.left = left_speed
    bot.drive_setting.right = right_speed
    bot.drive_setting.speed = drive_speed

def get_int_val(direction: Drive_Dir, speed: Drive_Speed):
    direction_val: int = direction.value
    speed_val: int = speed.value
    return direction_val, speed_val

all_drive_settings_2: list[list[Drive_Settings]] = [
    [Drive_Settings(0, 0, 1), Drive_Settings(0, 0, 2), Drive_Settings(0, 0, 6), Drive_Settings(0, 0, 10)], #forward
    [Drive_Settings(0, 0, -1), Drive_Settings(0, 0, -2), Drive_Settings(0, 0, -6), Drive_Settings(0, 0, -10)], #reverse
    [Drive_Settings(6, 0, 1), Drive_Settings(6, 0, 1), Drive_Settings(6, 0, 6), Drive_Settings(10, 0, 0)], #rotate left : 10 0 8
    [Drive_Settings(0, 6, 1), Drive_Settings(0, 6, 1), Drive_Settings(0, 6, 6), Drive_Settings(0, 10, 0)], #rotate right : 0 10 8
    [Drive_Settings(14, 0, 1), Drive_Settings(14, 0, 2), Drive_Settings(14, 0, 6), Drive_Settings(12, 0, 6)], # arcturn left
    [Drive_Settings(0, 14, 1), Drive_Settings(0, 14, 2), Drive_Settings(0, 14, 6), Drive_Settings(0, 12, 6)], # artcurn right
    [Drive_Settings(10, 0, 1), Drive_Settings(10, 0, 2), Drive_Settings(10, 0, 6), Drive_Settings(6, 0, 6)], # mid left 
    [Drive_Settings(0, 10, 1), Drive_Settings(0, 10, 2), Drive_Settings(0, 10, 6), Drive_Settings(0, 6, 6)], # mid right 
    [Drive_Settings(4, 0, 1), Drive_Settings(4, 0, 2), Drive_Settings(4, 0, 6), Drive_Settings(10, 0, 6)], # wide left
    [Drive_Settings(0, 4, 1), Drive_Settings(0, 4, 2), Drive_Settings(0, 4, 6), Drive_Settings(0, 10, 6)], # wide right 
    [Drive_Settings(0, 0, 0), Drive_Settings(0, 0, 0), Drive_Settings(0, 0, 0), Drive_Settings(0, 0, 0)], # NONE
]

def drive_setting_str(drive_setting: Drive_Settings, all_drive_settings: list[list[Drive_Settings]]=all_drive_settings):
    if drive_setting == all_drive_settings[0][3]:
        return 'FORWARD'
    elif drive_setting == all_drive_settings[1][3]:
        return 'REVERSE'
    elif drive_setting == all_drive_settings[2][3]:
        return 'ROT_LEFT'
    elif drive_setting == all_drive_settings[3][3]:
        return 'ROT_RIGHT'
    elif drive_setting == all_drive_settings[4][3]:
        return 'SHARP_LEFT'
    elif drive_setting == all_drive_settings[5][3]:
        return 'SHARP_RIGHT'
    elif drive_setting == all_drive_settings[6][3]:
        return 'MID_LEFT'
    elif drive_setting == all_drive_settings[7][3]:
        return 'MID_RIGHT'
    elif drive_setting == all_drive_settings[8][3]:
        return 'WIDE_LEFT'
    elif drive_setting == all_drive_settings[9][3]:
        return 'WIDE_RIGHT'
    elif drive_setting == all_drive_settings[10][3]:
        return 'NONE'
