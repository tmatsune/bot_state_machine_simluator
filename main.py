from scripts.settings import *
from scripts.utils import *
from bot.sumo_bot import *
from bot.timer import *
from simulator_settings.simulator import *

starting_positions: list[vec2] = [vec2(300, 400), vec2(300, 200)]
class App():
    def __init__(self) -> None:
        pg.init()
        self.screen: pg.display = pg.display.set_mode((WIDTH, HEIGHT))
        self.screen.fill((0, 0, 0))
        self.display: pg.Surface = pg.Surface((WIDTH, HEIGHT))
        self.delta_time: float = 0
        self.clock: pg.time = pg.time.Clock()
        self.timer: Timer = Timer(self)
        self.timer2: Timer = Timer(self)

        self.stage: dict = {'radius': 200}
        self.movement: list[bool] = [false, false, false, false]
        self.movement_2: list[bool] = [false, false, false, false]

        self.main_bot: SumoBot = SumoBot(self, starting_positions[0], [CELL_SIZE,CELL_SIZE],
                                         get_image('assets/images/bot_2.png', [30,30]), Test_State_Machine.FIRST)
        self.enemy_bot: SumoBot = SumoBot(self, starting_positions[1], [CELL_SIZE,CELL_SIZE],
                                          get_image('assets/images/enemy.png', [30,30]), Test_State_Machine.SECOND,  Bot_Type.ENEMY)
        
        self.main_bot.target = self.enemy_bot
        self.enemy_bot.target = self.main_bot

        self.text_size: int = 10        

        self.show_history_log: bool = false
        self.history_log_list: list = []

        self.simulator_settings: Simulator_Settings = Simulator_Settings(app=self)
        self.mpos: vec2 = vec2(0)
        #pg.mouse.set_visible(false)

    def get_internal_state(self, bot: SumoBot) -> str:
        curr_state: State_e = bot.state_machine.state
        if curr_state == State_e.STATE_RETREAT:
            return internal_state_to_str(curr_state, bot.state_machine.retreat_state.internal_state)
        elif curr_state == State_e.STATE_SEARCH:
            return internal_state_to_str(curr_state, bot.state_machine.search_state.internal_state)
        elif curr_state == State_e.STATE_ATTACK:
            return internal_state_to_str(curr_state, bot.state_machine.attack_state.internal_state)
        return 'NONE'

    def get_internal_state_2(self, bot: SumoBot) -> str:
        curr_state: State_e_2 = bot.state_machine.state
        if curr_state == State_e_2.STATE_ATTACK:
            pass
        elif curr_state == State_e_2.STATE_SEARCH:
            pass
        elif curr_state == State_e_2.STATE_FLANK:
            pass
        elif curr_state == State_e_2.STATE_RETREAT:
            pass
        return 'NONE'

    def render_bot_peripherals(self, surf, bot: SumoBot, pos: vec2):
        render_text_box(surf, pos=vec2(pos.x, pos.y), size=[140, 170], color=TEXT_BG)

        render_text(surf=surf, text=f'State: {state_to_str(bot.state_machine.state)}',
                    pos=vec2(pos.x + 10, pos.y + 10), offset=vec2(0), size=self.text_size, italic=false, rgb=WHITE)
        internal_state: str = self.get_internal_state(bot)
        render_text(surf=surf, text=f'Internal: {internal_state}',
                    pos=vec2(pos.x + 10, pos.y + 30), offset=vec2(0), size=self.text_size, italic=false, rgb=WHITE)
        render_text(surf=surf, text=f'Time: {self.timer.time} ',
                    pos=vec2(pos.x + 10, pos.y + 50), offset=vec2(0), size=self.text_size, italic=false, rgb=WHITE)
        render_text(surf=surf, text=f'Timeout: {self.timer.timeout}',
                    pos=vec2(pos.x + 10, pos.y + 70), offset=vec2(0), size=self.text_size, italic=false, rgb=WHITE)

    def render_bot_peripherals_2(self, surf, bot: SumoBot, pos: vec2):
        render_text_box(surf, pos=vec2(pos.x, pos.y), size=[140, 170], color=TEXT_BG)
        render_text(surf=surf, text=f'Enemy History : ', pos=vec2(pos.x+10, pos.y+10), offset=vec2(0), size=self.text_size, italic=false, rgb=WHITE)
        history_inputs: list[str] = bot.state_machine.input_history.get_str_vals()
        render_text_box(surf, pos=vec2(pos.x+4, pos.y+30), size=[120, 70], color=WHITE, hollow=1)
        for i in range(len(history_inputs)):
            render_text(surf=surf, text=f'{history_inputs[i]}', pos=vec2(pos.x+10, pos.y+30+(i * 10)), offset=vec2(0), size=self.text_size, italic=false, rgb=WHITE)

    def render_target_bot_peripherals(self, surf, bot: SumoBot, pos:vec2):
        render_text_box(surf, pos=vec2(pos.x, pos.y), size=[140, 170], color=TEXT_BG)

        render_text(surf=surf, text=f'State: {state_2_str(bot.state_machine.state)}',
                    pos=vec2(pos.x + 10, pos.y+10), offset=vec2(0), size=self.text_size, italic=false, rgb=WHITE)

        render_text(surf=surf, text=f'Time: {self.timer2.time} ',
                    pos=vec2(pos.x + 10, pos.y+30), offset=vec2(0), size=self.text_size, italic=false, rgb=WHITE)
        render_text(surf=surf, text=f'Timeout: {self.timer2.timeout}',
                    pos=vec2(pos.x + 10, pos.y+50), offset=vec2(0), size=self.text_size, italic=false, rgb=WHITE)
        #drive direction and speed
        render_text(surf=surf, text=f'Drive Setting: {drive_setting_str(bot.drive_setting, all_drive_settings_2)} ',
                    pos=vec2(pos.x + 10, pos.y+70), offset=vec2(0), size=self.text_size, italic=false, rgb=WHITE)

    def render_target_bot_peripherals_2(self, surf, bot: SumoBot):
        pass

    def align_right(self, screen_size: list[int], box_size: list[int]) -> vec2:
        box_pos: vec2 = vec2(0)
        mid_pos: vec2 = vec2(box_size[0] // 2, box_size[1] // 2)
        box_pos.x = (screen_size[0] // 2) - mid_pos.x
        box_pos.y = (screen_size[1] // 2) - mid_pos.y
        return box_pos

    def render_bot_history_log(self, surf):
        box_pos: vec2 = self.align_right([WIDTH, HEIGHT], HISTORY_SIZE)
        inner_box_pos: vec2 = self.align_right([WIDTH, HEIGHT], [HISTORY_SIZE[0] - 10, HISTORY_SIZE[1] - 10])
        render_text_box(surf, pos=vec2(box_pos.x, box_pos.y), size=HISTORY_SIZE, color=TEXT_BG)
        render_text_box(surf, pos=vec2(inner_box_pos.x, inner_box_pos.y), size=[HISTORY_SIZE[0] - 10, HISTORY_SIZE[1] - 10], color=WHITE, hollow=1)
        render_text(surf=surf, text=f'History Log', pos=vec2((WIDTH // 2) - 40, 140), offset=vec2(0), size=14, italic=false, rgb=WHITE)

        for i in range(len(self.history_log_list)):
            log_data: dict = self.history_log_list[i]
            log_data_str = f'State: {log_data["state"]} | Event: {log_data["event"]} | Drive Setting: {log_data["drive_setting"]} | {log_data["enemy"]} | Line: {log_data["line"]}'
            render_text(surf=surf, text=log_data_str, pos=vec2(60, 160 + (i * 11)), offset=vec2(0), size=8, italic=false, rgb=WHITE)

    def render(self):
        self.display.fill(GRAY)

        mouse_pos: list = pg.mouse.get_pos()
        self.mpos = vec2(mouse_pos[0], mouse_pos[1])

        pg.draw.circle(self.display, BLACK, (CENTER.x, CENTER.y), self.stage["radius"])
        pg.draw.circle(self.display, WHITE, (CENTER.x, CENTER.y), self.stage["radius"] + 4, 4)

        self.timer.tick()
        self.timer2.tick()

        # DISPLAY BOT SETTINGS
        # self.render_bot_settings(self.display, self.main_bot)
        # self.render_bot_settings_2(self.display, self.main_bot)

        # DISPLAY TARGET BOT SETTINGS
        # self.render_target_bot_settings(self.display, self.main_bot) # TODO change main_bot back to enemy_bot
        # self.render_target_bot_settings_2(self.display, self.main_bot) # TODO change main_bot back to enemy_bot

        # MAIN BOT
        self.main_bot.update()
        self.main_bot.render(self.display)

        # ENEMY BOT
        self.enemy_bot.enemy_update()
        self.enemy_bot.render(self.display)

        if self.show_history_log:
            self.render_bot_history_log(self.display)

        # SIMULATOR SETTINGS
        self.simulator_settings.update()
        self.simulator_settings.render(surf=self.display, mpos=self.mpos)

        self.screen.blit(self.display, (0, 0))
        pg.display.flip()
        pg.display.update()

    def check_inputs(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                logs: list = self.main_bot.history_log.convert_history_to_list()
                pg.quit()
                sys.exit()

            if e.type == pg.KEYDOWN:
                if e.key == pg.K_LEFT: self.movement[0] = true
                if e.key == pg.K_RIGHT: self.movement[1] = true
                if e.key == pg.K_UP: self.movement[2] = true
                if e.key == pg.K_DOWN: self.movement[3] = true

                if e.key == pg.K_a: self.movement_2[0] = true
                if e.key == pg.K_d: self.movement_2[1] = true
                if e.key == pg.K_w: self.movement_2[2] = true
                if e.key == pg.K_s: self.movement_2[3] = true

                if e.key == pg.K_c:
                    self.main_bot.ir_pressed = true
                    if TEST_CASE == Test_Cases.STATE_MACHINE_BOTH:
                        self.enemy_bot.ir_pressed = true
                if e.key == pg.K_m:
                    if TEST_CASE == Test_Cases.STATE_MACHINE_0 or TEST_CASE == Test_Cases.STATE_MACHINE_1:
                        self.main_bot.change_mode()
                    elif TEST_CASE == Test_Cases.STATE_MACHINE_BOTH:
                        self.enemy_bot.change_mode()
                        self.main_bot.change_mode()
                if e.key == pg.K_e:
                    self.enemy_bot.enemy_can_drive = not self.enemy_bot.enemy_can_drive
                if e.key == pg.K_h:
                    self.history_log_list = self.main_bot.history_log.convert_history_to_list()
                if e.key == pg.K_j:
                    self.show_history_log = not self.show_history_log

            if e.type == pg.KEYUP:
                if e.key == pg.K_LEFT: self.movement[0] = false
                if e.key == pg.K_RIGHT: self.movement[1] = false
                if e.key == pg.K_UP: self.movement[2] = false
                if e.key == pg.K_DOWN: self.movement[3] = false

                if e.key == pg.K_a: self.movement_2[0] = false
                if e.key == pg.K_d: self.movement_2[1] = false
                if e.key == pg.K_w: self.movement_2[2] = false
                if e.key == pg.K_s: self.movement_2[3] = false

                if e.key == pg.K_c:
                    self.main_bot.ir_pressed = false

            if e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    self.simulator_settings.clicked = true
            if e.type == pg.MOUSEBUTTONUP:
                if e.button == 1:
                    self.simulator_settings.clicked = false

    def update(self):
        self.clock.tick(60)
        pg.display.set_caption(f'{self.clock.get_fps()}')
        self.delta_time = self.clock.tick(60)
        self.delta_time /= 1000

    def run(self):
        while True:
            self.render()
            self.check_inputs()
            self.update()

if __name__ == '__main__':
    app = App()
    app.run()
