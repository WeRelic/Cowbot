"""
    CowBotTactics.py

    This script handles mass imports for the Tactical system.

    This system is built on the various implemented control sequences.

"""
from CowBotControlSequence import *
from CowBot_HalfFlip import *
from CowBot_Kickoffs import *
from enum import Enum


class KickoffType( Enum ):
    KICKOFF_LDIAG  = 0,
    KICKOFF_RDIAG  = 1,
    KICKOFF_LSIDE  = 2,
    KICKOFF_RSIDE  = 3,
    KICKOFF_GOALIE = 4
    

class DefenceSequenceType( Enum ):
    DEF_TYPE_SHADOW          = 0,
    DEF_TYPE_BACKBOARD       = 1,
    DEF_TYPE_MIDFIELD        = 2


class OffenceSequenceType( Enum ):
    OFF_TYPE_FLICK     = 0,
    OFF_TYPE_DRIBBLE   = 1,
    OFF_TYPE_AERIAL    = 2,
    OFF_TYPE_CEILING   = 3,
    OFF_TYPE_BACKBOARD = 4,


class GeneralSequenceType( Enum ):
    GEN_TYPE_DEMO              = 0,
    GEN_TYPE_STARVE            = 1,
    GEN_TYPE_GROUND_CHALLENGE  = 2,
    GEN_TYPE_AERIAL_CHALLENGE  = 3,
    GEN_TYPE_CATCH             = 4,
    GEN_TYPE_NET_ROTATE        = 5,
    GEN_TYPE_BOOST_ROTATE      = 6
    

class ControlSequenceType( Enum ):
    CTRL_TYPE_DEFENCE = 0,
    CTRL_TYPE_KICKOFF = 1,
    CTRL_TYPE_OFFENCE = 2,
    CTRL_TYPE_GENERAL = 3


def SelectControlSequence( seq_type = None ):
    """
        Use this function to select the general type of control sequence you want.
    """
    pass
