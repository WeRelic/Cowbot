'''

This file will hold functions for choosing which path to take.  It will be intermediate
 between Cowculate and Maneuvers.

Arc_line_arc is the first pathing we use, but could be replaced later.

This entire file might be obsolete because RLU does it better

'''

from math import pi, asin, sqrt, acos, atan2

from rlbot.agents.base_agent import SimpleControllerState

from CowBotVector import Vec3
from Maneuvers import GroundTurn
from Mechanics import FrontDodge
from Miscellaneous import angles_are_close, cap_magnitude, min_radius, is_drivable_point

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

        #A list of vec3 for the path
        self.discretized_path = None

        #The RLU Curve object for the path follower
        self.RLU_curve = None

    def input(self):
        '''
        Following a ground path.
        The path includes the correct starting position and direction.
        Keep track of those in path planning or this will not work.
        '''
        #Once we know the type of path, follow it
        #I think this is obsolete thanks to RLU path following
        if self.piece.shape == "Waypoint":
            return self.follow_waypoint()
        elif self.piece.shape == "Arc":
            return self.follow_arc()
        elif self.piece.shape == "Line":
            return self.follow_line()
        else:
            return self.follow_curve()

    #############################################################################################

    def follow_arc(self):
        #Also obsolete thanks to RLU
        controller_input = SimpleControllerState()

        try:
            center = self.center1
            radius = abs(self.radius1)
        except AttributeError:
            center = self.center
            radius = abs(self.radius)
        

        controller_input.steer = self.piece.direction * (min_radius(self.current_state.vel.magnitude()) / radius)

        controller_input.throttle = 1
        #If we're inside the circle, let off of steering to turn less sharply
        #TODO: Change this to a multiple so that we don't need a left/right split
        controller_input.steer *= 1.1*(self.current_state.pos - center).magnitude() / radius
        controller_input.steer = cap_magnitude(controller_input.steer)
        controller_input.throttle = cap_magnitude(controller_input.throttle)
        return controller_input

    #############################################################################################

    def follow_line(self):
        controller_input = SimpleControllerState()
        controller_input = GroundTurn( self.current_state,
                                       self.current_state.copy_state(pos = self.piece.end) ).input()
        
        return controller_input

    #############################################################################################


    def follow_curve(self):
        controller_input = SimpleControllerState()
        return controller_input

    #############################################################################################

    def follow_waypoint(self):
        controller_input = SimpleControllerState()
        controller_input = GroundTurn(self.current_state,
                                      self.current_state.copy_state(pos = self.piece.waypoint)).input()
        waypoint_distance = (self.current_state.pos - self.waypoints[0]).magnitude()
        wobble = Vec3(self.current_state.omega.x, self.current_state.omega.y, 0).magnitude()
        epsilon = 0.3
        angle_to_waypoint = atan2((self.waypoints[0] - self.current_state.pos).y , (self.waypoints[0] - self.current_state.pos).x)
        facing_waypoint = angles_are_close(angle_to_waypoint, self.current_state.rot.yaw, pi/12)
        good_direction = facing_waypoint and abs(self.current_state.omega.z) < epsilon
        speed = self.current_state.vel.magnitude()


        if len(self.waypoints) > 1:
            angle_to_next_waypoint = atan2((self.waypoints[1] - self.current_state.pos).y , (self.waypoints[0] - self.current_state.pos).x)
            facing_next_waypoint = angles_are_close(angle_to_next_waypoint, self.current_state.rot.yaw, pi/6)
            good_direction = facing_waypoint and abs(self.current_state.omega.z) < epsilon and facing_next_waypoint

        if waypoint_distance < 400*speed / 1410:
            #If we're close, start turning, and we'll hit the point through the turn.
            #TODO: Figure out a good path through waypoints, taking future points into account.
            self.waypoints = self.waypoints[1:]
            if len(self.waypoints) == 0:
                self.finished = True

        elif len(self.waypoints) > 0 and 1000 < speed < 2250 and waypoint_distance > 1200*(speed+500) / 1410 and wobble < epsilon and good_direction:
            #If we're decently far away from the next point, front flip for speed.
            controller_input = FrontDodge(self.current_state).input()

        elif facing_waypoint and self.current_state.wheel_contact and speed < 2300 and self.current_state.boost > 40:
            #If we're not supersonic and pointed the right way, boost to speed up
            controller_input.boost = 1
            
        return controller_input

    #############################################################################################

    def path_is_out_of_bounds( self ):
        '''
        Returns a Boolean for whether or not the given goes outside the stadium.
        For now, we count walls and curves as out of bounds.
        '''

        for point in self.discretized_path:
            if is_drivable_point(point):
                continue
            else:
                return True
        return False


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


