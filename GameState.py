from CowBotVector import *

class GameState:

    def __init__(self, packet, rigid_body_tick, field_info, my_name, my_index, my_team, teammate_indices, opponent_indices, me_jumped_last_frame):
        
        #Framerate info.  Find out how to get this automatically.
        self.fps = 60

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

        #Game time elapsed
        self.time = packet.game_info.seconds_elapsed


        #Minimum distance from the ball to an opponent
        self.opponent_distance = 10000
        for car in self.opponents:
            if (car.pos - self.ball.pos).magnitude() < self.opponent_distance:
                self.opponent_distance = (car.pos - self.ball.pos).magnitude()
            
##################################################################################

##################################################################################


def Ball(packet, state = None):

    #Packet is used for the current ball state in game.
    #State can be used instead to get a BallState object for a prediction in the future.

    if state == None:

        #Position
        x = packet.game_ball.physics.location.x
        y = packet.game_ball.physics.location.y
        z = packet.game_ball.physics.location.z
        pos = Vec3( x , y , z )

        #Rotation
        pitch = packet.game_ball.physics.rotation.pitch
        yaw = packet.game_ball.physics.rotation.yaw
        roll = packet.game_ball.physics.rotation.roll            
        rot = [ pitch, yaw, roll ]

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
        rot = [ pitch, yaw, roll ]

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

        self.x = pos.x
        self.y = pos.y
        self.z = pos.z
        self.pos = pos

        self.pitch = rot[0]
        self.yaw = rot[1]
        self.roll = rot[2]
        self.rot = rot

        self.vx = vel.x
        self.vy = vel.y
        self.vz = vel.z
        self.vel = vel

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
                    vel = None,
                    omega = None,
                    pitch = None,
                    yaw = None,
                    roll = None):

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

        rot_check = False
        if pitch != None:
            new_pitch = pitch
            rot_check = True
        else:
            new_pitch = self.pitch

        if yaw != None:
            new_yaw = yaw
            rot_check = True
        else:
            new_yaw = self.yaw

        if roll != None:
            rot_check = True
            new_roll = roll
        else:
            new_roll = self.roll

        if rot_check:
            new_rot = [ new_pitch, new_yaw, new_roll ]
        else:
            new_rot = [ pitch, yaw, roll ]

        return BallState(pos = new_pos,
                         rot = new_rot,
                         vel = new_vel,
                         omega = new_omega)




##################################################################################

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
    
    #TODO: get this in quaternion format?
    pitch = this_car.physics.rotation.pitch
    yaw = this_car.physics.rotation.yaw
    roll = this_car.physics.rotation.roll
    
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
                     pitch = pitch,
                     yaw = yaw,
                     roll = roll,
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
                  pitch = None,
                  yaw = None,
                  roll = None,
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
        self.pitch = pitch
        self.yaw = yaw
        self.roll = roll
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
                   pitch = None,
                   yaw = None,
                   roll = None):

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

        if pitch != None:
            new_pitch = pitch
        else:
            new_pitch = self.pitch

        if yaw != None:
            new_yaw = yaw
        else:
            new_yaw = self.yaw

        if roll != None:
            new_roll = roll
        else:
            new_roll = self.roll

        return CarState(new_pos,
                        new_pitch,
                        new_yaw,
                        new_roll,
                        new_vel,
                        new_omega,
                        self.demo,
                        self.wheel_contact,
                        self.supersonic,
                        self.jumped,
                        self.double_jumped,
                        self.boost,
                        self.jumped_last_frame,
                        self.index)

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

