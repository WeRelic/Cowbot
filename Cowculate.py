'''

This is currently the main decision process.  Currently runs the execution of the decisions made in Planning.
Parts are definitely worth keeping though, especially the functions at the end (at least worth looking at).

'''


from math import atan2, pi

from rlbot.agents.base_agent import SimpleControllerState

from BallPrediction import aerial_prediction, get_ball_arrival, choose_stationary_takeoff_time, is_ball_in_scorable_box
from CowBotVector import Vec3
from GameState import Orientation
from Maneuvers import GroundTurn, NavigateTo
from Mechanics import aerial, aerial_rotation, AirDodge, FrontDodge
from Miscellaneous import angles_are_close, cap_magnitude, car_coordinates_2d, linear_time_to_reach

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
        if plan.layers[1] == "Back Boost-":
            target_boost = game_info.boosts[3]
        elif plan.layers[1] == "Back Boost+":
            target_boost = game_info.boosts[4]
        elif plan.layers[1] == "Mid Boost-":
            target_boost = game_info.boosts[15]        
        elif plan.layers[1] == "Mid Boost+":
            target_boost = game_info.boosts[18]
        elif plan.layers[1] == "Pads":
            #This will skip the target boost loop and follow the path
            pass

        if target_boost != None:
            angle_to_boost = atan2((target_boost.pos - current_state.pos).y , (target_boost.pos - current_state.pos).x)
            facing_boost = angles_are_close(angle_to_boost, current_state.rot.yaw, pi/12)
            grounded_facing_boost = facing_boost and current_state.wheel_contact

            #Turn towards boostI
            controller_input = GroundTurn(current_state, current_state.copy_state(pos = target_boost.pos)).input()

            if 1000 < current_state.vel.magnitude() < 2250 and facing_boost and wobble < epsilon and (current_state.pos - target_boost.pos).magnitude() > 1000 and abs(current_state.omega.z) < epsilon:
                #If slow, not wobbling from a previous dodge, facing towards the boost,
                #and not already at the boost, dodge for speed
                controller_input = FrontDodge(current_state).input()

            elif current_state.vel.magnitude() < 2300 and (grounded_facing_boost or current_state.rot.pitch < -pi/12):
                controller_input.boost = 1

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

            #If we start to go up the wall on the way, turn back down.
            if current_state.rot.roll > 0.15:
                controller_input.steer = 1
            elif current_state.rot.roll < - 0.15:
                controller_input.steer = -1

        elif plan.layers[1] == "Wait in net":
            if plan.layers[2] == "Prep for Aerial":
                target_time, target_loc = get_ball_arrival(game_info,
                                                           is_ball_in_scorable_box)

                if game_info.game_time > choose_stationary_takeoff_time(game_info,
                                                                        target_loc,
                                                                        target_time) - 1/10:
                    if target_loc.z > 200 and -50 < current_state.vel.y < 200:
                        #TODO: Deal with aerials while moving
                        persistent.aerial.check = True
                        persistent.aerial.initialize = True
                        persistent = aerial_prediction(game_info, target_time, persistent)

            else:
                #Know where the ball is so we can face it
                ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                                   (game_info.ball.pos - current_state.pos).x)

                #Go to net, stop in the middle, then turn in place to face the ball.
                #TODO: Improve NavigateTo or replace completely
                rot = Orientation(pyr = [current_state.rot.pitch, ball_angle, current_state.rot.roll] )
                controller_input = NavigateTo(current_state, current_state.copy_state(pos = center_of_net, rot = rot)).input()

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

                '''
        elif plan.layers[1] == "Save" and plan.layers[2] == "Backwards":
                controller_input = GroundTurn(current_state,
                                              current_state.copy_state(pos = game_info.ball.pos),
                                              can_reverse = True).input()
                '''

        elif plan.layers[2] == "Aerial":

            controller_input, persistent = aerial(game_info.dt,
                                                  game_info.team_sign,
                                                  persistent)
                
        else:
            #TODO: Replace all of this with shooting/clearing/better code.
            #Need pathing to get to a reasonable spot, and intelligent dodges to place the ball properly.
            
            for i in range(100):

                #Adjust for Ball/Car radii
                ball_vel = ball_prediction.slices[i].vel

                try:
                    #Evil magic numbers.  TODO: Actual timing and arrival prediction.
                    target_pos = ball_prediction.slices[i].pos + ball_vel.normalize().scalar_multiply(150)
                except ZeroDivisionError:
                    target_pos = ball_prediction.slices[i].pos


                car_target_vector =  target_pos - current_state.pos
                turn_angle = abs(current_state.rot.yaw - atan2(car_target_vector.y , car_target_vector.x))
                time_estimate = linear_time_to_reach(game_info, target_pos) - (ball_vel.magnitude()/50)*(turn_angle)
                if ball_prediction.slices[i].time < time_estimate + 1/30:
                    break

            if plan.layers[1] == "Shot":
                #If the opponent isn't close to the ball, reposition to shoot towards net
                #Find the center of the opponent's net
                center_of_net = Vec3(0, 5120, game_info.ball.pos.z)

                #If the ball is left, go right, and vice versa.  
                if game_info.ball.pos.x > 0:
                    shooting_correction = (60*(5120 - abs(game_info.ball.pos.y))) / ((game_info.ball.pos - center_of_net).magnitude())
                else:
                    shooting_correction = - (60*(5120 - abs(game_info.ball.pos.y))) / ((game_info.ball.pos - center_of_net).magnitude())
                    
                    target_pos = Vec3(target_pos.x + shooting_correction, target_pos.y, target_pos.z)


            #Make sure we don't try to go to a point outside the map
            target_pos = Vec3(cap_magnitude(target_pos.x, 4096), cap_magnitude(target_pos.y, 5120) , target_pos.z)
            #Turn towards the target
            controller_input = GroundTurn(current_state, current_state.copy_state(pos = target_pos)).input()
    
            #If we're not supersonic, and we're facing roughly towards the ball, boost.
            ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                               (game_info.ball.pos - current_state.pos).x)
            if current_state.vel.magnitude() < 2250 and current_state.wheel_contact and angles_are_close(current_state.rot.yaw, ball_angle, pi/4):
                controller_input.boost = 1


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

