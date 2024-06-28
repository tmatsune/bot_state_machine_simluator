from scripts.settings import * 

@dataclass
class Display_Button:
    pos: vec2

disp: Display_Button = Display_Button(vec2(10))
print(disp)
print(disp.pos)