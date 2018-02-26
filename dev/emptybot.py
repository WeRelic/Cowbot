from math import pi, cos, sin, atan2

URotationToRadians = math.pi / float(32768)

class Agent:
    def __init__(self, name, team, index):
        self.name = name
        self.team = team  # 0 towards positive goal, 1 towards negative goal.
        self.index = index

    def get_output_vector(self, game_tick_packet):

        return [
            0.0, # throttle
            0.0, #steer
            0.0, # pitch
            0.0, # yaw
            0.0, # roll
            0, # jump
            0, # boost
            0  # handbrake
        ]


class Vector2:
    def __init__(self, x = 0.0, y = 0.0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, val):
        return Vector2( self.x + val.x, self.y + val.y)

    def __sub__(self,val):
        return Vector2( self.x - val.x, self.y - val.y)

    def correction_to(self, ideal):
        # The in-game axes are left handed, so use -x
        correction = math.atan2(ideal.y, -ideal.x) - math.atan2(self.y, -self.x)

        # Make sure we go the 'short way'
        if abs(correction) > math.pi:
            if correction < 0:
                correction += 2 * pi
            else:
                correction -= 2 * pi

        return correction


def get_car_facing_vector(car):

    pitch = float(car.Rotation.Pitch)
    yaw = float(car.Rotation.Yaw)

    facing_x = cos(pitch * URotationToRadians) * cos(yaw * URotationToRadians)
    facing_y = cos(pitch * URotationToRadians) * sin(yaw * URotationToRadians)

    return Vector2(facing_x, facing_y)
