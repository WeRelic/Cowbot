import math
from FrameInput import *
from CowBotVector import *

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from Cowculate import *
from GameState import *

class BooleanAlgebraCow(BaseAgent):

    def initialize_agent(self):
        #This runs once before the bot starts up
        self.controller_state = SimpleControllerState()
        
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:

        #Game state info
        field_info = self.get_field_info()
        game_info = GameState(packet, field_info)

        return Cowculate(game_info)




    



