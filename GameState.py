from CowBotVector import *

class GameState:

    def __init__(self, packet, rigid_body_tick, field_info, my_name, my_index, my_team, teammate_indices, opponent_indices, jumped_last_frame_list):
        
        #Framerate info.  Find out how to get this automatically.
        self.fps = 60

        self.is_kickoff_pause = packet.game_info.is_kickoff_pause
        self.first_frame_of_kickoff = False
        self.kickoff_position = "Other"

        #Ball info
        self.ball = Ball(packet)

        #Info for own car
        self.me = Car(packet, rigid_body_tick, jumped_last_frame_list[my_index], my_index, my_index)

        #Info for other cars
        self.my_team = my_team
        self.teammates = []
        self.opponents = []

        for i in range(packet.num_cars):
            if i != my_index:
                if i in teammate_indices:
                    self.teammates.append(Car(packet, rigid_body_tick, jumped_last_frame_list[i], i, my_index))
                else:
                    self.opponents.append(Car(packet, rigid_body_tick, jumped_last_frame_list[i], i, my_index))

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

        self.last_touch = packet.game_ball.latest_touch
        self.hit_location = Vec3(self.last_touch.hit_location.x,
                                 self.last_touch.hit_location.y,
                                 self.last_touch.hit_location.z)

def Car(packet, rigid_body_tick, jumped_last_frame, index, my_index):
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
    if index == my_index:
        jumped_this_frame = rigid_body_tick.players[index].input.jump
    else:
        jumped_this_frame = None
        
    return CarState( pos, pitch, yaw, roll , vel, omega, demo, wheel_contact, supersonic, jumped,
                     double_jumped, boost, jumped_last_frame )


class CarState:

    def __init__(self, pos, pitch, yaw, roll, vel, omega, demo, wheel_contact, supersonic, jumped, double_jumped, boost, jumped_last_frame):
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

        self.jumped_last_frame = jumped_last_frame


    #Return a copy of the CarState object, but with given values changed.
    #This will be useful for setting target states.
    def copy_state(self, pos = None, vel = None, omega = None,
                   pitch = None, yaw = None, roll = None):
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

        return CarState(new_pos, new_pitch, new_yaw, new_roll, new_vel, new_omega, self.demo, self.wheel_contact, self.supersonic, self.jumped, self.double_jumped, self.boost, self.jumped_last_frame)



class Boostpad:

    def __init__(self, index, pos, is_active, timer):
        self.index = index
        self.pos = pos
        self.is_active = is_active
        self.timer = timer












def get_jumped_this_frame_list(rigid_body_tick):

    jumped_this_frame_list = []
    for car in rigid_body_tick.players:
        if car.input.jump:
            jumped_this_frame_list.append(True)
        else:
            jumped_this_frame_list.append(False)

    return jumped_this_frame_list
