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


    def __init__(self, current_state, goal_state, old_state, boost_to_use = 30,
                 direction = 1, oversteer = True, boost_threshold = None, fps = 120):
        '''
        direction = 1 for right, direction = -1 for left.
        '''
        
        self.boost = current_state.boost
        self.current_state = current_state
        self.goal_state = goal_state
        self.old_state = old_state
        self.boost_to_use = boost_to_use
        self.direction = direction
        self.fps = fps
        self.oversteer = oversteer
        
        
        #Default to a front flip, so that we don't accidentally veer off-course if we
        #don't get an updated flip direction.  Given in yaw relative to car coordinates.
        #+x is forward, +y is right, and angle increases clockwise.
        self.space = self.check_for_space()
        if boost_threshold == None:
            self.boost_threshold = self.set_boost_threshold()
        else:
            self.boost_threshold = boost_threshold
        self.accel_threshold = self.set_accel_threshold()

        self.dodge_direction = self.set_dodge_direction(self.direction)
        self.dodge_threshold = self.set_dodge_threshold()
        self.jump_height = self.set_jump_height()

        
        
        #questionable if we're still turning
        #but it should be okay if we're driving straight.
        if self.dodge_direction.y > 0:
            self.dodge_angle = atan2((goal_state.pos - current_state.pos).y,
                                     (goal_state.pos - current_state.pos).x) - (pi/12)
        else:
            self.dodge_angle = atan2((goal_state.pos - current_state.pos).y,
                                     (goal_state.pos - current_state.pos).x) + (pi/12)


        self.movement_angle = atan2(current_state.vel.y, current_state.vel.x)

        #Currently set to opposite of the dodge direction.  This should be good for general use, up to oversteer.
        #Eventually wrap this into set_dodge_direction?
        self.turn_direction = self.set_turn_direction()


    def input(self):
        '''
        The final call to get the controller_input for the maneuver.
        '''
        
        controller_input = SimpleControllerState()
        #Speed up on the ground, turn as needed, then jump
        if self.current_state.wheel_contact:
            #Boost if we're slower than boost_threshold.
            #Also turn towards the goal_state if we're not facing it.
            if self.current_state.vel.magnitude() <= self.boost_threshold:
                #controller_input = GroundTurn(self.current_state,
                                              #self.current_state.copy_state(pos=Vec3(0,0,0))).input()
                controller_input.boost = 1
            #Accelerate if we're below accel_threshold
            elif self.current_state.vel.magnitude() <= self.accel_threshold:
                controller_input.throttle = 1
            elif ( abs(self.current_state.yaw - self.dodge_angle) < 0.2 ):
                #Once we turn partway, jump and turn the rest of the way
                if self.dodge_angle - self.current_state.yaw > 0:
                    controller_input = JumpTurn(self.current_state, self.jump_height, 1).input()
                else:
                    controller_input = JumpTurn(self.current_state, self.jump_height, 0).input()

            else:
                #Once we're up to speed, and not turned enough, turn away from the dodge
                controller_input = QuickTurn(self.turn_direction, 1).input()


        elif self.current_state.double_jumped:
            #Once we dodge, rotate back around to land properly
            controller_input.yaw = cap_magnitude(self.movement_angle - self.current_state.yaw, 1)

        elif not ( abs(self.current_state.yaw - self.dodge_angle) < 0.1 ):
            #Turn a bit more while in the air before dodging
            controller_input = JumpTurn(self.current_state, self.jump_height, self.turn_direction).input()
            controller_input.jump = 0

        elif self.current_state.pos.z > 50:
            #Once we're finally turned enough, dodge
            controller_input = AirDodge(self.dodge_direction, self.current_state.jumped_last_frame).input()

        controller_input.throttle = 1
        return controller_input

###############################################

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


    def set_boost_threshold(self):
        '''
        Determines how fast we should be going before we stop boosting.
        '''

        #Horizontal velocity
        #vel_2d = Vec3(self.current_state.vel.x, self.current_state.vel.y, 0)

        #Make sure we hit the target (2000 here) with the boost we're willing to use
        #If not, use what boost we can, then dodge anyway
        #Not thoroughly tested
        return 1200
        #return min(2000, find_final_vel(vel_2d.magnitude(), self.boost_to_use))

    def set_accel_threshold(self):
        '''
        Determines how fast we should be going before we stop accelerating without boosting 
        and jump.
        '''

        #Default to max non-boosting speed, minus arbitrarily chosen epsilon
        return min(1000, self.boost_threshold)


    def set_dodge_direction(self, direction):
        '''
        Decide which way we want to flip to maximize speed, or otherwise get to where
        we're going in a reasonable way.  Returns Vec3 relative to car coordinates.

        TODO: Eventually intelligently decide to flip either right or left.
        '''


        #45 Degree dodge for now.
        return Vec3(1/sqrt(2), direction * (1/sqrt(2)), 0)


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

        return 0


    def set_turn_direction(self):
        '''
        Returns 1 for "clockwise" and 0 for "counter-clockwise"
        We currently need 0 and 1 here for parity on the minus sign elsewhere.
        '''

        if (self.dodge_angle - self.current_state.yaw) >=0:
            return 1
        else:
            return 0




#############################################################################################

############################################################################################



class GroundTurn:

    def __init__(self, current_state, target_state):
        '''
        Turns on the ground towards the turn_target
        '''

        self.pos = current_state.pos
        self.vel = current_state.vel
        self.omega = current_state.omega

        self.target_state = target_state

        self.reference_angle = current_state.yaw

        pass


    def input(self):

        controller_input = SimpleControllerState()

        correction_vector = self.target_state.pos - self.pos

        #Rotated to the car's reference frame on the ground.
        rel_correction_vector = Vec3((correction_vector.x*cos(self.reference_angle)) + (correction_vector.y * sin(self.reference_angle)), (-(correction_vector.x*sin(self.reference_angle))) + (correction_vector.y * cos(self.reference_angle)), 0)

        correction_angle = atan2(rel_correction_vector.y, rel_correction_vector.x)

        controller_input.throttle = 1.0
        if correction_angle > 1.25:
            controller_input.handbrake = 1
        controller_input.steer = cap_magnitude(5*correction_angle, 1)

        return controller_input
        
