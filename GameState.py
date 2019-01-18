from CowBotVector import *

class GameState:

    def __init__(self, packet, field_info, my_name, my_index, my_team, teammate_indices, opponent_indices):

        #Framerate info.  Find out how to get this automatically.
        self.fps = 60



        self.is_kickoff_pause = packet.game_info.is_kickoff_pause
        self.first_frame_of_kickoff = False
        self.kickoff_position = "Other"

        #Ball info
        self.ball = Ball(packet)

        #Info for own car
        self.me = Car(packet, my_index)

        #Info for other cars
        self.teammates = []
        self.opponents = []

        for i in range(packet.num_cars):
            if i != my_index:
                if i in teammate_indices:
                    self.teammates.append(Car(packet, i))
                else:
                    self.opponents.append(Car(packet,i))

        #Boost info
        self.big_boosts = []
        self.small_boosts = []
        for i in range(field_info.num_boosts):
            pad = field_info.boost_pads[i]
            if pad.is_full_boost:
                self.big_boosts.append(Boostpad(i, pad.location, packet.game_boosts[i].is_active, packet.game_boosts[i].timer))

        #Game time elapsed
        self.time = packet.game_info.seconds_elapsed

class Ball:

    def __init__(self, packet):
        self.pos = Vec3( packet.game_ball.physics.location.x,
                         packet.game_ball.physics.location.y,
                         packet.game_ball.physics.location.z )

        #TODO: get this in quaternion format?
        #Note: ball rotation is only useful in snow day
        self.rot = [ packet.game_ball.physics.rotation.pitch,
                     packet.game_ball.physics.rotation.yaw,
                     packet.game_ball.physics.rotation.roll ]
        
        self.vel = Vec3( packet.game_ball.physics.velocity.x,
                         packet.game_ball.physics.velocity.y,
                         packet.game_ball.physics.velocity.z )
        
        self.omega = Vec3( packet.game_ball.physics.angular_velocity.x,
                           packet.game_ball.physics.angular_velocity.y,
                           packet.game_ball.physics.angular_velocity.z )




def Car(packet,index):
    '''
    Gets the game info for a given car, and returns the values.  Should be fed into a CarState object.
    '''

    this_car = packet.game_cars[index]
    pos = Vec3( this_car.physics.location.x,
                this_car.physics.location.y,
                this_car.physics.location.z )
    
    #TODO: get this in quaternion format?
    rot = [ this_car.physics.rotation.pitch,
            this_car.physics.rotation.yaw,
            this_car.physics.rotation.roll ]
    
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

    return CarState(pos, rot, vel, omega, demo, wheel_contact, supersonic, jumped, double_jumped, boost)


class CarState:

    def __init__(self, pos, rot, vel, omega, demo, wheel_contact, supersonic, jumped, double_jumped, boost):
        self.pos = pos
        self.rot = rot
        self.vel = vel
        self.omega = omega

        if self.rot != None:
            self.pitch = rot[0]
            self.yaw = rot[1]
            self.roll = rot[2]
 
        self.demo = demo
        self.wheel_contact = wheel_contact
        self.supersonic = supersonic
        self.jumped = jumped
        self.double_jumped = double_jumped
        self.boost = boost


class Boostpad:

    def __init__(self, index, pos, is_active, timer):
        self.index = index
        self.pos = pos
        self.is_active = is_active
        self.timer = timer


