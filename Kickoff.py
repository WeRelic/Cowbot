from CowBotVector import *
from rlbot.agents.base_agent import SimpleControllerState
from Mechanics import *
from BallPrediction import *
from Maneuvers import *





class Kickoff():

    def __init__(self, game_info, old_game_info, kickoff_position, memory):
        self.position = kickoff_position
        self.memory = memory
        self.current_state = game_info.me
        self.game_info = game_info
        self.old_game_info = old_game_info
        if old_game_info != None:
            self.old_state = old_game_info.me
        else:
            self.old_state = None
    def input(self):

        controller_input = SimpleControllerState()

        ball_angle = atan2((self.game_info.ball.pos - self.current_state.pos).y,
                           (self.game_info.ball.pos - self.current_state.pos).x)


        ###############################################################################
        
        if self.position == "Far Back":
            if self.game_info.my_team == 0:
                x_sign = -1
            else:
                x_sign = 1
            if abs(self.current_state.pos.y) > 3000:
                controller_input = FastDodge(self.current_state,
                                             self.current_state.copy_state(pos = Vec3(x_sign*100,0,0)),
                                             self.old_state,
                                             100, boost_threshold = 1250,
                                             direction = -1).input()
                
            elif abs(self.current_state.pos.y) < 400 and abs(self.game_info.opponents[0].pos.y) < 1000:
                #Flip forard.  This can be improved by flipping towards the center of the ball.
                controller_input = AirDodge(Vec3(1,0,0),
                                            self.current_state.jumped_last_frame).input()
            elif self.current_state.wheel_contact and abs(self.current_state.pos.y) < 1000 and abs(self.game_info.opponents[0].pos.y) < 1000:
                if self.current_state.yaw > ball_angle:
                    direction = 0
                else:
                    direction = 1
                controller_input = JumpTurn(self.current_state, 0, direction).input()
            elif abs(self.current_state.pos.y) < 375:
                controller_input.jump = 1
            elif self.current_state.wheel_contact:
                controller_input = GroundTurn(self.current_state,
                                              self.current_state.copy_state(pos=self.game_info.ball.pos)).input()
                controller_input.boost = 1

            else:
                controller_input = GroundTurn(self.current_state,
                                              self.current_state.copy_state(pos=self.game_info.ball.pos)).input()

        ###############################################################################

        elif self.position == "Back Left":
            if self.game_info.my_team == 0:
                first_boost = 7
                x_sign = -1
                y_sign = -1
            else:
                first_boost = 26
                x_sign = 1
                y_sign = 1
                #############
            if abs(self.current_state.pos.x) > 80:
                controller_input = GroundTurn(self.current_state,
                                              self.current_state.copy_state(pos=self.game_info.boosts[first_boost].pos+Vec3(0,y_sign*200,0))).input()
                controller_input.boost = 1
                
            elif abs(self.current_state.pos.y) > 1200:
                controller_input = FastDodge(self.current_state,
                                             self.current_state.copy_state(pos = Vec3(0,0,0)),
                                             self.old_state,
                                             boost_to_use = 100,
                                             oversteer = False,
                                             boost_threshold = 1200,
                                             direction = -1).input()

            elif abs(self.current_state.pos.y) < 350 and abs(self.game_info.opponents[0].pos.y) < 1000:
                #Flip forard.  This can be improved by flipping towards the center of the ball.
                controller_input = AirDodge(Vec3(1,0,0),
                                            self.current_state.jumped_last_frame).input()

            elif self.current_state.wheel_contact and (self.current_state.vel.magnitude() > 2000) and abs(self.game_info.opponents[0].pos.y) < 1000:
                if self.current_state.yaw > ball_angle:
                    direction = 0
                else:
                    direction = 1
                controller_input = JumpTurn(self.current_state, 0, direction).input()
            elif abs(self.current_state.pos.y) < 350:
                controller_input.jump = 1
            elif self.current_state.wheel_contact:
                controller_input = GroundTurn(self.current_state,
                                              self.current_state.copy_state(pos=self.game_info.ball.pos)).input()
                controller_input.boost = 1
            
            else:
                controller_input = GroundTurn(self.current_state,
                                              self.current_state.copy_state(pos=self.game_info.ball.pos)).input()
                
        ###############################################################################K


        elif self.position == "Back Right":
            if self.game_info.my_team == 0:
                first_boost = 7
                x_sign = 1
                y_sign = -1
            else:
                first_boost = 26
                x_sign = -1
                y_sign = 1

                ############
            if abs(self.current_state.pos.x) > 80:
                controller_input = GroundTurn(self.current_state,
                                              self.current_state.copy_state(pos=self.game_info.boosts[first_boost].pos+Vec3(0,y_sign*200,0))).input()
                controller_input.boost = 1
                
            elif abs(self.current_state.pos.y) > 1200:
                
                controller_input = FastDodge(self.current_state,
                                             self.current_state.copy_state(pos = Vec3(0,0,0)),
                                             self.old_state,
                                             boost_to_use = 100,
                                             oversteer = False,
                                             boost_threshold = 1200,
                                             direction = 1).input()
                
            elif abs(self.current_state.pos.y) < 350 and abs(self.game_info.opponents[0].pos.y) < 1000:
                #Flip forard.  This can be improved by flipping towards the center of the ball.
                controller_input = AirDodge(Vec3(1,0,0),
                                            self.current_state.jumped_last_frame).input()

            elif self.current_state.wheel_contact and (self.current_state.vel.magnitude() > 2000) and abs(self.game_info.opponents[0].pos.y) < 1000:
                if self.current_state.yaw > ball_angle:
                    direction = 0
                else:
                    direction = 1
                controller_input = JumpTurn(self.current_state, 0, direction).input()
            elif abs(self.current_state.pos.y) < 350:
                controller_input.jump = 1
            elif self.current_state.wheel_contact:
                controller_input = GroundTurn(self.current_state,
                                              self.current_state.copy_state(pos=self.game_info.ball.pos)).input()
                controller_input.boost = 1

            else:
                controller_input = GroundTurn(self.current_state,
                                              self.current_state.copy_state(pos=self.game_info.ball.pos)).input()

        ###############################################################################

        elif self.position == "Right":
            if self.game_info.my_team == 0:
                first_boost = 10
                x_sign = 1
                #y_sign = -1
            else:
                first_boost = 23
                x_sign = -1
                #ky_sign = 1


                
            if self.game_info.boosts[first_boost].is_active:
                controller_input = GroundTurn(self.current_state,
                                              self.current_state.copy_state(pos = self.game_info.boosts[first_boost].pos + Vec3(x_sign*125,0,0))).input()
                controller_input.boost = 1

            elif abs(self.current_state.pos.y) > 1200:
                controller_input = FastDodge(self.current_state,
                                             self.current_state.copy_state(pos = Vec3(x_sign*800,0,0)),
                                             self.old_state,
                                             boost_to_use = 100,
                                             boost_threshold = 1000,
                                             direction = 1).input()

            elif self.current_state.double_jumped:
                #controller_input.roll = 1
                #controller_input.pitch = -1
                controller_input.yaw = 1

            elif abs(self.current_state.pos.y) < 250 and abs(self.game_info.opponents[0].pos.y) < 1000:
                #Flip forard.  This can be improved by flipping towards the center of the ball.
                controller_input = AirDodge(Vec3(1/sqrt(2),1/sqrt(2),0),
                                            self.current_state.jumped_last_frame).input()

            elif self.current_state.wheel_contact and (self.current_state.vel.magnitude() > 1725) and abs(self.game_info.opponents[0].pos.y) < 1000:
                if self.current_state.yaw > ball_angle:
                    direction = 0
                else:
                    direction = 1
                controller_input = JumpTurn(self.current_state, 0, direction).input()
            elif abs(self.current_state.pos.y) < 350:
                controller_input.jump = 1
            elif self.current_state.wheel_contact:
                controller_input = GroundTurn(self.current_state,
                                              self.current_state.copy_state(pos=self.game_info.ball.pos)).input()
                controller_input.boost = 1

        ###############################################################################

        elif self.position == "Left":
            if self.game_info.my_team == 0:
                first_boost = 11
                x_sign = 1
                #y_sign = -1
            else:
                first_boost = 22
                x_sign = -1
                #y_sign = 1

                ##########


            if self.game_info.boosts[first_boost].is_active:
                controller_input = GroundTurn(self.current_state,
                                              self.current_state.copy_state(pos = self.game_info.boosts[first_boost].pos + Vec3(-x_sign*125,0,0))).input()
                controller_input.boost = 1


            if abs(self.current_state.pos.y) > 1200:
                controller_input = FastDodge(self.current_state,
                                             self.current_state.copy_state(pos = Vec3(-x_sign*700,0,0)),
                                             self.old_state,
                                             boost_to_use = 100,
                                             boost_threshold = 1000,
                                             direction = -1).input()

            elif self.current_state.double_jumped:
                #controller_input.roll = -1
                #controller_input.pitch = -1
                controller_input.yaw = -1

            elif abs(self.current_state.pos.y) < 250 and abs(self.game_info.opponents[0].pos.y) < 1000:
                #Flip forard.  This can be improved by flipping towards the center of the ball.
                controller_input = AirDodge(Vec3(1/sqrt(2),-1/sqrt(2),0),
                                            self.current_state.jumped_last_frame).input()

            elif self.current_state.wheel_contact and (self.current_state.vel.magnitude() > 1725) and abs(self.game_info.opponents[0].pos.y) < 1000:
                if self.current_state.yaw > ball_angle:
                    direction = 0
                else:
                    direction = 1
                controller_input = JumpTurn(self.current_state, 0, direction).input()
            elif abs(self.current_state.pos.y) < 350:
                controller_input.jump = 1
            elif self.current_state.wheel_contact:
                controller_input = GroundTurn(self.current_state,
                                              self.current_state.copy_state(pos=self.game_info.ball.pos)).input()
                controller_input.boost = 1

                




        else:
            controller_input.throttle = 1




        return controller_input















def update_kickoff_position(game_info, kickoff_position):
        '''
        Returns the current kickoff position.
        Gives "Other" except from the frame the countdown ends until either the ball is hit.
        During this time it returns the position the bot starts in for the kickoff.
        Eventually this will be map specific.  Currently only the standard pool.
        '''

        #if the kickoff has just started, update the position.
        if game_info.is_kickoff_pause and kickoff_position == "Other":
            kickoff_position = check_kickoff_position(game_info.me)

        #If the ball has just moved, reset the kickoff position.
        elif kickoff_position != "Other" and not game_info.is_kickoff_pause:
            kickoff_position = "Other"
        return kickoff_position


def check_kickoff_position(current_state):
    '''
    Returns a string encoding which starting position we have for kickoff.
    This only works for "mostly standard" maps.  I'll worry about the others later.
    '''

    kickoff_dict = {Vec3(0.0, -4608, 10): "Far Back", Vec3(0.0, 4608, 10): "Far Back", Vec3(-1952, -2464, 10): "Right", Vec3(1952, 2464, 10): "Right", Vec3(1952, -2464, 10): "Left", Vec3(-1952, 2464, 10): "Left", Vec3(-256.0, -3840, 10): "Back Right", Vec3(256.0, 3840, 10): "Back Right", Vec3(256.0, -3840, 10): "Back Left", Vec3(-256.0, 3840,10): "Back Left"}


    #Let's figure out which kickoff it is
    for spot in kickoff_dict.keys():
        if abs((current_state.pos - spot).magnitude()) < 500:
            kickoff_position = kickoff_dict[spot]
            break
        else:
            kickoff_position = "Other"


    return kickoff_position
