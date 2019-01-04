import math
#from FrameInput import *
from CowBotVector import *
from CowBotInit import *

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from Cowculate import *
from GameState import *

class BooleanAlgebraCow(BaseAgent):

    def initialize_agent(self):
        #This runs once before the bot starts up
        self.is_init = True
        self.controller_state = SimpleControllerState()
        self.teammate_indices = []
        self.opponent_indices = []
        self.old_game_info = None
        self.game_info = None


    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:

        #Initialization info
        if self.is_init:
            self.is_init = False
            self.field_info = self.get_field_info()

            #Find self and teams
            team_info = find_self_and_teams(packet, self.index, self.team)
            self.teammate_indices = team_info[0]
            self.opponent_indices = team_info[1]


        #Game state info
        self.old_game_info = self.game_info
        self.game_info = GameState(packet, self.field_info, self.name, self.index, self.team,
                              self.teammate_indices, self.opponent_indices)


        return Cowculate(self.game_info, self.old_game_info)







