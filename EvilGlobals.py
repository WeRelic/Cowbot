renderer = None
from CowBotVector import *

def draw_arc_3d( center, radius, start_angle, delta_angle, steps ):
    '''
    Returns a list of points for the renderer to draw a polyline in a circle
    Orientation is +1 for Counterclockwise
    Orienation is -1 for Clcokwise
    '''

    first_point = center + Vec3(cos(start_angle), sin(start_angle), 0).scalar_multiply(radius)
    locations = [ [first_point.x, first_point.y , 50] ]


    for step in range(1, steps+1):
        next_angle = start_angle + delta_angle*(step/steps)
        next_point = center + Vec3(cos(next_angle), sin(next_angle),0).scalar_multiply(radius)
        locations.append([ next_point.x, next_point.y, 50 ])

    return locations

def draw_circle_3d( center, radius, steps ):
    '''
    Returns a list of points for the renderer to draw a polyline in a circle
    '''

    first_point = center + Vec3(1,0,0).scalar_multiply(radius)
    locations = [ [first_point.x, first_point.y , 50] ]


    for theta in range(steps):
        next_point = center + Vec3(cos((2*pi)*(theta/steps)),sin((2*pi)*(theta/steps)),0).scalar_multiply(radius)
        locations.append([ next_point.x, next_point.y, 50 ])

    return locations

def draw_ball_path(prediction):
    '''
    Takes a CowBot prediction object, and draws the path on screen.
    '''
    prediction_list = []    
    for i in range(len(prediction.slices)):
        point = [ prediction.slices[i].pos.x, prediction.slices[i].pos.y, prediction.slices[i].pos.z ]
        prediction_list.append(point)
        
    renderer.begin_rendering()
    renderer.draw_polyline_3d( prediction_list, renderer.red())
    renderer.end_rendering()
