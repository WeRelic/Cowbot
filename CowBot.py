import math
#from FrameInput import *
from CowBotVector import *
from CowBotInit import *

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from Cowculate import *
from GameState import *
from Kickoff import *
from Planning import *
from EvilGlobals import renderer



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
        self.kickoff_data = None

        #This will be used to remember opponent actions.  Maybe load in bots preemptively one day?
        self.memory = None


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

            self.old_plan = None
            self.current_plan = None
            self.old_kickoff_data = None

        EvilGlobals.renderer = self.renderer

        #Game state info
        self.game_info = GameState(packet, self.get_rigid_body_tick(),
                                   self.field_info, self.name, self.index,
                                   self.team, self.teammate_indices, self.opponent_indices,
                                   self.jumped_last_frame_list)

        #Make a plan for now.  Can depend on previous plans, current game info, and opponent tendencies.
        #Very hacky for short deadline.  Fix after wintertide.
        self.current_plan = make_plan(self.game_info, self.old_plan)

        #Check if it's a kickoff.  If so, run kickoff code.
        self.kickoff_position = update_kickoff_position(self.game_info, self.kickoff_position)

        if self.current_plan == "Kickoff":
            if self.old_kickoff_data != None:
                self.kickoff_data = Kickoff(self.game_info, self.old_game_info, self.kickoff_position, self.old_kickoff_data.memory)
            else:
                self.kickoff_data = Kickoff(self.game_info, self.old_game_info, self.kickoff_position, None)
            controller_input = self.kickoff_data.input()
            output = self.kickoff_data.input()

        else:
            output = Cowculate(self.game_info, self.old_game_info, self.current_plan)

        #Update previous frame variables.
        self.old_plan = self.current_plan
        self.old_game_info = self.game_info
        self.jumped_last_frame_list = get_jumped_this_frame_list(self.get_rigid_body_tick())
        self.old_kickoff_data = self.kickoff_data

        #Make sure we don't get stuck turtling.
        if output.throttle == 0:
            output.throttle = 0.01
        return output



