from math import cos, sin

import rlbot.utils.game_state_util as framework
from rlutilities.linear_algebra import mat3, vec3

from CowBotVector import Vec3

############################
#Types transformations for other frameworks
############################

def rot_to_mat3(rot, team_sign):
    return mat3( team_sign*rot.front.x, team_sign*rot.left.x, team_sign*rot.up.x,
                 team_sign*rot.front.y, team_sign*rot.left.y, team_sign*rot.up.y,
                 rot.front.z, rot.left.z, rot.up.z )

def pyr_to_matrix(pyr):
    pitch = pyr[0]
    yaw = pyr[1]
    roll = pyr[2]

    front = Vec3(cos(yaw)*cos(pitch),
                 sin(yaw)*cos(pitch),
                 sin(pitch))
    left = Vec3(-cos(yaw)*sin(pitch)*sin(roll) - sin(yaw)*cos(roll),
                -sin(yaw)*sin(pitch)*sin(roll) + cos(yaw)*cos(roll),
                cos(pitch)*sin(roll))
    up = Vec3(-cos(yaw)*sin(pitch)*cos(roll) + sin(yaw)*sin(roll),
              -sin(yaw)*sin(pitch)*cos(roll) - cos(yaw)*sin(roll),
              cos(pitch)*cos(roll))
    
    return [front, left, up]


def Vec3_to_Vector3(vector):
    return framework.Vector3(x = vector.x, y = vector.y, z = vector.z)

def Vec3_to_vec3(vector, team_sign):
    return vec3(team_sign*vector.x, team_sign*vector.y, vector.z)

def vec3_to_Vec3(vector, team_sign):
    return Vec3(team_sign*vector[0], team_sign*vector[1], vector[2])
