"""
    CowBotVec2.py

    Contains a 2d vector class...

"""

from math import pi, atan2



class Vector2:
    def __init__(self, x = 0.0, y = 0.0):
        self.x = x
        self.y = y

    def __add__(self, val):
        return Vector2( self.x + val.x, self.y + val.y)

    def __sub__(self,val):
        return Vector2( self.x - val.x, self.y - val.y)
        
    def __str__(self):
        return "{" + "{0.x},{0.y}".format(self) + "}

    def correction_to(self, ideal):
        # The in-game axes are left handed, so use -x
        correction = atan2(ideal.y, -ideal.x) - atan2(self.y, -self.x)

        # Make sure we go the 'short way'
        if abs(correction) > pi:
            if correction < 0:
                correction += 2 * pi
            else:
                correction -= 2 * pi

        return correction
