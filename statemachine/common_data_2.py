from scripts.settings import * 
from bot.timer import * 
from bot.enemy import * 
from bot.lines import * 
from bot.input_history import *

class State_e_2(Enum):
    STATE_FLANK = 0
    STATE_ATTACK = 1
    STATE_SEARCH = 2
    STATE_RETREAT = 3
    STATE_WAIT = 4
    STATE_MANUAL = 5
    STATE_ATTACK_SEARCH = 6

class State_Event_2(Enum):
    STATE_EVENT_TIMEOUT = 0
    STATE_EVENT_LINE = 1
    STATE_EVENT_ENEMY = 2
    STATE_EVENT_FINISHED = 3
    STATE_EVENT_COMMAND = 4
    STATE_EVENT_NONE = 5
    STATE_EVENT_SUBCASE_FLAG = 6

class Common_Data_2:
    def __init__(self) -> None:
        from statemachine.state_machine_2 import State_Machine_2
        self.state_machine: State_Machine_2
        self.timer: Timer
        self.input_history: Input_History
        self.enemy: Enemy_Struct
        self.line: Line_Pos
        self.ir_command: Ir_Command
    
    def common_data_init(self, state_machine, timer: Timer, input_history: Input_History):
        self.state_machine = state_machine
        self.timer = timer
        self.input_history = input_history
        self.enemy = Enemy_Struct(position=Enemy_Pos.ENEMY_POS_NONE, range=Enemy_Range.ENEMY_RANGE_NONE)
        self.line = Line_Pos.LINE_NONE
        self.ir_command = Ir_Command.NONE

@dataclass
class Scene_Transition_2():
    from_state: State_e_2  # state where transition comes from
    event: State_Event_2   # event causing transition
    to_state: State_e_2    # state transition going to

scene_transitions_2: list[Scene_Transition_2] = [
    Scene_Transition_2(State_e_2.STATE_WAIT, State_Event_2.STATE_EVENT_NONE, State_e_2.STATE_WAIT),
    Scene_Transition_2(State_e_2.STATE_WAIT, State_Event_2.STATE_EVENT_COMMAND, State_e_2.STATE_SEARCH),
    Scene_Transition_2(State_e_2.STATE_WAIT, State_Event_2.STATE_EVENT_ENEMY, State_e_2.STATE_WAIT),
    Scene_Transition_2(State_e_2.STATE_WAIT, State_Event_2.STATE_EVENT_LINE, State_e_2.STATE_WAIT),

    Scene_Transition_2(State_e_2.STATE_SEARCH, State_Event_2.STATE_EVENT_NONE, State_e_2.STATE_SEARCH),
    Scene_Transition_2(State_e_2.STATE_SEARCH, State_Event_2.STATE_EVENT_TIMEOUT, State_e_2.STATE_SEARCH),
    Scene_Transition_2(State_e_2.STATE_SEARCH, State_Event_2.STATE_EVENT_ENEMY, State_e_2.STATE_FLANK),
    Scene_Transition_2(State_e_2.STATE_SEARCH, State_Event_2.STATE_EVENT_LINE, State_e_2.STATE_RETREAT),
    Scene_Transition_2(State_e_2.STATE_SEARCH, State_Event_2.STATE_EVENT_COMMAND, State_e_2.STATE_MANUAL),

    Scene_Transition_2(State_e_2.STATE_FLANK, State_Event_2.STATE_EVENT_NONE, State_e_2.STATE_FLANK),
    Scene_Transition_2(State_e_2.STATE_FLANK, State_Event_2.STATE_EVENT_TIMEOUT, State_e_2.STATE_FLANK),
    Scene_Transition_2(State_e_2.STATE_FLANK, State_Event_2.STATE_EVENT_ENEMY, State_e_2.STATE_FLANK),
    Scene_Transition_2(State_e_2.STATE_FLANK, State_Event_2.STATE_EVENT_LINE, State_e_2.STATE_RETREAT),
    Scene_Transition_2(State_e_2.STATE_FLANK, State_Event_2.STATE_EVENT_COMMAND, State_e_2.STATE_MANUAL),
    Scene_Transition_2(State_e_2.STATE_FLANK, State_Event_2.STATE_EVENT_FINISHED, State_e_2.STATE_SEARCH),

    Scene_Transition_2(State_e_2.STATE_RETREAT, State_Event_2.STATE_EVENT_NONE, State_e_2.STATE_RETREAT),
    Scene_Transition_2(State_e_2.STATE_RETREAT, State_Event_2.STATE_EVENT_LINE, State_e_2.STATE_RETREAT),
    Scene_Transition_2(State_e_2.STATE_RETREAT, State_Event_2.STATE_EVENT_FINISHED, State_e_2.STATE_SEARCH),
    Scene_Transition_2(State_e_2.STATE_RETREAT, State_Event_2.STATE_EVENT_TIMEOUT, State_e_2.STATE_RETREAT),
    Scene_Transition_2(State_e_2.STATE_RETREAT, State_Event_2.STATE_EVENT_ENEMY, State_e_2.STATE_RETREAT),
    Scene_Transition_2(State_e_2.STATE_RETREAT, State_Event_2.STATE_EVENT_COMMAND, State_e_2.STATE_MANUAL),

    #Scene_Transition_2(State_e_2.STATE_ATTACK, State_Event_2.STATE_EVENT_NONE, State_e_2.STATE_SEARCH),
    Scene_Transition_2(State_e_2.STATE_ATTACK, State_Event_2.STATE_EVENT_LINE, State_e_2.STATE_RETREAT),
    Scene_Transition_2(State_e_2.STATE_ATTACK, State_Event_2.STATE_EVENT_COMMAND, State_e_2.STATE_MANUAL),
    Scene_Transition_2(State_e_2.STATE_ATTACK, State_Event_2.STATE_EVENT_ENEMY, State_e_2.STATE_ATTACK),
    Scene_Transition_2(State_e_2.STATE_ATTACK, State_Event_2.STATE_EVENT_TIMEOUT, State_e_2.STATE_ATTACK),
    Scene_Transition_2(State_e_2.STATE_ATTACK, State_Event_2.STATE_EVENT_NONE, State_e_2.STATE_ATTACK_SEARCH),

    Scene_Transition_2(State_e_2.STATE_ATTACK_SEARCH, State_Event_2.STATE_EVENT_TIMEOUT, State_e_2.STATE_FLANK),
    Scene_Transition_2(State_e_2.STATE_ATTACK_SEARCH, State_Event_2.STATE_EVENT_LINE, State_e_2.STATE_RETREAT),
    Scene_Transition_2(State_e_2.STATE_ATTACK_SEARCH, State_Event_2.STATE_EVENT_ENEMY, State_e_2.STATE_ATTACK),
    Scene_Transition_2(State_e_2.STATE_ATTACK_SEARCH, State_Event_2.STATE_EVENT_NONE, State_e_2.STATE_ATTACK_SEARCH)
]

'''
    cases to fix: 
    - back right & left retreat
    - one case where gets stuck in between retreat and search back left & right sensors
    - flank, gets stuck when trying to flank right or left
'''

@dataclass
class Sub_Case:
    from_state: State_e_2  # state where transition comes from
    event: State_Event_2   # event causing transition
    to_state: State_e_2    # state transition going to
    lower_flag: bool

sub_cases: list[Sub_Case] = [
    Sub_Case(State_e_2.STATE_FLANK, State_Event_2.STATE_EVENT_ENEMY, State_e_2.STATE_ATTACK, true),
    Sub_Case(State_e_2.STATE_FLANK, State_Event_2.STATE_EVENT_NONE, State_e_2.STATE_FLANK, false),
    Sub_Case(State_e_2.STATE_FLANK, State_Event_2.STATE_EVENT_TIMEOUT, State_e_2.STATE_SEARCH, true),
    Sub_Case(State_e_2.STATE_FLANK, State_Event_2.STATE_EVENT_LINE, State_e_2.STATE_RETREAT, true),
]

def state_2_str(state: State_e_2) -> str:
    if state == State_e_2.STATE_FLANK:
        return 'FLANK'
    elif state == State_e_2.STATE_ATTACK:
        return 'ATTACK'
    elif state == State_e_2.STATE_SEARCH:
        return 'SEARCH'
    elif state == State_e_2.STATE_RETREAT:
        return 'RETREAT'
    elif state == State_e_2.STATE_WAIT:
        return 'WAIT'
    elif state == State_e_2.STATE_MANUAL:
        return 'MANUAL'
    elif state == State_e_2.STATE_ATTACK_SEARCH:
        return 'ATTACK_SEARCH' 
    else:
        return 'ERROR'

def event_2_str(event: State_Event_2) -> str:
    if event == State_Event_2.STATE_EVENT_TIMEOUT:
        return 'TIMEOUT'
    elif event == State_Event_2.STATE_EVENT_LINE:
        return 'LINE'
    elif event == State_Event_2.STATE_EVENT_ENEMY:
        return 'ENEMY'
    elif event == State_Event_2.STATE_EVENT_FINISHED:
        return 'FINISHED'
    elif event == State_Event_2.STATE_EVENT_COMMAND:
        return 'COMMAND'
    elif event == State_Event_2.STATE_EVENT_NONE:
        return 'NONE'
    elif event == State_Event_2.STATE_EVENT_SUBCASE_FLAG:
        return 'FLAG'
    else:
        return 'ERROR'

