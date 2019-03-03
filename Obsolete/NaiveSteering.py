from math import pi, atan2, sin, cos
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



def less_blindly_chase_ball(game_info):
    '''
    If a simple accelerate and turn will hit the ball, do that.
    Otherwise drive away from the ball until it will.
    '''

    if can_we_hit_ball(game_info.me, game_info.ball):
        return CarState( game_info.ball.pos,
                         None,
                         None,
                         None )
    else:
        return CarState( game_info.me.pos + game_info.me.pos - game_info.ball.pos,
                         None,
                         None,
                         None )
        

def naive_turn(current_state, target_state, controller_input):
    '''
    Returns a controller state that turns the car towards the target while holding accelerate.
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



def can_we_hit_ball(car, ball):
    relative_circle_center_1 = Vec3( 0,
                                     640,
                                     0 )
    relative_circle_center_2 = Vec3( 0,
                                     -640,
                                     0 )
    circle_center_1 = relative_to_absolute(relative_circle_center_1, car)
    circle_center_2 = relative_to_absolute(relative_circle_center_2, car)

    #Check if the ball is in either of our turning circles
    #incorporated half the width of the octane, 42uu, to remove some false negatives.
    if (ball.pos.x - circle_center_1.x)**2 + (ball.pos.y - circle_center_1.y)**2 <= (640-42)**2:
        return False
    elif (ball.pos.x - circle_center_2.x)**2 + (ball.pos.y - circle_center_2.y)**2 <= (640-42)**2:
        return False
    else:
        return True


def relative_to_absolute(rel_pos, car):
    '''
    Takes a coordinate, rel_pos, relative to car's position and orientation
    and transforms it into the absolute field coordinates.
    For now this only works with 2d coordinates on the ground.
    '''

    #rel_pos is +x in the direction of the car, +y clockwise by pi
    #car.yaw of zero means the car is facing in the +x direction.
    #yaw increases in the clockwise direction
    return Vec3( car.pos.x + rel_pos.x * cos(car.yaw) - rel_pos.y * sin(car.yaw),
                 car.pos.y + rel_pos.x * sin(car.yaw) + rel_pos.y * cos(car.yaw)    ,
                 car.pos.z )












