import rlutilities as util
from rlutilities.mechanics import AerialTurn
import rlutilities.linear_algebra as linear

from Miscellaneous import *

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


class PersistentMechanics:
    '''
    This class will hold information for mechanics that require past data.
    '''

    def __init__( self ):
        self.aerial_turn = Mechanic()
        



class Mechanic:
    '''
    
    '''

    def __init__( self ):
        self.check = False
        self.action = None
        self.target_rot = None




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

def aerial_rotation(target_rot, dt, persistent):
    persistent.aerial_turn.check = True
    persistent.aerial_turn.action.target = rot_to_mat3(target_rot)
    persistent.aerial_turn.action.step(dt)
    controller_input = persistent.aerial_turn.action.controls

    return controller_input, persistent




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
