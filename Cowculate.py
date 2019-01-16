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


def Cowculate(game_info, old_game_info, renderer):
    '''
    The main control function for BAC, Cowculate() returns the final input.
    It takes a GameState object and returns a controller_state object.
    Cowculate will be the framework of all decision making, and will be the highest level of abstraction.
    '''

    #Initialize a controller state object.
    controller_input = SimpleControllerState()

    plan = make_plan(game_info, old_game_info, renderer)

    if plan == "Kickoff":
        run_kickoff(game_info, old_game_info)

        #controller_input = run_kickoff(game_info, old_game_info)


    if plan == "Move":
        #I will want to wrap this up somewhere else eventually
        #Starting and target states for our car
        current_state = game_info.me

        #target_state = find_destination(game_info)

        time = game_info.time

        #Previous frame information
        if old_game_info != None:
            old_state = old_game_info.me
            old_time = old_game_info.time
        else:
            #This might be wrong
            old_time = -1/120
            old_state = game_info.me


        #This is the actual control function.
        #Currently a slot for testing functions.

        if (not game_info.me.wheel_contact):
            if abs(game_info.me.pos.z - 800) < 20:
                controller_input = AirDodge(Vec3(0, 0, 0)).input()
            else:
                controller_input = AerialRotation(current_state, 0, old_state, time, old_time).zero_omega_recovery() #aerial_rotations(current_state, 0, old_state, time, old_time)
        else:
            controller_input.throttle = 1.0
    return controller_input
 
#Eventually this will have more options, but I want to get basic movement controls down before I worry about that
def make_plan(game_info, old_game_info, renderer):
    '''
    make_plan returns a str to describe the highest-level plan for BAC.
    "Move" - change the position, orientation, and (angular) momentum of the car
    "Kickoff" - checks if we're in a kickoff and hands off control appropriately
    I plan to make something like "Move" be a last-resort goal.
    Goals should be higher level strategy than "Move", but more specific than "Defend", ideally.
    '''

    if is_kickoff(game_info, old_game_info)[0]:
        game_info.first_frame_of_kickoff = is_kickoff(game_info, old_game_info)[1]
        return "Kickoff"

    ball_prediction = make_ball_prediction(game_info.ball)

    draw_debug(renderer, game_info.me, game_info.ball, action_display = None)

    return "Move"


def find_destination(game_info):
    '''
    This will be more complicated in the future, but for now it's just a wrapper
    Outputs a CarState object for the target state.
    If a property (e.g., angular velocity) is "None", it means we don't care about the end result of that property.
    '''

    return less_blindly_chase_ball(game_info)


def draw_debug(renderer, car, ball, action_display = None):
    renderer.begin_rendering()
    # draw the expected path of the ball
    ball_path = make_ball_prediction(ball)
    renderer.draw_polyline_3d(ball_path, renderer.white())
    # print the action that the bot is taking
    #renderer.draw_string_3d(car.physics.location, 2, 2, action_display, renderer.white())
    renderer.end_rendering()

