'''

   In this file we define classes for the lowest level mechancis,
   so that we don't have to interface directly via controller inputs.
   This layer will go between the calculations in Cowculate() and the 
   output into CowBot.py.


'''

from rlbot.agents.base_agent import SimpleControllerState
from math import atan2, pi
from CowBotVector import *
from Miscellaneous import *



class GroundTurn:

    def __init__(self, game_info, turn_target):
        '''
        Turns on the ground towards the turn_target, with   
        '''

        pass







class AirDodge:
    '''
    Handles inputting air dodges.  Maybe prediction will go in here as well.
    It might be better to keep prediction in a different module, and make 
    this one specifically for once I've decided on what to do.
    '''


    def __init__(self, direction):
        '''
        'direction' is a Vec3 in the direction we want to dodge, relative to the car.
        direction = Vec3(0, 0, 0) gives a double jump.
        '''

        self.direction = direction




    def input(self):
        '''
        Returns the controller input to perform an air dodge on the frame called,
        in the desired direction.
        '''

        controller_input = SimpleControllerState()

        if self.direction.x == self.direction.y == self.direction.z == 0:
            controller_input.jump = 1
            return controller_input
        else:
            plane_direction = Vec3(self.direction.x, self.direction.y, 0)
            plane_direction_normalized = plane_direction.normalize()

            
            controller_input.jump = 1
            controller_input.yaw = plane_direction_normalized.y
            controller_input.pitch = - plane_direction_normalized.x
            
            return controller_input




class AerialRotation:

    def __init__(self, current_state, target_state, old_state, time, old_time):

    
        self.start_rot = current_state.rot
        self.start_omega = current_state.omega
        #self.target_rot = target_state.rot
        #self.target_omega = target_state.omega
        self.old_rot = old_state.rot
        self.old_omega = old_state.omega
        
        #This line only for testing and basic recovery, will be removed eventually.
        self.target_rot = [0, atan2(current_state.vel.y, current_state.vel.x) , 0]
        
        #controller_input = zero_omega_recovery(start_rot, 0, [0,atan2(current_state.vel.y, current_state.vel.x),0], 0, old_rot, old_omega, time, old_time)





        '''
        Returns a (pitch, yaw, roll) tuple of controller inputs to turn the car from the starting
        rotation towards the desired rotation. start_rot and target_rot are in (pitch, yaw, roll) form.
        '''



    
    def zero_omega_recovery(self):
        '''
        Returns a controller input to turn the car from the starting rotation towards the
        desired rotation. start_rot, target_rot, and old_rot are in (pitch, yaw, roll) form.
        This just uses three independent PIDs for each of pitch, yaw, roll.
        '''

        #Fix this eventually
        fps = 60

        
        controller_input = SimpleControllerState()

        pitch_error = self.target_rot[0] - self.start_rot[0]
        yaw_error = self.target_rot[1] - self.start_rot[1]
        roll_error = self.target_rot[2] - self.start_rot[2]    

        old_pitch_error = self.start_rot[0] - self.old_rot[0]
        old_yaw_error = self.start_rot[1] - self.old_rot[1]
        old_roll_error = self.start_rot[2] - self.old_rot[2]


        pitch_error = rotate_to_range(pitch_error, [-pi/2, pi/2])
        yaw_error = rotate_to_range(yaw_error, [-pi, pi])
        roll_error = rotate_to_range(roll_error, [-pi, pi])                    

        old_pitch_error = rotate_to_range(old_pitch_error, [-pi/2, pi/2])
        old_yaw_error = rotate_to_range(old_yaw_error, [-pi, pi])
        old_roll_error = rotate_to_range(old_roll_error, [-pi, pi])
        

        pitch_error_derivative = one_frame_derivative(pitch_error, old_pitch_error, fps)
        yaw_error_derivative = one_frame_derivative(yaw_error, old_yaw_error, fps)
        roll_error_derivative = one_frame_derivative(roll_error, old_roll_error, fps)

        #This is reasonable, but at the very least the coefficients need tuning.
        pitch_correction = 1 * pitch_error - .015 * pitch_error_derivative
        yaw_correction = 1 * yaw_error - .02 * yaw_error_derivative
        roll_correction = 1 * roll_error + .01 * roll_error_derivative

        #Normalize
        pitch_correction = cap_magnitude(pitch_correction, 1)
        yaw_correction = cap_magnitude(yaw_correction, 1)
        roll_correction = cap_magnitude(roll_correction, 1)
    
        #Final controller input values
        controller_input.pitch = pitch_correction
        controller_input.yaw = yaw_correction
        controller_input.roll = roll_correction
        controller_input.throttle = 1
        
        return controller_input




    


