from scripts.settings import * 
from statemachine.common_data import * 
from bot.drive import * 

class State_Machine:
    def __init__(self) -> None:
        from main import App
        from bot.sumo_bot import SumoBot
        self.user: SumoBot
        self.common_data: Common_Data      # common data between all states
        self.state: State_e                 # current state
    
        # all possible states
        self.wait_state: Wait_State
        self.search_state: Search_State
        self.attack_state: Attack_State
        self.retreat_state: Retreat_State
        self.manual_state: Manual_State

        self.internal_event: State_Event
        self.timer: Timer
        self.input_history: Input_History

def state_machine_init(state_machine: State_Machine, user):
    state_machine.user = user
    state_machine.common_data = Common_Data()
    state_machine.state = State_e.STATE_WAIT
    state_machine.timer = user.timer
    state_machine.input_history = Input_History()
    state_machine.timer.clear()

    state_machine.common_data.state_machine = state_machine
    state_machine.common_data.enemy.position = Enemy_Pos.ENEMY_POS_NONE
    state_machine.common_data.enemy.range = Enemy_Range.ENEMY_RANGE_NONE
    state_machine.common_data.line = Line_Pos.LINE_NONE
    state_machine.common_data.timer = state_machine.timer
    state_machine.common_data.input_history = state_machine.input_history
    state_machine.common_data.cmd = Ir_Command.NONE

    state_machine.internal_event = State_Event.STATE_EVENT_NONE
    state_machine.wait_state = Wait_State()
    state_machine.search_state = Search_State()
    state_machine.attack_state = Attack_State()
    state_machine.retreat_state = Retreat_State()
    state_machine.manual_state = Manual_State()

    state_machine.wait_state.common_data = state_machine.common_data
    state_machine.search_state.common_data = state_machine.common_data
    state_machine.attack_state.common_data = state_machine.common_data
    state_machine.retreat_state.common_data = state_machine.common_data
    state_machine.manual_state.common_data = state_machine.common_data

    state_search_init(state_machine.search_state)
    state_attack_init(state_machine.attack_state)
    state_retreat_init(state_machine.retreat_state)

def process_input(state_machine: State_Machine) -> State_Event:
    state_machine.common_data.enemy = state_machine.user.get_enemy_position()
    state_machine.common_data.line = state_machine.user.get_line_position()
    state_machine.common_data.cmd = state_machine.user.get_ir_command()

    data_input: Input = Input(state_machine.common_data.enemy, state_machine.common_data.line)
    input_history_save(state_machine.input_history, data_input)

    if state_machine.common_data.cmd != Ir_Command.NONE:
        return State_Event.STATE_EVENT_COMMAND
    elif has_internal_event(state_machine):
        return take_internal_event(state_machine)
    elif state_machine.common_data.timer.timer_timeout():
        return State_Event.STATE_EVENT_TIMEOUT
    elif state_machine.common_data.line != Line_Pos.LINE_NONE:
        return State_Event.STATE_EVENT_LINE
    elif enemy_detected(state_machine.common_data.enemy):
        return State_Event.STATE_EVENT_ENEMY
    return State_Event.STATE_EVENT_NONE

def process_event(state_machine: State_Machine, next_event: State_Event ):
    for i in range(len(state_transitions)):
        if state_machine.state == state_transitions[i].from_state and next_event == state_transitions[i].event_state:
            state_enter(state_machine, state_transitions[i].from_state, next_event, state_transitions[i].to_state)
            return
    assert 0, f'ERROR PROCESSING EVENT, ALL CASES SHOULD BE COVERED: {state_machine.state}, Event: {next_event}'

def state_enter(state_machine: State_Machine, from_state: State_e, event: State_Event, to_state: State_e) -> None:
    if from_state != to_state:
        state_machine.timer.clear()
        state_machine.state = to_state

    if to_state == State_e.STATE_WAIT:
        state_wait_enter(state_machine.wait_state, from_state, event)
        return 
    elif to_state == State_e.STATE_SEARCH:
        state_search_enter(state_machine.search_state, from_state, event)
        return 
    elif to_state == State_e.STATE_ATTACK:
        state_attack_enter(state_machine.attack_state, from_state, event)
        return 
    elif to_state == State_e.STATE_RETREAT:
        state_retreat_enter(state_machine.retreat_state, from_state, event)
        return 
    elif to_state == State_e.STATE_MANUAL:
        state_manual_enter(state_machine.manual_state, from_state, event)
        return 
    assert 0, f'STATE ERROR: SHOULD ALWAYS ENTER A STATE, TO_STATE:  {to_state}'


def state_machine_run(state_machine: State_Machine):
    event: State_Event = process_input(state_machine)
    process_event(state_machine, event)

# -------- handle internal state -------- #
# sometimes, will be states with mutiple timeouts, and only state knows when all timeouts are complete 
def state_machine_post_internal_event(state_machine: State_Machine, event: State_Event):
    assert not has_internal_event(state_machine), "should not have internal event"
    state_machine.internal_event = event

def has_internal_event(state_machine: State_Machine) -> bool:
    return state_machine.internal_event != State_Event.STATE_EVENT_NONE

def take_internal_event(state_machine: State_Machine) -> State_Event:
    assert has_internal_event(state_machine), "should have internal event"
    event: State_Event = state_machine.internal_event
    state_machine.internal_event = State_Event.STATE_EVENT_NONE
    return event

  
# --------------------------------- SEARCH ------------------------------ #
class Internal_Search_State(Enum):
    SEARCH_STATE_ROTATE = 0
    SEARCH_STATE_FORWARD = 1

SEARCH_ROTATE_TIMEOUT = 600
SEARCH_FORWARD_TIMEOUT = 800

class Search_State:
    def __init__(self) -> None:
        self.state: State_e = State_e.STATE_SEARCH
        self.common_data: Common_Data
        self.internal_state: Internal_Search_State

def state_search_enter(search_state: Search_State, from_state: State_e, event: State_Event):

    if from_state == State_e.STATE_WAIT:
        # COMING FROM WAIT, ONLY IF COMMAND IS RECEVIED
        ASSERT_EVENT(State_Event.STATE_EVENT_COMMAND, event, from_state)
        state_search_run(search_state)
    elif from_state == State_e.STATE_ATTACK or from_state == State_e.STATE_RETREAT: 
        # COMING FROM ATTACK OR RETREAT 
        if event == State_Event.STATE_EVENT_NONE: # IF FROM ATTACK AND EVENT IS NONE
            assert from_state == State_e.STATE_ATTACK, f'ERROR: in SEARCH_STATE_ENTER, EVENT: {event}, SHOULD ONLY FROM FROM {State_e.STATE_ATTACK}'
            state_search_run(search_state)
        elif event == State_Event.STATE_EVENT_FINISHED: # IF FROM RETREAT AND FINISHED WITH ALL RETREATS
            assert from_state == State_e.STATE_RETREAT, f'ERROR: in SEARCH_STATE_ENTER, EVENT: {event}, SHOULD ONLY FROM FROM {State_e.STATE_RETREAT}'
            if search_state.internal_state == Internal_Search_State.SEARCH_STATE_FORWARD: # PREVENT FROM GOING BACK AND FORTH
                search_state.internal_state = Internal_Search_State.SEARCH_STATE_ROTATE
            state_search_run(search_state)
        elif event == State_Event.STATE_EVENT_COMMAND or \
              event == State_Event.STATE_EVENT_TIMEOUT or \
              event == State_Event.STATE_EVENT_LINE or \
              event == State_Event.STATE_EVENT_ENEMY:
            assert 0, f'ERROR: in SEARCH_STATE_ENTER, event should never be {event}'

    elif from_state == State_e.STATE_SEARCH:
        if event == State_Event.STATE_EVENT_NONE: # IN SEARCH STATE AND NOTHING HAS HAPPENED
            return
        elif event == State_Event.STATE_EVENT_TIMEOUT: # STILL IN SEARCH GO TO NEXT SEARCH MOVE
            if search_state.internal_state == Internal_Search_State.SEARCH_STATE_ROTATE:
                search_state.internal_state = Internal_Search_State.SEARCH_STATE_FORWARD
            elif search_state.internal_state == Internal_Search_State.SEARCH_STATE_FORWARD:
                search_state.internal_state = Internal_Search_State.SEARCH_STATE_ROTATE
            state_search_run(search_state)
        else:
            assert 0, f'ERROR: in SEARCH_STATE_ENTER, EVENT SHOULD NEVER BE |{event}| IF FROM |{State_e.STATE_SEARCH}|'
    elif from_state == State_e.STATE_MANUAL:
        pass

def state_search_run(search_state: Search_State):
    if search_state.internal_state == Internal_Search_State.SEARCH_STATE_ROTATE:
        last_enemy: Enemy_Struct = input_history_last_directed_enemy(search_state.common_data.input_history)
        if last_enemy and enemy_at_right(last_enemy):
            drive_set(Drive_Dir.DRIVE_DIR_ROTATE_RIGHT, Drive_Speed.DRIVE_SPEED_MAX, search_state.common_data.state_machine.user)
        else:
            drive_set(Drive_Dir.DRIVE_DIR_ROTATE_LEFT, Drive_Speed.DRIVE_SPEED_MAX, search_state.common_data.state_machine.user)
        search_state.common_data.timer.start_new_timer(SEARCH_ROTATE_TIMEOUT)

    elif search_state.internal_state == Internal_Search_State.SEARCH_STATE_FORWARD:
        drive_set(Drive_Dir.DRIVE_DIR_FORWARD, Drive_Speed.DRIVE_SPEED_MAX, search_state.common_data.state_machine.user) 
        search_state.common_data.timer.start_new_timer(SEARCH_FORWARD_TIMEOUT)

def state_search_init(search_state: Search_State):
    search_state.internal_state = Internal_Search_State.SEARCH_STATE_ROTATE

# --------------------------------- ATTACK ------------------------------ #

class Internal_Attack_State(Enum): # three internal states
    ATTACK_STATE_FORWARD = 0
    ATTACK_STATE_LEFT = 1
    ATTACK_STATE_RIGHT = 2

ATTACK_STATE_TIMEOUT = 3400
    
class Attack_State:
    def __init__(self) -> None:
        self.state: State_e = State_e.STATE_ATTACK
        self.common_data: Common_Data
        self.internal_state: Internal_Attack_State

def state_attack_enter(attack_state: Attack_State, from_state: State_e, event: State_Event):  

    prev_attack_state = attack_state.internal_state
    attack_state.internal_state = next_attack_state(attack_state.common_data.enemy)

    if from_state == State_e.STATE_SEARCH: # JUST DETECTED ENEMY
        if event == State_Event.STATE_EVENT_ENEMY:
            state_attack_run(attack_state)
        else:
            assert 0, f'ERROR IN ATTACK ENTER FROM SEARCH, EVENT SHOULD NOT BE {event}'
    elif from_state == State_e.STATE_ATTACK: # STILL IN ATTACK STATE
        if event == State_Event.STATE_EVENT_ENEMY: # IF DETECTED ENEMY AGAIN, COULD BE IN DIFFERENCE DIRECTION
            if prev_attack_state != attack_state.internal_state:
                state_attack_run(attack_state)
                # BREAK
        elif event == State_Event.STATE_EVENT_TIMEOUT:
            assert 0, "NOTE: MIGHT HAVE TO IMPLEMENT NEW STRATEGY"
        else:
            assert 0, f'ERROR: IN ATTACK ENTER FROM ATTACK, EVENT SHOULD NOT BE {event}'
    elif from_state == State_e.STATE_RETREAT:
        assert 0, f'ERROR: IN ATTACK FROM RETREAT, SHOULD GO THROUGH SEARCH BEFORE THIS'
    else:
        assert 0, f'ERROR: IN ATTACK FROM |{from_state}|'

def next_attack_state(enemy: Enemy_Struct) -> Internal_Attack_State:
    if enemy_at_front(enemy):
        return Internal_Attack_State.ATTACK_STATE_FORWARD
    elif enemy_at_left(enemy):
        return Internal_Attack_State.ATTACK_STATE_LEFT
    elif enemy_at_right(enemy):
        return Internal_Attack_State.ATTACK_STATE_RIGHT
    else:
        assert 0, f'ERROR: ENEMY SHOULD BE ONE OF THREE DIRECTIONS'
    return Internal_Attack_State.ATTACK_STATE_FORWARD

def state_attack_run(attack_state: Attack_State):
    if attack_state.internal_state == Internal_Attack_State.ATTACK_STATE_FORWARD:
        drive_set(Drive_Dir.DRIVE_DIR_FORWARD, Drive_Speed.DRIVE_SPEED_MAX, attack_state.common_data.state_machine.user)
    elif attack_state.internal_state == Internal_Attack_State.ATTACK_STATE_LEFT:
        drive_set(Drive_Dir.DRIVE_DIR_ARCTURN_WIDE_LEFT, Drive_Speed.DRIVE_SPEED_MAX, attack_state.common_data.state_machine.user)
    elif attack_state.internal_state == Internal_Attack_State.ATTACK_STATE_RIGHT:
        drive_set(Drive_Dir.DRIVE_DIR_ARCTURN_WIDE_RIGHT, Drive_Speed.DRIVE_SPEED_MAX, attack_state.common_data.state_machine.user)
    attack_state.common_data.timer.start_new_timer(ATTACK_STATE_TIMEOUT)


def state_attack_init(attack_state: Attack_State):
    attack_state.internal_state = Internal_Attack_State.ATTACK_STATE_FORWARD

# --------------------------------- RETREAT ------------------------------ #

class Internal_Retreat_State(Enum):
    RETREAT_STATE_REVERSE = 0
    RETREAT_STATE_FORWARD = 1
    RETREAT_STATE_ROTATE_LEFT = 2
    RETREAT_STATE_ROTATE_RIGHT = 3
    RETREAT_STATE_ARCTURN_LEFT = 4
    RETREAT_STATE_ARCTURN_RIGHT = 5
    RETREAT_STATE_ALIGN_LEFT = 6
    RETREAT_STATE_ALIGN_RIGHT = 7

@dataclass
class Move:
    direction: Drive_Dir
    speed: Drive_Speed
    duration: float

class Retreat_Move:
    def __init__(self, moves, move_count) -> None:
        self.moves: list[Move] = moves
        self.move_count: int = move_count
        
retreat_states: list[Retreat_Move] = [
    Retreat_Move(  # RETREAT_STATE_REVERSE
        moves=[Move(direction=Drive_Dir.DRIVE_DIR_REVERSE, speed=Drive_Speed.DRIVE_SPEED_MAX, duration=150)], 
        move_count=1
    ),
    Retreat_Move(  # RETREAT_STATE_FORWARD
        moves=[Move(direction=Drive_Dir.DRIVE_DIR_FORWARD, speed=Drive_Speed.DRIVE_SPEED_MAX, duration=150)], 
        move_count=1
    ),
    Retreat_Move(  # RETREAT_STATE_ROTATE_LEFT
        moves=[Move(direction=Drive_Dir.DRIVE_DIR_ROTATE_LEFT, speed=Drive_Speed.DRIVE_SPEED_FAST, duration=120)],
        move_count=1
    ),
    Retreat_Move(  # RETREAT_STATE_ROTATE_RIGHT
        moves=[Move(direction=Drive_Dir.DRIVE_DIR_ROTATE_RIGHT, speed=Drive_Speed.DRIVE_SPEED_MAX, duration=120)],
        move_count=1
    ),
    Retreat_Move(  # RETREAT_STATE_ARCTURN_LEFT
        moves=[Move(direction=Drive_Dir.DRIVE_DIR_ARCTURN_SHARP_LEFT, speed=Drive_Speed.DRIVE_SPEED_MAX, duration=120)],
        move_count=1
    ),
    Retreat_Move(  # RETREAT_STATE_ARCTURN_RIGHT
        moves=[Move(direction=Drive_Dir.DRIVE_DIR_ARCTURN_SHARP_RIGHT, speed=Drive_Speed.DRIVE_SPEED_MAX, duration=120)],
        move_count=1
    ),
    Retreat_Move(  # RETREAT_STATE_ALIGN_LEFT
        moves=[
            Move(direction=Drive_Dir.DRIVE_DIR_REVERSE, speed=Drive_Speed.DRIVE_SPEED_MAX, duration=150),
            Move(direction=Drive_Dir.DRIVE_DIR_ARCTURN_SHARP_LEFT, speed=Drive_Speed.DRIVE_SPEED_MAX, duration=80),
            Move(direction=Drive_Dir.DRIVE_DIR_ARCTURN_MID_RIGHT, speed=Drive_Speed.DRIVE_SPEED_MAX, duration=80),
        ],
        move_count=3
    ),
    Retreat_Move(  # RETREAT_STATE_ALIGN_RIGHT
        moves=[
            Move(direction=Drive_Dir.DRIVE_DIR_REVERSE, speed=Drive_Speed.DRIVE_SPEED_MAX, duration=150),
            Move(direction=Drive_Dir.DRIVE_DIR_ARCTURN_SHARP_RIGHT, speed=Drive_Speed.DRIVE_SPEED_MAX, duration=80),
            Move(direction=Drive_Dir.DRIVE_DIR_ARCTURN_MID_LEFT, speed=Drive_Speed.DRIVE_SPEED_MAX, duration=80),
        ],
        move_count=3
    ),
]

class Retreat_State:
    def __init__(self) -> None:
        self.state: State_e = State_e.STATE_RETREAT
        self.common_data: Common_Data
        self.internal_state: Internal_Retreat_State
        self.move_idx: int = 0
        
def state_retreat_enter(retreat_state: Retreat_State, from_state: State_e, event: State_Event):
        if from_state == State_e.STATE_SEARCH or from_state == State_e.STATE_ATTACK:
            if event == State_Event.STATE_EVENT_LINE:
                state_retreat_run(retreat_state)
            else:
                assert 0, f'ERROR IN ENTER_RETREAT_STATE, EVENT |{event}| SHOULD NOT CAUSE REREAT'
        elif from_state == State_e.STATE_RETREAT: # CURRENTLY DRIVING AWAY FROM LINE
            if event == State_Event.STATE_EVENT_LINE: # DETECTED LINE AGAIN, RESTART
                state_retreat_run(retreat_state)
            elif event == State_Event.STATE_EVENT_TIMEOUT: # DONE WITH CURRENT MOVE, INCREMENT MOVE INDEX
                retreat_state.move_idx += 1
                if retreat_state_done(retreat_state):
                    # POST EVENT FINISHED SINCE REREAT STATE IS ONLY PLACE KNOWS WHETHER DONE WITH THIS STATE
                    # STATE MACHINE WILL PICK UP THIS EVENT AND TRANSITION TO NEW STATE
                    state_machine_post_internal_event(retreat_state.common_data.state_machine, State_Event.STATE_EVENT_FINISHED)
                else:
                    start_retreat_move(retreat_state)
            elif event == State_Event.STATE_EVENT_NONE or event == State_Event.STATE_EVENT_ENEMY: #IGNORE ENEMY WHEN RETREATING
                pass
            else:
                assert 0, f'ERROR IN ENTER_RETREAT_STATE, EVENT |{event}| SHOULD NOT CAUSE RETREAT'

        else:
            assert 0, f'ERROR IN ENTER_RETREAT_STATE, SHOULD NOT COME FROM |{from_state}|'

def state_retreat_run(retreat_state: Retreat_State):
    retreat_state.move_idx = 0
    retreat_state.internal_state = next_retreat_state(retreat_state) # DECIDE WHICH NEXT RETREAT STATE TO USE BASED ON LINE DETECTION
    start_retreat_move(retreat_state)

def start_retreat_move(retreat_state: Retreat_State):
    assert retreat_state.move_idx < retreat_states[retreat_state.internal_state.value].move_count, f'ERROR IN START_RETREAT_MOVE, INDEX TOO LARGE FOR RETERAT MOVES {retreat_states[retreat_state.internal_state.value]}'
    move: Move = retreat_states[retreat_state.internal_state.value].moves[retreat_state.move_idx]
    retreat_state.common_data.timer.start_new_timer(move.duration)
    drive_set(move.direction, move.speed, retreat_state.common_data.state_machine.user)

def retreat_state_done(retreat_state: Retreat_State) -> bool:
    return retreat_state.move_idx == retreat_states[retreat_state.internal_state.value].move_count

def current_move(retreat_state: Retreat_State) -> Move:
    return retreat_states[retreat_state.internal_state.value].moves[retreat_state.move_idx]

def next_retreat_state(retreat_state: Retreat_State) -> Internal_Retreat_State:
    line: Line_Pos = retreat_state.common_data.line

    if line == Line_Pos.LINE_FRONT_LEFT:
        if enemy_at_right(retreat_state.common_data.enemy) or enemy_at_front(retreat_state.common_data.enemy):
            return Internal_Retreat_State.RETREAT_STATE_ALIGN_RIGHT
        elif enemy_at_left(retreat_state.common_data.enemy):
            return Internal_Retreat_State.RETREAT_STATE_ALIGN_LEFT
        else:
            return Internal_Retreat_State.RETREAT_STATE_REVERSE
        
    elif line == Line_Pos.LINE_FRONT_RIGHT:
        if enemy_at_left(retreat_state.common_data.enemy) or enemy_at_front(retreat_state.common_data.enemy):
            return Internal_Retreat_State.RETREAT_STATE_ALIGN_LEFT
        elif enemy_at_right(retreat_state.common_data.enemy):
            return Internal_Retreat_State.RETREAT_STATE_ALIGN_RIGHT
        else:
            return Internal_Retreat_State.RETREAT_STATE_REVERSE
        
    elif line == Line_Pos.LINE_BACK_LEFT:
        if current_move(retreat_state).direction == Drive_Dir.DRIVE_DIR_REVERSE:
            return Internal_Retreat_State.RETREAT_STATE_ARCTURN_RIGHT
        elif retreat_state.internal_state == Internal_Retreat_State.RETREAT_STATE_ARCTURN_RIGHT:
            return Internal_Retreat_State.RETREAT_STATE_ARCTURN_RIGHT
        return Internal_Retreat_State.RETREAT_STATE_FORWARD
    
    elif line == Line_Pos.LINE_BACK_RIGHT:
        if current_move(retreat_state).direction == Drive_Dir.DRIVE_DIR_REVERSE:
            return Internal_Retreat_State.RETREAT_STATE_ARCTURN_LEFT
        elif retreat_state.internal_state == Internal_Retreat_State.RETREAT_STATE_ARCTURN_LEFT:
            return Internal_Retreat_State.RETREAT_STATE_ARCTURN_LEFT
        return Internal_Retreat_State.RETREAT_STATE_FORWARD
    
    elif line == Line_Pos.LINE_FRONT:
        if enemy_at_front(retreat_state.common_data.enemy):
            return Internal_Retreat_State.RETREAT_STATE_ARCTURN_LEFT
        elif enemy_at_right(retreat_state.common_data.enemy):
            return Internal_Retreat_State.RETREAT_STATE_ALIGN_RIGHT
        else:
            return Internal_Retreat_State.RETREAT_STATE_REVERSE

    elif line == Line_Pos.LINE_BACK:
        return Internal_Retreat_State.RETREAT_STATE_FORWARD
    
    elif line == Line_Pos.LINE_LEFT:
        return Internal_Retreat_State.RETREAT_STATE_ARCTURN_RIGHT
    
    elif line == Line_Pos.LINE_RIGHT:
        return Internal_Retreat_State.RETREAT_STATE_ARCTURN_LEFT
    
    elif line == Line_Pos.LINE_DIAGONAL_LEFT:
        assert 0, f'ERROR IN NEXT_RETREAT_STATE, LINE: |{line}| NOT LIKELY'
    elif line == Line_Pos.LINE_DIAGONAL_RIGHT:
        assert 0, f'ERROR IN NEXT_RETREAT_STATE, LINE: |{line}| NOT LIKELY'
    elif line == Line_Pos.LINE_NONE:
        assert 0, f'ERROR IN NEXT_RETREAT_STATE, LINE SHOULD NOT BE NONE'

    return Internal_Retreat_State.RETREAT_STATE_REVERSE

def state_retreat_init(retreat_state: Retreat_State):
    retreat_state.internal_state = Internal_Retreat_State.RETREAT_STATE_REVERSE
    retreat_state.move_idx = 0

# --------------------------------- WAIT ------------------------------ #
class Wait_State:
    def __init__(self) -> None:
        self.state: State_e = State_e.STATE_WAIT
        self.common_data: Common_Data

def state_wait_enter(wait_state: Wait_State, from_state: State_e, event: State_Event):
    assert from_state == State_e.STATE_WAIT, "SHOULD ONLY ONE FROM WAIT STATE"

# --------------------------------- MANUAL ------------------------------ #
class Manual_State():
    def __init__(self) -> None:
        self.common_data: Common_Data
def state_manual_enter(manual_state: Manual_State, from_state: State_e, event: State_Event):
    if event != State_Event.STATE_EVENT_COMMAND:
        assert 0, f'ERROR IN MANUAL ENTER, CAN ONLY ENTER IF COMMAND, GOT {event}'

# --------------------------------------------ASSERT FUNCTION------------------------------------------#

def internal_state_to_str(state: State_e, internal_state):
        if state == State_e.STATE_ATTACK:
            if internal_state == Internal_Attack_State.ATTACK_STATE_FORWARD:
                return 'AF'
            elif internal_state == Internal_Attack_State.ATTACK_STATE_LEFT:
                return 'AL'
            elif internal_state == Internal_Attack_State.ATTACK_STATE_RIGHT:
                return 'AR'
        elif state == State_e.STATE_RETREAT:
            if internal_state == Internal_Retreat_State.RETREAT_STATE_ALIGN_LEFT:
                return 'ALIGN LT'
            elif internal_state == Internal_Retreat_State.RETREAT_STATE_ALIGN_RIGHT:
                return 'ALIGN RT'
            elif internal_state == Internal_Retreat_State.RETREAT_STATE_ARCTURN_LEFT:
                return 'ARCTURN LT'
            elif internal_state == Internal_Retreat_State.RETREAT_STATE_ARCTURN_RIGHT:
                return 'ARCTURN RT'
            elif internal_state == Internal_Retreat_State.RETREAT_STATE_FORWARD:
                return 'FORWARD'
            elif internal_state == Internal_Retreat_State.RETREAT_STATE_REVERSE:
                return 'REVERSE'
            elif internal_state == Internal_Retreat_State.RETREAT_STATE_ROTATE_LEFT:
                return 'ROTATE LT'
            elif internal_state == Internal_Retreat_State.RETREAT_STATE_ROTATE_RIGHT:
                return 'ROTATE RT'
        elif state == State_e.STATE_SEARCH:
            if internal_state == Internal_Search_State.SEARCH_STATE_FORWARD:
                return 'FORWARD'
            elif internal_state == Internal_Search_State.SEARCH_STATE_ROTATE:
                return 'ROTATE'
        assert 0, 'ERROR SHOULD HAVE INTERNAL STATE'

def ASSERT_EVENT(expected_event: State_Event, event: State_Event, from_state: State_e):
    assert expected_event == event, f'ERROR: CAME FROM {from_state}, EXPECTED EVENT {expected_event}, GOT: {event}'
