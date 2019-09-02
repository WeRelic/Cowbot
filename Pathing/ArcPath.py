'''

The class for calculating an Arc path, given the parameters.

'''

from math import pi, asin, sqrt, acos, atan2, ceil, cos, sin

from rlbot.agents.base_agent import SimpleControllerState
from rlutilities.linear_algebra import vec3
from rlutilities.simulation import Curve

from Conversions import Vec3_to_vec3
from CowBotVector import Vec3
from Pathing.Pathing import GroundPath, PathPiece

import EvilGlobals


#############################################################################################

#############################################################################################


class ArcPath(GroundPath):

    def __init__( self,
                  start = None,
                  start_tangent = None,
                  end = None,
                  end_tangent = None,
                  radius = None,
                  current_state = None):

        '''
        radius > 0 for CW, radius < 0 for CCW
        __init__ does all the calculations for setting up the path
        '''

        self.phi = None
        self.start = start.to_2d()
        self.end = end.to_2d()
        self.start_tangent = start_tangent.to_2d().normalize()
        self.end_tangent = end_tangent.to_2d().normalize()
        self.radius = radius
        self.current_state = current_state

        self.center = self.end + self.end_tangent.normal_2d().scalar_multiply(radius)

        #+1 for CCW, -1 for CW
        if ( self.start_tangent.cross(self.center - self.start) ).z > 0:
            direction = 1
        else:
            direction = -1

        self.piece = PathPiece(shape = "Arc",
                               start = self.start,
                               end = self.end,
                               direction = direction,
                               center = self.center)

        #Angle and length stuff
        center_to_end_unit_vector = (self.end - self.start).normalize()

        #The angles we travel around the circle.
        start_normal = self.start_tangent.normal_2d()
        self.phi = 2*asin(abs(start_normal.dot(center_to_end_unit_vector)))

        #Check that the angles are going around the circle the right way.
        if (center_to_end_unit_vector.dot(self.start_tangent)) < 0:
            self.phi = abs(self.phi-(2*pi))

        self.length = self.phi * abs(self.radius)

        self.draw_path()


    def draw_path( self ):

        starting_point = self.start - self.center

        start_angle = atan2( starting_point.y , starting_point.x )

        #+1 for CW, -1 for CCW
        direction = - ( self.start_tangent.cross(self.center - self.start) ).normalize().z

        center_list = [ self.center.x, self.center.y, self.center.z ]
        #Draw the path to make sure we got the right one.
        EvilGlobals.renderer.begin_rendering()
        EvilGlobals.renderer.draw_polyline_3d( EvilGlobals.draw_arc_3d(self.center, self.radius, start_angle, - direction*self.phi, 60), EvilGlobals.renderer.red())
        EvilGlobals.renderer.end_rendering()



    def update_path(self, current_state):
        path = ArcPath(start = self.start,
                       start_tangent = self.start_tangent,
                       end = self.end,
                       end_tangent = self.end_tangent,
                       radius = self.radius,
                       current_state = current_state)
            
        if (self.current_state.pos - path.end).magnitude() < 150:
            path = None

        return path


    #############################################################################################
        
    def to_Curve(self, team_sign):

        control_points = []

        steps = ceil((30*self.phi) / (2*pi))
        delta = self.phi / steps
        center = Vec3_to_vec3(self.center, team_sign)
     
        for i in range(steps):
            angle = self.phi + delta*i
            next_point = center + self.radius*vec3(cos(angle), sin(angle),0)
            normal = normalize(next_point - center)

            next_control_point = ControlPoint()
            next_control_point.p = next_point
            next_control_point.t = cross(normal)
            next_control_point.n = normal
            control_points.append(next_control_point)


        curve = Curve(control_points)
        return curve
       



   
