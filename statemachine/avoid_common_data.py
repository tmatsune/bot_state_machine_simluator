from scripts.settings import * 
from bot.drive import *
from bot.enemy import *
from bot.input_history import *
from bot.lines import *
from bot.timer import *

class State_e_a(Enum):
    STATE_WAIT = 0
    STATE_SEARCH = 1
    STATE_RETREAT = 2
    STATE_EVADE = 3
    STATE_MANUAL = 4    

class State_Event_a(Enum):
	STATE_EVENT_TIMEOUT = 0
	STATE_EVENT_LINE = 1
	STATE_EVENT_ENEMY = 2
	STATE_EVENT_FINISHED = 3
	STATE_EVENT_COMMAND = 4
	STATE_EVENT_NONE = 5

class Avoid_Common_Data:
    def __init__(self):
        from statemachine.avoid_state_machine import Avoid_State_Machine
        self.state_machine: Avoid_State_Machine

