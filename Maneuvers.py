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
from math import sin, cos
from Mechanics import *



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


    def __init__(self, current_state, goal_state, old_state, fps):
        '''
        boost can be either a boolean (easy planning), or a float (advanced planning).
        Always give booleans as True or False, so that there isn't confusion over what we mean by "1".
        '''
        
        self.boost = current_state.boost
        self.current_state = current_state
        self.goal_state = goal_state
        self.old_state = old_state
        self.fps = fps

        #Default to a front flip, so that we don't accidentally veer off-course if we
        #don't get an updated flip direction.  Given in yaw relative to car coordinates.
        #+x is forward, +y is right, and angle increases clockwise.
        self.space = self.check_for_space()

        self.accel_threshold = self.set_accel_threshold()

        self.boost_threshold = self.set_boost_threshold()

        self.dodge_direction = self.set_dodge_direction()

        self.dodge_threshold = self.set_dodge_threshold()

    def input(self):
        '''
        The final call to get the controller_input for the maneuver.
        '''
        dot_epsilon = 2

        car_direction_2d = Vec3( cos(self.current_state.yaw) , sin(self.current_state.yaw) , 0)
        if Vec3(self.current_state.vel.x, self.current_state.vel.y, 0).magnitude() != 0:
            car_vel_normalized = Vec3(self.current_state.vel.x, self.current_state.vel.y, 0).normalize()

        controller_input = SimpleControllerState()
        #Speed up on the ground, then jump
        if self.current_state.wheel_contact:
            if self.current_state.vel.magnitude() <= self.boost_threshold:
                controller_input.boost = 1

            elif self.current_state.vel.magnitude() <= self.accel_threshold:
                controller_input.throttle = 1.0
           
            else:
                controller_input.jump = 1
                #TODO: Worry about boosting and turning on this frame?
                #For now I'll leave it as a pure jump; it's only a one frame difference.
        
        elif self.current_state.vel.z < 300 and abs( car_direction_2d.dot( self.dodge_direction ) - self.dodge_threshold ) < dot_epsilon:
            #If we're in the air and we've turned close enough to the angle we want, flip.
            controller_input = AirDodge(self.dodge_direction).input()
        else:
            #If we're in the air but haven't turned enough yet, keep turning.
            controller_input = AerialRotation( self.current_state, self.current_state.copy_state(rot = [self.current_state.pitch, self.current_state.yaw + atan2(-self.dodge_direction.y, self.dodge_direction.x), self.current_state.roll]), self.old_state, self.fps ).input()



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

        #Default to zero in case we don't want to use boost.
        return 0


    def set_dodge_direction(self):
        '''
        Decide which way we want to flip to maximize speed, or otherwise get to where
        we're going in a reasonable way.  Returns Vec3 relative to car coordinates.
        '''


        #Default to front flip.
        return Vec3( 1, 0, 0 )


    def set_dodge_threshold(self):
        '''
        Returns the (normalized) dot product of car orientation and velocity that we want for our second flip.
        '''


        #Default to zero for a front flip.
        return 1





