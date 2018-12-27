from math import pi, atan2
from CowBotVector import *
from GameState import *

def blindly_chase_ball(game_info):
    '''
    This just returns the ball position as a target CarState
    '''

    return CarState( game_info.ball.pos,
             None,
             None,
             None )

def naive_turn(current_state, target_state, controller_input):
    '''
    Returns a controller state that turns the car towards the ball while holding accelerate.
    There are a few parameters to eliminate wiggle and improve accuracy and efficiency.
    '''

    controller_input.throttle = 1.0

    #Check that we have a target position
    if target_state.pos != None:
        #Get the current angle of the car (yaw)
        twod_current_rot = current_state.rot[1]

        #Get the vector from the car to the target
        twod_current = Vec3( current_state.pos.x,
                           current_state.pos.y,
                           0 )
        twod_target = Vec3( target_state.pos.x,
                          target_state.pos.y,
                          0 )
        twod_current_to_target = twod_target - twod_current
        twod_target_rot = atan2(twod_current_to_target.y, twod_current_to_target.x)

        #Find the angle between current orientation and the target
        correction_angle = twod_current_rot - twod_target_rot
        if correction_angle > pi:
            correction_angle -= 2*pi
        elif correction_angle < -pi:
            correction_angle += 2*pi

        #Steer to fix the angle.
        #Use proportional input for small corrections
        if correction_angle > 0.5:
            controller_input.steer = -1
        elif correction_angle < -0.5:
            controller_input.steer = 1
        else:
            controller_input.steer = - 2*correction_angle
            
    return controller_input
