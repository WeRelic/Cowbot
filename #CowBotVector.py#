"""

"""
 
from math import pi, atan2, sqrt



class Vec3:
    def __init__(self, x = 0, y = 0, z = 0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

        
    def __add__(self, val):
        return Vec3(self.x + val.x, self.y + val.y, self.z + val.z)
    
    
    def __sub__(self, val):
        return Vec3(self.x - val.x, self.y - val.y, self.z - val.z)
        
        
    def __str__(self):
        return '{' + ', '.join([str(self.x), str(self.y), str(self.z)]) + '}'
    
    
    #Still broken
    #This will need an (angle, axis) pair.
    #Alternatively we could use two angles.
    #Also, do we really want "position" here?  Maybe "target"?
#    def angle_to( self, position = Vec3() ):
#        return Vec3()

    #This had a default, scalar = 0.0
    #I think it's better to require an input each time.
    def scalar_multiply( self, scalar ):
        return Vec3( self.x * scalar, self.y * scalar, self.z * scalar )


    def cross( self, other ):
        return Vec3( 
                self.y * other.z - self.z * other.y,
                self.z * other.x - self.x * other.z,
                self.x * other.y - self.y * other.x
            )
    
    
    def distance( self, other ):
        return sqrt(
            ( other.x - x ) ** 2 + ( other.y - y ) ** 2 + ( other.z - z ) ** 2
        )


    #Remvoing the "other = None" case
    #In that case we should be using "magnitude" instead,
    #or at least dot(x,x)
    def dot( self, other ):
            return ( self.x * other.x ) + ( self.y * other.y ) + ( self.z * other.z )
    

    def magnitude( self ):
        return sqrt( ( self.x**2 ) + ( self.y**2 ) + ( self.z**2 ) )


    # TODO: 3D rotations

