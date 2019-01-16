from GameState import *
from CowBotVector import *
from NaiveSteering import *
from Testing import *
from math import sin, cos, pi, atan2

#This will be phased out of this file once I get through testing.
from rlbot.agents.base_agent import SimpleControllerState

def aerial_rotations(current_state, target_state, old_state, time, old_time):
    '''
    Returns a (pitch, yaw, roll) tuple of controller inputs to turn the car from the starting
    rotation towards the desired rotation. start_rot and target_rot are in (pitch, yaw, roll) form.
    '''
    ''''''

    controller_state = SimpleControllerState()

    start_rot = current_state.rot
    start_omega = current_state.omega
    #target_rot = target_state.rot
    #target_omega = target_state.omega
    old_rot = old_state.rot
    old_omega = old_state.omega

    target_rot = [0, atan2(current_state.vel.y, current_state.vel.x) , 0]

    controller_state = zero_omega_recovery(start_rot, 0, [0,atan2(current_state.vel.y, current_state.vel.x),0], 0, old_rot, old_omega, time, old_time)

    return controller_state

def zero_omega_recovery(start_rot, start_omega, target_rot, target_omega, old_rot, old_omega, time, old_time):
    '''
    Returns a controller input to turn the car from the starting rotation towards the
    desired rotation. start_rot, target_rot, and old_rot are in (pitch, yaw, roll) form.
    This just uses three independent PIDs for each of pitch, yaw, roll.
    '''

    controller_state = SimpleControllerState()

    #First assume start_omega = target_omega = 0

    
    pitch_error = target_rot[0] - start_rot[0]
    if pitch_error > pi / 2:
        pitch_error -= pi
    elif pitch_error < - pi / 2:
        pitch_error += pi

    yaw_error = target_rot[1] - start_rot[1]
    if yaw_error > pi:
        yaw_error -= 2*pi
    elif yaw_error < -pi:
        yaw_error += 2*pi

    roll_error = target_rot[2] - start_rot[2]
    if roll_error > pi:
        roll_error -= 2*pi
    elif roll_error < -pi:
        roll_error += 2*pi



    old_pitch_error = start_rot[0] - old_rot[0]
    if old_pitch_error > pi / 2:
        old_pitch_error -= pi
    elif old_pitch_error < - pi / 2:
        old_pitch_error += pi

    old_yaw_error = start_rot[1] - old_rot[1]
    if old_yaw_error > pi:
        old_yaw_error -= 2*pi
    elif old_yaw_error < -pi:
        old_yaw_error += 2*pi

    old_roll_error = start_rot[2] - old_rot[2]
    if old_roll_error > pi:
        old_roll_error -= 2*pi
    elif old_roll_error < -pi:
        old_roll_error += 2*pi



    pitch_error_derivative = one_frame_derivative(pitch_error, old_pitch_error, time, old_time)
    yaw_error_derivative = one_frame_derivative(yaw_error, old_yaw_error, time, old_time)
    roll_error_derivative = one_frame_derivative(roll_error, old_roll_error, time, old_time)

    #Will need testing for coefficients
    #Check that this is reasonable, at the very least the coefficients need tuning.
    pitch_correction = 1 * pitch_error - .015 * pitch_error_derivative
    yaw_correction = 1 * yaw_error - .02 * yaw_error_derivative
    roll_correction = 1 * roll_error + .01 * roll_error_derivative


    #Normalize
    if pitch_correction > 1:
        pitch_correction = 1
    elif pitch_correction < -1:
        pitch_correction = -1

    if yaw_correction > 1:
        yaw_correction = 1
    elif yaw_correction < -1:
        yaw_correction = -1

    if roll_correction > 1:
        roll_correction = 1
    elif roll_correction < -1:
        roll_correction = -1

    #Final controller input values
    controller_state.pitch = pitch_correction
    controller_state.yaw = yaw_correction
    controller_state.roll = roll_correction
    controller_state.throttle = 1

    return controller_state




def one_frame_derivative(f, old_f, time, old_time):
    return (f - old_f) / (1/60)
















































def pyr_to_quat(pitch, yaw, roll):
    '''
    Converts a pitch, yaw, roll representation of a 3d rotation and returns the quaternion representation.
    '''

    w = cos(roll / 2)
    x = cos(yaw) * cos(pitch) * sin(roll / 2)
    y = sin(yaw) * cos(pitch) * sin(roll / 2)
    z = sin(pitch) * sin(roll / 2)


    return Quaternion(w, x, y, z)
    


class Quaternion():


    def __init__(self, w, x, y, z):
        self.w = w
        self.x = x
        self.y = y
        self.z = z








