from GameState import *
from CowBotVector import *
from rlbot.agents.base_agent import SimpleControllerState
from NaiveSteering import *
from Testing import *

def Cowculate(game_info):
    '''
    The main control function for BAC.  
    It takes a GameState object and returns a controller_state object.
    Cowculate will be the framework of all decision making, and will be the highest level of abstraction.
    '''

    #Initialize a controller state object.
    controller_input = SimpleControllerState()

    plan = make_plan(game_info)

    if plan == "Move":
        #Starting and target states for our car
        current_state = game_info.me
        target_state = find_destination(game_info)
        controller_input = naive_turn(current_state, target_state, controller_input)

    return controller_input
 
#Eventually this will have more options, but I want to get basic movement controls down before I worry about that
def make_plan(game_info):
    '''
    make_plan returns a str to describe the highest-level plan for BAC.
    "Move" - change the position, orientation, and (angular) momentum of the car
    I plan to make something like "Move" be a last-resort goal.
    Goals should be higher level strategy than "Move", but more specific than "Defend", ideally.
    '''

    return "Move"


def find_destination(game_info):
    '''
    This will be more complicated in the future, but for now it's just a wrapper
    Outputs a CarState object for the target state.
    If a property (e.g., angular velocity) is "None", it means we don't care about the end result of that property.
    '''

    return less_blindly_chase_ball(game_info)
