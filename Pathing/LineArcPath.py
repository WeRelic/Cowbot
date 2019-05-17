'''

The class for calculating and LineArc path, given the parameters.

'''

from math import pi, asin, sqrt, acos

from rlbot.agents.base_agent import SimpleControllerState

from CowBotVector import *
import EvilGlobals
from Miscellaneous import *
from Pathing.Pathing import GroundPath, PathPiece

#############################################################################################

#############################################################################################


class LineArcPath(GroundPath):

    def __init__( self,
                  start = None,
                  end = None,
                  start_tangent = None,
                  end_tangent = None,
                  radius = None,
                  current_state = None):

        '''
        radius > 0 for CW, radius < 0 for CCW
        __init__ does all the calculations for setting up the path
        '''

        self.phi = None
        self.start = start.Vec3_to_2d()
        self.end = end.Vec3_to_2d()
        self.start_tangent = start_tangent
        self.end_tangent = end_tangent
        self.radius = radius
        self.current_state = current_state

        self.center = self.end + self.end_tangent.normal_2d().scalar_multiply(radius)
        self.transition = self.center - (start_tangent).Vec3_to_2d().normal_2d().scalar_multiply(radius)

        self.piece = PathPiece(shape = "Line",
                               start = self.start,
                               end = self.transition)

        #Angle and length stuff
        center_to_end_unit_vector = (self.end - self.transition).normalize()

        #The angles we travel around the circles, respectively.
        start_normal = self.start_tangent.normal_2d()
        self.phi = 2*asin(abs(start_normal.dot(center_to_end_unit_vector)))

        #Check that the angles are going around the circle the right way.
        if (center_to_end_unit_vector.dot(self.start_tangent)) < 0:
            self.phi = abs(self.phi-(2*pi))

        #self.draw_path()


    def draw_path( self ):

        start_angle = atan2( (self.transition - self.center).y , (self.transition - self.center).x )

        #+1 for CW, -1 for CCW
        direction = - ( self.start_tangent.cross(self.center - self.transition) ).normalize().z

        point1 = [self.start.x, self.start.y, 50]
        point2 = [self.transition.x, self.transition.y, 50]

        center_list = [ self.center.x, self.center.y, self.center.z ]
        #Draw the path to make sure we got the right one.
        EvilGlobals.renderer.begin_rendering()
        EvilGlobals.renderer.draw_line_3d(point1, point2, EvilGlobals.renderer.red())
        EvilGlobals.renderer.draw_polyline_3d( EvilGlobals.draw_arc_3d(self.center, self.radius, start_angle, - direction*self.phi, 30), EvilGlobals.renderer.red())
        EvilGlobals.renderer.end_rendering()

