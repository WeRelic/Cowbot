import math
#from FrameInput import *
from CowBotVector import *
from CowBotInit import *

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from Cowculate import *
from GameState import *
from Kickoff import *

class BooleanAlgebraCow(BaseAgent):

    def initialize_agent(self):
        #This runs once before the bot starts up
        self.is_init = True
        self.controller_state = SimpleControllerState()
        self.teammate_indices = []
        self.opponent_indices = []
        self.old_game_info = None
        self.game_info = None
        self.kickoff_position = "Other"


    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:

        #Initialization info
        if self.is_init:
            self.is_init = False
            self.field_info = self.get_field_info()

            #Find self and teams
            team_info = find_self_and_teams(packet, self.index, self.team)
            self.teammate_indices = team_info[0]
            self.opponent_indices = team_info[1]
            self.jumped_last_frame_list = []
            for car in packet.game_cars:
                self.jumped_last_frame_list.append(False)


        #Game state info
        self.old_game_info = self.game_info
        self.game_info = GameState(packet, self.get_rigid_body_tick(),
                                   self.field_info, self.name, self.index,
                                   self.team, self.teammate_indices, self.opponent_indices,
                                   self.jumped_last_frame_list)

        #updated for next frame - Cowculate doesn't see this variable
        self.jumped_last_frame_list = get_jumped_this_frame_list(self.get_rigid_body_tick())

        #updated for current frame
        self.kickoff_position = self.update_kickoff_position()
        
        return Cowculate(self.game_info, self.old_game_info, self.kickoff_position, self.renderer)




    def update_kickoff_position(self):
        '''
        Returns the current kickoff position.
        Gives "Other" except from the frame the countdown ends until either the ball is hit.
        During this time it returns the position the bot starts in for the kickoff.
        Eventually this will be map specific.  Currently only the standard pool.
        '''

        #Keep the same value most of the time.
        kickoff_position = self.kickoff_position

        #if the kickoff has just started, update the position.
        if self.game_info.is_kickoff_pause and self.kickoff_position == "Other":
            kickoff_position = check_kickoff_position(self.game_info.me)

        #If the ball has just moved, reset the kickoff position.
        elif self.kickoff_position != "Other" and self.game_info.ball.vel.magnitude() > 0:
            kickoff_position = "Other"
        return kickoff_position




