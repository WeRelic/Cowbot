from CowBotVector import *


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

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):

        
        new_pos = self.current_pos + self.current_vel.scalar_multiply(1 / 60)
        new_vel = self.current_vel.scalar_multiply(0.9995) + Vec3(0, 0, -650/60)

        if abs(new_pos.x) > 5140 or abs(new_pos.y) > 4120 or new_pos.z > 2044 or new_pos.z < 0:
            self.collision = True


        self.current_pos = new_pos
        self.current_vel = new_vel


        if self.collision:
            raise StopIteration()
        else:
            return [new_pos.x, new_pos.y, new_pos.z]


















