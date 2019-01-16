from CowBotVector import *
from GameState import *


def make_ball_prediction(ball):
    '''
    Predicts where the ball will be.
    Outputs a list of 3D position lists for the ball's path
    '''

    ball_path = [[ball.pos.x, ball.pos.y, ball.pos.z]]
    ball_path_generator = PathPrediction(ball)

    for step in ball_path_generator:
        ball_path.append(step)

    return ball_path


class PathPrediction:

    def __init__(self, obj):
        self.obj = obj
        self.current_pos = obj.pos
        self.next_step = None
        self.collision = False
        self.current_vel = obj.vel
        self.bounce_count = 0
        self.obj = obj

        #Friction constants
        self.mu = 0.285
        self.Y = 2.0


        #Ball radius and gravity should be pulled game files, since mutators can change it.
        self.ball_radius = 92.75
        self.gravity = - 650

        #frame rate should be pulled from the framework somehow
        self.framerate = 60

        #A Vec3 for the normal to the plane that the ball bounce off of if not touched by a car.
        self.normal = None

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):

        #Estimate, I should get store it higher up as well.
        curve_radius = 250

        is_corner_bounce = self.check_corner_bounce


        test_pos = self.current_pos + self.current_vel.scalar_multiply(1 / self.framerate)

        #Deal with nonstandard maps eventually
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

        
        new_pos = self.current_pos + self.current_vel.scalar_multiply(1 / self.framerate)
        new_vel = self.current_vel

        #Air drag, - 0.03v / second
        new_vel = new_vel.scalar_multiply(1 - (0.03 / self.framerate))

        #Gravity
        new_vel += Vec3(0, 0, self.gravity / self.framerate)


        #Only look at bounces for the ball, not for cars
        if type(self.obj) == Ball and self.collision:

            #Bounces still are a little off, but they're very close (flat walls)
            #Bounce impulse
            orth_vel = self.normal.scalar_multiply(self.current_vel.dot(self.normal))
            new_vel += orth_vel.scalar_multiply(- 1.6)
            

            #Bounce friction
            spin = self.normal.cross(self.obj.omega).scalar_multiply(self.ball_radius)
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
                        
        self.current_pos = new_pos
        self.current_vel = new_vel


        if self.collision:
            self.collision = False
            self.bounce_count += 1

            #This can be extended to cut off for different parameters than the number of bounces
            if self.bounce_count > 3:
                raise StopIteration()
            else:
                return [new_pos.x, new_pos.y, new_pos.z]
        else:
            return [new_pos.x, new_pos.y, new_pos.z]






    def check_corner_bounce(self):
        pass











