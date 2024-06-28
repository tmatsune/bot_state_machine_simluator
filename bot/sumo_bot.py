from scripts.settings import * 
from scripts.utils import * 
from bot.lines import * 
from bot.enemy import * 
from bot.drive import * 
from bot.timer import * 
from statemachine.state_machine import * 
from statemachine.state_machine_2 import * 

class Bot_Mode(Enum):
    MANUAL = 0
    AUTONOMOUS = 1

class Bot_Type(Enum):
    MAIN = 0
    ENEMY = 1

class Test_State_Machine(Enum):
    FIRST = 1 
    SECOND = 2

class Test_Cases(Enum):
    STATE_MACHINE_0 = 0
    STATE_MACHINE_1 = 1
    STATE_MACHINE_BOTH = 2

TEST_CASE: Test_Cases = Test_Cases.STATE_MACHINE_0


class SumoBot():
    def __init__(self, app, position: vec2, size: list[int], image: pg.image, state_machine_test_num, bot_type: Bot_Type = Bot_Type.MAIN) -> None:
        from main import App
        self.app: App = app
        self.size: list[int] = size
        self.image: pg.image = image
        self.pos: vec2 = position
        self.angle: float = 0
        self.velocity: vec2 = vec2(0)
        self.vel: vec2 = vec2(0)
        self.force: vec2 = vec2(0)
        self.kinetic_friction = 0.34
        self.target: EnemyBot
        self.mode = Bot_Mode.MANUAL
        self.speed: int = 8
        self.enemy_speed: int = 10
        self.timer: Timer = app.timer
        self.timer2: Timer = app.timer2
        self.bot_type: Bot_Type = bot_type

        self.mask = pg.mask.from_surface(image)
        self.drive_setting: Drive_Settings = Drive_Settings(0,0,0)

        self.test_state_machine: Test_State_Machine = state_machine_test_num

        self.angles: list[int] = [45, 135, 225, 315]
        self.vertices: list[vec2] = [vec2(0), vec2(0), vec2(0), vec2(0)]

        # peripherals
        self.line_sensors = [false, false, false, false]
        self.enemy_sensors = [false, false, false]
        self.range_distance = [inf, inf, inf]

        self.ir_command: bool = false
        self.ir_pressed: bool = false

        self.line_distance: int = 26
        self.vertex_mult: int = 20

        # state machine
        self.state_machine = State_Machine()
        self.init_state_machine()
        
        self.history_log: Bot_History_Log = Bot_History_Log(app=app, bot=self, max_size=20)
        self.can_drive: bool = true

    def init_state_machine(self):
        if self.test_state_machine == Test_State_Machine.FIRST:
            self.state_machine = State_Machine()
            state_machine_init(self.state_machine, self)
        elif self.test_state_machine == Test_State_Machine.SECOND:
            self.state_machine: State_Machine_2 = State_Machine_2()
            self.state_machine.state_machine_init(self)

    def update(self):
        self.angle %= 360
        if self.mode == Bot_Mode.MANUAL and self.can_drive:
            self.angle += (self.app.movement[1] - self.app.movement[0]) * 8
            #self.move_with_physics()
            if self.app.movement[2] or self.app.movement[3]:
                self.move()
        elif self.mode == Bot_Mode.AUTONOMOUS:
            self.autonomous_drive_2()

        # PERIPHERALS
        self.update_line_sensors()
        self.raycast()

        # STATE MACHINE 
        if self.test_state_machine == Test_State_Machine.FIRST: state_machine_run(self.state_machine)
        elif self.test_state_machine == Test_State_Machine.SECOND: self.state_machine.state_machine_run()

        # history log
        if self.test_state_machine == Test_State_Machine.SECOND:
            self.history_log.insert_log() # NOTE note for debugging state machine 

        normal, depth, colliding = boxes_colliding(self, self.target)
        if colliding:
                self.step(-normal * depth / 2)
                self.target.step(normal * depth / 2)   

    def render(self, surf):
        image = pg.transform.rotate(self.image, -self.angle)
        img_rect = image.get_rect(center=(self.pos.x, self.pos.y))
        surf.blit(image, img_rect)
    
    def step(self, vector: vec2):
        self.pos += vector

    def move(self):
        forward: int = 1 if self.app.movement[2] else -1
        x_speed = math.cos(math.radians(self.angle))
        y_speed = math.sin(math.radians(self.angle))
        self.vel = vec2(x_speed, y_speed) * self.speed * forward
        self.pos += self.vel
        '''
        self.pos.x += self.vel.x
        if mask_collision(self.mask, self.pos, self.target.mask, self.target.pos):
            if self.vel.x < 0:  self.target.pos.x = self.pos.x - CELL_SIZE
            elif self.vel.x > 0: self.target.pos.x = self.pos.x + CELL_SIZE
        self.pos.y += self.vel.y
        if mask_collision(self.mask, self.pos, self.target.mask, self.target.pos):
            if self.vel.y > 0: self.target.pos.y = self.pos.y + CELL_SIZE
            elif self.vel.y < 0: self.target.pos.y = self.pos.y - CELL_SIZE        
        '''
    def move_2(self):
        forward: int = 1 if self.app.movement_2[2] else -1
        x_speed = math.cos(math.radians(self.angle))
        y_speed = math.sin(math.radians(self.angle))
        self.vel = vec2(x_speed, y_speed) * self.speed * forward
        self.pos += self.vel

    def move_with_physics(self):
        forward: int = 1 if self.app.movement[2] else 0
        if not forward: forward = -1 if self.app.movement[3] else 0
        x_speed = math.cos(math.radians(self.angle))
        y_speed = math.sin(math.radians(self.angle))
        force: vec2 = vec2(x_speed, y_speed) * 5 * forward
        self.velocity += force

        self.pos += self.velocity

        if self.velocity != vec2(0):
            self.velocity += (self.velocity) * self.kinetic_friction * -1
            if self.velocity.length() < self.kinetic_friction: self.velocity = vec2(0)

        '''
        self.pos.x += self.velocity.x
        if mask_collision(self.mask, self.pos, self.target.mask, self.target.pos):
            if self.velocity.x < 0: self.target.pos.x = self.pos.x - CELL_SIZE
            elif self.velocity.x > 0: self.target.pos.x = self.pos.x + CELL_SIZE
        self.pos.y += self.velocity.y
        if mask_collision(self.mask, self.pos, self.target.mask, self.target.pos):
            if self.velocity.y > 0: self.target.pos.y = self.pos.y + CELL_SIZE
            elif self.velocity.y < 0: self.target.pos.y = self.pos.y - CELL_SIZE
        '''


    def autonomous_drive(self):
        self.angle += self.drive_setting.right - self.drive_setting.left
        x_speed = math.cos(math.radians(self.angle))
        y_speed = math.sin(math.radians(self.angle))
        speed = vec2(x_speed, y_speed) * self.drive_setting.speed * .66
        self.vel += speed
        
        if self.vel != vec2(0):
            self.vel += (self.vel) * self.kinetic_friction * -1
            if self.vel.length() < self.kinetic_friction: self.vel = vec2(0)

        self.pos += self.vel
        '''
        self.pos.x += self.vel.x
        if mask_collision(self.mask, self.pos, self.target.mask, self.target.pos):
            if self.vel.x < 0: self.target.pos.x = self.pos.x - CELL_SIZE
            elif self.vel.x > 0: self.target.pos.x = self.pos.x + CELL_SIZE
        self.pos.y += self.vel.y
        if mask_collision(self.mask, self.pos, self.target.mask, self.target.pos):
            if self.vel.y > 0: self.target.pos.y = self.pos.y + CELL_SIZE
            elif self.vel.y < 0: self.target.pos.y = self.pos.y - CELL_SIZE
        '''

    def autonomous_drive_2(self):
        self.angle += self.drive_setting.right - self.drive_setting.left
        x_speed = math.cos(math.radians(self.angle))
        y_speed = math.sin(math.radians(self.angle))
        speed = vec2(x_speed, y_speed) * self.drive_setting.speed * 1.2
        self.pos += speed
    # -------- control functions -------- #

    def change_mode(self):
        if self.mode == Bot_Mode.MANUAL: self.mode = Bot_Mode.AUTONOMOUS
        elif self.mode == Bot_Mode.AUTONOMOUS: self.mode = Bot_Mode.MANUAL
    
    def set_autonomous(self): self.mode = Bot_Mode.AUTONOMOUS
    def set_manual(self): self.mode = Bot_Mode.MANUAL

    def set_drive_mode(self): self.can_drive = not self.can_drive
        
    # --------- GET PERIPHERALS --------- #
    
    def get_ir_command(self):
        can: bool = self.ir_pressed
        if can and not self.ir_command:
            self.ir_command = true
            return Ir_Command.RUN
        if not can: self.ir_command = false
        return Ir_Command.NONE
    
    def get_line_position(self):
        front_right = self.line_sensors[0]
        front_left = self.line_sensors[3]
        back_right = self.line_sensors[1]
        back_left = self.line_sensors[2]
        if front_left:
            if front_right:
                return Line_Pos.LINE_FRONT
            elif back_left:
                return Line_Pos.LINE_LEFT
            elif back_right:
                return Line_Pos.LINE_DIAGONAL_LEFT
            else:
                return Line_Pos.LINE_FRONT_LEFT
        elif front_right:
            if back_right:
                return Line_Pos.LINE_RIGHT
            elif back_left:
                return Line_Pos.LINE_DIAGONAL_RIGHT
            else:
                return Line_Pos.LINE_FRONT_RIGHT
        elif back_left:
            if back_right:
                return Line_Pos.LINE_BACK
            else:
                return Line_Pos.LINE_BACK_LEFT
        elif back_right:
            return Line_Pos.LINE_BACK_RIGHT

        return Line_Pos.LINE_NONE

    def get_enemy_position(self):
        enemy = Enemy_Struct(Enemy_Pos.ENEMY_POS_NONE, Enemy_Range.ENEMY_RANGE_NONE)
        enemy_range: int = 0

        front_range: float = self.range_distance[1]
        front_left_range: float = self.range_distance[0]
        front_right_range: float = self.range_distance[2]

        front: bool = front_range < RANGE_THRESHOLD
        front_left: bool = front_left_range < RANGE_THRESHOLD
        front_right: bool = front_right_range < RANGE_THRESHOLD

        if front and front_left and front_right:
            enemy.position = Enemy_Pos.ENEMY_POS_FRONT_ALL
            enemy_range = (front_range + front_left_range + front_right_range) // 3
        elif front_left and front_right:
            enemy.position = Enemy_Pos.ENEMY_POS_IMPOSSIBLE
        elif front_left:
            if front:
                enemy.position = Enemy_Pos.ENEMY_POS_FRONT_AND_FRONT_LEFT
                enemy_range = (front_range + front_left_range) // 2
            else:
                enemy.position = Enemy_Pos.ENEMY_POS_FRONT_LEFT
                enemy_range = front_left_range // 1
        elif front_right:
            if front:
                enemy.position = Enemy_Pos.ENEMY_POS_FRONT_AND_FRONT_RIGHT
                enemy_range = (front_range + front_right_range) // 2
            else:
                enemy.position = Enemy_Pos.ENEMY_POS_FRONT_RIGHT
                enemy_range = front_right_range // 1
        elif front:
            enemy.position = Enemy_Pos.ENEMY_POS_FRONT
            enemy_range = front_range // 1
        else:
            enemy.position = Enemy_Pos.ENEMY_POS_NONE
        
        if enemy_range == 0: return enemy

        if enemy_range > 200: enemy.range = Enemy_Range.ENEMY_RANGE_FAR
        elif enemy_range > 100: enemy.range = Enemy_Range.ENEMY_RANGE_MID
        else: enemy.range = Enemy_Range.ENEMY_RANGE_CLOSE

        return enemy

    # --------- PERIPHERALS --------- # 
    def update_line_sensors(self):
        self.line_sensors = [false, false, false, false]
        for i in range(len(self.angles)):
            offset = self.angles[i]
            x_speed = math.cos(math.radians(self.angle + offset)) * self.line_distance
            y_speed = math.sin(math.radians(self.angle + offset)) * self.line_distance
            vertex = vec2(self.pos.x + x_speed, self.pos.y + y_speed)


            pg.draw.circle(self.app.display, GREEN, (vertex.x, vertex.y), 4)
            if not check_circle_collision([vertex.x, vertex.y, 4], [CENTER.x, CENTER.y, 200]):
                pg.draw.circle(self.app.display, RED, (vertex.x, vertex.y), 4)
                self.line_detected_bool = True
                self.line_sensors[i] = True

            x_pos = math.cos(math.radians(self.angle + offset)) * self.vertex_mult
            y_pos = math.sin(math.radians(self.angle + offset)) * self.vertex_mult
            vertex_pos = vec2(self.pos.x + x_pos, self.pos.y + y_pos)
            if self.angles[i] == 45: self.vertices[2] = vertex_pos     # bottom right
            elif self.angles[i] == 135: self.vertices[3] = vertex_pos  # bottom left
            elif self.angles[i] == 225: self.vertices[0] = vertex_pos  # top left
            elif self.angles[i] == 315: self.vertices[1] = vertex_pos  # top right

    def raycast(self):
        self.enemy_sensors = [False, False, False]
        self.range_distance = [inf, inf, inf]
        angles = [-15, 0, 15]
        for i in range(len(angles)):
            angle = math.radians(self.angle + angles[i]) + .0001
            if angle < 0:
                angle += 2 * math.pi
            if angle > math.pi * 2:
                angle -= 2 * math.pi

            horiz_dist = float('inf')
            vert_dist = float('inf')

            player_pos = self.pos.copy()

            horiz_x, horiz_y, horiz_hit = self.check_horizontal(angle, player_pos)
            vert_x, vert_y, vert_hit = self.check_vertical(angle, player_pos)

            horiz_dist = distance( player_pos.x, horiz_x, player_pos.y, horiz_y)
            vert_dist = distance(player_pos.x, vert_x, player_pos.y, vert_y)
            end_x = 0
            end_y = 0

            if vert_dist < horiz_dist:
                end_x, end_y = vert_x, vert_y
            if horiz_dist < vert_dist:
                end_x, end_y = horiz_x, horiz_y

            if not horiz_hit and not vert_hit:
                tile_key = f'{int(end_x // CELL_SIZE)},{int(end_y // CELL_SIZE)}'
                self.line_of_sight = False
                self.enemy_in_front_bool = False
                pg.draw.line(self.app.display, RED, (self.pos.x, self.pos.y), (end_x, end_y), 1)
            else:
                self.line_of_sight = True
                self.enemy_in_front_bool = True
                self.enemy_sensors[i] = True
                self.range_distance[i] = min(horiz_dist, vert_dist)
                pg.draw.line(self.app.display, GREEN, (self.pos.x, self.pos.y), (end_x, end_y), 1)

    def check_horizontal(self, ray_angle, player_pos):
        player_x = player_pos.x
        player_y = player_pos.y
        ray_pos_x = 0
        ray_pos_y = 0
        y_offset = 0
        x_offset = 0
        a_tan = -1 / math.tan(ray_angle)
        dof = 16
        player_hit = False

        if ray_angle > PI:  # looking up
            ray_pos_y = int(player_y // CELL_SIZE) * CELL_SIZE - .0001
            ray_pos_x = (player_y - ray_pos_y) * a_tan + player_x
            y_offset = -CELL_SIZE
            x_offset = -y_offset * a_tan
        if ray_angle < PI:  # looking down
            ray_pos_y = int(player_y // CELL_SIZE) * CELL_SIZE + CELL_SIZE
            ray_pos_x = (player_y - ray_pos_y) * a_tan + player_x
            y_offset = CELL_SIZE
            x_offset = -y_offset * a_tan
        if ray_angle == 0 or ray_angle == math.pi:
            ray_pos_x = player_x
            ray_pos_y = player_y
            dof = 0

        player_key = f'{int(self.target.pos.x // CELL_SIZE)},{int(self.target.pos.y // CELL_SIZE)}'
        for i in range(dof):
            ray_pos = (int(ray_pos_x // CELL_SIZE), int(ray_pos_y // CELL_SIZE))
            str_ray_pos = f'{ray_pos[0]},{ray_pos[1]}'
            if ray_pos[0] < -1 or ray_pos[0] > 20 or ray_pos[1] < -1 or ray_pos[1] > 20:
                break
            # if str_ray_pos in self.app.tile_map.tiles: break
            if player_key == str_ray_pos:
                player_hit = True
                break
            ray_pos_x += x_offset
            ray_pos_y += y_offset

        return ray_pos_x, ray_pos_y, player_hit

    def check_vertical(self, ray_angle, player_pos):
        player_x = player_pos.x
        player_y = player_pos.y
        ray_pos_x = 0
        ray_pos_y = 0
        y_offset = 0
        x_offset = 0
        n_tan = -math.tan(ray_angle)
        dof = 16
        player_hit = False

        P2 = math.pi / 2
        P3 = (math.pi * 3) / 2

        if ray_angle > P2 and ray_angle < P3:  # looking left
            ray_pos_x = int(player_x // CELL_SIZE) * CELL_SIZE - .0001
            ray_pos_y = (player_x - ray_pos_x) * n_tan + player_y
            x_offset = -CELL_SIZE
            y_offset = -x_offset * n_tan
        if ray_angle < P2 or ray_angle > P3:  # looking right
            ray_pos_x = int(player_x // CELL_SIZE) * CELL_SIZE + CELL_SIZE
            ray_pos_y = (player_x - ray_pos_x) * n_tan + player_y
            x_offset = CELL_SIZE
            y_offset = -x_offset * n_tan
        if ray_angle == 0 or ray_angle == math.pi:
            ray_pos_x = player_x
            ray_pos_y = player_y
            dof = 0

        player_key = f'{int(self.target.pos.x // CELL_SIZE)},{int(self.target.pos.y // CELL_SIZE)}'
        for i in range(dof):
            ray_pos = (int(ray_pos_x // CELL_SIZE),
                       int(ray_pos_y // CELL_SIZE))
            str_ray_pos = f'{ray_pos[0]},{ray_pos[1]}'
            if ray_pos[0] < -1 or ray_pos[0] > 20 or ray_pos[1] < -1 or ray_pos[1] > 20:
                break
            # if str_ray_pos in self.app.tile_map.tiles: break
            if player_key == str_ray_pos:
                player_hit = True
                break
            ray_pos_x += x_offset
            ray_pos_y += y_offset

        return ray_pos_x, ray_pos_y, player_hit

    def enemy_update(self):
        self.angle %= 360
        if self.mode == Bot_Mode.MANUAL and self.can_drive:
            self.angle += (self.app.movement_2[1] - self.app.movement_2[0]) * self.enemy_speed
            if self.app.movement_2[2] or self.app.movement_2[3]:
                self.move_2()
        elif self.mode == Bot_Mode.AUTONOMOUS:
            self.autonomous_drive_2()

        # PERIPHERALS
        self.update_line_sensors()
        self.raycast()
        
        # STATE MACHINE
        if self.test_state_machine == Test_State_Machine.FIRST: state_machine_run(self.state_machine)
        elif self.test_state_machine == Test_State_Machine.SECOND: self.state_machine.state_machine_run()

        normal, depth, colliding = boxes_colliding(self, self.target)
        if colliding:
            self.step(-normal * depth / 2)
            self.target.step(normal * depth / 2)

# --------------------------------------- LOG HISTORY --------------------------------------- #
class Log_Data:
    def __init__(self) -> None:
        self.state: State_e

class Log_Data_2:
    def __init__(self, state: State_e_2, event: State_Event_2, drive_setting: Drive_Settings, input_history, enemy: Enemy_Struct, line: Line_Pos) -> None:
        self.state: State_e_2 = state
        self.event: State_Event_2 = event
        self.drive_setting: Drive_Settings = drive_setting
        self.input_history: Input = input_history
        self.enemy: Enemy_Struct = enemy
        self.line: Line_Pos = line

    def output_log(self) -> dict:
        log_state: str = state_2_str(self.state)
        log_event: str = event_2_str(self.event)
        log_drive_setting: str = drive_setting_str(self.drive_setting, all_drive_settings=all_drive_settings_2)
        log_enemy: str = f'Enemy Position: {enemy_pos_to_str(self.enemy.position)} , Enemy Range: {enemy_range_to_str(self.enemy.range)}' if self.input_history else 'NO ENEMY'
        log_line: str = f'Line Position: {line_to_str(self.line)}' if self.input_history else 'NO LINE'
        return {
            'state' : log_state,
            'event': log_event,
            'drive_setting': log_drive_setting,
            'enemy': log_enemy,
            'line': log_line
        }

class Node_Log:
    def __init__(self, log_data: Log_Data_2) -> None:
        self.log_data: Log_Data_2 = log_data
        self.next: Node_Log = NULL
    
class Bot_History_Log:
    def __init__(self, app, bot: SumoBot, max_size: int) -> None:
        from main import App
        self.app: App = app
        self.bot: SumoBot = bot
        self.state_machine : State_Machine if self.bot else State_Machine_2 = bot.state_machine
        self.output_logs: list = []
        self.root: Node_Log = NULL
        self.top: Node_Log = NULL
        self.curr_size: int = 0
        self.max_size: int = max_size

    def insert_log(self) -> NULL:
        if self.curr_size == self.max_size:
            self.pop_log()
        new_log_data: Log_Data_2 = Log_Data_2(state=self.state_machine.state, 
                                              event=self.state_machine.last_event, 
                                              drive_setting=self.bot.drive_setting, 
                                              input_history=self.bot.state_machine.input_history.peek_top(), 
                                              enemy=self.state_machine.common_data.enemy, 
                                              line=self.state_machine.common_data.line)
        new_log: Node_Log = Node_Log(new_log_data)
        if not self.root:
            self.root = new_log
            self.top = new_log
            self.curr_size = 1
            return 
        self.top.next = new_log
        self.top = new_log
        self.curr_size += 1

    def pop_log(self) -> Node_Log:
        if self.curr_size == 0 or not self.root:
            return 
        self.curr_size -= 1
        res_node: Node_Log = self.root
        if self.root.next:
            new_root: Node_Log = res_node.next
            self.root = new_root
        else: self.root = NULL
        return res_node
    
    def convert_history_to_list(self) -> list:
        vals: list = []
        curr_node: Node_Log = self.root
        while curr_node:
            log_data: dict[str:str] = curr_node.log_data.output_log()
            vals.append(log_data)
            curr_node = curr_node.next
        return vals

# --------------------------------------- ENEMY --------------------------------------- #

class EnemyBot():
    def __init__(self, app, position: vec2, size: list[int], image: pg.image) -> None:
        from main import App
        self.app: App = app
        self.position: vec2 = position
        self.size: list[int] = size
        self.image: pg.image = image
        self.pos: vec2 = position
        self.angle: float = 0
        self.mask = pg.mask.from_surface(image)
        self.speed: int = 8

        self.target: SumoBot
        
    def update(self):
        if self.target.mode == Bot_Mode.MANUAL:
            pass
        elif self.target.mode == Bot_Mode.AUTONOMOUS:
            self.angle += (self.app.movement[1] - self.app.movement[0]) * 8
            if self.app.movement[2] or self.app.movement[3]:
                self.move()

    def move(self):
        forward: int = 1 if self.app.movement[2] else -1
        x_speed = math.cos(math.radians(self.angle))
        y_speed = math.sin(math.radians(self.angle))
        self.vel = vec2(x_speed, y_speed) * self.speed * forward

        self.pos.x += self.vel.x
        self.pos.y += self.vel.y
            
    def render(self, surf):
        image = pg.transform.rotate(self.image, -self.angle)
        img_rect = image.get_rect(center=(self.pos.x, self.pos.y))
        surf.blit(image, img_rect)
