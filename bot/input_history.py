from scripts.settings import * 
from bot.lines import * 
from bot.enemy import * 

@dataclass
class Input:
    enemy: Enemy_Struct
    line: Line_Pos

class Node():
    def __init__(self, val) -> None:
        self.val: Input = val
        self.next = None

class Input_History():
    def __init__(self) -> None:
        self.root = None
        self.top = None
        self.max_size: int
        self.curr_size: int
        self.history_init(6)

    def history_init(self, max_size: int):
        self.max_size = max_size
        self.curr_size = 0

    def put(self, val):
        if self.curr_size == self.max_size: 
            self.pop()
        new_node = Node(val)
        if not self.root:
            self.root = new_node
            self.top = new_node
            self.curr_size = 1
            return 
        self.top.next = new_node
        self.top = new_node
        self.curr_size += 1
       
    def pop(self):
        if not self.root: return None
        self.curr_size -= 1
        res = self.root.val
        if self.root.next:
            next_root = self.root.next
            self.root = next_root
        else:
            self.root = None
        return res
    
    def input_history_empty(self):
        return self.curr_size == 0

    def peek_root(self):
        return self.root.val if self.curr_size > 0 else None
    def peek_top(self):
        return self.top.val if self.curr_size > 0 else None
    
    def print_all(self):
        curr: Node = self.root
        while(curr):
            print(curr.val, end = " ")
            curr = curr.next
        print('---------')
    
    def get_str_vals(self) -> list[str]:
        vals: list[str] = []
        curr: Node = self.root
        if not curr: vals = ['NONE']
        else:
            while curr:
                vals.append(f'pos: {enemy_pos_to_str(curr.val.enemy.position)} | range: {enemy_range_to_str(curr.val.enemy.range)}')
                curr = curr.next
        return vals
        
def input_equal(a: Input, b: Input) -> bool:
    return a.line == b.line \
          and a.enemy.range == b.enemy.range \
          and a.enemy.position == b.enemy.position

def input_history_save(history: Input_History, input_data: Input) -> None:
    if input_data.enemy.position == Enemy_Pos.ENEMY_POS_NONE and input_data.line == Line_Pos.LINE_NONE:
        return 
    if not history.input_history_empty():
        last_input = history.peek_top()
        if input_equal(input_data, last_input):
            return 
    history.put(input_data)

def input_history_last_directed_enemy(history: Input_History) -> Enemy_Struct:
    curr = history.root
    enemy_val: Enemy_Struct = Enemy_Struct(Enemy_Pos.ENEMY_POS_NONE, Enemy_Range.ENEMY_RANGE_NONE)
    while curr:
        input_data: Input = curr.val
        if input_data and (enemy_at_left(input_data.enemy) or enemy_at_right(input_data.enemy)):
            enemy_val = input_data.enemy
        curr = curr.next
    return enemy_val if enemy_val else None
   