from GameState import *
from CowBotVector import *
from rlbot.agents.base_agent import SimpleControllerState
from NaiveSteering import *
from Testing import *
from BallPrediction import *
from Kickoff import *
from Mechanics import *
from math import sin, cos
from Maneuvers import *
from Pathing import *
from GamePlan import *
import EvilGlobals
from Miscellaneous import *



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

        controller_input = SimpleControllerState()

        if plan == "Boost-" or plan == "Boost+":
            if plan == "Boost-":
                if game_info.my_team == 0:
                    target_boost = game_info.boosts[3]
                else:
                    target_boost = game_info.boosts[29]

            else:
                if game_info.my_team == 0:
                    target_boost = game_info.boosts[4]
                else:
                    target_boost = game_info.boosts[30]

            
            angle_to_boost = atan2((target_boost.pos - current_state.pos).y , (target_boost.pos - current_state.pos).x)

            '''if (abs(current_state.yaw - angle_to_boost) < pi/3) and (current_state.vel.magnitude() < 2250):
                if (current_state.yaw - angle_to_boost) < 0:
                    return FastDodge(current_state,
                                     current_state.copy_state(pos = target_boost.pos),
                                     old_state,
                                     direction = 1,
                                     boost_to_use = current_state.boost-1,
                                     boost_threshold = 1200).input()
                else:
                    return FastDodge(current_state,
                                     current_state.copy_state(pos = target_boost.pos),
                                     old_state,
                                     direction = -1,
                                     boost_to_use = current_state.boost-1,
                                     boost_threshold = 1200).input()'''

                
            controller_input = GroundTurn(current_state, current_state.copy_state(pos = target_boost.pos)).input()

            if current_state.vel.magnitude() < 2250 and current_state.wheel_contact:
                controller_input.boost = 1
            return controller_input
            

        elif plan == "Goal":
            if game_info.my_team == 0:
                center_of_net = Vec3(0,-5120,0)
            else:
                center_of_net = Vec3(0,5120,0)

            controller_input = GroundTurn(current_state, current_state.copy_state(pos = center_of_net)).input()

            if current_state.roll > 0.1:
                controller_input.steer = 1
            elif current_state.roll < - 0.1:
                controller_input.steer = -1
            return controller_input

        elif (not current_state.wheel_contact) and plan != "Flip into Ball":
        
            controller_input = AerialRotation(current_state,
                                              current_state.copy_state(pitch = 0,
                                                                       roll = 0,
                                                                       yaw = atan2(current_state.vel.y,
                                                                                   current_state.vel.x)),
                                              old_state, 120).input()
            controller_input.throttle = 1

            return controller_input

        elif plan == "Ball":
            if game_info.my_team == 0:
                y_sign = 1
            else:
                y_sign = -1

            
            ball_in_defensive_corner = not (y_sign*game_info.ball.pos.y > -1500 or abs(game_info.ball.pos.x) < 1500)
            ball_in_offensive_corner = not (y_sign*game_info.ball.pos.y < 1000 or abs(game_info.ball.pos.x) < 1500)
            if not ball_in_defensive_corner and not ball_in_offensive_corner and current_state.wheel_contact:
                if (Vec3(cos(current_state.yaw) , sin(current_state.yaw), 0)).dot((game_info.ball.vel).normalize()) > - 0.7:
                    time_guess = ((game_info.ball.pos - current_state.pos).magnitude()) / (max((current_state.vel).magnitude(), 1000))
                    target_pos = game_info.ball.pos + (game_info.ball.vel.scalar_multiply(time_guess))

                else:
                    target_pos = game_info.ball.pos


                if (game_info.opponents[0].pos - game_info.ball.pos).magnitude() > 1000:
                    #opponent net this time
                    if game_info.my_team == 0:
                        center_of_net = Vec3(0,5120,game_info.ball.pos.z)
                    else:
                        center_of_net = Vec3(0,-5120,game_info.ball.pos.z)

                    if game_info.ball.pos.x > 0:
                        shooting_correction = (60*(5120 - abs(game_info.ball.pos.y))) / ((game_info.ball.pos - center_of_net).magnitude())

                    else:
                        shooting_correction = - (60*(5120 - abs(game_info.ball.pos.y))) / ((game_info.ball.pos - center_of_net).magnitude())

                    target_pos = Vec3(target_pos.x + shooting_correction, target_pos.y, target_pos.z)

                #Make sure we don't try to go to a point outside the map
                target_pos = Vec3(cap_magnitude(target_pos.x, 4096), cap_magnitude(target_pos.y, 5120) , target_pos.z)
                controller_input = GroundTurn(current_state, current_state.copy_state(pos = target_pos)).input()
                ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                                   (game_info.ball.pos - current_state.pos).x)

                if current_state.vel.magnitude() < 2250 and current_state.wheel_contact and (current_state.yaw - ball_angle) < pi/6:
                    controller_input.boost = 1
                return controller_input

            elif ball_in_defensive_corner or ball_in_offensive_corner:
                if game_info.my_team == 0:
                    center_of_net = Vec3(0,-5120,0)
                else:
                    center_of_net = Vec3(0,5120,0)


                ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                                   (game_info.ball.pos - current_state.pos).x)
                return NavigateTo(current_state, current_state.copy_state(pos = center_of_net,
                                                                          yaw = ball_angle), game_info.ball).input()

     

            

        elif plan == "Flip into Ball":
            if current_state.wheel_contact:
                controller_input.jump = 1
            else:
                controller_input = AirDodge(car_coordinates_2d(current_state, game_info.ball.pos - current_state.pos),
                                            current_state.jumped_last_frame).input()
    
            return controller_input

        else:
            controller_input = GroundTurn(current_state, current_state.copy_state(pos = game_info.ball.pos)).input()
            if current_state.vel.magnitude() < 2250 and current_state.wheel_contact:
                controller_input.boost = 1
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

