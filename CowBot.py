from math import pi
import random

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
import rlutilities as utils
from rlutilities.mechanics import AerialTurn, Aerial

from BallPrediction import PredictionPath #Maybe kick all this into Planning?
from Conversions import Vec3_to_vec3
import CowBotInit #only used for find_teammates_and_opponents - move more into this file?
from Cowculate import Cowculate #deprecate and rename planning?
from GamePlan import GamePlan
from GameState import BallState, CarState, GameState
from Kickoffs.Kickoff import Kickoff, update_kickoff_position
from Mechanics import PersistentMechanics
from Miscellaneous import predict_for_time
from Pathing.Path_Planning import follow_waypoints
import Planning.OnesPlanning.Planning as OnesPlanning
import Planning.TeamPlanning.Planning as TeamPlanning


#A flag for testing code.
#When True, all match logic will be ignored.
#Planning will still take place, but can be overridden,
#and no action will be taken outside of the "if TESTING:" blocks.
TESTING = False
DEBUGGING = True
if TESTING or DEBUGGING:
    import EvilGlobals #Only needed for rendering.
    from StateSetting import *
    from BallPrediction import *
    
class BooleanAlgebraCow(BaseAgent):

    '''
    This is the class within which our entire bot lives.
    Anything not saved to an attribute of this class will be deleted after an input for the frame is returned.
    The only methods of this class that we use are to get information from the framework, like field info or rigid body tick
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
        self.path_state = 'Reset'
        self.path = None
        self.waypoint_index = 2

        self.plan = GamePlan()
        self.old_kickoff_data = None
        self.utils_game = None
        self.old_inputs = SimpleControllerState()

        #This will be used to remember opponent actions.  Maybe load in opponent bots preemptively one day?
        self.memory = None

        #These are used to specify or set states in the code.  State setting
        #using state.copy_state() didn't work as expected.
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

        #Initialization info
        if self.is_init:
            self.is_init = False
            self.field_info = self.get_field_info()
 
            #Find teammates and opponents
            self.teammate_indices, self.opponent_indices = CowBotInit.find_self_and_teams(packet, self.index, self.team)

            
            self.utils_game = utils.simulation.Game(self.index, self.team)
            utils.simulation.Game.set_mode("soccar")

        if TESTING or DEBUGGING:
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
        
        ###############################################################################################
        #Planning
        ###############################################################################################

        if self.game_info.team_mode == "1v1":
            self.plan, self.path, self.persistent = OnesPlanning.make_plan(self.game_info,
                                                                           self.plan.old_plan,
                                                                           self.persistent)
        else:
            self.plan, self.path, self.persistent = TeamPlanning.make_plan(self.game_info,
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

        #If we're in the first frame of an RLU mechanic, start up the object.
        if self.persistent.aerial_turn.initialize:
            self.persistent.aerial_turn.action = AerialTurn(self.game_info.utils_game.my_car)
            self.persistent.aerial_turn.action.target = self.persistent.aerial_turn.target_orientation
            self.persistent.aerial_turn.initialize = False
        elif not self.persistent.aerial_turn.check:
            self.persistent.aerial_turn.action = None
        self.persistent.aerial_turn.check = False
        #
        if self.persistent.aerial.initialize:
            self.persistent.aerial.action = Aerial(self.game_info.utils_game.my_car)
            self.persistent.aerial.action.target = self.persistent.aerial.target_location
            self.persistent.aerial.action.arrival_time = self.persistent.aerial.target_time
            self.persistent.aerial.action.up = Vec3_to_vec3(self.persistent.aerial.target_up, self.game_info.team_sign)
            self.persistent.aerial.initialize = False
        elif not self.persistent.aerial.check:
            self.persistent.aerial.action = None
        self.persistent.aerial.check = False


        ###############################################################################################
        #Testing 
        ###############################################################################################


        if TESTING:

            #Copy-paste from a testing file here
            controller_input = SimpleControllerState()
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

        #Make sure we don't get stuck turtling. Not sure how effective this is.
        if output.throttle == 0:
            output.throttle = 0.01

        #Making sure that RLU output is interpreted properly as an input for RLBot
        framework_output = SimpleControllerState()
        framework_output.throttle = output.throttle
        framework_output.steer = output.steer
        framework_output.yaw = output.yaw
        framework_output.pitch = output.pitch
        framework_output.roll = output.roll
        framework_output.boost = output.boost
        framework_output.handbrake = output.handbrake
        framework_output.jump = output.jump
        return framework_output







