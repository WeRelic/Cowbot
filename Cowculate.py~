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
import EvilGlobals



def Cowculate(game_info, old_game_info, plan):
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
        #Just assign the current frame on load - there is no previous frame.
        old_state = game_info.me


    current_state = game_info.me

    return execute(plan, game_info, current_state, old_state)





def execute(plan, game_info, current_state, old_state):


    controller_input = AerialRotation(current_state,
                              current_state.copy_state(pitch = 0,
                                                       roll = 0,
                                                       yaw = atan2(current_state.vel.y,
                                                                   current_state.vel.x)),
                              old_state, 120).input()

    if current_state.wheel_contact:

        if plan == "Boost-":
            if game_info.my_team == 0:
                target_boost = game_info.boosts[3]
            else:
                target_boost = game_info.boosts[29]

            angle_to_boost = atan2((target_boost.pos - current_state.pos).y , (target_boost.pos - current_state.pos).x)

            if abs(angle_to_boost) < pi/12:
                return FastDodge(current_state,
                                 current_state.copy_state(pos = target_boost.pos),
                                 old_state).input()

            return GroundTurn(current_state, current_state.copy_state(pos = target_boost.pos)).input()

        elif plan == "Boost+":
            if game_info.my_team == 0:
                target_boost = game_info.boosts[4]
            else:
                target_boost = game_info.boosts[30]

            angle_to_boost = atan2((target_boost.pos - current_state.pos).y , (target_boost.pos - current_state.pos).x)

            if abs(angle_to_boost) < pi/12:
                return FastDodge(current_state,
                                 current_state.copy_state(pos = target_boost.pos),
                                 old_state).input()

            return GroundTurn(current_state, current_state.copy_state(pos = target_boost.pos)).input()
            

        elif plan == "Goal":
            if game_info.my_team == 0:
                center_of_net = Vec3(0,-5120,0)
            else:
                center_of_net = Vec3(0,5120,0)

            return GroundTurn(current_state, current_state.copy_state(pos = center_of_net)).input()




        else:
            controller_input = GroundTurn(current_state, current_state.copy_state(pos = game_info.ball.pos)).input()
            if current_state.vel.magnitude() < 2250:
                controller_input.boost = 1
            return controller_input

    return controller_input
































































def testing(current_state, old_state, ball, goal_state, fps):
    '''
    This will be for whenever I'm testing out a new feature or behavior.
    This should not be called at runtime for a finished bot.
    '''
    controller_input = SimpleControllerState()

    controller_input = AerialRotation(current_state,
                                      current_state.copy_state(pitch = 0, yaw = atan2(current_state.vel.y, current_state.vel.x), roll = 0), old_state, fps).input()

    controller_input.throttle = 1
  
    return controller_input

