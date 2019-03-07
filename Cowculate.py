from GameState import *
from CowBotVector import *
from rlbot.agents.base_agent import SimpleControllerState
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
    It takes a GameState object and returns a controller_input object.
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
        team_sign = game_info.team_sign
        shot_on_goal = False
        #Look ahead two seconds to see if the ball is rolling into the net
        for step in range(100):
            ball_prediction = (game_info.ball.pos + game_info.ball.vel.scalar_multiply(0.02*step))
            if abs(ball_prediction.x) < 915 and team_sign*ball_prediction.y < -5120:
                shot_on_goal = True

        #Fix this once we add flips, but this is fine for now.
        if (plan == "Boost-" or plan == "Boost+") and current_state.wheel_contact:
            controller_input = go_for_boost(plan, game_info, controller_input)
            

        elif plan == "Goal" and current_state.wheel_contact and len(game_info.teammates) == 0:
            controller_input = go_to_net(plan, game_info, old_state, controller_input)

        elif plan == "Ball" and len(game_info.teammates) == 0:
            #Team variable to deal with both sides
            

            ball_in_defensive_corner = not (team_sign*game_info.ball.pos.y > -1500 or abs(game_info.ball.pos.x) < 1500)
            ball_in_offensive_corner = not (team_sign*game_info.ball.pos.y < 950 or abs(game_info.ball.pos.x) < 1500)
            if not ball_in_defensive_corner and not ball_in_offensive_corner and current_state.wheel_contact:
                controller_input = go_for_ball(game_info, shot_on_goal, controller_input)

            elif ball_in_defensive_corner or ball_in_offensive_corner:
                controller_input = wait_in_net(game_info, controller_input)


        elif plan == "Flip into Ball":
            controller_input = flip_into_ball(game_info, controller_input)

        elif (not current_state.wheel_contact):
            #If we're in the air, and not trying to hit the ball, recover.
        
            controller_input = AerialRotation(current_state,
                                              current_state.copy_state(pitch = 0,
                                                                       roll = 0,
                                                                       yaw = atan2(current_state.vel.y,
                                                                                   current_state.vel.x)),
                                              old_state, 120).input()
            controller_input.throttle = 1
            return controller_input


        elif len(game_info.teammates) > 0:
            ball_in_defensive_corner = not (team_sign*game_info.ball.pos.y > -1500 or abs(game_info.ball.pos.x) < 1500)
            teammate_in_net = abs(game_info.teammates[0].pos.x) < 900 and team_sign*game_info.teammates[0].pos.y < -4700
                
            if team_sign * game_info.ball.pos.y > -1500:
                #Don't go into the opponents' half
                controller_input = wait_in_net(game_info, controller_input)
            elif teammate_in_net and not shot_on_goal:
                #Don't cut off teammate unless you need to make a save
                controller_input = wait_far_post(game_info, controller_input)
            elif ball_in_defensive_corner:
                #Wait in net if the ball is in the corner and teammate isn't in net
                controller_input = wait_in_net(game_info, controller_input)
            else:
                controller_input = go_for_ball(game_info, shot_on_goal, controller_input)




        else:
            #If it's a 1v1, go for the ball next
            controller_input = ball_chase(game_info, controller_input)


            
        return controller_input


#########################################################################################
#########################################################################################


def go_to_net(plan, game_info, old_state, controller_input):
    current_state = game_info.me

    #Find the center of our net
    center_of_net = Vec3(0,-game_info.team_sign*5120,0)

    #Turn towards the center of our net
    controller_input = GroundTurn(current_state, current_state.copy_state(pos = center_of_net)).input()

    #If we start to go up the wall on the way, turn back down.
    if current_state.roll > 0.1:
        controller_input.steer = 1
    elif current_state.roll < - 0.1:
        controller_input.steer = -1
    return controller_input

#########################################################################################



def go_for_boost(plan, game_info, controller_input):
    current_state = game_info.me

    #Check -x coordinate boosts
    if plan == "Boost-":
        if game_info.my_team == 0:
            target_boost = game_info.boosts[3]
        else:
            target_boost = game_info.boosts[29]

    #Check +x coordinate boosts
    else:
        if game_info.my_team == 0:
            target_boost = game_info.boosts[4]
        else:
            target_boost = game_info.boosts[30]


    angle_to_boost = atan2((target_boost.pos - current_state.pos).y , (target_boost.pos - current_state.pos).x)

    #Turn towards boost
    controller_input = GroundTurn(current_state, current_state.copy_state(pos = target_boost.pos)).input()

    #If slow and on the ground, boost
    if current_state.vel.magnitude() < 2250 and current_state.wheel_contact and abs(angle_to_boost - current_state.yaw) < pi/6:
        controller_input.boost = 1
    return controller_input



#########################################################################################

def go_for_ball(game_info, shot_on_goal, controller_input):

    current_state = game_info.me
    if shot_on_goal and (Vec3(cos(current_state.yaw) , sin(current_state.yaw), 0)).dot((game_info.ball.vel).normalize()) < - pi/8:
        return GroundTurn(current_state, game_info.ball.pos, can_reverse = True).input()



    elif game_info.ball.vel.magnitude() > 0 and (Vec3(cos(current_state.yaw) , sin(current_state.yaw), 0)).dot((game_info.ball.vel).normalize()) > - 0.7:
    #If the ball isn't coming right at us, try to lead it to make contact.
        #time for us to reach the ball's current position at our current speed, which is
        #bounded below to avoid bad things
        time_guess = ((game_info.ball.pos - current_state.pos).magnitude()) / (max((current_state.vel).magnitude(), 1000))
        #The place the ball will be after the above time at its current velocity
        target_pos = game_info.ball.pos + (game_info.ball.vel.scalar_multiply(time_guess))
        
    else:
        #if the ball is coming right at us, just drive at it
        target_pos = game_info.ball.pos

        
    if (game_info.opponents[0].pos - game_info.ball.pos).magnitude() > 1000:
        #If the opponent isn't close to the ball, reposition to shoot on net
        #Find the center of the opponent's net
        center_of_net = Vec3(0,game_info.team_sign*5120,game_info.ball.pos.z)

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

    ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                       (game_info.ball.pos - current_state.pos).x)

    #If we're not supersonic, and we're facing roughly towards the ball, boost.
    if current_state.vel.magnitude() < 2250 and current_state.wheel_contact and (current_state.yaw - ball_angle) < pi/6:
        controller_input.boost = 1


    return controller_input


#########################################################################################

def wait_in_net(game_info, controller_input):
    current_state = game_info.me
    #Find our net
    center_of_net = Vec3(0,-game_info.team_sign*5120,0)

    #Know where the ball is so we can face it
    ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                       (game_info.ball.pos - current_state.pos).x)

    #Go to net, stop in the middle, then turn in place to face the ball.
    return NavigateTo(current_state, current_state.copy_state(pos = center_of_net, yaw = ball_angle)).input()


#########################################################################################


def flip_into_ball(game_info, controller_input):
    current_state = game_info.me
    #if still on ground, jump
    if current_state.wheel_contact:
        controller_input.jump = 1
    else:
        #Once we've jumped, dodge towards the ball
        controller_input = AirDodge(car_coordinates_2d(current_state, game_info.ball.pos - current_state.pos),
                                    current_state.jumped_last_frame).input()
        
    return controller_input


#########################################################################################


def ball_chase(game_info, controller_input):
    current_state = game_info.me

    #Turn towards ball, and boost if on the ground and not supersonic.
    controller_input = GroundTurn(current_state, current_state.copy_state(pos = game_info.ball.pos)).input()
    if current_state.vel.magnitude() < 2250 and current_state.wheel_contact:
        controller_input.boost = 1
    return controller_input

#########################################################################################

def wait_far_post(game_info, controller_input):
    current_state = game_info.me
    #Find our net
    if game_info.ball.pos.x > 0:
        far_post = Vec3(-900,-game_info.team_sign*5000,0)
    else:
        far_post = Vec3(900,-game_info.team_sign*5000,0)

    #Know where the ball is so we can face it
    ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                       (game_info.ball.pos - current_state.pos).x)

    #Go to net, stop in the middle, then turn in place to face the ball.
    return NavigateTo(current_state, current_state.copy_state(pos = far_post, yaw = ball_angle)).input()
