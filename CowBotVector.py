"""
    CowBotVec2.py

    Contains a 2d vector class...

"""

from math import pi, atan2, sqrt


        
class Vector3:
    def __init__(self, x = 0, y = 0, z = 0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        
        
    def magnitude( self ):
        return sqrt( ( self.x**2 ) + ( self.y**2 ) + ( self.z**2 ) )
        
        
    def __add__(self, val):
        return Vector3(self.x + val.x, self.y + val.y, self.z + val.z)
    
    
    def __sub__(self, val):
        return Vector3(self.x - val.x, self.y - val.y, self.z - val.z)
        
        
    def __str__(self):
        return '{' + ', '.join([self.x, self.y, self.z]) + '}'
    
    
    # Still broken
    def angle_to( self, position = Vector3() ):
        return Vector3()
    
    
    def scalar_multiply( self, scalar = 0.0 ):
        return Vector3( self.x * scalar, self.y * scalar, self.z * scalar )
    
    
    def cross( self, other ):
        return Vector3( 
                self.y * other.z - self.z * other.y,
                self.z * other.x - self.x * other.z,
                self.x * other.y - self.y * other.x
            )
    
    
    def distance( self, other ):
        return sqrt(
            ( other.x - x ) ** 2 + ( other.y - y ) ** 2 + ( other.z - z ) ** 2
        )
    
    
    def dot( self, other = None ):
        if other not None:
            return ( self.x * other.x ) + ( self.y * other.y ) + ( self.z * other.z )
        else:
            return ( self.x ** 2 ) + ( self.y ** 2 ) + ( self.z ** 2 )
    
    
    # TODO: this is slightly more interesting in 3D, so keeping the 2D version for now
    def correction_to(self, ideal):
        # The in-game axes are left handed, so use -x
        current_in_radians = math.atan2(self.y, -self.x)
        ideal_in_radians = math.atan2(ideal.y, -ideal.x)

        correction = ideal_in_radians - current_in_radians

        # Make sure we go the 'short way'
        if abs(correction) > math.pi:
            if correction < 0:
                correction += 2 * math.pi
            else:
                correction -= 2 * math.pi

        return correction

