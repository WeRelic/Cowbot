from math import pi
import random

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
import rlutilities as utils
from rlutilities.mechanics import AerialTurn, Aerial

from BallPrediction import PredictionPath #Maybe kick all this into Planning?
from Conversions import Vec3_to_vec3, rot_to_mat3
from Cowculate import Cowculate #deprecate and rename planning?
from GamePlan import GamePlan
from GameState import BallState, CarState, GameState
from Kickoffs.Kickoff import Kickoff, update_kickoff_position
from Mechanics import PersistentMechanics
from Miscellaneous import predict_for_time
from Pathing.Path_Planning import follow_waypoints
import Planning.OnesPlanning.Planning as OnesPlanning
#import Planning.TeamPlanning.Planning as TeamPlanning  #Team planning is no longer in this version due to bugs.  Copy from Ones planning and update team strategy at some point before the next team event.


from Pathing.WaypointPath import WaypointPath


#A flag for testing code.
#When True, all match logic will be ignored.
#Planning will still take place, but can be overridden,
#and no action will be taken outside of the "if TESTING:" blocks.
TESTING = False
DEBUGGING = False
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
            self.teammate_indices = []
            self.opponent_indices = []
    
            for i in range(packet.num_cars):
                if i == self.index:
                    pass
                elif packet.game_cars[i].team == self.team:
                    self.teammate_indices.append(i)
                else:
                    self.opponent_indices.append(i)
            
            self.utils_game = utils.simulation.Game(self.index, self.team)
            utils.simulation.Game.set_mode("soccar")

        if TESTING or DEBUGGING:
            EvilGlobals.renderer = self.renderer

        self.prediction = PredictionPath(ball_prediction = self.get_ball_prediction_struct(),
                                         source = "Framework",
                                         team = self.team)

        #Game state info
        self.game_info = GameState(packet = packet,
                                   rigid_body_tick = self.get_rigid_body_tick(),
                                   utils_game = self.utils_game,
                                   field_info = self.field_info,
                                   my_index = self.index,
                                   my_team = self.team,
                                   ball_prediction = self.prediction,
                                   teammate_indices = self.teammate_indices,
                                   opponent_indices = self.opponent_indices,
                                   my_old_inputs = self.old_inputs)
        
        ###############################################################################################
        #Planning
        ###############################################################################################

        #For now everything is a 1v1.  I'll fix team code again in the future.
        #if self.game_info.team_mode == "1v1":
        self.plan, self.persistent = OnesPlanning.make_plan(self.game_info,
                                                            self.plan.old_plan,
                                                            self.plan.path,
                                                            self.persistent)
        '''        else:
            self.plan, self.persistent = TeamPlanning.make_plan(self.game_info,
                                                                self.plan.old_plan,
                                                                self.plan.path,
                                                                self.persistent)
        '''


        #Check if it's a kickoff.  If so, we'll run kickoff code later on.
        self.kickoff_position = update_kickoff_position(self.game_info,
                                                        self.kickoff_position)

        #If we're in the first frame of an RLU mechanic, start up the object.
        #If we're finished with it, reset it to None
        ###
        if self.persistent.aerial_turn.initialize:
            self.persistent.aerial_turn.initialize = False
            self.persistent.aerial_turn.action = AerialTurn(self.game_info.utils_game.my_car)
            self.persistent.aerial_turn.action.target = rot_to_mat3(self.persistent.aerial_turn.target_orientation)
        elif not self.persistent.aerial_turn.check:
            self.persistent.aerial_turn.action = None
        self.persistent.aerial_turn.check = False
        ###
        if self.persistent.aerial.initialize:
            self.persistent.aerial.initialize = False
            self.persistent.aerial.action = Aerial(self.game_info.utils_game.my_car)
            self.persistent.aerial.action.target = Vec3_to_vec3(self.persistent.aerial.target_location, self.game_info.team_sign)
            self.persistent.aerial.action.arrival_time = self.persistent.aerial.target_time
            self.persistent.aerial.action.up = Vec3_to_vec3(self.persistent.aerial.target_up, self.game_info.team_sign)
        elif not self.persistent.aerial.check:
            self.persistent.aerial.action = None
        self.persistent.aerial.check = False
        ###

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
                                            self.kickoff_position,
                                            self.old_kickoff_data.memory,
                                            self.persistent)
            else:
                self.kickoff_data = Kickoff(self.game_info,
                                            self.kickoff_position,
                                            None,
                                            self.persistent)

            output, self.persistent = self.kickoff_data.input()

        else:
            output, self.persistent = Cowculate(self.plan,
                                                self.game_info,
                                                self.prediction,
                                                self.persistent)



        ###############################################################################################
        #Update previous frame variables.
        ###############################################################################################
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







