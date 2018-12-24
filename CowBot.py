import math
from FrameInput import *
from CowBotVector import *

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket



class BooleanAlgebraCow(BaseAgent):

    def initialize_agent(self):
        #This runs once before the bot starts up
        self.controller_state = SimpleControllerState()
        
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:

        #Game state info
        field_info = self.get_field_info()
        game_info = GameState(packet, field_info)

        if not game_info.big_boosts[0].is_active:
            print( '{' + ', '.join([str(game_info.big_boosts[0].pos.x),
                                    str(game_info.big_boosts[0].pos.y),
                                    str(game_info.big_boosts[0].pos.z)]) + '}' , game_info.me.pos)

        #Decide on what to do
#        controller_input = FrameInput()

        #Translation for a frame of controller input.
#        self.controller_state.throttle = controller_input.throttle
#        self.controller_state.steer = controller_input.steer
#        self.controller_state.pitch = controller_input.pitch
#        self.controller_state.yaw = controller_input.yaw
#        self.controller_state.roll = controller_input.roll
#        self.controller_state.jump = controller_input.jump
#        self.controller_state.boost = controller_input.boost
#        self.controller_state.brake = controller_input.drift

        return self.controller_state

def find_self_and_teams(packet):
    #This feels about as wrong as it can be, but it should work.
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

        #TODO: get this in quaternion format
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
        

class Car(GameState):

    def __init__(self, packet, index):
        
        this_car = packet.game_cars[index]
        self.pos = Vec3( this_car.physics.location.x,
                         this_car.physics.location.y,
                         this_car.physics.location.z )

        #TODO: get this in quaternion format
        self.rot = [ this_car.physics.rotation.pitch,
                     this_car.physics.rotation.yaw,
                     this_car.physics.rotation.roll ]
        
        self.vel = Vec3( this_car.physics.velocity.x,
                         this_car.physics.velocity.y,
                         this_car.physics.velocity.z )
        
        self.omega = Vec3( this_car.physics.angular_velocity.x,
                           this_car.physics.angular_velocity.y,
                           this_car.physics.angular_velocity.z )


class Boostpad(GameState):

    def __init__(self, index, pos, is_active, timer):
        self.index = index
        self.pos = pos
        self.is_active = is_active
        self.timer = timer
    



