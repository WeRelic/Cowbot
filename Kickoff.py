from CowBotVector import *
from rlbot.agents.base_agent import SimpleControllerState
from Mechanics import *
from BallPrediction import *
from Maneuvers import *



def update_kickoff_position(game_info, kickoff_position):
    '''
    Returns the current kickoff position.
    Gives "Other" except from the frame the countdown ends until either the ball is hit.
    During this time it returns the position the bot starts in for the kickoff.
    Eventually this will be map specific.  Currently only the standard pool.
    '''

    #if the kickoff has just started, update the position.k
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




#########################################################################################################

#########################################################################################################

#########################################################################################################


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

        if self.position == "Far Back":
           controller_input = self.far_back(self.game_info.opponent_distance, self.game_info.team_sign, controller_input)

        elif self.position == "Back Left":
            x_sign = - self.game_info.team_sign
            controller_input = self.back_left(self.game_info.opponent_distance, self.game_info.team_sign, x_sign, controller_input)
                
        elif self.position == "Back Right":
            x_sign = self.game_info.team_sign
            controller_input = self.back_right(self.game_info.opponent_distance, self.game_info.team_sign, x_sign, controller_input)

        elif self.position == "Left":
            x_sign = - self.game_info.team_sign
            controller_input = self.left(self.game_info.opponent_distance, self.game_info.team_sign, x_sign, controller_input)

        elif self.position == "Right":
            x_sign = self.game_info.team_sign
            controller_input = self.right(self.game_info.opponent_distance, self.game_info.team_sign, x_sign, controller_input)

        return controller_input

#########################################################################################################

#########################################################################################################


    def far_back(self, opponent_distance, team_sign, controller_input):
        ball_angle = atan2((self.game_info.ball.pos - self.current_state.pos).y,
                           (self.game_info.ball.pos - self.current_state.pos).x)

        if abs(self.current_state.pos.y) > 3000:
            #If we're far away, fast dodge to speed up
            controller_input = FastDodge(self.current_state,
                                         self.current_state.copy_state(pos = Vec3(-250*team_sign,0,0)),
                                         self.old_state,
                                         100, boost_threshold = 1250,
                                         direction = -1).input()
                
        elif abs(self.current_state.pos.y) < 400 and opponent_distance < 1000:
            #Dodge into the ball.
            controller_input = AirDodge(Vec3(1,0,0),
                                        self.current_state.jumped_last_frame).input()

        elif self.current_state.wheel_contact and abs(self.current_state.pos.y) < 1000 and abs(self.game_info.opponents[0].pos.y) < 1000:
            #If we're on the ground, close, and the opponent is also close,
            #jump and turn towards the ball to prep for the dodge.
            if self.current_state.yaw > ball_angle:
                direction = 0
            else:
                direction = 1
            controller_input = JumpTurn(self.current_state, 0, direction).input()

        elif abs(self.current_state.pos.y) < 375:
            #If the opponent is far away and we're close to the ball, take a single jump shot
            controller_input.jump = 1

        elif self.current_state.wheel_contact:
            #Otherwise if we're on the ground, boost and turn towards the ball
            controller_input = GroundTurn(self.current_state,
                                          self.current_state.copy_state(pos=self.game_info.ball.pos)).input()
            controller_input.boost = 1
            
        else:
            #Otherwise turn towards the ball (this might not actually do anything)
            controller_input = GroundTurn(self.current_state,
                                          self.current_state.copy_state(pos=self.game_info.ball.pos)).input()

        return controller_input

    #########################################################################################################


    def back_left(self, opponent_distance, team_sign, x_sign, controller_input):
        ball_angle = atan2((self.game_info.ball.pos - self.current_state.pos).y,
                           (self.game_info.ball.pos - self.current_state.pos).x)

        #Set which boost we want based on team.
        if team_sign == 1:
            first_boost = 7
        else:
            first_boost = 26

        if abs(self.current_state.pos.x) > 80 and abs(self.current_state.pos.y) > 3200:
            #If we're not near the center-line of the field, boost towards the first small boost
            controller_input = GroundTurn(self.current_state,
                                          self.current_state.copy_state(pos=self.game_info.boosts[first_boost].pos+Vec3(0,team_sign*200,0))).input()
            controller_input.boost = 1
                
        elif abs(self.current_state.pos.y) > 1200:
            #If we're far away, fast dodge to speed up.
            controller_input = FastDodge(self.current_state,
                                         self.current_state.copy_state(pos = Vec3(-450*team_sign,0,0)),
                                         self.old_state,
                                         boost_to_use = 100,
                                         oversteer = False,
                                         boost_threshold = 1200,
                                         direction = -1).input()

        elif abs(self.current_state.pos.y) < 350 and opponent_distance < 1000:
            #Dodge into the ball.
            controller_input = AirDodge(Vec3(1,0,0),
                                        self.current_state.jumped_last_frame).input()

        elif self.current_state.wheel_contact and (self.current_state.vel.magnitude() > 2000) and abs(self.game_info.opponents[0].pos.y) < 1000:
            #If we're approaching the ball and the opponent is close, jump turn to prep for the dodge
            if self.current_state.yaw > ball_angle:
                direction = 0
            else:
                direction = 1
            controller_input = JumpTurn(self.current_state, 0, direction).input()
        elif abs(self.current_state.pos.y) < 350:
            #If we're close and the opponent isn't, single jump to shoot on net
            controller_input.jump = 1
        elif self.current_state.wheel_contact:
            #If we're on the ground between stages, boost and turn towards the ball
            controller_input = GroundTurn(self.current_state,
                                          self.current_state.copy_state(pos=self.game_info.ball.pos)).input()
            controller_input.boost = 1
            
        else:
            #Otherwise turn towards the ball (this might not actually do anything)
            controller_input = GroundTurn(self.current_state,
                                          self.current_state.copy_state(pos=self.game_info.ball.pos)).input()

        return controller_input


    #########################################################################################################


    def back_right(self, opponent_distance, team_sign, x_sign, controller_input):
        ball_angle = atan2((self.game_info.ball.pos - self.current_state.pos).y,
                           (self.game_info.ball.pos - self.current_state.pos).x)

        #Set which boost we want based on team.
        if team_sign == 1:
            first_boost = 7
        else:
            first_boost = 26
            
        if abs(self.current_state.pos.x) > 80 and abs(self.current_state.pos.y) > 3200:
            #If we're not near the center-line of the field, boost towards the first small boost
            controller_input = GroundTurn(self.current_state,
                                          self.current_state.copy_state(pos=self.game_info.boosts[first_boost].pos+Vec3(0,team_sign*200,0))).input()
            controller_input.boost = 1
                
        elif abs(self.current_state.pos.y) > 1200:
            #If we're far away, fast dodge to speed up.
            controller_input = FastDodge(self.current_state,
                                         self.current_state.copy_state(pos = Vec3(450 * team_sign,0,0)),
                                         self.old_state,
                                         boost_to_use = 100,
                                         oversteer = False,
                                         boost_threshold = 1200,
                                         direction = 1).input()
                
        elif abs(self.current_state.pos.y) < 350 and opponent_distance < 1000:
            #Dodge into the ball.
            controller_input = AirDodge(Vec3(1,0,0),
                                        self.current_state.jumped_last_frame).input()

        elif self.current_state.wheel_contact and (self.current_state.vel.magnitude() > 2000) and opponent_distance < 1000:
            #If we're approaching the ball and the opponent is close, jump turn to prep for the dodge
            if self.current_state.yaw > ball_angle:
                direction = 0
            else:
                direction = 1
            controller_input = JumpTurn(self.current_state, 0, direction).input()
        elif abs(self.current_state.pos.y) < 350:
            #If we're close and the opponent isn't, single jump to shoot on net
            controller_input.jump = 1
        elif self.current_state.wheel_contact:
            #If we're on the ground between stages, boost and turn towards the ball
            controller_input = GroundTurn(self.current_state,
                                          self.current_state.copy_state(pos=self.game_info.ball.pos)).input()
            controller_input.boost = 1

        else:
            #Otherwise turn towards the ball (this might not actually do anything)
            controller_input = GroundTurn(self.current_state,
                                          self.current_state.copy_state(pos=self.game_info.ball.pos)).input()

        return controller_input



    #########################################################################################################


    

    def left(self, opponent_distance, team_sign, x_sign, controller_input):
        ball_angle = atan2((self.game_info.ball.pos - self.current_state.pos).y,
                           (self.game_info.ball.pos - self.current_state.pos).x)

        #Set which boost we want based on team.
        if team_sign == 1:
            first_boost = 11
        else:
            first_boost = 22

        if self.game_info.boosts[first_boost].is_active:
            #If we haven't taken the small boost yet, drive towards it
            controller_input = GroundTurn(self.current_state,
                                          self.current_state.copy_state(pos = self.game_info.boosts[first_boost].pos + Vec3(x_sign*125,0,0))).input()
            controller_input.boost = 1


        elif abs(self.current_state.pos.y) > 1200:
            #If we've taken the boost but are still far away, fast dodge to speed up`
            controller_input = FastDodge(self.current_state,
                                         self.current_state.copy_state(pos = Vec3(x_sign*500,0,0)),
                                         self.old_state,
                                         boost_to_use = 100,
                                         boost_threshold = 1000,
                                         direction = -1).input()

        elif self.current_state.double_jumped:
            #Once we dodge, turn towards the ball in the air.
            controller_input.yaw = -1

        elif abs(self.current_state.pos.y) < 250 and opponent_distance < 1000:
            #If both players are close to the ball, dodge into the ball.
            print("dodge")
            controller_input = AirDodge(Vec3(1/sqrt(2),-1/sqrt(2),0),
                                        self.current_state.jumped_last_frame).input()

        elif self.current_state.wheel_contact and (self.current_state.vel.magnitude() > 1725) and opponent_distance < 1000:
            #If we're approaching the ball and the opponent is close,
            #jump turn into ball to prep for the dodge
            if self.current_state.yaw > ball_angle:
                direction = 0
            else:
                direction = 1
            controller_input = JumpTurn(self.current_state, 0, direction).input()

        elif abs(self.current_state.pos.y) < 350:
            #If we're close to the ball and the opponent is far away, take a single jump shot.
            controller_input.jump = 1

        elif self.current_state.wheel_contact:
            #If we're on the ground between stages, boost and turn towards the ball
            controller_input = GroundTurn(self.current_state,
                                          self.current_state.copy_state(pos=self.game_info.ball.pos)).input()
            controller_input.boost = 1

        return controller_input

    #########################################################################################################
    
    def right(self, opponent_distance, team_sign, x_sign, controller_input):
        ball_angle = atan2((self.game_info.ball.pos - self.current_state.pos).y,
                           (self.game_info.ball.pos - self.current_state.pos).x)

        #Set which boost we want based on team.
        if team_sign == 1:
            first_boost = 10
        else:
            first_boost = 23
                
        if self.game_info.boosts[first_boost].is_active:
            #If we haven't taken the small boost yet, drive towards it
            controller_input = GroundTurn(self.current_state,
                                          self.current_state.copy_state(pos = self.game_info.boosts[first_boost].pos + Vec3(x_sign*125,0,0))).input()
            controller_input.boost = 1

        elif abs(self.current_state.pos.y) > 1200:
            #If we've taken the boost but are still far away, fast dodge to speed up
            controller_input = FastDodge(self.current_state,
                                         self.current_state.copy_state(pos = Vec3(x_sign*500,0,0)),
                                         self.old_state,
                                         boost_to_use = 100,
                                         boost_threshold = 1000,
                                         direction = 1).input()

        elif self.current_state.double_jumped:
            #Once we dodge, turn towards the ball in the air.
            controller_input.yaw = 1

        elif abs(self.current_state.pos.y) < 250 and opponent_distance < 1000:
            #If both players are close to the ball, dodge into the ball.
            controller_input = AirDodge(Vec3(1/sqrt(2),1/sqrt(2),0),
                                        self.current_state.jumped_last_frame).input()
            
        elif self.current_state.wheel_contact and (self.current_state.vel.magnitude() > 1725) and opponent_distance < 1000:
            #If we're approaching the ball and the opponent is close,
            #jump turn into ball to prep for the dodge
            if self.current_state.yaw > ball_angle:
                direction = 0
            else:
                direction = 1
            controller_input = JumpTurn(self.current_state, 0, direction).input()

        elif abs(self.current_state.pos.y) < 350:
            #If we're close to the ball and the opponent is far away, take a single jump shot.
            controller_input.jump = 1

        elif self.current_state.wheel_contact:
            #If we're on the ground between stages, boost and turn towards the ball
            controller_input = GroundTurn(self.current_state,
                                          self.current_state.copy_state(pos=self.game_info.ball.pos)).input()
            controller_input.boost = 1

        return controller_input



