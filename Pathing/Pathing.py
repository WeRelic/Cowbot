'''

This file will hold functions for choosing which path to take.  It will be intermediate
 between Cowculate and Maneuvers.

Arc_line_arc is the first pathing we use, but could be replaced later.

'''

from math import pi, asin, sqrt, acos

from rlbot.agents.base_agent import SimpleControllerState

from CowBotVector import Vec3
from Maneuvers import GroundTurn
from Miscellaneous import cap_magnitude

import EvilGlobals

#############################################################################################

#############################################################################################

class GroundPath:

    def __init__(self, current_state = None):
        self.length = None
        self.time_to_traverse = None
        self.waypoints = []
        self.current_state = current_state
        self.finished = False

    def input(self):
        '''
        First attempt at following a ground path.
        For now I'll assume the path includes our starting position, 
        and the correct starting direction.
        Hopefully I'll be able to keep those decisions within path planning.
        '''

        if self.piece.shape == "Waypoint":
            return self.follow_waypoint(self.current_state)
        if self.piece.shape == "Arc":
            return self.follow_arc(self.current_state)
        elif self.piece.shape == "Line":
            return self.follow_line(self.current_state)
        else:
            return self.follow_curve(self.current_state)


    def follow_arc(self, current_state):
        controller_input = SimpleControllerState()
        controller_input.steer = self.piece.direction

        try:
            center = self.center1
            radius = self.radius1
        except AttributeError:
            center = self.center
            radius = self.radius

        controller_input.throttle = 1
        if (current_state.pos - center).magnitude() > radius:
            controller_input.throttle -= ((current_state.pos - center).magnitude() - radius) / radius
        elif controller_input.steer > 0:
            controller_input.steer -= 2*(radius - (current_state.pos - center).magnitude()) / radius
        else:
            controller_input.steer += 2*(radius - (current_state.pos - center).magnitude()) / radius
        controller_input.steer = cap_magnitude(controller_input.steer)
        controller_input.throttle = cap_magnitude(controller_input.throttle)
        return controller_input



    def follow_line(self, current_state):
        controller_input = SimpleControllerState()
        controller_input = GroundTurn( current_state,
                                       current_state.copy_state(pos = self.piece.end) ).input()
        
        return controller_input



    def follow_curve(self, current_state):
        controller_input = SimpleControllerState()
        return controller_input


    def follow_waypoint(self, current_state):
        controller_input = SimpleControllerState()
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos = self.piece.waypoint)).input()

        return controller_input



#############################################################################################

#############################################################################################

class PathPiece():
    '''
    The segment of a path that we will try to follow.
    For arcs, we specify direction = 1 for CCW, direction = -1 for CW.
    '''
    def __init__(self,
                 shape = None,
                 start = None,
                 end = None,
                 start_tangent = None,
                 end_tangent = None,
                 center = None,
                 radius = None,
                 direction = None,
                 waypoint = None):
        self.shape = shape
        self.start = start
        self.end = end
        self.start_tangent = start_tangent
        self.end_tangent = end_tangent
        self.direction = direction
        self.waypoint = waypoint


#############################################################################################

#############################################################################################


