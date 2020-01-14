'''

   In this file we define classes for the lowest level mechanics,
   so that we don't have to interface directly via controller inputs.
   This layer will go between the calculations in Cowculate() and the 
   output into CowBot.py.

'''


from math import atan2, pi, sin, cos, sqrt

from rlbot.agents.base_agent import SimpleControllerState

from Conversions import rot_to_mat3, Vec3_to_vec3
from CowBotVector import Vec3


class PersistentMechanics:
    '''
    This class will hold information for mechanics that require past data.
    '''

    def __init__( self ):
        self.aerial_turn = Mechanic()
        self.aerial = Mechanic()
        self.hit_ball = Mechanic()
        self.path_follower = Mechanic()
        self.dodge = Mechanic()


class Mechanic:
    '''
    This is the class for a mechanic (typically from RLUtilities) that requires past information.
    Each mechanic has a check, which records if the mechanics 
    is currently operating, so that we don't overwrite it while it's running.
    Each mechanic also has an action, which will be the corresponding object from RLU.
    Mechanic.data will be used for any planning that needs to be recorded, e.g., the takeoff time 
    for an aerial.
    Mechanic.initialize will be used as a flag to know when we should start the mechanic;
    e.g., it's changed to True once the game time is greater than the planned takeoff
    time for an aerial.
    '''

    def __init__( self ):
        self.check = False
        self.action = None
        self.data = None
        self.initialize = False
        self.path = None

        #Aerial Turn
        self.target_orientation = None

        #Aerial
        self.target_location = None
        self.target_time = None
        self.target_up = Vec3(0,0,1)

#############################################################################################

#############################################################################################


def aerial(dt, team_sign, persistent):
    '''
    Takes a time delta (float), a team sign (+1 for blue, or -1 or orange) and a PersistentMechanics object.
    Returns contoller input and an updated PersistentMechanics object for the next frame.
    These are the steps to access RLUtilities' Aerial functions. All the math happens there.
    '''
    persistent.aerial.check = True
    persistent.aerial.action.step(dt)
    controller_input = persistent.aerial.action.controls

    return controller_input, persistent


#############################################################################################

#############################################################################################


def aerial_rotation(dt, persistent):
    '''
    Takes a target Orientation object, a time delta (float), and a PersistentMechanics object.
    Returns contoller input and an updated PersistentMechanics object for the next frame.
    These are the steps to access RLUtilities' AerialTurn functions. All the math happens there.
    '''
    persistent.aerial_turn.check = True
    persistent.aerial_turn.action.step(dt)
    controller_input = persistent.aerial_turn.action.controls

    return controller_input, persistent




#############################################################################################

#############################################################################################



class AirDodge:
    '''
    Handles inputting air dodges. 
    '''


    def __init__(self,
                 direction,
                 jumped_last_frame):
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


class JumpTurn:
    '''
    This mechanic is to jump and turn to face a given direction.
    '''

    def __init__(self,
                 current_state,
                 jump_height,
                 turn_direction):
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
            raise AttributeError("turn direction should be 1 or -1")
        controller_input.yaw = self.turn_direction

        return controller_input





#############################################################################################

#############################################################################################


class QuickTurn:
    '''
    A powerslide turn to turn a small amount quickly.  Designed for flipping for speed.
    Might be useful for shooting as well.
    '''

    def __init__(self,
                 direction,
                 boost):
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


    def __init__(self,
                 current_state,
                 dodge_direction):
        #Dodge direction is a Vec3
        self.double_jumped = current_state.double_jumped
        self.dodge_direction = dodge_direction
        self.current_state = current_state


    def input(self):
        controller_input = SimpleControllerState()

        if self.current_state.pos.z < 40:
            #If we're too close to the ground to dodge, just keep boosting.
            controller_input.boost = 1
            return controller_input

        if not self.double_jumped:
            #If we haven't double jumped yet, dodge
            return AirDodge(self.dodge_direction, self.current_state.jumped_last_frame).input()


        else:
            #If we have double jumped, pull back to cancel the forward portion of the dodge.
            controller_input.boost = 1
            controller_input.pitch = 1
            return controller_input

#############################################################################################

#############################################################################################


class FrontDodge:
    '''
    FrontDodge is the mechanic where one dodges forward to go faster
    '''


    def __init__(self, current_state):
        #Dodge direction is 1 for right, -1 for left
        self.double_jumped = current_state.double_jumped
        self.current_state = current_state

    def input(self):
        controller_input = SimpleControllerState()
        if self.current_state.pos.z < 40 and not self.current_state.double_jumped:
            controller_input.jump = 1
        elif self.double_jumped:
            pass
        elif self.current_state.pos.z > 40:
            controller_input = AirDodge(Vec3(1,0,0), self.current_state.jumped_last_frame).input()

        return controller_input
