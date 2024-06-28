from scripts.settings import * 
from statemachine.avoid_common_data import * 

class Avoid_State_Machine:
    def __init__(self) -> None:
        from bot.sumo_bot import SumoBot
        self.common_data: Avoid_Common_Data
        self.user: SumoBot
        self.state: State_e_a

        self.search_state: Search_State_a
        self.retreat_state: Retreat_State_a
        self.attack_state: Attack_State_a
        self.wait_state: Wait_State_a
        self.manual_state: Manual_State_a

        self.timer: Timer
        self.input_history: Input_History
        self.internal_event: State_Event_a

# ------------------------------------- SEARCH ----------------------------------- #
class Search_State_a:
    def __init__(self) -> None:
        self.common_data: Avoid_Common_Data

# ------------------------------------- RETREAT ----------------------------------- #
class Retreat_State_a:
    def __init__(self) -> None:
        self.common_data: Avoid_Common_Data

# ------------------------------------- ATTACK ----------------------------------- #
class Attack_State_a:
    def __init__(self) -> None:
        self.common_data: Avoid_Common_Data

# ------------------------------------- WAIT ----------------------------------- #
class Wait_State_a:
    def __init__(self) -> None:
        self.common_data: Avoid_Common_Data

# ------------------------------------- MANUAL ----------------------------------- #
class Manual_State_a:
    def __init__(self) -> None:
        self.common_data: Avoid_Common_Data

