from math import pi, ceil
import random
from functools import partial

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
import rlutilities as utils
from rlutilities.mechanics import AerialTurn as RLU_AerialTurn
from rlutilities.mechanics import Aerial as RLU_Aerial
from rlutilities.mechanics import Dodge as RLU_Dodge
from rlutilities.mechanics import FollowPath as RLU_FollowPath
from rlutilities.simulation import Curve

from BallPrediction import PredictionPath, ball_contact_binary_search
from Conversions import Vec3_to_vec3, rot_to_mat3
from Cowculate import Cowculate #deprecate and rename planning?
from GamePlan import GamePlan
from GameState import BallState, CarState, GameState, Hitbox, Orientation
from Kickoffs.Kickoff import Kickoff, update_kickoff_position
from Mechanics import PersistentMechanics, FrontDodge
from Miscellaneous import predict_for_time
from Pathing.PathPlanning import shortest_arclinearc
import Planning.OnesPlanning.Planning as OnesPlanning
#import Planning.TeamPlanning.Planning as TeamPlanning  #Team planning is no longer in this version due to bugs.  Copy from Ones planning and update team strategy at some point before the next team event.


#A flag for testing code.
#When True, all match logic will be ignored.
#Planning will still take place, but can be overridden,
#and no action will be taken outside of the "if TESTING:" blocks.

TESTING = True
DEBUGGING = True
if TESTING or DEBUGGING:
    import random
    from math import sqrt
    

    import EvilGlobals #Only needed for rendering.
    from StateSetting import *
    from BallPrediction import *
    from Mechanics import CancelledFastDodge, aerial_rotation
    from Maneuvers import GroundTurn
    from Pathing.ArcLineArc import ArcLineArc
    from Simulation import *



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
        self.my_timer = 0

        #Exception variables that hopefully don't get used
        self.Body_ID_Exception = False
        
        #Put testing-only variables here
        if TESTING:
            self.state = "Reset"
            self.target_loc = None
            self.target_time = None
            self.takeoff_time = None
            self.start_time = None
            self.old_game_info = None
            self.RESET = True
            self.dodge = None
            self.path_target = None
            #self.state = "Reset"
            #self.path_plan = "ArcLineArc"
            #self.path_switch = True

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:

        ###############################################################################################
        #Exception handling - better keep track of when things might go wrong,
        #but in a way we want our bot to ignore.
        ###############################################################################################

        #I guess we don't need this anymore, because someone finally decided to tell me information they should've told me a month ago when I asked... I'll keep it because it's a good structure to have in case we need it in the future.

        ###############################################################################################
        #Startup info - run once at start
        ###############################################################################################

        #Initialization info
        if self.is_init:
            self.is_init = False
            self.field_info = self.get_field_info()
            self.match_settings = self.get_match_settings()
 
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


        ###############################################################################################
        #Prediction and Game state info
        ###############################################################################################

        self.prediction = PredictionPath(ball_prediction = self.get_ball_prediction_struct(),
                                         source = "Framework",
                                         team = self.team,
                                         utils_game = self.utils_game,
                                         condition = lambda slices: len(slices) < 360)

        #Game state info
        self.game_info = GameState( packet = packet,
                                    rigid_body_tick = self.get_rigid_body_tick(),
                                    utils_game = self.utils_game,
                                    field_info = self.field_info,
                                    match_settings = self.match_settings,
                                    my_index = self.index,
                                    my_team = self.team,
                                    ball_prediction = self.prediction,
                                    teammate_indices = self.teammate_indices,
                                    opponent_indices = self.opponent_indices,
                                    my_old_inputs = self.old_inputs )

        ###############################################################################################
        #Planning
        ###############################################################################################

        if not TESTING:
            #For now everything is a 1v1.  I'll fix team code again in the future.
            #if self.game_info.team_mode == "1v1":
            self.plan, self.persistent = OnesPlanning.make_plan(self.game_info,
                                                                self.plan.old_plan,
                                                                self.plan.path,
                                                                self.persistent)

            '''
            else:
                self.plan, self.persistent = TeamPlanning.make_plan(self.game_info,
                                                                    self.plan.old_plan,
                                                                    self.plan.path,
                                                                    self.persistent)
            '''

            #Check if it's a kickoff.  If so, we'll run kickoff code later on.
            self.kickoff_position = update_kickoff_position(self.game_info,
                                                            self.kickoff_position)

        ###############################################################################################
        #Update RLU Mechanics as needed
        ###############################################################################################

        #If we're in the first frame of an RLU mechanic, start up the object.
        #If we're finished with it, reset it to None
        ###
        if self.persistent.aerial_turn.initialize:
            self.persistent.aerial_turn.initialize = False
            self.persistent.aerial_turn.action = RLU_AerialTurn(self.game_info.utils_game.my_car)
            self.persistent.aerial_turn.action.target = rot_to_mat3(self.persistent.aerial_turn.target_orientation, self.game_info.team_sign)
        elif not self.persistent.aerial_turn.check:
            self.persistent.aerial_turn.action = None
        self.persistent.aerial_turn.check = False
        ###
        if self.persistent.aerial.initialize:
            self.persistent.aerial.initialize = False
            self.persistent.aerial.action = RLU_Aerial(self.game_info.utils_game.my_car)
            self.persistent.aerial.action.target = Vec3_to_vec3(self.persistent.aerial.target_location, self.game_info.team_sign)
            self.persistent.aerial.action.arrival_time = self.persistent.aerial.target_time
            self.persistent.aerial.action.up = Vec3_to_vec3(self.persistent.aerial.target_up, self.game_info.team_sign)
        elif not self.persistent.aerial.check:
            self.persistent.aerial.action = None
        self.persistent.aerial.check = False
        ###
        
        if not self.persistent.path_follower.check:
            self.persistent.path_follower.action = None
        self.persistent.path_follower.check = False
        ###
        if not self.persistent.dodge.check:
            self.persistent.dodge.action = None
        self.persistent.dodge.check = False

        ###############################################################################################
        #Testing 
        ###############################################################################################


        if TESTING:

            #Copy-paste from a testing file here
            output = SimpleControllerState()
            current_state = self.game_info.me
            ball_distance = (self.game_info.ball.pos - current_state.pos).magnitude()

            ###

            #Reset the testing position
            if self.state == "Reset":
                output = SimpleControllerState()
                self.my_timer = self.game_info.game_time
                self.RESET = False                    
                
                #Reset to a stationary setup when the bot is reloaded
                ball_pos = Vec3(-2000, 0, 150)
                ball_state = self.zero_ball_state.copy_state(pos = ball_pos,
                                                             rot = Orientation(pyr = [0,0,0]),
                                                             vel = Vec3(1000, 0, 1000),
                                                             omega = Vec3(0,0,0))
                car_pos = Vec3(0, -4000, 18.65)
                car_vel = Vec3(0, 0, 0)

                #Set car state
                car_state = self.zero_car_state.copy_state(pos = car_pos,
                                                           vel = car_vel,
                                                           rot = Orientation(pitch = 0,
                                                                             yaw = 0,
                                                                             roll = 0),
                                                           boost = 100)
                self.set_game_state(set_state(self.game_info,
                                              current_state = car_state,
                                              ball_state = ball_state))

                self.state = "Wait"

            ###

            elif self.state == "Wait":
                #Wait for state setting to work
                output = SimpleControllerState()
                if self.game_info.game_time - self.my_timer < 0.2:
                    self.state = "Choose path"
                

            ###   

            elif self.state == "Choose path":
                EvilGlobals.draw_ball_path(self.game_info.ball_prediction)
                #If we don't already have a path, plan one
                self.persistent.path_follower.check = True
                intercept_slice, self.persistent.path_follower.path, self.persistent.path_follower.action = ball_contact_binary_search(self.game_info, end_tangent = Vec3(0,1,0))
                if self.persistent.path_follower.action != None:
                    self.state = "Follow path"

            ###

            elif self.state == "Follow path":
                print("following: ", self.persistent.path_follower.path.end)
                #If we're far from the end of the path, follow the path
                #Follow the ArcLineArc path
                self.persistent.path_follower.check = True
                self.persistent.path_follower.action.step(self.game_info.dt)
                output = self.persistent.path_follower.action.controls
                if (current_state.pos - self.persistent.path_follower.path.end).magnitude() < 500:
                    self.state = "Choose dodge"

            ###

            elif self.state == "Choose dodge":
                #If we don't already have a dodge planned, plan one
                self.persistent.dodge.check = True
                dodge_simulation_results = moving_ball_dodge_contact(self.game_info)
                self.persistent.dodge.action = RLU_Dodge(self.game_info.utils_game.my_car)
                self.persistent.dodge.action.duration = dodge_simulation_results[0]
                self.persistent.dodge.action.delay = dodge_simulation_results[1]
                self.persistent.dodge.action.target = Vec3_to_vec3(self.game_info.ball.pos, self.game_info.team_sign)
                self.persistent.dodge.action.preorientation = roll_away_from_target(self.persistent.dodge.action.target,
                                                                                    pi/4,
                                                                                    self.game_info)            
                if self.persistent.dodge.action != None:
                    self.state = "Dodge"

            ###

            elif self.state == "Dodge":
                #If we've planned a dodge, do it
                self.persistent.dodge.check = True
                self.persistent.dodge.action.step(self.game_info.dt)
                output = self.persistent.dodge.action.controls
                output.boost = 1



            #####################################
            #End of frame stuff that needs to be in the testing block as well
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
        #Update previous frame variables and return
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





        





    
