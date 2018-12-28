from CowBotVector import *

class GameState:

    def __init__(self, packet, field_info):

        #Find self and teams
        team_info = find_self_and_teams(packet)
        self.my_index = team_info[0]
        self.my_team = team_info[1]
        self.teammate_indices = team_info[2]
        self.opponent_indices = team_info[3]

        #Ball info
        self.ball = Ball(packet)

        #Info for own car
        self.me = Car(packet, self.my_index)

        #Info for other cars
        self.teammates = []
        self.opponents = []
        
        for i in range(packet.num_cars):
            if i != self.my_index:
                if i in self.teammate_indices:
                    self.teammates.append(Car(packet, i))
                else:
                    self.opponents.append(Car(packet,i))

        self.big_boosts = []
        self.small_boosts = []
        for i in range(field_info.num_boosts):
            pad = field_info.boost_pads[i]
            if pad.is_full_boost:
                self.big_boosts.append(Boostpad(i, pad.location, packet.game_boosts[i].is_active, packet.game_boosts[i].timer))

class Ball(GameState):

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

    return CarState(pos, rot, vel, omega)


class CarState(GameState):

    def __init__(self, pos, rot, vel, omega):
        self.pos = pos
        self.rot = rot
        self.vel = vel
        self.omega = omega

        if self.rot != None:
            self.pitch = rot[0]
            self.yaw = rot[1]
            self.roll = rot[2]
            

class Boostpad(GameState):

    def __init__(self, index, pos, is_active, timer):
        self.index = index
        self.pos = pos
        self.is_active = is_active
        self.timer = timer

def find_self_and_teams(packet):
    #I shouldn't be doing this every frame :/
    #I also shouldn't need to hard code the bot name
    for i in range(packet.num_cars):
        if packet.game_cars[i].name == "Boolean Algebra Cow":
            my_index = i
            my_team = packet.game_cars[i].team
            break
        
    teammate_indices = []
    opponent_indices = []
    
    for i in range(packet.num_cars):
        if i == my_index:
            pass
        elif packet.game_cars[i].team == my_team:
            teammate_indices.append(i)
        else:
            opponent_indices.append(i)

    return my_index, my_team, teammate_indices, opponent_indices
