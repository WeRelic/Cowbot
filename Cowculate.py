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


def Cowculate(game_info, old_game_info, kickoff_position, renderer):
    '''
    The main control function for BAC, Cowculate() returns the final input.
    It takes a GameState object and returns a controller_state object.
    Cowculate will be the framework of all decision making, and will be the highest level of abstraction.
    '''

    #Initialize a controller state object.
    

    plan = make_plan(game_info, old_game_info, kickoff_position, renderer)

    if plan == "Kickoff":

        return run_kickoff(game_info, kickoff_position)
        


    elif plan == "Move":

        #Previous frame information
        if old_game_info != None:
            old_state = old_game_info.me
            old_time = old_game_info.time
        else:
            old_state = game_info.me

        #Find closest big gboost
        min_boost_dist = 20000
        for boost in game_info.big_boosts:
            if (game_info.me.pos - boost.pos).magnitude() < min_boost_dist:
                if boost.is_active:
                    min_boost_dist = (game_info.me.pos - boost.pos).magnitude()
                    closest_boost = boost


       
        return testing(game_info.me, old_state, game_info.ball, game_info.me.copy_state(pos = closest_boost.pos), game_info.fps)
 
#Eventually this will have more options, but I want to get basic movement controls down before I worry about that
def make_plan(game_info, old_game_info, kickoff_position, renderer):
    '''
    make_plan returns a str to describe the highest-level plan for BAC.
    "Move" - change the position, orientation, and (angular) momentum of the car
    "Kickoff" - checks if we're in a kickoff and hands off control appropriately
    I plan to make something like "Move" be a last-resort goal.
    Goals should be higher level strategy than "Move", but more specific than "Defend", ideally.
    '''

    if kickoff_position != "Other":
        return "Kickoff"

    #Ball prediction for use of the bot
    ball_prediction = make_ball_prediction(game_info.ball, game_info.fps, ('x', 0))
    path = ArcLineArc( game_info.me.pos, game_info.ball.pos, game_info.me.vel, Vec3(0,1,0), -400, 300, renderer)

 
    return "Move"


def find_destination(game_info):
    '''
    This will be more complicated in the future, but for now it's just a wrapper
    Outputs a CarState object for the target state.
    If a property (e.g., angular velocity) is "None", it means we don't care about the end result of that property.
    '''

    return less_blindly_chase_ball(game_info)


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
