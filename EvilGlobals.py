renderer = None


def draw_arc_3d( center, radius, start_angle, delta_angle, steps ):
    '''
    Returns a list of points for the renderer to draw a polyline in a circle
    Orientation is +1 for Counterclockwise
    Orienation is -1 for Clcokwise
    '''

    first_point = center + Vec3(cos(start_angle), sin(start_angle), 0).scalar_multiply(radius)
    locations = [ [first_point.x, first_point.y , 0] ]


    for theta in range(steps):
        next_point = center + Vec3(cos(start_angle + (delta_angle*(theta/steps))), sin(start_angle + (delta_angle*(theta/steps))),0).scalar_multiply(radius)
        locations.append([ next_point.x, next_point.y, 0 ])

    return locations




def draw_circle_3d( center, radius, steps ):
    '''
    Returns a list of points for the renderer to draw a polyline in a circle
    '''

    first_point = center + Vec3(1,0,0).scalar_multiply(radius)
    locations = [ [first_point.x, first_point.y , 0] ]


    for theta in range(steps):
        next_point = center + Vec3(cos((2*pi)*(theta/steps)),sin((2*pi)*(theta/steps)),0).scalar_multiply(radius)
        locations.append([ next_point.x, next_point.y, 0 ])

    return locations
