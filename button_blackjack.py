import time
from machine import Pin

input_allowed = True
BREAK_TIME = None


PRESS_MAPPING = {("short",) : "hit", ("short", "short") : "double down", ("long",) : "stand", ("short", "short", "short") : "split", ("long", "long") : "surrender"}


button = Pin(28, Pin.IN, Pin.PULL_UP)


def button_rising_interupt():
    global BREAK_TIME

    if input_allowed:
        cur_time = (time.time_ns() - start_time) / 1000000000
        if presses and cur_time - presses[-1][1] < 0.05:
            if actions: 
                actions.pop()
            presses[-1][1] = None
        else:
            presses.append([cur_time, None])
        
        BREAK_TIME = None



def button_falling_interupt():
    global BREAK_TIME

    if input_allowed and presses:
        cur_time = (time.time_ns() - start_time) / 1000000000

        presses[-1][1] = cur_time
        duration = cur_time - presses[-1][0]

        if 0.05 < duration < 0.5:
            actions.append("short")
            BREAK_TIME = cur_time + 1

        elif 0.5 <= duration < 5:
            actions.append("long")
            BREAK_TIME = cur_time + 1


def setup_input():
    global presses, actions, BREAK_TIME, start_time, old_value
    presses = []
    actions=[]
    BREAK_TIME = None
    start_time = time.time_ns()
    old_value = button.value()
    
def check_input(any):
    global presses, actions, BREAK_TIME, start_time, old_value
    if any and BREAK_TIME:
        return True
    if BREAK_TIME and (time.time_ns() - start_time) / 1000000000 > BREAK_TIME:
        result = PRESS_MAPPING.get(tuple(actions))
        if result:
            return result
        else:
            setup_input()
    else:
        new_value = button.value()
        if new_value != old_value:
            old_value = new_value
            if not new_value:
                button_rising_interupt()
            else:
                button_falling_interupt()

if __name__ == "__main__":
    any = False
    setup_input()
    while not (output := check_input(any)):
        print(button.value())
        time.sleep(0.01)
    print(output)
