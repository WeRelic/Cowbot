'''

    This file is for the second-to-the-bottom layer of planning, just above Mechanics.py.
    Here we deal with things that are still universally referred to as "mechanics" by human
    players, but require more complicated inputs consisting of multiple sequential inputs.
    These will involve conditionals so that the same line can call the entire maneuver, e.g.,
    for a fast diagonal flip, the code here should check on which frames to jump, turn, 
    flip, and boost.

    
    Conventions:

    This file will use goal_state for where we want the car to end up.  Mechanics.py will use
    target_state.  This keeps naming clear between immediate and slightly-less-immediate plans.

    Coordinates in this file are relative to the car, until fed into a Mechanics.py class.

    Classes in this file should never use game_info, only CarState objects for our car,
    where our car was previously, and where we want our car to go.  Other game objects
    should only be called at higher levels, where we're planning what to do.  For example, hitting
    the ball should be higher up, then get a ball prediction, decide where the car needs to end up,
    then feed that decision into a class here.

'''

from rlbot.agents.base_agent import SimpleControllerState
from math import sin, cos, log, exp, sqrt
from Mechanics import *
from Miscellaneous import *


#############################################################################################

#############################################################################################

class FastDodge:
    '''
    FastFlip will be called to flip for speed whenever we need to go fast and have space
    for a flip.  Eventually decisions on whether to front or diagonal flip, how much 
    (if at all) to boost, etc. will be handled by this class.  Note: this is only for flips
    to gain speed in the direction the car is currently moving.  Half flips will be 
    handled seperately, along with turning to face the right direction for the flip.


    Before fully fleshed out, this will cause weird behavior if path planning decides
    to do a flip when a flip is a bad idea.  Keep this in mind until "check_for_space()"
    works properly.

    '''


    def __init__(self, current_state, goal_state, old_state, boost_to_use, fps):
        '''
        boost can be either a boolean (easy planning), or a float (advanced planning).
        Always give booleans as True or False, so that there isn't confusion over what we mean by "1".
        '''
        
        self.boost = current_state.boost
        self.current_state = current_state
        self.goal_state = goal_state
        self.old_state = old_state
        self.boost_to_use = boost_to_use
        self.fps = fps

        #Default to a front flip, so that we don't accidentally veer off-course if we
        #don't get an updated flip direction.  Given in yaw relative to car coordinates.
        #+x is forward, +y is right, and angle increases clockwise.
        self.space = self.check_for_space()

        self.accel_threshold = self.set_accel_threshold()

        self.boost_threshold = self.set_boost_threshold()

        #For now this is always front-right.  Later I'll optimize.
        self.dodge_direction = self.set_dodge_direction()

        self.dodge_threshold = self.set_dodge_threshold()

        self.jump_height = self.set_jump_height()

        #Always left for now, since we're always flipping front-right
        self.turn_direction = self.set_turn_direction()


    def input(self):
        '''
        The final call to get the controller_input for the maneuver.
        '''

        car_direction_2d = Vec3( cos(self.current_state.yaw) , sin(self.current_state.yaw) , 0)
        if Vec3(self.current_state.vel.x, self.current_state.vel.y, 0).magnitude() != 0:
            car_vel_normalized = Vec3(self.current_state.vel.x, self.current_state.vel.y, 0).normalize()

        controller_input = SimpleControllerState()
        #Speed up on the ground, then jump
        if self.current_state.wheel_contact:
            if self.current_state.vel.magnitude() <= self.boost_threshold:
                controller_input.boost = 1
                controller_input.throttle = 1

            elif self.current_state.vel.magnitude() <= self.accel_threshold:
                controller_input.throttle = 1.0
           
            else:
                controller_input = JumpTurn(self.current_state, self.jump_height, self.turn_direction).input()

        elif not ( abs(self.current_state.yaw - atan2(self.current_state.vel.y, self.current_state.vel.x) + (pi/4)) < 0.2 ):
            #If we're in the air but haven't turned enough yet, keep turning.
            controller_input = JumpTurn(self.current_state, self.jump_height, self.turn_direction).input()
        else:
            #If we're in the air and we've turned close enough to the angle we want, flip.
            print('dodge')
            controller_input = AirDodge(self.dodge_direction, self.current_state.jumped_last_frame).input()

        return controller_input



    def check_for_space(self):
        '''
        We want the car to be back on the ground by time it gets to the target, so that
        it doesn't miss its turn.  This function checks that we do in fact have enough
        space to get a flip in before reaching the target.  This will also tell if we 
        should stick to a front flip, or if we have room for a diagonal flip.
        '''

        #True for "all the room in the world"
        #Other values will be introduced as I figure out what I'm doing.
        return True


    def set_accel_threshold(self):
        '''
        Determines how fast we should be going before we stop accelerating without boosting 
        and jump.
        '''

        #Default to max non-boosting speed, minus arbitrarily chosen epsilon
        return 1400


    def set_boost_threshold(self):
        '''
        Determines how fast we should be going before we stop boosting.
        '''

        #Horizontal velocity
        vel_2d = Vec3(self.current_state.vel.x, self.current_state.vel.y, 0)

        #Make sure we hit the target (2000 here) with the boost we're willing to use
        #If not, use what boost we can, then dodge anyway
        #Not thoroughly tested
        return min(2000, find_final_vel(vel_2d.magnitude(), self.boost_to_use))


    def set_dodge_direction(self):
        '''
        Decide which way we want to flip to maximize speed, or otherwise get to where
        we're going in a reasonable way.  Returns Vec3 relative to car coordinates.

        TODO: Eventually intelligently decide to flip either right or left.
        '''


        #45 Degree dodge for now.
        return Vec3(1/sqrt(2), 1/sqrt(2), 0)


    def set_dodge_threshold(self):
        '''
        Returns the (normalized) dot product of car orientation and velocity that we want for our second flip.
        '''


        #Default to 1 to make sure we flip
        return 1

    def set_jump_height(self):
        '''
        Decide how high the car needs to jump to be able to complete the turn before flipping.
        '''

        return 100


    def set_turn_direction(self):
        '''
        Returns 1 for "clockwise" and 0 for "counter-clockwise"
        ''' 


        return 0




#############################################################################################

############################################################################################



class GroundTurn:

    def __init__(self, current_state, target):
        '''
        Turns on the ground towards the turn_target
        '''

        self.pos = current_state.pos
        self.vel = current_state.vel
        self.omega = current_state.omega

        self.target = target

        self.reference_angle = current_state.yaw

        pass


    def input(self):

        controller_input = SimpleControllerState()

        correction_vector = self.target.pos - self.pos

        #Rotated to the car's reference frame on the ground.
        rel_correction_vector = Vec3((correction_vector.x*cos(self.reference_angle)) + (correction_vector.y * sin(self.reference_angle)), (-(correction_vector.x*sin(self.reference_angle))) + (correction_vector.y * cos(self.reference_angle)) ,0)

        correction_angle = atan2(rel_correction_vector.y, rel_correction_vector.x)

        controller_input.throttle = 1.0
        if correction_angle > 1.25:
            controller_input.handbrake = 1
        controller_input.steer = cap_magnitude(5*correction_angle, 1)

        return controller_input
        
