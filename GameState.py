import rlutilities as utils
from rlutilities.simulation import Game

from CowBotVector import *
from Miscellaneous import *

class GameState:

    def __init__(self, packet, rigid_body_tick, utils_game, field_info, my_name, my_index, my_team, teammate_indices, opponent_indices, me_jumped_last_frame):
        
        #Framerate.  Eventually phase this out for time_delta instead.
        self.fps = 120

        self.is_kickoff_pause = packet.game_info.is_kickoff_pause
        self.first_frame_of_kickoff = False
        self.kickoff_position = "Other"

        #Ball info
        self.ball = Ball(packet)

        #Info for own car
        self.me = Car(packet,
                      rigid_body_tick,
                      me_jumped_last_frame,
                      my_index,
                      my_index)
        self.my_index = my_index

        #Info for other cars
        self.my_team = my_team
        if self.my_team == 0:
            self.team_sign = 1
        else:
            self.team_sign = -1
        self.teammates = []
        self.opponents = []

        for i in range(packet.num_cars):
            if i != my_index:
                if i in teammate_indices:
                    self.teammates.append(Car(packet, rigid_body_tick, None, i, my_index))
                else:
                    self.opponents.append(Car(packet, rigid_body_tick, None, i, my_index))

        #Boost info
        self.big_boosts = []
        self.boosts = []
        for i in range(field_info.num_boosts):
            pad = field_info.boost_pads[i]
            pad_pos = Vec3(pad.location.x, pad.location.y, pad.location.z)
            self.boosts.append(Boostpad(i, pad_pos, packet.game_boosts[i].is_active, packet.game_boosts[i].timer))
            if pad.is_full_boost:
                self.big_boosts.append(Boostpad(i, pad_pos, packet.game_boosts[i].is_active, packet.game_boosts[i].timer))

        #Other Game info
        self.game_time = packet.game_info.seconds_elapsed
        if utils_game != None:
            self.utils_game = utils_game
            self.dt = utils_game.time_delta
            self.utils_game.read_game_information(packet,
                                                  rigid_body_tick,
                                                  field_info)
        else:
            self.dt = 1/120
            self.utils_game = None

        #Minimum distance from the ball to an opponent
        self.opponent_distance = 10000
        for car in self.opponents:
            if (car.pos - self.ball.pos).magnitude() < self.opponent_distance:
                self.opponent_distance = (car.pos - self.ball.pos).magnitude()
            


##################################################################################
#Orientation
##################################################################################

class Orientation:

    '''
    This is an orientation matrix with columns Front, Left, Up.
    This will be the working object for a car or ball orientation.
    '''


    def __init__( self ,
                  pitch = None,
                  yaw = None,
                  roll = None,
                  pyr = None,
                  front = None,
                  left = None,
                  up = None
    ):

        if pitch != None and yaw != None and roll != None:
            pyr = [ pitch, yaw, roll ]

        if pyr != None:
            self.matrix = pyr_to_matrix(pyr)

        if front != None and left != None and up != None:
            self.matrix = [ front, left, up ]

        self.front = self.matrix[0]
        self.left = self.matrix[1]
        self.up = self.matrix[2]

        if pyr != None:
            self.pitch = pyr[0]
            self.yaw = pyr[1]
            self.roll = pyr[2]
        else:
            self.yaw = atan2( self.front.y , self.front.x )
            self.pitch = atan2( self.front.z , sqrt(self.left.z**2 + self.up.z**2) )
            self.roll = atan2( self.left.z , self.up.z )


##################################################################################
#Ball
##################################################################################



def Ball(packet, state = None):

    #Packet is used for the current ball state in game.
    #State can be used instead to get a BallState object for a prediction in the future.

    if state == None:

        #Position
        x = packet.game_ball.physics.location.x
        y = packet.game_ball.physics.location.y
        z = packet.game_ball.physics.location.z
        pos = Vec3( x, y, z )

        #Rotation
        pitch = packet.game_ball.physics.rotation.pitch
        yaw = packet.game_ball.physics.rotation.yaw
        roll = packet.game_ball.physics.rotation.roll            
        rot = Orientation( pitch = pitch,
                           yaw = yaw,
                           roll = roll )

        #Velocity
        vx = packet.game_ball.physics.velocity.x
        vy = packet.game_ball.physics.velocity.y
        vz = packet.game_ball.physics.velocity.z
        vel = Vec3( vx, vy, vz )

        #Angular velocity
        omegax = packet.game_ball.physics.angular_velocity.x
        omegay = packet.game_ball.physics.angular_velocity.y
        omegaz = packet.game_ball.physics.angular_velocity.z
        omega = Vec3( omegax, omegay, omegaz )

        #Miscellaneous
        last_touch = packet.game_ball.latest_touch
        hit_location = Vec3(last_touch.hit_location.x,
                                 last_touch.hit_location.y,
                                 last_touch.hit_location.z)

    else:
        #Position
        x = state.x
        y = state.y
        z = state.z
        pos = Vec3(x, y, z)

        #Velocity
        velx = state.velx
        vely = state.vely
        velz = state.velz
        vel = Vec3(vx, vy, vz)

        #Rotation
        pitch = state.pitch
        yaw = state.yaw
        roll = state.roll
        rot = Orientation( pitch = pitch,
                           yaw = yaw,
                           roll = roll )

        #Angular velocity
        omegax = state.omegax
        omegay = state.omegay
        omegaz = state.omegaz
        omega = Vec3(omegax, omegay, omegaz)


    return BallState(pos = pos,
                     rot = rot,
                     vel = vel,
                     omega = omega,
                     last_touch = last_touch,
                     hit_location = hit_location)


class BallState:

    def __init__( self,
                  pos = None,
                  rot = None,
                  vel = None,
                  omega = None,
                  last_touch = None,
                  hit_location = None):

        self.pos = None
        self.rot = None
        self.vel = None
        self.omega = None
        
        if pos != None:
            self.x = pos.x
            self.y = pos.y
            self.z = pos.z
            self.pos = pos

        if rot != None:
            self.rot = rot

        if vel != None:
            self.vx = vel.x
            self.vy = vel.y
            self.vz = vel.z
            self.vel = vel

        if omega != None:
            self.omegax = omega.x
            self.omegay = omega.y
            self.omegaz = omega.z
            self.omega = omega

        self.last_touch = last_touch
        self.hit_location = hit_location


    #Return a copy of the BallState object, but with given values changed.
    #This will be useful for setting target states.
    def copy_state( self,
                    pos = None,
                    rot = None,
                    vel = None,
                    omega = None):

        if pos != None:
            new_pos = pos
        else:
            new_pos = self.pos

        if vel != None:
            new_vel = vel
        else:
            new_vel = self.vel

        if omega != None:
            new_omega = omega
        else:
            new_omega = self.omega

        if rot != None:
            new_rot = rot
        else:
            new_rot = self.rot

        return BallState(pos = new_pos,
                         rot = new_rot,
                         vel = new_vel,
                         omega = new_omega)




##################################################################################
#Car
##################################################################################

def Car(packet,
        rigid_body_tick,
        jumped_last_frame,
        index,
        my_index):

    '''
    Gets the game info for a given car, and returns the values.  Should be fed into a CarState object.
    '''

    this_car = packet.game_cars[index]
    pos = Vec3( this_car.physics.location.x,
                this_car.physics.location.y,
                this_car.physics.location.z )
    
    pitch = this_car.physics.rotation.pitch
    yaw = this_car.physics.rotation.yaw
    roll = this_car.physics.rotation.roll
    rot = Orientation( pitch = pitch,
                            yaw = yaw,
                            roll = roll )
    
    vel = Vec3( this_car.physics.velocity.x,
                this_car.physics.velocity.y,
                this_car.physics.velocity.z )
    
    omega = Vec3( this_car.physics.angular_velocity.x,
                  this_car.physics.angular_velocity.y,
                  this_car.physics.angular_velocity.z )

    demo = this_car.is_demolished
    wheel_contact = this_car.has_wheel_contact
    supersonic = this_car.is_super_sonic
    jumped = this_car.jumped
    double_jumped = this_car.double_jumped
    boost = this_car.boost
        
    return CarState( pos = pos,
                     rot = rot,
                     vel = vel,
                     omega = omega,
                     demo = demo,
                     wheel_contact = wheel_contact,
                     supersonic = supersonic,
                     jumped = jumped,
                     double_jumped = double_jumped,
                     boost = boost,
                     jumped_last_frame = jumped_last_frame,
                     index = index )


class CarState:

    def __init__( self,
                  pos = None,
                  rot = None,
                  vel = None,
                  omega = None,
                  demo = None,
                  wheel_contact = None,
                  supersonic = None,
                  jumped = None,
                  double_jumped = None,
                  boost = None,
                  jumped_last_frame = None,
                  index = None ):

        self.pos = pos
        self.rot = rot
        self.vel = vel
        self.omega = omega

        self.demo = demo
        self.wheel_contact = wheel_contact
        self.supersonic = supersonic
        self.jumped = jumped
        self.double_jumped = double_jumped
        self.boost = boost
        self.index = index

        self.jumped_last_frame = jumped_last_frame


    #Return a copy of the CarState object, but with given values changed.
    #This will be useful for setting target states.
    def copy_state(self,
                   pos = None,
                   vel = None,
                   omega = None,
                   rot = None,
                   boost = None):

        if pos != None:
            new_pos = pos
        else:
            new_pos = self.pos

        if vel != None:
            new_vel = vel
        else:
            new_vel = self.vel

        if omega != None:
            new_omega = omega
        else:
            new_omega = self.omega

        if rot != None:
            new_rot = rot
        else:
            new_rot = self.rot

        if boost != None:
            new_boost = boost
        else:
            new_boost = self.boost
            

        return CarState(pos = new_pos,
                        rot = new_rot,
                        vel = new_vel,
                        omega = new_omega,
                        demo = self.demo,
                        wheel_contact = self.wheel_contact,
                        supersonic = self.supersonic,
                        jumped = self.jumped,
                        double_jumped = self.double_jumped,
                        boost = new_boost,
                        jumped_last_frame = self.jumped_last_frame,
                        index = self.index)

##################################################################################

##################################################################################

class Boostpad:

    def __init__(self, index, pos, is_active, timer):
        self.index = index
        self.pos = pos
        self.is_active = is_active
        self.timer = timer


##################################################################################

##################################################################################

