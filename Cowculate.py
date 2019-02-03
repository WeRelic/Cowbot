from GameState import *
from CowBotVector import *
from rlbot.agents.base_agent import SimpleControllerState
from NaiveSteering import *
from Testing import *
#AerialRotations.py is now deprecated, replaced by the AerialRotation class in Mechanics.py
#from AerialRotations import *
from BallPrediction import *
from Kickoff import *
from Mechanics import *
from math import sin, cos
from Maneuvers import *
from Pathing import *
from GamePlan import *


def Cowculate(game_info, old_game_info, plan, renderer):
    '''
    The main control function for BAC, Cowculate() returns the final input.
    It takes a GameState object and returns a controller_state object.
    Cowculate will be the framework of all decision making, and will be the highest level of abstraction.
    '''

    #Previous frame information
    if old_game_info != None:
        old_state = old_game_info.me
        old_time = old_game_info.time
    else:
        old_state = game_info.me

    #Find closest big boost
    min_boost_dist = 20000
    for boost in game_info.big_boosts:
        if (game_info.me.pos - boost.pos).magnitude() < min_boost_dist:
            if boost.is_active:
                min_boost_dist = (game_info.me.pos - boost.pos).magnitude()
                closest_boost = boost

    return testing(game_info.me, old_state, game_info.ball,
                   game_info.me.copy_state(pos = closest_boost.pos), game_info.fps)



def testing(current_state, old_state, ball, goal_state, fps):
    '''
    This will be for whenever I'm testing out a new feature or behavior.
    This should not be called at runtime for a finished bot.
    '''
    controller_input = SimpleControllerState()

    
    controller_input = GroundTurn(current_state, goal_state).input()
    if current_state.boost == 100:
        controller_input.boost = 1

    return controller_input
