import math
import random

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
import rlutilities as utils

from BallPrediction import *
from CowBotInit import *
from CowBotVector import *
from Cowculate import *
from EvilGlobals import renderer
from GameState import *
from Kickoffs.Kickoff import *
from Mechanics import *
from Pathing.Pathing import *
from Pathing.Path_Planning import *
from Planning import *
from StateSetting import *

TESTING = True


class BooleanAlgebraCow(BaseAgent):

    def initialize_agent(self):
        #This runs once before the bot starts up
        self.is_init = True
        self.teammate_indices = []
        self.opponent_indices = []
        self.old_game_info = None
        self.game_info = None
        self.kickoff_position = "Other"
        self.kickoff_data = None
        self.jumped_last_frame = None
        self.path_state = None
        self.path = None
        self.waypoint_index = 2


        self.utils_game = None

        #This will be used to remember opponent actions.  Maybe load in bots preemptively one day?
        self.memory = None

        self.zero_ball_state = BallState(pos = None,
                                         rot = None,
                                         vel = None,
                                         omega = None,
                                         last_touch = None,
                                         hit_location = None)
        self.zero_car_state = CarState(pos = None,
                                       rot = None,
                                       vel = None,
                                       omega = None,
                                       demo = None,
                                       wheel_contact = None,
                                       supersonic = None,
                                       jumped = None,
                                       double_jumped = None,
                                       boost = None,
                                       jumped_last_frame = None)

        
        self.persistent = PersistentMechanics()
        self.timer = 8

        
        #Put testing-only variables here
        if TESTING:
            self.state = "Reset"
            self.path_plan = "ArcLineArc"
            self.path_switch = True
            
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:

        ###############################################################################################
        #Startup and frame info
        ###############################################################################################

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

            self.utils_game = utils.simulation.Game(self.index, self.team)
            utils.simulation.Game.set_mode("soccar")

        EvilGlobals.renderer = self.renderer

        #Game state info
        self.game_info = GameState(packet, self.get_rigid_body_tick(), self.utils_game,
                                   self.field_info, self.name, self.index,
                                   self.team, self.teammate_indices, self.opponent_indices,
                                   self.jumped_last_frame)

        if self.old_game_info == None:
            #This avoids TypeErrors on calls to old_game_info on the first frame of a kickoff.
            #The first frame shouldn't be calling previous frame information anyway
            self.old_game_info = self.game_info

        #Update persistent mechanics if we're not doing them, otherwise let them do their thing.
        #The checks will be set to true when the mechanic is called.
        if not self.persistent.aerial_turn.check:
            self.persistent.aerial_turn.action = AerialTurn(self.game_info.utils_game.my_car)
        self.persistent.aerial_turn.check = False

        if not self.persistent.aerial.check:
            self.persistent.aerial.action = Aerial(self.game_info.utils_game.my_car)
        self.persistent.aerial.check = False
        
        ###############################################################################################
        #Planning
        ###############################################################################################

        self.current_plan = make_plan(self.game_info,
                                      self.old_plan)

        #Check if it's a kickoff.  If so, run kickoff code.
        self.kickoff_position = update_kickoff_position(self.game_info,
                                                        self.kickoff_position)
        if TESTING:
              boost_list = [10,5,21,10,6]
              waypoint_list = [ self.game_info.boosts[boost_list[i]].pos for i in range(len(boost_list)) ]
              self.path, self.path_state, self.waypoint_index = follow_waypoints(self.game_info,
                                                                                 self.path,
                                                                                 waypoint_list,
                                                                                 self.waypoint_index,
                                                                                 self.path_state)
                

        ###############################################################################################
        #Testing 
        ###############################################################################################


        if TESTING:
            controller_input = SimpleControllerState()

            controller_input = self.path.input()


            return controller_input


        ''' AERIAL TESTING - Important, but not implemented anywhere else yet!
            self.timer += self.game_info.dt

            if self.state == "Reset":
                #Reset everything
                self.timer = 0

                #Set the game state
                ball_pos = Vec3(0, 0, 1000)
                ball_state = self.zero_ball_state.copy_state(pos = ball_pos,
                                                             rot = Orientation(pyr = [0,0,0]),
                                                             vel = Vec3(0, -2200, 800),
                                                             omega = Vec3(0,0,0))

                car_pos = Vec3(0, -2000, 15)
                car_state = self.zero_car_state.copy_state(pos = car_pos,
                                                           vel = Vec3(0, 0, 0),
                                                           rot = Orientation(pitch = 0,
                                                                             yaw = -pi/2,
                                                                             roll = 0),
                                                           boost = 100)

                self.set_game_state(set_state(self.game_info,
                                              current_state = car_state,
                                              ball_state = ball_state))
                self.state = "Wait"
                controller_state = SimpleControllerState()
                controller_state.boost = 1
                return controller_state

            elif self.state == "Wait":
                if self.timer > 0.2:
                    self.state = "Boost"


            elif self.state == "Boost":
                controller_state = SimpleControllerState()
                controller_state.boost = 1
                if self.timer > 0.5:
                    self.state = "Initialize"

                
                return controller_state


            elif self.state == "Initialize":
                self.persistent.aerial.check = True
                self.persistent = aerial_prediction(self.game_info, self.persistent)

                self.state = "Go"

                return SimpleControllerState()

            elif self.state == "Go":

                #Controller inputs and persistent mechanics
                controller_input, self.persistent = aerial(vec3_to_Vec3(self.persistent.aerial.action.target),
                                                           Vec3(0,0,1),
                                                           self.game_info.dt,
                                                           self.persistent)
                if self.timer > 5:
                    self.state = "Reset"
                return controller_input'''




        ###############################################################################################
        #Run either Kickoff or Cowculate
        ###############################################################################################

        if self.current_plan == "Kickoff":
            if self.old_kickoff_data != None:
                self.kickoff_data = Kickoff(self.game_info,
                                            self.old_game_info,
                                            self.kickoff_position,
                                            self.old_kickoff_data.memory,
                                            self.persistent)
            else:
                self.kickoff_data = Kickoff(self.game_info,
                                            self.old_game_info,
                                            self.kickoff_position,
                                            None,
                                            self.persistent)

            output, persistent = self.kickoff_data.input()

        else:
            output, self.persistent = Cowculate(self.game_info,
                               self.old_game_info,
                               self.current_plan,
                               self.persistent)



        ###############################################################################################
        #Update previous frame variables.
        ###############################################################################################
        self.old_plan = self.current_plan
        self.old_game_info = self.game_info
        self.old_kickoff_data = self.kickoff_data
        if output.jump == 1:
            self.jumped_last_frame = True
        else:
            self.jumped_last_frame = False


        self.persistent.aerial_turn.check = False


        #Make sure we don't get stuck turtling.
        if output.throttle == 0:
            output.throttle = 0.01
        return output















