'''

   In this file we define classes for the lowest level mechancis,
   so that we don't have to interface directly via controller inputs.
   This layer will go between the calculations in Cowculate() and the 
   output into CowBot.py.


'''

from rlbot.agents.base_agent import SimpleControllerState
from math import atan2, pi, sin, cos, sqrt
from CowBotVector import *
from Miscellaneous import *


#############################################################################################

#############################################################################################



class AirDodge:
    '''
    Handles inputting air dodges.  Maybe prediction will go in here as well.
    It might be better to keep prediction in a different module, and make 
    this one specifically for once I've decided on what to do.
    '''


    def __init__(self, direction, jumped_last_frame):
        '''
        'direction' is a Vec3 in the direction we want to dodge, relative to the car.
        "Forward" is the +x direction, with +y to the right, and +z up.
        direction = Vec3(0, 0, 0) gives a double jump.
        '''

        self.jumped_last_frame = jumped_last_frame
        self.direction = direction




    def input(self):
        '''
        Returns the controller input to perform an air dodge on the frame called,
        in the desired direction.
        '''

        controller_input = SimpleControllerState()

        if (not self.jumped_last_frame):
            if (self.direction.x == self.direction.y == self.direction.z == 0):
                controller_input.jump = 1
                return controller_input
            else:
                plane_direction = Vec3(self.direction.x, self.direction.y, 0)
                plane_direction_normalized = plane_direction.normalize()
                
                controller_input.jump = 1
                controller_input.yaw = plane_direction_normalized.y
                controller_input.pitch = - plane_direction_normalized.x
                
        return controller_input


#############################################################################################

#############################################################################################

class AerialRotation:

    def __init__(self, current_state, target_state, old_state, fps = 120):

    
        self.start_pitch = current_state.pitch
        self.start_roll = current_state.roll
        self.start_yaw = current_state.yaw

        self.start_omega = current_state.omega

        self.target_pitch = target_state.pitch
        self.target_roll = target_state.roll
        self.target_yaw = target_state.yaw

        self.target_omega = target_state.omega

        self.old_pitch = old_state.pitch
        self.old_roll = old_state.roll
        self.old_yaw = old_state.yaw
        self.old_omega = old_state.omega

        self.fps = fps



    def input(self):
        '''
        Returns a controller input to turn the car from the starting rotation towards the
        desired rotation. start_rot, target_rot, and old_rot are in (pitch, yaw, roll) form.
        This just uses three independent PIDs for each of pitch, yaw, roll.
        '''

        controller_input = SimpleControllerState()

        pitch_error = self.target_pitch - self.start_pitch
        yaw_error = self.target_yaw - self.start_yaw
        roll_error = self.target_roll - self.start_roll    

        old_pitch_error = self.start_pitch - self.old_pitch
        old_yaw_error = self.start_yaw - self.old_yaw
        old_roll_error = self.start_roll - self.old_roll


        pitch_error = rotate_to_range(pitch_error, [-pi/2, pi/2])
        yaw_error = rotate_to_range(yaw_error, [-pi, pi])
        roll_error = rotate_to_range(roll_error, [-pi, pi])                    

        old_pitch_error = rotate_to_range(old_pitch_error, [-pi/2, pi/2])
        old_yaw_error = rotate_to_range(old_yaw_error, [-pi, pi])
        old_roll_error = rotate_to_range(old_roll_error, [-pi, pi])
        

        pitch_error_derivative = one_frame_derivative(pitch_error, old_pitch_error, self.fps)
        yaw_error_derivative = one_frame_derivative(yaw_error, old_yaw_error, self.fps)
        roll_error_derivative = one_frame_derivative(roll_error, old_roll_error, self.fps)

        #This is reasonable, but at the very least the coefficients need tuning.
        pitch_correction = 1 * pitch_error# - .015 * pitch_error_derivative
        yaw_correction = 1 * yaw_error - .01 * yaw_error_derivative
        roll_correction = 1 * roll_error + .01 * roll_error_derivative

        #Normalize
        pitch_correction = cap_magnitude(pitch_correction, 1)
        yaw_correction = 5*cap_magnitude(yaw_correction, 1/5)
        roll_correction = cap_magnitude(roll_correction, 1)
    
        #Final controller input values
        controller_input.pitch = pitch_correction
        controller_input.yaw = yaw_correction
        controller_input.roll = roll_correction
        controller_input.throttle = 1
        
        return controller_input    




#############################################################################################

#############################################################################################

class JumpTurn:
    '''
    This mechanic is to jump and turn to face a given direction.
    '''

    def __init__(self, current_state, jump_height, turn_direction):
        self.jump_height = jump_height
        self.current_state = current_state

        #1 for clockwise, -1 for counterclockwise
        self.turn_direction = turn_direction


    def input(self):
        controller_input = SimpleControllerState()
        #Add a catch to make sure jump_height isn't higher than the max jump height
        #For now make sure jump_height is zero or higher than the height of the car at rest.

        #Zero jump height means we just jump on frame 1
        if self.jump_height == 0 and self.current_state.wheel_contact:
            controller_input.jump = 1

        #If we're not to jump_height yet, hold jump to jump higher.
        elif self.current_state.pos.z < self.jump_height:
            controller_input.jump = 1

        #Turn in the right direction.
        if self.turn_direction ==0:
            raise TypeError("turn direction should be 1 or -1")
        controller_input.yaw = self.turn_direction

        return controller_input





#############################################################################################

#############################################################################################


class QuickTurn():
    '''
    A powerslide turn to turn a small amount quickly.  Designed for flipping for speed.
    Might be useful for shooting as well.
    '''

    def __init__(self, direction, boost):
        '''
        +1 direction for right, -1 for left
        boost is a boolean
        '''

        
        self.direction = direction
        self.boost = boost


    def input(self):
        controller_input = SimpleControllerState()
        controller_input.throttle = 1
        if self.boost == 1:
            controller_input.boost = 1
        controller_input.handbrake = 1
        controller_input.steer = self.direction
        return controller_input



#############################################################################################

#############################################################################################


class CancelledFastDodge:
    '''
    CancelledFastDodge is the mechanic where one dodges diagonally forward, then cancels
    the forward portion of the flip.  This might be useful on kickoffs, since it should be faster 
    than a standard dodge.
    '''


    def __init__(self, current_state, dodge_direction):
        #Dodge direction is 1 for right, -1 for left
        self.double_jumped = current_state.double_jumped
        self.dodge_direction = dodge_direction
        self.current_state = current_state




    def input(self):
        controller_input = SimpleControllerState()

        if self.current_state.pos.z < 50:
            #If we're too close to the ground to dodge, just keep boosting.
            controller_input.boost = 1
            return controller_input

        if not self.double_jumped:
            #If we haven't double jumped yet, dodge
            return AirDodge(Vec3(1/sqrt(2), self.dodge_direction / sqrt(2), 0), self.current_state.jumped_last_frame).input()


        else:
            #If we have double jumped, pull back to cancel the forward portion of the dodge.
            controller_input.boost = 1
            controller_input.pitch = 1
            return controller_input
