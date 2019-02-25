import math
#from FrameInput import *
from CowBotVector import *
from CowBotInit import *

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from Cowculate import *
from GameState import *
from Kickoff import *
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

        
        return output




def make_plan(game_info, old_plan):

    if game_info.my_team == 0:
        y_sign = 1
    else:
        y_sign = -1

    current_state = game_info.me

    if game_info.is_kickoff_pause:
        return "Kickoff"
    elif old_plan == "Kickoff":
        if y_sign*(game_info.ball.pos.y - game_info.me.pos.y) > 0:
            return "Ball"
        else:
            return check_boost_side(game_info)
    elif old_plan == "Ball" and game_info.ball.last_touch.team == game_info.my_team:
        return check_boost_side(game_info)
    elif old_plan == "Ball" and y_sign*(game_info.ball.pos.y - game_info.me.pos.y) < 0:
        return check_boost_side(game_info)
    elif (old_plan == "Boost+" or old_plan == "Boost-") and game_info.me.boost == 100:
        return "Goal"
    elif old_plan == "Goal" and abs(game_info.me.pos.x) < 900:
        return "Ball"
    else:
        return old_plan


def check_boost_side(game_info):
    if game_info.ball.pos.x > 0:
        return "Boost-"
    else:
        return "Boost+"


