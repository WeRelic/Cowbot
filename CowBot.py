from math import pi
import random

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
import rlutilities as utils
from rlutilities.mechanics import AerialTurn, Aerial, Dodge

from BallPrediction import PredictionPath #Maybe kick all this into Planning?
from Conversions import Vec3_to_vec3, rot_to_mat3
from Cowculate import Cowculate #deprecate and rename planning?
from GamePlan import GamePlan
from GameState import BallState, CarState, GameState, Hitbox, Orientation
from Kickoffs.Kickoff import Kickoff, update_kickoff_position
from Mechanics import PersistentMechanics
from Miscellaneous import predict_for_time
from Pathing.Path_Planning import follow_waypoints
import Planning.OnesPlanning.Planning as OnesPlanning
from Simulation import * #Temporary for testing and porting to new files
#import Planning.TeamPlanning.Planning as TeamPlanning  #Team planning is no longer in this version due to bugs.  Copy from Ones planning and update team strategy at some point before the next team event.


#A flag for testing code.
#When True, all match logic will be ignored.
#Planning will still take place, but can be overridden,
#and no action will be taken outside of the "if TESTING:" blocks.
TESTING = True
DEBUGGING = False
if TESTING or DEBUGGING:
    import random
    from math import sqrt
    

    import EvilGlobals #Only needed for rendering.
    from StateSetting import *
    from BallPrediction import *
    from Maneuvers import GroundTurn


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
            #self.state = "Reset"
            #self.path_plan = "ArcLineArc"
            #self.path_switch = True

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:


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
            self.car_hitboxes = []
    
            for i in range(packet.num_cars):
                self.car_hitboxes.append(Hitbox(self.match_settings.PlayerConfigurations(i).Loadout().CarId()))

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
                                         team = self.team)

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
                                    my_old_inputs = self.old_inputs,
                                    hitboxes = self.car_hitboxes )
        
        ###############################################################################################
        #Planning
        ###############################################################################################

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
            self.persistent.aerial_turn.action = AerialTurn(self.game_info.utils_game.my_car)
            self.persistent.aerial_turn.action.target = rot_to_mat3(self.persistent.aerial_turn.target_orientation, self.game_info.team_sign)
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
            current_state = self.game_info.me
            self.my_timer += self.game_info.dt


            ###

            #Using simulation to make solid contact
            if self.RESET == 'waiting' or self.RESET:

                self.my_timer = 0
                if self.RESET == 'waiting':
                    self.RESET = False
                else:
                    self.RESET = 'waiting'
                #Reset to a stationary setup when the bot is reloaded
                ball_pos = Vec3(0, 600, 500)
                ball_state = self.zero_ball_state.copy_state(pos = ball_pos,
                                                             rot = Orientation(pyr = [0,0,0]),
                                                             vel = Vec3(0, 0, 0),
                                                             omega = Vec3(0,0,0))
                car_pos = Vec3(0, -4000, 18.65)
                car_vel = Vec3(0, 0, 0)

                #Random starting yaw
                car_state = self.zero_car_state.copy_state(pos = car_pos,
                                                           vel = car_vel,
                                                           rot = Orientation(pitch = 0,
                                                                             yaw = pi/2,
                                                                             roll = 0),
                                                           boost = 100)

                self.set_game_state(set_state(self.game_info,
                                              current_state = car_state,
                                              ball_state = ball_state))

            #####

            elif self.dodge != None:
                #If we've already decided on a dodge, execute the dodge.
                self.dodge.step(self.game_info.dt)
                controller_input = self.dodge.controls
                controller_input.boost = 1

            else:
                #Approach the ball, for now just by boosting.  Eventually this will be a path to follow.
                controller_input.boost = 1
                
                #As we approach the ball, calculate when dodging results in a good touch
                test_dodge = Dodge(self.game_info.utils_game.my_car)
                
                test_dodge.duration, test_dodge.delay, simulation = stationary_ball_dodge_contact(self.game_info,
                                                                                                  self.game_info.ball.pos.z - 0)
                test_dodge.target = Vec3_to_vec3(self.game_info.ball.pos, 1) #TODO: Intelligently choose this?

                #Air roll shots.  TODO: intelligently choose angle
                test_dodge.preorientation = roll_away_from_target(test_dodge.target, pi/4, self.game_info)

                #If the dodge hits the ball, check if it's a good touch
                if simulation.ball_contact:
                    flip_before_contact = simulation.time - test_dodge.delay > 0
                    not_too_early = simulation.time - test_dodge.delay < 0.05
                    dodge_timing = flip_before_contact and not_too_early

                    nose_contact = front_face_contact(simulation.time,
                                                      simulation.box,
                                                      self.game_info.ball,
                                                      self.game_info.team_sign)
                    if nose_contact and dodge_timing:
                        self.dodge = test_dodge
                        
                        controller_input = self.dodge.controls                

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



