from scripts.settings import * 


class Ir_Command(Enum):
    NONE = 0
    RUN = 1

class Line_Pos(Enum):
    LINE_NONE = 0
    LINE_FRONT = 1
    LINE_BACK = 2
    LINE_LEFT = 3
    LINE_RIGHT = 4
    LINE_FRONT_LEFT = 5
    LINE_FRONT_RIGHT = 6
    LINE_BACK_LEFT = 7
    LINE_BACK_RIGHT = 8
    LINE_DIAGONAL_LEFT = 9
    LINE_DIAGONAL_RIGHT = 10
    
def line_enum_to_str(line: Line_Pos):
    print("Line: ", end=" ")
    if line == Line_Pos.LINE_NONE:
        print("LINE_NONE")
    elif line == Line_Pos.LINE_FRONT:
        print("LINE_FRONT")
    elif line == Line_Pos.LINE_BACK:
        print("LINE_BACK")
    elif line == Line_Pos.LINE_LEFT:
        print("LINE_LEFT")
    elif line == Line_Pos.LINE_RIGHT:
        print("LINE_RIGHT")
    elif line == Line_Pos.LINE_FRONT_LEFT:
        print("LINE_FRONT_LEFT")
    elif line == Line_Pos.LINE_FRONT_RIGHT:
        print("LINE_FRONT_RIGHT")
    elif line == Line_Pos.LINE_BACK_LEFT:
        print("LINE_BACK_LEFT")
    elif line == Line_Pos.LINE_BACK_RIGHT:
        print("LINE_BACK_RIGHT")
    elif line == Line_Pos.LINE_DIAGONAL_LEFT:
        print("LINE_DIAGONAL_LEFT")
    elif line == Line_Pos.LINE_DIAGONAL_RIGHT:
        print("LINE_DIAGONAL_RIGHT")
        
def line_to_str(line: Line_Pos) -> str:
    if line == Line_Pos.LINE_NONE:
        return 'LINE NONE'
    elif line == Line_Pos.LINE_FRONT:
        return "LINE_FRONT"
    elif line == Line_Pos.LINE_BACK:
        return "LINE_BACK"
    elif line == Line_Pos.LINE_LEFT:
        return "LINE_LEFT"
    elif line == Line_Pos.LINE_RIGHT:
        return "LINE_RIGHT"
    elif line == Line_Pos.LINE_FRONT_LEFT:
        return "LINE_FRONT_LEFT"
    elif line == Line_Pos.LINE_FRONT_RIGHT:
        return "LINE_FRONT_RIGHT"
    elif line == Line_Pos.LINE_BACK_LEFT:
        return "LINE_BACK_LEFT"
    elif line == Line_Pos.LINE_BACK_RIGHT:
        return "LINE_BACK_RIGHT"
    elif line == Line_Pos.LINE_DIAGONAL_LEFT:
        return "LINE_DIAGONAL_LEFT"
    elif line == Line_Pos.LINE_DIAGONAL_RIGHT:
        return "LINE_DIAGONAL_RIGHT"
