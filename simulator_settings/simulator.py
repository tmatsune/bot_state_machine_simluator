from scripts.settings import * 
from scripts.utils import text_surface, render_text_box
from bot.sumo_bot import * 

class Click(Enum):
    NONE = 0
    CLICK_FIRST_PRESSED = 1
    CLICK_DOWN = 2
    CLICK_UP = 3

@dataclass
class Button:
    display: bool
    pos: vec2
    size: list[int]
    button_title: str

@dataclass
class Button_Click:
    pos: vec2
    size: list[int]
    button_title: str
    func: any 
    args: list

class Simulator_Settings:
    def __init__(self, app) -> None:
        from main import App
        self.app: App = app
        self.main_bot: SumoBot = self.app.main_bot
        self.enemy_bot: SumoBot = self.app.enemy_bot
        self.starting_positions: list[vec2] = [vec2(300, 400), vec2(300, 200)]

        self.test_case: Test_Cases = Test_Cases.STATE_MACHINE_0
        self.display_buttons: list[Button] = [
            Button(false, vec2((WIDTH // 2) - 30, 0), [60, 20], 'Tests'),
            Button(false, vec2(0,0), [80,20], 'main bot 1'),
            Button(false, vec2(90,0), [80,20], 'main bot 2'),
            Button(false, vec2(WIDTH-80,0), [80,20], 'enemy bot 1'),
            Button(false, vec2(WIDTH-170,0), [80,20], 'enemy bot 2'),
            Button(false, vec2(0,HEIGHT-220), [50, 20], 'Bot 1'),
            Button(false, vec2(WIDTH-50,HEIGHT-220), [50, 20], 'Bot 2'),
        ]
        self.test_options: list[Button_Click] = [
            Button_Click(vec2(0), [80, 20], 'Test 1', self.test_zero, []),
            Button_Click(vec2(0), [80, 20], 'Test 2', self.test_one, []),
            Button_Click(vec2(0), [80, 20], 'Test 3', self.test_two, []),
            Button_Click(vec2(0), [80, 20], 'reset', self.reset_bots, []),
        ]
        self.bot_buttons: list[Button_Click] = [
            Button_Click(vec2(0), [80, 20], 'Ir Command', self.send_ir_command, ['main_bot']),
            Button_Click(vec2(0), [80, 20], 'state machine 0', None, []),
            Button_Click(vec2(0), [80, 20], 'state machine 2', None, []),
            Button_Click(vec2(0), [80, 20], 'Manual', self.set_bot_maunual, ['main_bot']),
            Button_Click(vec2(0), [80, 20], 'Autonomous', self.set_bot_autonomous, ['main_bot']),
            Button_Click(vec2(0), [80, 20], 'drive mode', self.set_bot_drive_mode, ['main_bot']),
        ]
        self.bot_buttons_2: list[Button_Click] = [
            Button_Click(vec2(0), [80, 20], 'Ir Command', self.send_ir_command, ['enemy_bot']),
            Button_Click(vec2(0), [80, 20], 'state machine 0', None, []),
            Button_Click(vec2(0), [80, 20], 'state machine 2', None, []),
            Button_Click(vec2(0), [80, 20], 'Manual', self.set_bot_maunual, ['enemy_bot']),
            Button_Click(vec2(0), [80, 20], 'Autonomous', self.set_bot_autonomous, ['enemy_bot']),
            Button_Click(vec2(0), [80, 20], 'drive mode', self.set_bot_drive_mode, ['enemy_bot']),
        ]

        self.click: Click = Click.NONE
        self.clicked: bool = false
        self.click_size: list[int] = [8,8]

    def update(self):
        self.handle_click()
    def render(self, surf, mpos: vec2):
        mpos_rect: pg.rect = pg.Rect(mpos.x, mpos.y, self.click_size[0], self.click_size[1])

        for i in range(len(self.display_buttons)):
            button_pressed: bool = self.button_box(surf=surf, pos=self.display_buttons[i].pos, size=self.display_buttons[i].size, 
                                                   button_title=self.display_buttons[i].button_title, mpos_rect=mpos_rect)
            if button_pressed:
                self.flip_display_option(self.display_buttons[i])
            if self.display_buttons[i].display:
                if self.display_buttons[i].button_title == 'Tests':
                    self.multiple_buttons_box(surf=surf, buttons=self.test_options, mpos_rect=mpos_rect,
                                              pos=vec2(WIDTH//2+(140//2), 0), size=[140, 120], box_title='Test Cases')
                elif self.display_buttons[i].button_title == 'main bot 1': 
                    self.app.render_bot_peripherals(surf, self.app.main_bot, vec2(0,20))
                elif self.display_buttons[i].button_title == 'main bot 2': 
                    self.app.render_bot_peripherals_2(surf, self.app.main_bot, vec2(0, 190))  # WIDTH - 140
                elif self.display_buttons[i].button_title == 'enemy bot 1':
                    self.app.render_target_bot_peripherals(surf, self.app.enemy_bot, vec2(WIDTH-140,20))
                elif self.display_buttons[i].button_title == 'Bot 1':
                    self.multiple_buttons_box(surf=surf, buttons=self.bot_buttons, mpos_rect=mpos_rect, 
                                              pos=vec2(0, HEIGHT-200), size=[140, 200], box_title='Main Controls')
                elif self.display_buttons[i].button_title == 'Bot 2':
                    self.multiple_buttons_box(surf=surf, buttons=self.bot_buttons_2, mpos_rect=mpos_rect, 
                                              pos=vec2(WIDTH-140, HEIGHT-200), size=[140, 200], box_title='Enemy Controls')


        pg.draw.rect(surf, PINK, (mpos.x - 4, mpos.y - 4, self.click_size[0], self.click_size[1]), 1, 1)

    # -------- button functions ------- #

    def reset_bots(self):
        self.app.timer.reset_timeout()
        self.app.timer2.reset_timeout()
        main_bot: SumoBot = self.app.main_bot
        enemy_bot: SumoBot = self.app.enemy_bot
        main_bot.pos = self.starting_positions[0].copy()
        enemy_bot.pos = self.starting_positions[1].copy() 
        self.set_bot_maunual('main_bot')
        self.set_bot_maunual('enemy_bot')
        DRIVE_STOP(main_bot)
        DRIVE_STOP(enemy_bot)
        #main_bot.state_machine.state = State_e.STATE_WAIT
        #enemy_bot.state_machine.state = State_e_2.STATE_WAIT
        main_bot.angle = 0
        enemy_bot.angle = 0

    def send_ir_command(self, bot):
        if bot == 'main_bot': self.app.main_bot.ir_pressed = true
        elif bot == 'enemy_bot': self.app.enemy_bot.ir_pressed = true

    def set_bot_autonomous(self, bot):
        if bot == 'main_bot': self.app.main_bot.set_autonomous()
        elif bot == 'enemy_bot': self.app.enemy_bot.set_autonomous()

    def set_bot_maunual(self, bot):
        if bot == 'main_bot': self.app.main_bot.set_manual()
        elif bot == 'enemy_bot': self.app.enemy_bot.set_manual()

    def set_bot_drive_mode(self, bot):
        if bot == 'main_bot': self.app.main_bot.set_drive_mode()
        elif bot == 'enemy_bot': self.app.enemy_bot.set_drive_mode()

    def test_zero(self):
        self.set_bot_autonomous('main_bot')
        self.send_ir_command('main_bot')
        self.set_bot_maunual('enemy_bot')
    def test_one(self):
        self.set_bot_autonomous('enemy_bot')
        self.send_ir_command('enemy_bot')
    def test_two(self):
        self.test_zero()
        self.test_one()

    # --------- user interface -------- #

    def multiple_buttons_box(self, surf, buttons: list[Button_Click], mpos_rect: pg.rect, pos: vec2, size: list[int], box_title: str):
        render_text_box(surf, pos=vec2(pos.x, pos.y), size=size, color=TEXT_BG)

        text_surf = text_surface(text=box_title, size=12, italic=false, rgb=WHITE)
        text_size: list[int] = text_surf.get_size()
        text_pos: vec2 = vec2(pos.x + (size[0] - text_size[0]) // 2, pos.y + 8)
        surf.blit(text_surf, (text_pos.x, text_pos.y))

        for i in range(len(buttons)):
            button_pos: vec2 = vec2(pos.x + (size[0]//2) - buttons[i].size[0]//2, pos.y + (i * 26) + 30)
            button_pressed: bool = self.button_box(surf=surf, pos=button_pos, size=buttons[i].size,
                                                   button_title=buttons[i].button_title, mpos_rect=mpos_rect, font_size=10)
            if button_pressed and buttons[i].func:
                num_of_args = len(buttons[i].args)
                if num_of_args == 0: buttons[i].func()
                elif num_of_args == 1: buttons[i].func(buttons[i].args[0])
                elif num_of_args == 2: buttons[i].func(buttons[i].args[0], buttons[i].args[1])
                elif num_of_args == 3: buttons[i].func(buttons[i].args[0], buttons[i].args[1], buttons[i].args[2])

    def button_box(self, surf, pos: vec2, size: list[int], button_title: str, mpos_rect: pg.rect, inner_col: tuple=BUTTON_COLOR, outline_col: tuple=OUTLINE_COLOR, inner_size: float=.94, font_size:int=12) -> bool:
        inner_box_size: list[int] = [int(size[0] * inner_size), int(size[1] * inner_size)]
        inner_box_pos: vec2 = vec2(pos.x + (size[0] - inner_box_size[0]) // 2, pos.y + (size[1] - inner_box_size[1]) // 2)

        pg.draw.rect(surf, inner_col, (pos.x, pos.y, size[0], size[1]), 0, 1)

        text_surf = text_surface(text=button_title, size=font_size, italic=false, rgb=WHITE)
        text_size: list[int] = text_surf.get_size()
        text_pos: vec2 = vec2(pos.x + (size[0] - text_size[0]) // 2, pos.y + (size[1] - text_size[1]) // 2)
        surf.blit(text_surf, (text_pos.x, text_pos.y))

        button_rect: pg.rect = pg.Rect(pos.x, pos.y, size[0], size[1])
        if mpos_rect.colliderect(button_rect) and self.click == Click.NONE:
            pg.draw.rect(surf, outline_col, (inner_box_pos.x, inner_box_pos.y, inner_box_size[0], inner_box_size[1]), 1, 1)
        if self.click == Click.CLICK_DOWN and mpos_rect.colliderect(button_rect):
            pg.draw.rect(surf, outline_col, (inner_box_pos.x, inner_box_pos.y, inner_box_size[0], inner_box_size[1]), 3, 1)
        if self.click == Click.CLICK_FIRST_PRESSED and mpos_rect.colliderect(button_rect): return true
        return false

    def flip_display_option(self, display_button: Button):
        display_button.display = not display_button.display

    def handle_click(self):
        if self.clicked:
            if self.click == Click.CLICK_FIRST_PRESSED or self.click == Click.CLICK_DOWN: self.click = Click.CLICK_DOWN
            elif self.click == Click.CLICK_UP or self.click == Click.NONE: self.click = Click.CLICK_FIRST_PRESSED
        elif not self.clicked:
            if self.click == Click.NONE or self.click == Click.CLICK_UP: self.click = Click.NONE
            else: self.click = Click.CLICK_UP
        return self.click