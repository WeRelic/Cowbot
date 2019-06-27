import math
import random

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
import rlutilities as utils
from rlutilities.mechanics import AerialTurn, Aerial

from BallPrediction import * #Not used yet.  Maybe will be used here, maybe only in Planning.py?
import CowBotInit #only used for find_teammates_and_opponents - move more into this file?
from Cowculate import * #deprecate and rename planning?
import EvilGlobals
from GamePlan import GamePlan
from GameState import GameState
from Kickoffs.Kickoff import *
from Mechanics import * #Only for the PersistentMechanics class? Try to remove this if I can.
from Pathing.Path_Planning import *
from Planning.Planning import *


#A useful flag for testing code.
#When True, all match logic will be ignored.
#Planning will still take place, but can be overridden,
#and no action will be taken outside of the "if TESTING:" blocks.
TESTING = False
if TESTING:
    from StateSetting import *

class BooleanAlgebraCow(BaseAgent):

    '''
    This is the class within which our entire bot lives.
    Anything not saved to an attribute of this class will be deleted after an input for the frame is returned.
    We never explicitly call any methods of this class.  The framework calls initialize_agent once at the start,
    and it calls get_output at the start of each frame.  All of our logic lives inside get_output.
    '''

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

        self.plan = GamePlan()
        self.old_kickoff_data = None
        self.utils_game = None
        self.old_inputs = SimpleControllerState()

        #This will be used to remember opponent actions.  Maybe load in bots preemptively one day?
        self.memory = None

        #These are used to specify or set states in the code.  State setting
        #using state.copy_state() doesn't work as expected.
        self.zero_ball_state = BallState(pos = None,
                                         rot = None,
                                         vel = None,
                                         omega = None,
                                         latest_touch = None,
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
        self.timer = 0
        
        #Put testing-only variables here
        if TESTING:
            self.state = "Reset"
            self.target_loc = None
            self.target_time = None
            self.takeoff_time = None
            self.start_time = None
            #self.state = "Reset"
            #self.path_plan = "ArcLineArc"
            #self.path_switch = True
            pass
            
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:

        ###############################################################################################
        #Startup and frame info
        ###############################################################################################
        
        #Initialization info - move all of this into CowBotInit?
        if self.is_init:
            self.is_init = False
            self.field_info = self.get_field_info()
 
            #Find self and teams
            team_info = CowBotInit.find_self_and_teams(packet, self.index, self.team)
            self.teammate_indices = team_info[0]
            self.opponent_indices = team_info[1]

            
            self.utils_game = utils.simulation.Game(self.index, self.team)
            utils.simulation.Game.set_mode("soccar")

        EvilGlobals.renderer = self.renderer

        #Game state info
        self.game_info = GameState(packet, self.get_rigid_body_tick(), self.utils_game,
                                   self.field_info, self.index,
                                   self.team, self.teammate_indices, self.opponent_indices,
                                   self.old_inputs)

        if self.old_game_info == None:
            #This avoids AttributeErrors on calls to old_game_info on the first frame of a kickoff.
            #The first frame shouldn't be calling previous frame information anyway
            self.old_game_info = self.game_info

        #Update persistent mechanics if we're not doing them, otherwise let them do their thing.
        #The checks will be set to true when the mechanic is called.
        #Eventually this might get swallowed into a bigger state machine.
        if not self.persistent.aerial_turn.check:
            self.persistent.aerial_turn.action = AerialTurn(self.game_info.utils_game.my_car)
        self.persistent.aerial_turn.check = False

        if not self.persistent.aerial.check:
            self.persistent.aerial.action = Aerial(self.game_info.utils_game.my_car)
        self.persistent.aerial.check = False
        
        ###############################################################################################
        #Planning
        ###############################################################################################

        self.plan, self.path, self.persistent = make_plan(self.game_info,
                              self.plan.old_plan,
                              self.persistent)

        #Check if it's a kickoff.  If so, we'll run kickoff code later on.
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


        self.prediction = PredictionPath(self.game_info.utils_game, predict_for_time(3))
        #EvilGlobals.draw_ball_path(self.prediction)


        ###############################################################################################
        #Testing 
        ###############################################################################################


        if TESTING:
            return SimpleControllerState()
            if self.state != "Reset":
                self.timer = self.game_info.game_time - self.start_time

            if self.state == "Reset":
                #Reset everything
                self.timer = 0
                self.start_time = self.game_info.game_time

                #Set the game state
                ball_pos = Vec3(2000, -5010, 1000)
                ball_state = self.zero_ball_state.copy_state(pos = ball_pos,
                                                             rot = Orientation(pyr = [0,0,0]),
                                                             vel = Vec3(-700, 0, 800),
                                                             omega = Vec3(0,0,0))

                car_pos = Vec3(-600, -5300, 15)
                car_state = self.zero_car_state.copy_state(pos = car_pos,
                                                           vel = Vec3(0, 0, 0),
                                                           rot = Orientation(pitch = 0,
                                                                             yaw = pi/3,
                                                                             roll = 0),
                                                           boost = 100)

                self.set_game_state(set_state(self.game_info,
                                              current_state = car_state,
                                              ball_state = ball_state))
                self.state = "Wait"
                return SimpleControllerState()

            elif self.state == "Wait":
                if self.timer > 0.2:
                    self.state = "Plan"
                return SimpleControllerState()


            elif self.state == "Plan":
                try:
                    self.target_time, self.target_loc = get_ball_arrival(self.game_info,
                                                                         ball_is_in_front_of_net)
                except TypeError:
                    return SimpleControllerState()
                self.takeoff_time = choose_stationary_takeoff_time(self.game_info,
                                                              self.target_loc,
                                                              self.target_time)
                self.target_loc -= Vec3_to_vec3(Vec3(0,0,40), team_sign)
                self.state = "Patience"
                return SimpleControllerState()


            elif self.state == "Patience":
                if self.game_info.game_time > self.takeoff_time:
                    self.state = "Initialize"

                return SimpleControllerState()


            elif self.state == "Initialize":
                self.persistent.aerial.check = True
                self.persistent.aerial.action.target = self.target_loc
                self.persistent.aerial.action.arrival_time = self.target_time

                self.state = "Go"

                return SimpleControllerState()

            elif self.state == "Go":

                #Controller inputs and persistent mechanics
                controller_input, self.persistent = aerial(vec3_to_Vec3(self.persistent.aerial.action.target, team_sign),
                                                           Vec3(0,0,1),
                                                           self.game_info.dt,
                                                           self.persistent)
                if self.timer > 5:
                    self.state = "Reset"
                return controller_input




        ###############################################################################################
        #Run either Kickoff or Cowculate
        ###############################################################################################

        if self.plan.layers[0] == "Kickoff":
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

            output, self.persistent = self.kickoff_data.input()

        else:
            output, self.persistent = Cowculate(self.plan,
                                                self.path,
                                                self.game_info,
                                                self.old_game_info,
                                                self.prediction,
                                                self.persistent)



        ###############################################################################################
        #Update previous frame variables.
        ###############################################################################################
        self.old_game_info = self.game_info
        self.old_kickoff_data = self.kickoff_data
        self.old_inputs = output


        #I feel like this line breaks aerial turning, but I don't remember why it's here in the first place
        self.persistent.aerial_turn.check = False


        #Make sure we don't get stuck turtling. Not sure how effective this is.
        if output.throttle == 0:
            output.throttle = 0.01
        return output







