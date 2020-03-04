'''

This is currently the main decision process.  Currently runs the execution of the decisions made in Planning.
Parts are definitely worth keeping though, especially the functions at the end (at least worth looking at).

'''


from math import atan2, pi

from rlbot.agents.base_agent import SimpleControllerState
from BallPrediction import get_ball_arrival, choose_stationary_takeoff_time, is_ball_in_scorable_box, prediction_binary_search
from CowBotVector import Vec3
from GameState import Orientation
from Maneuvers import GroundTurn, NavigateTo
from Mechanics import aerial, aerial_rotation, AirDodge, FrontDodge
from Miscellaneous import angles_are_close, cap_magnitude, car_coordinates_2d
from Simulation import linear_time_to_reach

import EvilGlobals #Only needed for rendering and debugging


def Cowculate(plan, game_info, ball_prediction, persistent):
    '''
    The main control function for BAC, Cowculate() returns the final input.
    It takes a GameState object, a plan, and returns a controller_input object.
    Cowculate will be the framework of all decision making, and will be the highest level of abstraction.
    '''

    controller_input = SimpleControllerState()
    current_state = game_info.me

    ############################################################################# 

    if plan.layers[0] == "Boost":
        '''
        Decide how to get the boost we want to go for.
        '''

        #TODO: Optimize these, or phase them out for RLU or similar.
        wobble = Vec3(current_state.omega.x, current_state.omega.y, 0).magnitude()
        epsilon = 0.3
        
        target_boost = None
        if type(plan.layers[1]) == int:
            target_boost = game_info.boosts[plan.layers[1]]
        elif plan.layers[1] == "Pads":
            #This will skip the target boost loop and follow the path
            pass

        if target_boost != None:
            angle_to_boost = atan2((target_boost.pos - current_state.pos).y , (target_boost.pos - current_state.pos).x)
            facing_boost = angles_are_close(angle_to_boost, current_state.rot.yaw, pi/12)
            grounded_facing_boost = facing_boost and current_state.wheel_contact

            #Turn towards boost
            controller_input = GroundTurn(current_state, current_state.copy_state(pos = target_boost.pos)).input()

            if 1000 < current_state.vel.magnitude() < 2250 and facing_boost and wobble < epsilon and (current_state.pos - target_boost.pos).magnitude() > 1000 and abs(current_state.omega.z) < epsilon:
                #If slow, not wobbling from a previous dodge, facing towards the boost,
                #and not already at the boost, dodge for speed
                controller_input = FrontDodge(current_state).input()

            elif current_state.vel.magnitude() < 2300 and (grounded_facing_boost or current_state.rot.pitch < -pi/12):
                controller_input.boost = 1

        elif plan.path == None:
            #Copied the "go to net" code because I don't plan on really improving this for now.
            #This section will be greatly improved once I have ground recovery code in place.
            #TODO: Reocvery code into picking a path more intelligently.
            center_of_net = Vec3(0,-5120,0)
            
            #Turn towards the center of our net
            controller_input = GroundTurn(current_state, current_state.copy_state(pos = center_of_net)).input()

            #Variables to check if we want to flip for speed.
            displacement_from_net = center_of_net - current_state.pos
            distance_to_net = displacement_from_net.magnitude()
            angle_to_net = atan2(displacement_from_net.y, displacement_from_net.x)
            facing_net = angles_are_close(angle_to_net, current_state.rot.yaw, pi/12)
            speed = current_state.vel.magnitude()

            if distance_to_net > 1500 * ((speed+500) / 1410) and 1000 < speed < 2000 and facing_net:
                controller_input = FrontDodge(current_state).input()                
            elif current_state.boost > 60 and facing_net and current_state.wheel_contact and speed < 2300:
                controller_input.boost = 1

            #If we start to go up the wall on the way, turn back down.
            if current_state.wheel_contact:
                if current_state.rot.roll > 0.15:
                    controller_input.steer = 1
                elif current_state.rot.roll < - 0.15:
                    controller_input.steer = -1

        else:
            controller_input = plan.path.input()

    #############################################################################

    elif plan.layers[0] == "Goal":
        '''
        Decide how to go to or wait in net
        '''

        #Useful locations
        center_of_net = Vec3(0,-5120,0)
        if game_info.ball.pos.x > 0:
            far_post = Vec3(-1150, -5120+300, 0)
            far_boost = game_info.boosts[3].pos
        else:
            far_post = Vec3(1150, -5120+300, 0)
            far_boost = game_info.boosts[4].pos

        if plan.layers[1] == "Go to net":
            #Turn towards the center of our net
            controller_input = GroundTurn(current_state, current_state.copy_state(pos = center_of_net)).input()

            #Variables to check if we want to flip for speed.
            displacement_from_net = center_of_net - current_state.pos
            distance_to_net = displacement_from_net.magnitude()
            angle_to_net = atan2(displacement_from_net.y, displacement_from_net.x)
            facing_net = angles_are_close(angle_to_net, current_state.rot.yaw, pi/12)
            speed = current_state.vel.magnitude()
            
            if distance_to_net > 1500 and 1000 < speed < 2000 and facing_net:
                controller_input = FrontDodge(current_state).input()
            elif current_state.boost > 60 and facing_net and current_state.wheel_contact and speed < 2300:
                controller_input.boost = 1

            #If we start to go up the wall on the way, turn back down.
            if current_state.wheel_contact:
                if current_state.rot.roll > 0.15:
                    controller_input.steer = 1
                elif current_state.rot.roll < - 0.15:
                    controller_input.steer = -1

        elif plan.layers[1] == "Wait in net":
            if plan.layers[2] == "Prep for Aerial":
                controller_input = SimpleControllerState()

            else:
                ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                                   (game_info.ball.pos - current_state.pos).x)

                #Go to net, stop in the middle, then turn in place to face the ball.
                #TODO: Improve NavigateTo or replace completely
                rot = Orientation(pyr = [current_state.rot.pitch, ball_angle, current_state.rot.roll] )
                target_state = current_state.copy_state(pos = center_of_net, rot = rot)
                controller_input = NavigateTo(current_state, target_state).input()

    #############################################################################

    elif plan.layers[0] == "Ball":
        '''
        Calculate how to go for the ball as decided in planning.
        '''

        if plan.layers[1] == "Challenge":
            #TODO: Intelligent challenges.
            if current_state.wheel_contact:
                #If still on ground, jump
                controller_input.jump = 1
            else:
                #Once we've jumped, dodge towards the ball
                controller_input = AirDodge(car_coordinates_2d(current_state,
                                                               game_info.ball.pos - current_state.pos),
                                            current_state.jumped_last_frame).input()


        elif plan.layers[1] == "Save":
            if persistent.path_follower.action != None:
                #Follow the ArcLineArc path
                persistent.path_follower.action.step(game_info.dt)
                controller_input = persistent.path_follower.action.controls
            #else:
            #    controller_input = jump_turn() #TODO: When facing walls, all paths go about of bounds.  Turn around first.

        elif plan.layers[2] == "Aerial":

            controller_input, persistent = aerial(game_info.dt,
                                                  game_info.team_sign,
                                                  persistent)

        elif (plan.layers[1] == "Shot" or plan.layers[1] == "Clear") and plan.layers[2] == "Path":
            if persistent.path_follower.action != None:
                #Follow the ArcLineArc path
                persistent.path_follower.action.step(game_info.dt)
                controller_input = persistent.path_follower.action.controls
            #else:
            #    controller_input = jump_turn() #TODO: When facing walls, all paths go about of bounds.  Turn around first.

        elif (plan.layers[1] == "Shot" or plan.layers[1] == "Clear") and plan.layers[2] == "Hit ball":
            if persistent.doddge.action == None:
                persistent.dodge.check = True
                dodge_simulation_results = moving_ball_dodge_contact(game_info)
                persistent.dodge.action = RLU_Dodge(game_info.utils_game.my_car)
                persistent.dodge.action.duration = dodge_simulation_results[0]
                persistent.dodge.action.delay = dodge_simulation_results[1]
                persistent.dodge.action.target = Vec3_to_vec3(game_info.ball.pos, game_info.team_sign)
                persistent.dodge.action.preorientation = roll_away_from_target(persistent.dodge.action.target,
                                                                                    pi/4,
                                                                                    game_info)            
            else:
                persistent.dodge.check = True
                persistent.dodge.action.step(game_info.dt)
                output = persistent.dodge.action.controls
                output.boost = 1

        elif (plan.layers[1] == "Shot" or plan.layers[1] == "Clear") and plan.layers[2] == "Chase":
            controller_input = GroundTurn(current_state, current_state.copy_state(pos = game_info.ball.pos)).input()


    #############################################################################

    elif plan.layers[0] == "Recover":
        if plan.layers[1] == "Air":
            #If we're in the air, and not trying to hit the ball, recover.

            controller_input, persistent = aerial_rotation(game_info.dt,
                                                           persistent)

        elif plan.layers[1] == "Ground":
            controller_input = GroundTurn(current_state,
                                          current_state.copy_state(pos = Vec3(0,-5120,0))).input()
            #TODO: Work on have_steering_control, powersliding, etc.


    return controller_input, persistent





