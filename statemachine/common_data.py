from scripts.settings import * 
from bot.enemy import * 
from bot.lines import * 
from bot.input_history import * 
from bot.timer import *
# ALL STATES


class State_e(Enum):
	STATE_WAIT = 0
	STATE_SEARCH = 1
	STATE_ATTACK = 2
	STATE_RETREAT = 3
	STATE_MANUAL = 4

# ALL EVENTS THAT CAN HAPPEN
class State_Event(Enum):
	STATE_EVENT_TIMEOUT = 0
	STATE_EVENT_LINE = 1
	STATE_EVENT_ENEMY = 2
	STATE_EVENT_FINISHED = 3
	STATE_EVENT_COMMAND = 4
	STATE_EVENT_NONE = 5

# everything that needs to accessible in individual states

class Common_Data():
    def __init__(self) -> None:
        # forward declarations
        from statemachine.state_machine import State_Machine
        self.state_machine: State_Machine
        self.timer: Timer
        self.enemy: Enemy_Struct = Enemy_Struct(Enemy_Pos.ENEMY_POS_NONE, Enemy_Range.ENEMY_RANGE_NONE)
        self.line: Line_Pos
        self.input_history: Input_History
        self.cmd: Ir_Command

@dataclass
class Scene_Transition():
    from_state: State_e # state where transition comes from 
    event_state: State_Event # event causing transition
    to_state: State_e # state transition going to 

# all possible transitions
state_transitions = [
    Scene_Transition(State_e.STATE_WAIT, State_Event.STATE_EVENT_NONE, State_e.STATE_WAIT),
    Scene_Transition(State_e.STATE_WAIT, State_Event.STATE_EVENT_LINE, State_e.STATE_WAIT),
    Scene_Transition(State_e.STATE_WAIT, State_Event.STATE_EVENT_ENEMY, State_e.STATE_WAIT),
    Scene_Transition(State_e.STATE_WAIT, State_Event.STATE_EVENT_COMMAND, State_e.STATE_SEARCH),
    Scene_Transition(State_e.STATE_SEARCH, State_Event.STATE_EVENT_NONE, State_e.STATE_SEARCH),
    Scene_Transition(State_e.STATE_SEARCH, State_Event.STATE_EVENT_TIMEOUT, State_e.STATE_SEARCH),
    Scene_Transition(State_e.STATE_SEARCH, State_Event.STATE_EVENT_ENEMY, State_e.STATE_ATTACK),
    Scene_Transition(State_e.STATE_SEARCH, State_Event.STATE_EVENT_LINE, State_e.STATE_RETREAT),
    Scene_Transition(State_e.STATE_SEARCH, State_Event.STATE_EVENT_COMMAND, State_e.STATE_MANUAL),
    Scene_Transition(State_e.STATE_ATTACK, State_Event.STATE_EVENT_ENEMY, State_e.STATE_ATTACK),
    Scene_Transition(State_e.STATE_ATTACK, State_Event.STATE_EVENT_LINE, State_e.STATE_RETREAT),
    Scene_Transition(State_e.STATE_ATTACK, State_Event.STATE_EVENT_NONE, State_e.STATE_SEARCH), # Enemy lost
    Scene_Transition(State_e.STATE_ATTACK, State_Event.STATE_EVENT_COMMAND, State_e.STATE_MANUAL),
    Scene_Transition(State_e.STATE_ATTACK, State_Event.STATE_EVENT_TIMEOUT, State_e.STATE_ATTACK),
    Scene_Transition(State_e.STATE_RETREAT, State_Event.STATE_EVENT_LINE, State_e.STATE_RETREAT),
    Scene_Transition(State_e.STATE_RETREAT, State_Event.STATE_EVENT_FINISHED, State_e.STATE_SEARCH),
    Scene_Transition(State_e.STATE_RETREAT, State_Event.STATE_EVENT_TIMEOUT, State_e.STATE_RETREAT),
    Scene_Transition(State_e.STATE_RETREAT, State_Event.STATE_EVENT_ENEMY, State_e.STATE_RETREAT),
    Scene_Transition(State_e.STATE_RETREAT, State_Event.STATE_EVENT_NONE, State_e.STATE_RETREAT),
    Scene_Transition(State_e.STATE_RETREAT, State_Event.STATE_EVENT_COMMAND, State_e.STATE_MANUAL),
    Scene_Transition(State_e.STATE_MANUAL, State_Event.STATE_EVENT_COMMAND, State_e.STATE_MANUAL),
    Scene_Transition(State_e.STATE_MANUAL, State_Event.STATE_EVENT_NONE, State_e.STATE_MANUAL),
    Scene_Transition(State_e.STATE_MANUAL, State_Event.STATE_EVENT_LINE, State_e.STATE_MANUAL),
    Scene_Transition(State_e.STATE_MANUAL, State_Event.STATE_EVENT_ENEMY, State_e.STATE_MANUAL),
]
   
def state_to_str(state: State_e):
    if state == State_e.STATE_ATTACK:
        return 'ATTACK'
    elif state == State_e.STATE_RETREAT:
        return 'RETREAT'
    elif state == State_e.STATE_SEARCH:
        return 'SEARCH'
    elif state == State_e.STATE_WAIT:
        return 'WAIT'
    elif state == State_e.STATE_MANUAL:
        return 'MANUAL'
