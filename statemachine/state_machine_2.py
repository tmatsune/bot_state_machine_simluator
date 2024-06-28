from scripts.settings import * 
from statemachine.common_data_2 import * 
from bot.drive import * 

class State_Machine_2:
    def __init__(self) -> None:
        from bot.sumo_bot import SumoBot
        self.user: SumoBot
        self.common_data: Common_Data_2
        self.state: State_e_2
        self.internal_event: State_Event_2

        self.flank_state: Flank_State
        self.attack_state: Attack_State
        self.search_state: Search_State
        self.wait_state: Wait_State
        self.manual_state: Manual_State

        self.timer: Timer
        self.input_history: Input_History

    def state_machine_init(self, user):
        self.user = user
        self.common_data = Common_Data_2()
        self.state = State_e_2.STATE_WAIT
        self.internal_event: State_Event_2 = State_Event_2.STATE_EVENT_NONE
        self.sub_case_flag: bool = false

        self.flank_state: Flank_State = Flank_State()
        self.attack_state: Attack_State = Attack_State()
        self.search_state: Search_State = Search_State()
        self.wait_state: Wait_State = Wait_State()
        self.manual_state: Manual_State = Manual_State()
        self.retreat_state: Retreat_State = Retreat_State()
        self.attack_search_state: Attack_Search_State = Attack_Search_State()

        self.flank_state.common_data = self.common_data
        self.attack_state.common_data = self.common_data
        self.search_state.common_data = self.common_data
        self.wait_state.common_data = self.common_data
        self.manual_state.common_data = self.common_data
        self.retreat_state.common_data = self.common_data
        self.attack_search_state.common_data = self.common_data

        self.timer = user.timer2
        self.input_history = Input_History()

        self.common_data.common_data_init(self, user.timer2, self.input_history)

        # debugging
        self.last_event: State_Event_2 = State_Event_2.STATE_EVENT_NONE

    def state_machine_run(self):
        next_event: State_e_2 = self.get_input()
        self.last_event = next_event                # NOTE for debugging remove on bot
        self.process_event(next_event)
        

    def get_input(self) -> State_Event_2:

        self.common_data.enemy = self.user.get_enemy_position()
        self.common_data.line = self.user.get_line_position()
        self.common_data.ir_command = self.user.get_ir_command()

        data_input: Input = Input(self.common_data.enemy, self.common_data.line)
        input_history_save(self.input_history, data_input)

        if self.common_data.ir_command != Ir_Command.NONE:
            return State_Event_2.STATE_EVENT_COMMAND
        elif self.internal_event_done():
            return self.take_internal_event()
        elif self.timer.timer_timeout():
            return State_Event_2.STATE_EVENT_TIMEOUT
        elif self.common_data.line != Line_Pos.LINE_NONE:
            return State_Event_2.STATE_EVENT_LINE
        elif self.common_data.enemy.position != Enemy_Pos.ENEMY_POS_NONE:
            return State_Event_2.STATE_EVENT_ENEMY
        return State_Event_2.STATE_EVENT_NONE
    
    def process_event(self, event: State_Event_2) -> NULL:
        if self.sub_case_flag:
            for i in range(len(sub_cases)):
                if sub_cases[i].event == event and sub_cases[i].from_state == self.state:
                    self.enter_state(sub_cases[i].from_state, sub_cases[i].event, sub_cases[i].to_state)
                    if sub_cases[i].lower_flag: self.lower_sub_case_flag()
                    return NULL
            assert 0, f'ERROR ALL SUBCASES SHOULD BE FOUND, CURRENT STATE: {self.state}, WITH EVENT: {event}'
        else:
            for i in range(len(scene_transitions_2)):
                if scene_transitions_2[i].event == event and scene_transitions_2[i].from_state == self.state:
                    self.enter_state(scene_transitions_2[i].from_state, scene_transitions_2[i].event, scene_transitions_2[i].to_state)
                    return NULL
            assert 0, f'ERROR ALL CASES SHOULD BE FOUND, CURRENT STATE: {self.state}, WITH EVENT: {event}'

    def enter_state(self, from_state: State_e_2, event: State_Event_2, to_state: State_e_2) -> NULL:
        if from_state != to_state:
            self.timer.clear()
            self.state = to_state
        if to_state == State_e_2.STATE_FLANK:
            self.flank_state.enter_flank_state(from_state, event)
        elif to_state == State_e_2.STATE_ATTACK:
            self.attack_state.enter_attack_state(from_state, event)
        elif to_state == State_e_2.STATE_SEARCH:
            self.search_state.enter_search_state(from_state, event)
        elif to_state == State_e_2.STATE_RETREAT:
            self.retreat_state.enter_retreat_state(from_state, event)
        elif to_state == State_e_2.STATE_ATTACK_SEARCH:
            self.attack_search_state.enter_attack_search_state(from_state, event)
        elif to_state == State_e_2.STATE_WAIT:
            self.wait_state.enter_wait_state(from_state, event)
        elif to_state == State_e_2.STATE_MANUAL:
            self.manual_state.enter_manual_state(from_state, event)

    def internal_event_done(self) -> bool:
        if self.internal_event != State_Event_2.STATE_EVENT_NONE:
            return true
        return false
        
    def take_internal_event(self) -> State_Event_2:
        saved_event: State_Event_2 = self.internal_event
        self.internal_event = State_Event_2.STATE_EVENT_NONE
        return saved_event
    
    def post_internal_event(self, internal_event: State_Event_2) -> None:
        assert self.internal_event == State_Event_2.STATE_EVENT_NONE, f'ERROR INTERNAL EVENT SHOULD BE NONE'
        self.internal_event = internal_event
    
    def raise_sub_case_flag(self) -> None:
        assert self.sub_case_flag == false, f'ERROR SUBCASE FLAG SHOULD BE SET TO FALSE IS {self.sub_case_flag}'
        self.sub_case_flag = true
    def lower_sub_case_flag(self) -> None:
        assert self.sub_case_flag == true, f'ERROR SUBCASE FLAG SHOULD BE SET TO TRUE IS {self.sub_case_flag}'
        self.sub_case_flag = false

# ------------------------------------ FLANK ---------------------------------- #

class Internal_Flank_State(Enum):
    RIGHT_FLANK = 0
    LEFT_FLANK = 1
    FEIGNED_RETREAT = 2
    RIGHT_BEHIND_FLANK = 3
    LEFT_BEHIND_FLANK = 4
    FLAKN_NONE = 5

@dataclass
class Move_Setting:
    direction: Drive_Dir
    speed: Drive_Speed
    duration: float
    search_for_enemy: bool

class Flank_Tactic:
    def __init__(self, moves: list[Move_Setting], move_count: int) -> None:
        self.moves: list[Move_Setting] = moves
        self.move_count: int = move_count
        self.internal_state: Internal_Flank_State = Internal_Flank_State.RIGHT_FLANK

flank_maneuvers: list[Flank_Tactic] = [
    Flank_Tactic(moves=[
            Move_Setting(Drive_Dir.DRIVE_DIR_ROTATE_RIGHT, Drive_Speed.DRIVE_SPEED_MAX, 40, false),
            Move_Setting(Drive_Dir.DRIVE_DIR_FORWARD, Drive_Speed.DRIVE_SPEED_MAX, 250, false),
            Move_Setting(Drive_Dir.DRIVE_DIR_ROTATE_LEFT, Drive_Speed.DRIVE_SPEED_MAX, 140, true),
        ], move_count=3), 
    Flank_Tactic(moves=[
            Move_Setting(Drive_Dir.DRIVE_DIR_ROTATE_LEFT, Drive_Speed.DRIVE_SPEED_MAX, 40, false),
            Move_Setting(Drive_Dir.DRIVE_DIR_FORWARD, Drive_Speed.DRIVE_SPEED_MAX, 250, false),
            Move_Setting(Drive_Dir.DRIVE_DIR_ROTATE_RIGHT, Drive_Speed.DRIVE_SPEED_MAX, 140, true),
        ], move_count=3), 
]

class Flank_State:
    def __init__(self) -> None:
        self.common_data: Common_Data_2
        self.state: State_e_2 = State_e_2.STATE_FLANK
        self.internal_state: Internal_Flank_State = Internal_Flank_State.RIGHT_FLANK
        self.move_index: int = 0
        
    def enter_flank_state(self, from_state: State_e_2, event: State_Event_2):
        if from_state == State_e_2.STATE_SEARCH:
            if event == State_Event_2.STATE_EVENT_ENEMY:
                self.start_flank_maneuver()
        elif from_state == State_e_2.STATE_FLANK:
            if event == State_Event_2.STATE_EVENT_TIMEOUT:
                self.move_index += 1
                if self.move_index >= flank_maneuvers[self.internal_state.value].move_count:
                    self.common_data.state_machine.post_internal_event(State_Event_2.STATE_EVENT_FINISHED)
                elif flank_maneuvers[self.internal_state.value].moves[self.move_index].search_for_enemy:
                    self.common_data.state_machine.raise_sub_case_flag()
                    self.flank_set_drive()
                else:
                    self.flank_set_drive()
        elif from_state == State_e_2.STATE_ATTACK_SEARCH:
            if event == State_Event_2.STATE_EVENT_TIMEOUT:
                self.start_flank_maneuver()
            else:
                assert 0, f'ERROR ENTERING {state_2_str(self.state)} SHOULD NOT HAVE EVENT: {event_2_str(event)}'
        elif from_state == State_e_2.STATE_ATTACK or \
             from_state == State_e_2.STATE_MANUAL or \
             from_state == State_e_2.STATE_RETREAT or \
             from_state == State_e_2.STATE_WAIT:
            assert 0, f'ERROR ENTERING {state_2_str(self.state)} SHOULD NOT HAVE EVENT: {event_2_str(event)}'

    def start_flank_maneuver(self):
        last_enemy: Enemy_Struct = self.common_data.enemy
        if last_enemy.range == Enemy_Range.ENEMY_RANGE_MID or last_enemy.range == Enemy_Range.ENEMY_RANGE_CLOSE:
            self.common_data.state_machine.raise_sub_case_flag()
            return
        self.move_index = 0
        self.internal_state = self.choose_flank_maneuver()
        self.flank_set_drive()

    def flank_set_drive(self):
        assert self.move_index < flank_maneuvers[self.internal_state.value].move_count, f'ERROR: MOVE INDEX OUT OF BOUNDS INTERNAL STATE: {self.internal_state}'
        current_move: Move_Setting = flank_maneuvers[self.internal_state.value].moves[self.move_index]
        self.common_data.timer.start_new_timer(current_move.duration)
        drive_set(direction=current_move.direction, speed=current_move.speed, bot=self.common_data.state_machine.user, all_drive_settings=all_drive_settings_2)

    def choose_flank_maneuver(self) -> Internal_Flank_State:
        last_enemy: Enemy_Struct = self.common_data.enemy
        if enemy_at_left(last_enemy):
            if last_enemy.range == Enemy_Range.ENEMY_RANGE_CLOSE:
                return Internal_Flank_State.RIGHT_FLANK
            elif last_enemy.range == Enemy_Range.ENEMY_RANGE_MID:
                return Internal_Flank_State.RIGHT_FLANK
            elif last_enemy.range == Enemy_Range.ENEMY_RANGE_FAR:
                return Internal_Flank_State.RIGHT_FLANK
            else:
                return Internal_Flank_State.RIGHT_FLANK
        else:
            return Internal_Flank_State.LEFT_FLANK

    def run_flank_state(self):
        pass

# ------------------------------------ ATTACK: STATE ---------------------------------- #

ATTACK_TIMEOUT = 4000

class Internal_Attack_State(Enum):
    ATTACK_FORWARD = 0
    ATTACK_LEFT = 1
    ATTACK_RIGHT = 2

class Attack_State:
    def __init__(self) -> None:
        self.common_data: Common_Data_2
        self.state: State_e_2 = State_e_2.STATE_ATTACK
        self.internal_state: Internal_Attack_State = Internal_Attack_State.ATTACK_FORWARD

    def enter_attack_state(self, from_state: State_e_2, event: State_Event_2) -> NULL:
        next_attack_state: Internal_Attack_State = self.get_next_attack_state()
        self.internal_state = next_attack_state

        if from_state == State_e_2.STATE_FLANK:
            if event == State_Event_2.STATE_EVENT_ENEMY:
                self.run_attack_state()
        elif from_state == State_e_2.STATE_ATTACK:
            if event == State_Event_2.STATE_EVENT_ENEMY:
                self.run_attack_state()
            elif event == State_Event_2.STATE_EVENT_TIMEOUT:
                assert 0, f'NOT AN ERROR, RARE CASE, TRY TO IMPLEMENT NEW STRATEGY'
            else:
                assert 0, f'ERROR ENTERING {state_2_str(self.state)} SHOULD NOT HAVE EVENT: {event_2_str(event)}'
        elif from_state == State_e_2.STATE_ATTACK_SEARCH:
            if event == State_Event_2.STATE_EVENT_ENEMY:
                self.run_attack_state()
        else:
            assert 0, f'ERROR ENTERING {self.state} FROM STATE SHOULD NOT BE {state_2_str(from_state)}'
    
    def run_attack_state(self) -> NULL:
        if self.internal_state == Internal_Attack_State.ATTACK_FORWARD:
            drive_set(direction=Drive_Dir.DRIVE_DIR_FORWARD, speed=Drive_Speed.DRIVE_SPEED_MAX, 
                      bot=self.common_data.state_machine.user, all_drive_settings=all_drive_settings_2)
        elif self.internal_state == Internal_Attack_State.ATTACK_LEFT:
            drive_set(direction=Drive_Dir.DRIVE_DIR_ARCTURN_WIDE_LEFT, speed=Drive_Speed.DRIVE_SPEED_MAX,
                      bot=self.common_data.state_machine.user, all_drive_settings=all_drive_settings_2)
        elif self.internal_state == Internal_Attack_State.ATTACK_RIGHT:
            drive_set(direction=Drive_Dir.DRIVE_DIR_ARCTURN_WIDE_RIGHT, speed=Drive_Speed.DRIVE_SPEED_MAX,
                      bot=self.common_data.state_machine.user, all_drive_settings=all_drive_settings_2)
        else: drive_set(direction=Drive_Dir.DRIVE_DIR_FORWARD, speed=Drive_Speed.DRIVE_SPEED_MAX,
                        bot=self.common_data.state_machine.user, all_drive_settings=all_drive_settings_2)

    def get_next_attack_state(self) -> Internal_Attack_State:
        assert self.common_data.enemy.position != Enemy_Pos.ENEMY_POS_NONE, f'ERROR SHOULD HAVE ENEMY POSITION GOT {self.common_data.enemy}'
        last_enemy: Enemy_Struct = self.common_data.enemy
        if enemy_at_front(last_enemy):
            return Internal_Attack_State.ATTACK_FORWARD
        elif enemy_at_left(last_enemy):
            return Internal_Attack_State.ATTACK_LEFT
        elif enemy_at_right(last_enemy):
            return Internal_Attack_State.ATTACK_RIGHT
        else:
            assert 0, 'ERROR: ENEMY NOT IN ANY DIRECTION IS NOT POSSIBLE IN THIS STATE'
        return Internal_Attack_State.ATTACK_FORWARD

# ------------------------------------ SEARCH: STATE ---------------------------------- #

class Internal_Search_State(Enum):
    FORWARD = 0
    ROTATE = 1

SEARCH_ROTATE_TIMEOUT = 600
SEARCH_FORWARD_TIMEOUT = 800

class Search_State:
    def __init__(self) -> None:
        self.common_data: Common_Data_2
        self.state: State_e_2 = State_e_2.STATE_SEARCH
        self.internal_state: Internal_Search_State = Internal_Search_State.ROTATE

    def enter_search_state(self, from_state: State_e_2, event: State_Event_2):
        if from_state == State_e_2.STATE_SEARCH:
            if event == State_Event_2.STATE_EVENT_NONE:
                return 
            elif event == State_Event_2.STATE_EVENT_TIMEOUT:
                if self.internal_state == Internal_Search_State.FORWARD:
                    self.internal_state = Internal_Search_State.ROTATE
                elif self.internal_state == Internal_Search_State.ROTATE:
                    self.internal_state = Internal_Search_State.FORWARD
                self.run_search_state()
        elif from_state == State_e_2.STATE_RETREAT:
            if event == State_Event_2.STATE_EVENT_NONE:
                self.run_search_state()
            elif event == State_Event_2.STATE_EVENT_FINISHED:
                self.run_search_state()
            else:
                assert 0, f'ERROR ENTERING {state_2_str(self.state)} SHOULD NOT HAVE EVENT: {event_2_str(event)}'
        elif from_state == State_e_2.STATE_WAIT:
            if event == State_Event_2.STATE_EVENT_COMMAND:
                self.run_search_state()
            elif event == State_Event_2.STATE_EVENT_ENEMY or \
                event == State_Event_2.STATE_EVENT_FINISHED or \
                event == State_Event_2.STATE_EVENT_LINE or \
                event == State_Event_2.STATE_EVENT_NONE or \
                event == State_Event_2.STATE_EVENT_TIMEOUT:
                assert 0, f'ERROR ENTERING {state_2_str(self.state)} SHOULD NOT HAVE EVENT: {event_2_str(event)}'
        elif from_state == State_e_2.STATE_ATTACK:
            self.run_search_state()
        elif from_state == State_e_2.STATE_FLANK:
            self.run_search_state()
        elif from_state == State_e_2.STATE_ATTACK_SEARCH:
            self.run_search_state()
        elif from_state == State_e_2.STATE_MANUAL:
            assert 0, f'ERROR ENTERING {state_2_str(self.state)}'
    
    def run_search_state(self):
        if self.internal_state == Internal_Search_State.ROTATE:
            last_enemy: Enemy_Struct = input_history_last_directed_enemy(self.common_data.input_history)
            if last_enemy and enemy_at_right(last_enemy):
                drive_set(direction=Drive_Dir.DRIVE_DIR_ROTATE_RIGHT, speed=Drive_Speed.DRIVE_SPEED_MAX, 
                        bot=self.common_data.state_machine.user, all_drive_settings=all_drive_settings_2)
                self.common_data.timer.start_new_timer(SEARCH_FORWARD_TIMEOUT)
            else:
                drive_set(direction=Drive_Dir.DRIVE_DIR_ROTATE_LEFT, speed=Drive_Speed.DRIVE_SPEED_MAX, 
                        bot=self.common_data.state_machine.user, all_drive_settings=all_drive_settings_2)
                self.common_data.timer.start_new_timer(SEARCH_ROTATE_TIMEOUT)
            return 
        elif self.internal_state == Internal_Search_State.FORWARD:
            drive_set(direction=Drive_Dir.DRIVE_DIR_FORWARD, speed=Drive_Speed.DRIVE_SPEED_MAX,
                      bot=self.common_data.state_machine.user, all_drive_settings=all_drive_settings_2)
            self.common_data.timer.start_new_timer(SEARCH_FORWARD_TIMEOUT)
            self.internal_state = Internal_Search_State.ROTATE
            return 
        assert 0, f'ERROR ALL INTERNAL STATES SHOULD BE COVERED INTERNAL: {self.internal_state}'
# ------------------------------------ ATTACK SEARCH: STATE ---------------------------------- #
class Internal_Attack_Search_State(Enum):
    ATTACK_SEARCH_FORWARD = 0
    ATTACK_SEARCH_LEFT = 1
    ATTACK_SEARCH_RIGHT = 2

ATTACK_SEARCH_TIMEOUT = 300

class Attack_Search_State:
    def __init__(self) -> None:
        self.state: State_e_2 = State_e_2.STATE_ATTACK_SEARCH
        self.common_data: Common_Data_2
        self.internal_state: Internal_Attack_Search_State = Internal_Attack_Search_State.ATTACK_SEARCH_FORWARD
        
    def enter_attack_search_state(self, from_state: State_e_2, event: State_Event_2):
        if from_state == State_e_2.STATE_ATTACK:
            if event == State_Event_2.STATE_EVENT_NONE:
                self.run_attack_search_state()
                self.start_attack_search_timer()
            else:
                assert 0, f'ERROR ENTERING {state_2_str(self.state)} SHOULD NOT HAVE EVENT: {event_2_str(event)}'
        elif from_state == State_e_2.STATE_ATTACK_SEARCH:
            if event == State_Event_2.STATE_EVENT_NONE:
                self.run_attack_search_state()
            else:
                assert 0, f'ERROR ENTERING {state_2_str(self.state)} SHOULD NOT HAVE EVENT: {event_2_str(event)}'
        else:
            assert 0, f'ERROR ENTERING {self.state} FROM STATE SHOULD NOT BE {state_2_str(from_state)}'

    def run_attack_search_state(self):
        last_enemy: Enemy_Struct = input_history_last_directed_enemy(self.common_data.input_history)
        if enemy_at_left(last_enemy):
            drive_set(direction=Drive_Dir.DRIVE_DIR_ARCTURN_WIDE_LEFT, speed=Drive_Speed.DRIVE_SPEED_MAX, 
                      bot=self.common_data.state_machine.user, all_drive_settings=all_drive_settings_2)

        elif enemy_at_right(last_enemy):
            drive_set(direction=Drive_Dir.DRIVE_DIR_ARCTURN_WIDE_RIGHT, speed=Drive_Speed.DRIVE_SPEED_MAX,
                      bot=self.common_data.state_machine.user, all_drive_settings=all_drive_settings_2)
            
        else:
            drive_set(direction=Drive_Dir.DRIVE_DIR_ROTATE_LEFT, speed=Drive_Speed.DRIVE_SPEED_MAX,
                      bot=self.common_data.state_machine.user, all_drive_settings=all_drive_settings_2)
            
    def start_attack_search_timer(self):
        self.common_data.timer.start_new_timer(ATTACK_SEARCH_TIMEOUT)

# ------------------------------------ RETREAT ---------------------------------- #
class Internal_Retreat_State(Enum):
    RETREAT_STATE_REVERSE = 0
    RETREAT_STATE_FORWARD = 1
    RETREAT_STATE_ROTATE_LEFT = 2
    RETREAT_STATE_ROTATE_RIGHT = 3
    RETREAT_STATE_ARCTURN_LEFT = 4
    RETREAT_STATE_ARCTURN_RIGHT = 5
    RETREAT_STATE_ALIGN_LEFT = 6
    RETREAT_STATE_ALIGN_RIGHT = 7
 

class Retreat_Tactic:
    def __init__(self, moves: list[Move_Setting], move_count: int) -> None:
        self.moves: list[Move_Setting] = moves
        self.move_count: int = move_count

retreat_tactics: list[Retreat_Tactic] = [
    Retreat_Tactic(moves=[ # reverse state
        Move_Setting(Drive_Dir.DRIVE_DIR_REVERSE, Drive_Speed.DRIVE_SPEED_MAX, 100, false),
    ], move_count=1),
    Retreat_Tactic(moves=[ # forward state
        Move_Setting(Drive_Dir.DRIVE_DIR_FORWARD, Drive_Speed.DRIVE_SPEED_MAX, 150, false)
    ], move_count=1),
    Retreat_Tactic(moves=[ # rotate left 
        Move_Setting(Drive_Dir.DRIVE_DIR_REVERSE, Drive_Speed.DRIVE_SPEED_MAX, 150, false),
        Move_Setting(Drive_Dir.DRIVE_DIR_ROTATE_LEFT, Drive_Speed.DRIVE_SPEED_MAX, 90, false)
    ], move_count=2),
    Retreat_Tactic(moves=[ # rotate right
        Move_Setting(Drive_Dir.DRIVE_DIR_REVERSE, Drive_Speed.DRIVE_SPEED_MAX, 150, false),
        Move_Setting(Drive_Dir.DRIVE_DIR_ROTATE_RIGHT, Drive_Speed.DRIVE_SPEED_MAX, 90, false)
    ], move_count=2),
    Retreat_Tactic(moves=[ # arcturn left 
        Move_Setting(Drive_Dir.DRIVE_DIR_ARCTURN_SHARP_LEFT, Drive_Speed.DRIVE_SPEED_MAX, 100, false)
    ], move_count=1),
    Retreat_Tactic(moves=[ # arcturn right
        Move_Setting(Drive_Dir.DRIVE_DIR_ARCTURN_SHARP_RIGHT, Drive_Speed.DRIVE_SPEED_MAX, 100, false)
    ], move_count=1),
    Retreat_Tactic(moves=[ # align left
        Move_Setting(Drive_Dir.DRIVE_DIR_REVERSE, Drive_Speed.DRIVE_SPEED_MAX, 150, false),
        Move_Setting(Drive_Dir.DRIVE_DIR_ARCTURN_SHARP_LEFT, Drive_Speed.DRIVE_SPEED_MAX, 80, false),
        Move_Setting(Drive_Dir.DRIVE_DIR_ARCTURN_WIDE_RIGHT, Drive_Speed.DRIVE_SPEED_MAX, 80, false),
    ], move_count=3),
    Retreat_Tactic(moves=[ # align right 
        Move_Setting(Drive_Dir.DRIVE_DIR_REVERSE, Drive_Speed.DRIVE_SPEED_MAX, 150, false),
        Move_Setting(Drive_Dir.DRIVE_DIR_ARCTURN_SHARP_RIGHT, Drive_Speed.DRIVE_SPEED_MAX, 80, false),
        Move_Setting(Drive_Dir.DRIVE_DIR_ARCTURN_WIDE_LEFT, Drive_Speed.DRIVE_SPEED_MAX, 80, false),
    ], move_count=3),
]

class Retreat_State:
    def __init__(self) -> None:
        self.common_data: Common_Data_2
        self.state: State_e_2 = State_e_2.STATE_RETREAT
        self.internal_state: Internal_Retreat_State = Internal_Retreat_State.RETREAT_STATE_REVERSE
        self.move_index: int = 0

    def enter_retreat_state(self, from_state: State_e_2, event: State_Event_2):
        if  from_state == State_e_2.STATE_ATTACK_SEARCH or \
            from_state == State_e_2.STATE_ATTACK or \
            from_state == State_e_2.STATE_SEARCH:
            if event == State_Event_2.STATE_EVENT_LINE:
                self.start_retreat_state()
            else:
                assert 0, f'ERROR ENTERING RETREAT STATE: {from_state} CAME FROM EVENT: {event} SHOULD ONLY BE LINE'

        elif from_state == State_e_2.STATE_FLANK:
            if event == State_Event_2.STATE_EVENT_LINE:
                self.start_retreat_state()  # NOTE this is temporary, implment new strategy later 
            else:
                assert 0, f'ERROR ENTERING RETREAT STATE: {from_state} CAME FROM EVENT: {event} SHOULD ONLY BE LINE'

        elif from_state == State_e_2.STATE_RETREAT:
            if event == State_Event_2.STATE_EVENT_LINE:
                self.start_retreat_state()
            elif event == State_Event_2.STATE_EVENT_TIMEOUT:
                self.move_index += 1
                if self.retreat_tactic_done():
                    self.common_data.state_machine.post_internal_event(State_Event_2.STATE_EVENT_FINISHED)
                else:
                    self.retreat_set_drive()
        elif from_state == State_e_2.STATE_WAIT == from_state == State_e_2.STATE_MANUAL:
            assert 0, f'ERROR ENTERING {self.state} FROM STATE SHOULD NOT BE {state_2_str(from_state)}'

    def choose_retreat_move(self):
        line: Line_Pos = self.common_data.line
        last_enemy: Enemy_Struct = self.common_data.enemy
        if line == Line_Pos.LINE_FRONT:
            if enemy_at_left(last_enemy): return Internal_Retreat_State.RETREAT_STATE_ALIGN_LEFT
            elif enemy_at_right(last_enemy): return Internal_Retreat_State.RETREAT_STATE_ALIGN_RIGHT
            elif enemy_at_front(last_enemy): return Internal_Retreat_State.RETREAT_STATE_ALIGN_LEFT  # NOTE temp implement new strat later
            return Internal_Retreat_State.RETREAT_STATE_REVERSE
        elif line == Line_Pos.LINE_FRONT_LEFT:
            if enemy_at_left(last_enemy): return Internal_Retreat_State.RETREAT_STATE_ALIGN_LEFT
            elif enemy_at_right(last_enemy): return Internal_Retreat_State.RETREAT_STATE_ALIGN_RIGHT
            elif enemy_at_front(last_enemy): return Internal_Retreat_State.RETREAT_STATE_ALIGN_LEFT  # NOTE temp implement new strat later
            return Internal_Retreat_State.RETREAT_STATE_ROTATE_RIGHT
        elif line == Line_Pos.LINE_FRONT_RIGHT:
            if enemy_at_left(last_enemy): return Internal_Retreat_State.RETREAT_STATE_ALIGN_LEFT
            elif enemy_at_right(last_enemy): return Internal_Retreat_State.RETREAT_STATE_ALIGN_RIGHT
            elif enemy_at_front(last_enemy): return Internal_Retreat_State.RETREAT_STATE_ALIGN_LEFT  # NOTE temp implement new strat later
            return Internal_Retreat_State.RETREAT_STATE_ROTATE_LEFT
        
        elif line == Line_Pos.LINE_BACK_LEFT:
            if self.current_move(retreat_tactics).direction == Drive_Dir.DRIVE_DIR_REVERSE: 
                return Internal_Retreat_State.RETREAT_STATE_ARCTURN_RIGHT
            elif self.internal_state == Internal_Retreat_State.RETREAT_STATE_ARCTURN_RIGHT:
                return Internal_Retreat_State.RETREAT_STATE_ARCTURN_RIGHT
            return Internal_Retreat_State.RETREAT_STATE_FORWARD
        elif line == Line_Pos.LINE_BACK_RIGHT:
            if self.current_move(retreat_tactics).direction == Drive_Dir.DRIVE_DIR_REVERSE:
                return Internal_Retreat_State.RETREAT_STATE_ARCTURN_LEFT
            elif self.internal_state == Internal_Retreat_State.RETREAT_STATE_ARCTURN_LEFT:
                return Internal_Retreat_State.RETREAT_STATE_ARCTURN_LEFT
            return Internal_Retreat_State.RETREAT_STATE_FORWARD
        
        elif line == Line_Pos.LINE_BACK:
            return Internal_Retreat_State.RETREAT_STATE_FORWARD
        elif line == Line_Pos.LINE_LEFT:
            return Internal_Retreat_State.RETREAT_STATE_ARCTURN_RIGHT
        elif line == Line_Pos.LINE_RIGHT:
            return Internal_Retreat_State.RETREAT_STATE_ARCTURN_LEFT
        elif line == Line_Pos.LINE_DIAGONAL_LEFT:
            assert 0, 'NOT LIKELY LINE CASE FOR RETREAT'
        elif line == Line_Pos.LINE_DIAGONAL_RIGHT:
            assert 0, 'NOT LIKELY LINE CASE FOR RETREAT'
        assert 0, f'ERROR: ALL LINE CASES SHOULD BE COVERED, LINE: {line}'
        return Internal_Retreat_State.RETREAT_STATE_REVERSE

    def start_retreat_state(self):
        self.move_index = 0
        self.internal_state = self.choose_retreat_move()
        self.retreat_set_drive()

    def retreat_set_drive(self):
        assert self.move_index < retreat_tactics[self.internal_state.value].move_count, f'ERROR MOVE INDEX OUT OF RANGE OF MOVES'
        move_setting: Move_Setting = retreat_tactics[self.internal_state.value].moves[self.move_index]
        drive_set(direction=move_setting.direction, speed=move_setting.speed, bot=self.common_data.state_machine.user, all_drive_settings=all_drive_settings_2)
        self.common_data.timer.start_new_timer(move_setting.duration)

    def current_move(self, tactics: list[Move_Setting]) -> Move_Setting:
        return tactics[self.internal_state.value].moves[self.move_index]
    
    def retreat_tactic_done(self) -> bool:
        return self.move_index == retreat_tactics[self.internal_state.value].move_count

# ------------------------------------ WAIT ---------------------------------- #

class Wait_State:
    def __init__(self) -> None:
        self.common_data: Common_Data_2
        self.state: State_e_2 = State_e_2.STATE_WAIT

    def enter_wait_state(self, from_state: State_e_2, event: State_Event_2):
        assert from_state == State_e_2.STATE_WAIT, f'ERROR SHOULD ONLY COME FROM WAIT'

# ------------------------------------ MANUAL ---------------------------------- #

class Manual_State:
    def __init__(self) -> None:
        self.common_data: Common_Data_2
        self.state: State_e_2 = State_e_2.STATE_MANUAL

    def enter_manual_state(self, from_state: State_e_2, event: State_Event_2):
        pass
