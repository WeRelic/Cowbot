'''

The class for calculating and ArcLineArc path, given the parameters.

'''

from math import pi, asin, sqrt, acos, atan2, ceil, cos, sin

from rlbot.agents.base_agent import SimpleControllerState
from rlutilities.linear_algebra import vec3, cross, normalize
from rlutilities.simulation import Curve, ControlPoint

from Conversions import Vec3_to_vec3, vec3_to_Vec3
from CowBotVector import Vec3
import EvilGlobals
from Miscellaneous import cap_magnitude, min_radius
from Pathing.Pathing import GroundPath, PathPiece
from Pathing.ArcPath import ArcPath
from Pathing.LineArcPath import LineArcPath


#############################################################################################

#############################################################################################

class ArcLineArc(GroundPath):

    def __init__(self,
                 start = None,
                 end = None,
                 start_tangent = None,
                 end_tangent = None,
                 radius1 = None,
                 radius2 = None,
                 current_state = None,
                 team_sign = None):
        '''
        Postiive radius means Clockwise
        Negative radius means Counter-clockwise
        Zero radius means no arc: the endpoint is on the line segment.
        __init__ does all the calculations for setting up the path
        '''

        #Obsolete, probably
        self.path_following_state = "First Arc"

        #Make sure tangents aren't the zero vector
        if start_tangent.to_2d().magnitude() == 0:
            print(ValueError("start_tangent can't be length zero"))
        if end_tangent.to_2d().magnitude() == 0:
            print(ValueError("end_tangent can't be length zero"))

        self.current_state = current_state
        self.start = start.to_2d()
        self.end = end.to_2d()
        self.start_tangent = start_tangent.to_2d().normalize()
        self.end_tangent = end_tangent.to_2d().normalize()
        self.radius1 = radius1
        self.radius2 = radius2
        self.start_normal = self.start_tangent.normal_2d().normalize()
        self.end_normal = self.end_tangent.normal_2d().normalize()

        #Find the centers of the circles
        self.center1 = self.start + self.start_normal.scalar_multiply(self.radius1)
        self.center2 = self.end + self.end_normal.scalar_multiply(self.radius2)

        self.transition1 = None
        self.transition2 = None
        self.length = None
        self.is_valid = None

    
        #Signs of the radii, and the characteristic sign for the path
        #Negative if both circles are the same orientation
        #Positive if one of them is clockwise and the other is counterclockwise
        self.sgn1 = self.radius1 / abs(self.radius1)
        self.sgn2 = self.radius2 / abs(self.radius2)

        sign = - (self.sgn1 * self.sgn2)


        #Distance between the centers of the circles.
        center_separation = (self.center1 - self.center2).magnitude()

        #Find the "net radius" of the geometry.
        #This is used for checking validity, and finding transition points.
        net_radius = abs(self.radius1) + sign*abs(self.radius2)

        #Check that the path is valid
        if (self.center1 - self.center2).magnitude() < max(radius1, radius2):
            self.is_valid = False
            #print("A circle center is contained in the other circle.")
        elif ((net_radius)**2) / ((center_separation)**2) >= 0.97:
            self.is_valid = False
            #print("ArcLineArc Path is not valid")
        else:

            #Find the offsets of the transition points from the centers
            e1 = (self.center2 - self.center1).normalize()
            e2 = e1.normal_2d().scalar_multiply(-self.sgn1)
            component1 = e1.scalar_multiply(net_radius / center_separation)
            component2 = e2.scalar_multiply(sqrt(1 - (net_radius / center_separation)**2))

            #Find transition points
            self.transition1 = self.center1 + (component1 + component2).scalar_multiply(abs(radius1))
            self.transition2 = self.center2 - (component1 + component2).scalar_multiply(sign * abs(radius2))

            #Find the total length of the path.
            self.length_circle1, self.length_line, self.length_circle2 = self.find_lengths()
            self.length = self.length_circle1 + self.length_line + self.length_circle2

            #The first segment of the path
            if self.radius1 < 0:
                direction = 1
            else:
                direction = -1
            self.piece = PathPiece(shape = "Arc",
                                   start = self.start,
                                   end = self.transition1,
                                   start_tangent = self.start_tangent,
                                   end_tangent = (self.transition1 - self.start).normalize(),
                                   direction = direction)

            self.to_Curve(team_sign)
            if self.path_is_out_of_bounds():
                self.is_valid = False
            else:
                self.is_valid = True


                
            #self.draw_path()


        #############################################################################################

    def find_lengths(self):
        '''
        Find the length of an ArcLineArc path.  Returns the lengths of the segments
        in the order they're traversed.
        '''
        
        length_line = (self.transition2 - self.transition1).magnitude()
        
        #All vectors normalized here
        start_normal = (self.start - self.center1).normalize()
        end_normal = (self.end - self.center2).normalize()
        direction1 = (self.transition1 - self.start).normalize()
        direction2 = (self.end - self.transition2).normalize()
        
        #The angles we travel around the circles, respectively.
        self.phi1 = 2*asin(abs(start_normal.dot(direction1)))
        self.phi2 = 2*asin(abs(end_normal.dot(direction2)))
        
        #Check that the angles are going around the circle the right way.
        if (direction1.dot(self.start_tangent)) < 0:
            self.phi1 = abs(self.phi1-(2*pi))
        if (direction2.dot(self.end_tangent)) < 0:
            self.phi2 = abs(self.phi2-(2*pi))

        length_circle1 = self.phi1 * abs(self.radius1)
        length_circle2 = self.phi2 * abs(self.radius2)

        return length_circle1, length_line, length_circle2


    #############################################################################################

    def draw_path( self ):
        point1 = [ self.transition1.x , self.transition1.y , 50 ]
        point2 = [ self.transition2.x, self.transition2.y, 50 ]

        direction1 = self.start - self.center1
        angle1 = atan2( direction1.y , direction1.x )
        direction2 = self.transition2 - self.center2
        angle2 = atan2( direction2.y , direction2.x )

        #Draw the path to make sure we got the right one.
        EvilGlobals.renderer.begin_rendering()
        EvilGlobals.renderer.draw_line_3d(point1, point2, EvilGlobals.renderer.red())
        EvilGlobals.renderer.draw_polyline_3d( EvilGlobals.draw_arc_3d(self.center1, abs(self.radius1), angle1, - self.sgn1*self.phi1, 30), EvilGlobals.renderer.red())
        EvilGlobals.renderer.draw_polyline_3d( EvilGlobals.draw_arc_3d(self.center2, abs(self.radius2), angle2, - self.sgn2*self.phi2, 30), EvilGlobals.renderer.red() )
        EvilGlobals.renderer.end_rendering()

    #############################################################################################

    def update_path(self, current_state):

        if self.path_following_state == "First Arc":
            path = ArcLineArc(start = self.start,
                              end = self.end,
                              start_tangent = self.start_tangent,
                              end_tangent = self.end_tangent,
                              radius1 = self.radius1,
                              radius2 = self.radius2,
                              current_state = current_state)

            if (self.current_state.pos - path.transition1).magnitude() < 150:
                path.path_following_state = "Switch to Line"
            else:
                path.path_following_state = "First Arc"
                
                ##############################
                
        elif self.path_following_state == "Switch to Line":
            #If we're on the first frame of the line segment,
            #match everything up accoringly, then go over to normal "Line" following
            path = LineArcPath(start = current_state.pos,
                               start_tangent = current_state.rot.front,
                               end = self.end,
                               end_tangent = self.end_tangent,
                               radius = self.radius2,
                               current_state = current_state)
            path.path_following_state = "Line"

        return path


    #############################################################################################
        
    def to_Curve(self, team_sign):
        '''
        Converts the path to an RLU Curve object that can be followed
        '''

        control_points = []

        #The first arc
        direction1 = self.start - self.center1
        starting_angle = atan2( direction1.y, direction1.x )
        steps = ceil(30*(self.phi1 / (2*pi)))
        delta = - self.sgn1 * self.phi1 / steps
        center1 = Vec3_to_vec3(self.center1, team_sign)

        for i in range(1, steps-2):
            angle = starting_angle + delta*i
            next_point = center1 + abs(self.radius1)*vec3(cos(angle), sin(angle),0)
            normal = normalize(next_point - center1)

            next_control_point = ControlPoint()
            next_control_point.p = next_point
            next_control_point.t = cross(normal)
            next_control_point.n = normal
            control_points.append(next_control_point)

        #The line
        steps = max(10, ceil(self.length_line / 300))
        delta = self.length_line / steps
        tangent = Vec3_to_vec3((self.transition2 - self.transition1).normalize(), team_sign)
        normal = cross(tangent)

        for i in range(0, steps + 1):
            next_point = Vec3_to_vec3(self.transition1, team_sign) + delta*tangent*i

            next_control_point = ControlPoint()
            next_control_point.p = next_point
            next_control_point.t = tangent
            next_control_point.n = normal
            control_points.append(next_control_point)

        #The second arc
        direction2 = self.transition2 - self.center2
        starting_angle = atan2( direction2.y, direction2.x )
        steps = ceil(30*(self.phi2 / (2*pi)))
        delta = - self.sgn2 * self.phi2 / steps
        center2 = Vec3_to_vec3(self.center2, team_sign)

        for i in range(1, steps + 1):
            angle = starting_angle + delta*i
            next_point = center2 + abs(self.radius2)*vec3(cos(angle), sin(angle),0)
            normal = normalize(next_point - center2)

            next_control_point = ControlPoint()
            next_control_point.p = next_point
            next_control_point.t = cross(normal)
            next_control_point.n = normal
            control_points.append(next_control_point)

        curve = Curve(control_points)

        self.RLU_curve = curve
        self.discretized_path = [ vec3_to_Vec3(point.p, team_sign) for point in control_points ]




