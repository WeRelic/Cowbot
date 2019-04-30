import rlutilities as utils

from CowBotVector import *
from GameState import *


class BallPredictionSlice:

    def __init__(self, current_slice, prev_slice):

        #Position, rotation, velocity, omega for the current slice
        self.x = current_slice.physics.location.x
        self.y = current_slice.physics.location.y
        self.z = current_slice.physics.location.z
        self.pos = Vec3(self.x, self.y, self.z)
        
        pitch = current_slice.physics.rotation.pitch
        yaw = current_slice.physics.rotation.yaw
        roll = current_slice.physics.rotation.roll
        self.rot = Orientation(pyr = [ pitch, yaw, roll] )

        self.vx = current_slice.physics.velocity.x
        self.vy = current_slice.physics.velocity.y
        self.vz = current_slice.physics.velocity.z
        self.vel = Vec3(self.vx, self.vy, self.vz)
        
        self.omegax = current_slice.physics.angular_velocity.x
        self.omegay = current_slice.physics.angular_velocity.y
        self.omegaz = current_slice.physics.angular_velocity.z
        self.omega = Vec3(self.omegax, self.omegay, self.omegaz)
        
        self.time = current_slice.game_seconds

        ########################################################

        if prev_slice != None:

            #Position, rotation, velocity, omega for the previous slice,
            #assuming we have a previous slice
            self.old_x = prev_slice.physics.location.x
            self.old_y = prev_slice.physics.location.y
            self.old_z = prev_slice.physics.location.z
            self.old_pos = Vec3(self.x, self.y, self.z)
            
            old_pitch = prev_slice.physics.rotation.pitch
            old_yaw = prev_slice.physics.rotation.yaw
            old_roll = prev_slice.physics.rotation.roll
            self.old_rot = Orientation(pyr = [ old_pitch, old_yaw, old_roll] )

            
            self.old_vx = prev_slice.physics.velocity.x
            self.old_vy = prev_slice.physics.velocity.y
            self.old_vz = prev_slice.physics.velocity.z
            self.old_vel = Vec3(self.vx, self.vy, self.vz)
            
            self.old_omegax = prev_slice.physics.angular_velocity.x
            self.old_omegay = prev_slice.physics.angular_velocity.y
            self.old_omegaz = prev_slice.physics.angular_velocity.z
            self.old_omega = Vec3(self.omegax, self.omegay, self.omegaz)
            
            self.old_time = prev_slice.game_seconds

        ########################################################


    def check_rolling(self):
        #Add in a check if contact surface speed is zero.  This needs RLU to find the contact point.
        return False


    def check_bounce(self):

        #Three states: Rolling, Bouncing, Neither.  If we're rolling, we're not bouncing.
        if self.check_rolling():
            return False
        else:
            #Check if acceleration is close to that of just gravity.
            #If it is, then we're at a bounce.
            epsilon = 25
            gravity_accel = -650
            ball_accel = self.vel - self.prev_vel
            if abs(gravity_accel - ball_acel) / (self.current_time - self.old_time) > epsilon:
                return True
            else:
                return False



#############################################################################################

#############################################################################################



class PredictionPath:

    def __init__(self, pred):
        #Assemble a list of the slices in our predicted path.
        self.slices = []
        #For the first slice, there is no previous slice.
        self.slices.append(BallPredictionSlice(pred.slices[0], None))
        for i in range(1, pred.num_slices):
            #For all other slices, we have a previous slice.
            self.slices.append(BallPredictionSlice(pred.slices[i], pred.slices[i - 1]))

    ######################

    def state_at_time(self, time):
        #Return the slice closest to the given time.
        for step in self.slices:
            #60 slices per second.  FPS check?
            if abs(step.time - time) <= 1/60:
                return step
        #If time is too far in the future, it won't be in the prediction
        return None

    ######################

    def check_on_net(self):
        #Check if at some point the ball is between the posts and behind the goal line.
        for step in self.slices.keys():
            if abs(step.x) < 0 and step.y > 5130:
                return "Orange"
            elif abs(step.x) < 0 and step.y < -5130:
                return "Blue"
        return None

    ######################

    def check_corner(self):
        #Eventually this will tell me if the ball is going into a corner (and staying there?),
        #and if so, which one
        return False

    ######################

    def bounces(self):
        #Returns a list of slices in which the ball bounces
        bounces = []
        for step in self.slices:
            if step.check_bouncing():
                bounces.append(step)
        return bounces














def aerial_prediction(game_info, persistent):
    prediction = utils.simulation.Ball(game_info.utils_game.ball)
    ball_predictions = [prediction.location]
    
    for i in range(100):
        
        prediction.step(1/60)
        
        ball_predictions.append(prediction.location)
        
        if prediction.location[2] > 150:
            
            persistent.aerial.action.target = prediction.location
            persistent.aerial.action.arrival_time = prediction.time
            simulation = persistent.aerial.action.simulate()
            
            if (vec3_to_Vec3(simulation.location) - vec3_to_Vec3(persistent.aerial.action.target)).magnitude() < 30:
                break


    return persistent




'''
def make_prediction_path(prediction, end):
    prediction_list = [prediction]
    for i in range(end):
   '''     









