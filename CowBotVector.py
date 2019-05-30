"""

"""
 
from math import pi, atan2, sqrt, sin, cos



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
    
    def __list__(self):
        return [self.x, self.y, self.z]

    def __neg__(self):
        return Vec3(-self.x, -self.y, -self.z)


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


    def dot( self, other ):
            return ( self.x * other.x ) + ( self.y * other.y ) + ( self.z * other.z )
    
    def magnitude( self ):
        return sqrt( ( self.x**2 ) + ( self.y**2 ) + ( self.z**2 ) )

    def normalize( self ):
        return self.scalar_multiply( 1/(self.magnitude()) )

    def normal_2d( self ):
        '''
        Return the 2d normal vector
        '''
        return Vec3(self.y, -self.x, 0)

    def to_2d( self ):
        '''
        This just discards the z component
        '''
        return Vec3(self.x, self.y, 0)






    
