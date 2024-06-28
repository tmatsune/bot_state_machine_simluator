from scripts.settings import *

RANGE_THRESHOLD = 300

class Enemy_Pos(Enum):
    ENEMY_POS_NONE = 0
    ENEMY_POS_FRONT_LEFT = 1
    ENEMY_POS_FRONT = 2
    ENEMY_POS_FRONT_RIGHT = 3
    ENEMY_POS_LEFT = 4
    ENEMY_POS_RIGHT = 5
    ENEMY_POS_FRONT_AND_FRONT_LEFT = 6
    ENEMY_POS_FRONT_AND_FRONT_RIGHT = 7
    ENEMY_POS_FRONT_ALL = 8
    ENEMY_POS_IMPOSSIBLE = 9

class Enemy_Range(Enum):
    ENEMY_RANGE_NONE = 0
    ENEMY_RANGE_CLOSE = 1
    ENEMY_RANGE_MID = 2
    ENEMY_RANGE_FAR = 3

@dataclass
class Enemy_Struct():
    position: Enemy_Pos
    range: Enemy_Range
 
enemy_null: Enemy_Struct = Enemy_Struct(Enemy_Pos.ENEMY_POS_NONE, Enemy_Range.ENEMY_RANGE_NONE)

def enemy_at_left(enemy: Enemy_Struct):
    return enemy.position == Enemy_Pos.ENEMY_POS_LEFT \
        or enemy.position == Enemy_Pos.ENEMY_POS_FRONT_LEFT \
        or enemy.position == Enemy_Pos.ENEMY_POS_FRONT_AND_FRONT_LEFT


def enemy_at_right(enemy: Enemy_Struct):
    return enemy.position == Enemy_Pos.ENEMY_POS_RIGHT \
        or enemy.position == Enemy_Pos.ENEMY_POS_FRONT_RIGHT \
        or enemy.position == Enemy_Pos.ENEMY_POS_FRONT_AND_FRONT_RIGHT

def enemy_at_front(enemy: Enemy_Struct):
    return enemy.position == Enemy_Pos.ENEMY_POS_FRONT or enemy.position == Enemy_Pos.ENEMY_POS_FRONT_ALL

def enemy_detected(enemy: Enemy_Struct):
    return enemy.position != Enemy_Pos.ENEMY_POS_NONE and enemy.range != Enemy_Range.ENEMY_RANGE_NONE


def enemy_enum_to_str(enemy: Enemy_Struct):
    print("Enemy Position: ", end=" ")
    if enemy.position == Enemy_Pos.ENEMY_POS_NONE:
        print("ENEMY_POS_NONE ", end=" ")
    elif enemy.position == Enemy_Pos.ENEMY_POS_FRONT_LEFT:
        print("ENEMY_POS_FRONT_LEFT ", end=" ")
    elif enemy.position == Enemy_Pos.ENEMY_POS_FRONT:
        print("ENEMY_POS_FRONT", end=" ")
    elif enemy.position == Enemy_Pos.ENEMY_POS_FRONT_RIGHT:
        print("ENEMY_POS_FRONT_RIGHT", end=" ")
    elif enemy.position == Enemy_Pos.ENEMY_POS_LEFT:
        print("ENEMY_POS_LEFT", end=" ")
    elif enemy.position == Enemy_Pos.ENEMY_POS_RIGHT:
        print("ENEMY_POS_RIGHT", end=" ")
    elif enemy.position == Enemy_Pos.ENEMY_POS_FRONT_AND_FRONT_LEFT:
        print("ENEMY_POS_FRONT_AND_FRONT_LEFT", end=" ")
    elif enemy.position == Enemy_Pos.ENEMY_POS_FRONT_AND_FRONT_RIGHT:
        print("ENEMY_POS_FRONT_AND_FRONT_RIGHT", end=" ")
    elif enemy.position == Enemy_Pos.ENEMY_POS_FRONT_ALL:
        print("ENEMY_POS_FRONT_ALL", end=" ")
    elif enemy.position == Enemy_Pos.ENEMY_POS_IMPOSSIBLE:
        print("ENEMY_POS_IMPOSSIBLE", end=" ")
    else:
        assert 0, "ERROR, NO POSITION DETECTED"

    if enemy.range == Enemy_Range.ENEMY_RANGE_CLOSE:
        print("ENEMY_RANGE_CLOSE")
    elif enemy.range == Enemy_Range.ENEMY_RANGE_MID:
        print("ENEMY_RANGE_MID")
    elif enemy.range == Enemy_Range.ENEMY_RANGE_FAR:
        print("ENEMY_RANGE_FAR")
    elif enemy.range == Enemy_Range.ENEMY_RANGE_NONE:
        print("ENEMY_RANGE_NONE")
    else:
        assert 0, "ERROR, NO RANGE DETECTED"


def enemy_pos_to_str(enemy_pos: Enemy_Pos) -> str:
    if enemy_pos == Enemy_Pos.ENEMY_POS_NONE:
        return 'NONE'
    elif enemy_pos == Enemy_Pos.ENEMY_POS_FRONT_LEFT:
        return 'FL'
    elif enemy_pos == Enemy_Pos.ENEMY_POS_FRONT:
        return 'F'
    elif enemy_pos == Enemy_Pos.ENEMY_POS_FRONT_RIGHT:
        return 'FR'
    elif enemy_pos == Enemy_Pos.ENEMY_POS_LEFT:
        return 'L'
    elif enemy_pos == Enemy_Pos.ENEMY_POS_RIGHT:
        return 'R'
    elif enemy_pos == Enemy_Pos.ENEMY_POS_FRONT_AND_FRONT_LEFT:
        return 'F&FL'
    elif enemy_pos == Enemy_Pos.ENEMY_POS_FRONT_AND_FRONT_RIGHT:
        return 'F&FR'
    elif enemy_pos == Enemy_Pos.ENEMY_POS_FRONT_ALL:
        return 'FA'
    elif enemy_pos == Enemy_Pos.ENEMY_POS_IMPOSSIBLE:
        return 'I'

def enemy_range_to_str(enemy_range: Enemy_Range) -> str:
    if enemy_range == Enemy_Range.ENEMY_RANGE_CLOSE:
        return 'CLOSE'
    elif enemy_range == Enemy_Range.ENEMY_RANGE_MID:
        return 'MID'
    elif enemy_range == Enemy_Range.ENEMY_RANGE_FAR:
        return 'FAR'
    elif enemy_range == Enemy_Range.ENEMY_RANGE_NONE:
        return 'NONE'

