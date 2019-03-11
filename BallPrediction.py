from CowBotVector import *
from GameState import *


class BallPredictionSlice:

    def __init__(self, current_slice, prev_slice):

        #Position, rotation, velocity, omega for the current slice
        self.x = current_slice.physics.location.x
        self.y = current_slice.physics.location.y
        self.z = current_slice.physics.location.z
        self.pos = Vec3(self.x, self.y, self.z)
        
        self.pitch = current_slice.physics.rotation.pitch
        self.yaw = current_slice.physics.rotation.yaw
        self.roll = current_slice.physics.rotation.roll
        
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
            
            self.old_pitch = prev_slice.physics.rotation.pitch
            self.old_yaw = prev_slice.physics.rotation.yaw
            self.old_roll = prev_slice.physics.rotation.roll
            
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





































'''
This is my own implementation of basic ball prediction.  Will be obsolete once the above is complete.


def renderer_ball_prediction(ball):
 
    Predicts where the ball will be.
    Outputs a list of 3D position lists for the ball's path for renderer()
 

    ball_path = [[ball.pos.x, ball.pos.y, ball.pos.z]]
    ball_path_generator = PathPrediction(ball)

    for step in ball_path_generator:
        ball_path.append([step[0].x, step[0].y, step[0].z])

    return ball_path


def make_ball_prediction(ball, fps, target = None):

    Predicts where the ball will be.
    Returns the ballk's location at time, or when target is achieved.


    ball_path_generator = PathPrediction(ball)

    #Return the position of the ball when target is achieved.
    if target != None and target[0] == 'x':
        for step in ball_path_generator:
            if abs(step[0].x - target[1]) < 50:
                return step[0]

    if target != None and target[0] == 'y':
        for step in ball_path_generator:
            if abs(step[0].y - target[1]) < 50:
                return step[0]

    if target != None and target[0] == 'z':
        for step in ball_path_generator:
            if abs(step[0].z - target[1]) < 50:
                return step[0]

    if target != None and target[0] == 't':
        for step in ball_path_generator:
            #Catches float errors, but every now and then we'll be a frame off.
            if abs(target[1] - step[1]) <= 1/(fps-1):
                return step[0]

    #If no target is specified, don't do anything
    if target == None:
        pass



    #return ball_pos

class PathPrediction:

    def __init__(self, obj):
        self.obj = obj
        self.current_pos = obj.pos
        self.next_step = None
        self.collision = False
        self.current_vel = obj.vel
        self.bounce_count = 0
        self.obj = obj
        self.time = 0
        self.omega = obj.omega

        #Friction constants
        self.mu = 0.285
        self.Y = 2.0


        #Ball radius and gravity should be pulled game files, since mutators can change it.
        self.ball_radius = 92.75
        self.gravity = - 650

        #Frame rate should be pulled from the framework somehow
        self.fps = 60

        #A Vec3 for the normal to the plane that the ball bounce off of if not touched by a car.
        self.normal = None

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):

        #Estimate, I should get store it higher up as well.
        curve_radius = 250

        #is_corner_bounce = self.check_corner_bounce

        self.time += 1/self.fps
        test_pos = self.current_pos + self.current_vel.scalar_multiply(1 / self.fps)

        #Realize when the ball collides with a wall
        #Deal with nonstandard maps and corners eventually
        if (test_pos.x > 4096 - self.ball_radius) and (self.current_vel.x > 0):
            self.collision = True
            self.normal  = Vec3(-1, 0, 0)

        elif (test_pos.x < - (4096 - self.ball_radius)) and (self.current_vel.x < 0):
            self.collision = True
            self.normal = Vec3(1, 0, 0)

        elif (test_pos.y > 5120 - self.ball_radius) and (self.current_vel.y > 0):
            self.collision = True
            self.normal = Vec3(0, -1, 0)

        elif (test_pos.y < - (5120 - self.ball_radius)) and (self.current_vel.y < 0):
            self.collision = True
            self.normal = Vec3(0, 1, 0)

        elif (test_pos.z > 2044 - self.ball_radius) and (self.current_vel.z > 0):
            self.collision = True
            self.normal = Vec3(0, 0, -1)

        elif (test_pos.z < self.ball_radius) and (self.current_vel.z < 0):
            self.collision = True
            self.normal = Vec3(0, 0, 1)

        #Update for next tick
        new_pos = self.current_pos + self.current_vel.scalar_multiply(1 / self.fps)
        new_vel = self.current_vel

        #Air drag, - 0.03v / second
        new_vel = new_vel.scalar_multiply(1 - (0.03 / self.fps))

        #Gravity
        new_vel += Vec3(0, 0, self.gravity / self.fps)


        #Only look at bounces for the ball, not for cars
        if type(self.obj) == Ball and self.collision:

            #Bounces still are a little off, but they're very close (flat walls)
            #Bounce impulse
            orth_vel = self.normal.scalar_multiply(self.current_vel.dot(self.normal))
            new_vel += orth_vel.scalar_multiply(- 1.6)
            
            #Bounce friction
            spin = self.normal.cross(self.omega).scalar_multiply(self.ball_radius)
            parallel_vel = self.current_vel - orth_vel
            slip = spin + parallel_vel
            if slip.magnitude() != 0:
                ratio = orth_vel.magnitude() / slip.magnitude()
                coef = -(self.mu * (min(1, self.Y*ratio)))
                new_vel += slip.scalar_multiply(coef)
                #rest the normal vector
                self.normal = None

            self.current_pos = new_pos
            self.current_vel = new_vel

        #Update position and velocity to continue
        self.current_pos = new_pos
        self.current_vel = new_vel


        #Check number of bounces to end prediction.
        #Can be replaced by a timer, etc.
        if self.collision:
            self.collision = False
            self.bounce_count += 1

            #This can be extended to cut off for different parameters than the number of bounces
            if self.bounce_count > 3:
                raise StopIteration()
            else:
                return Vec3(new_pos.x, new_pos.y, new_pos.z), self.time
        else:
            return Vec3(new_pos.x, new_pos.y, new_pos.z), self.time
'''










