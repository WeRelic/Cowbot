'''
This file defines the GamePlan class.  The GamePlan object is 
used to keep track of multiple levels of planning, across frames.
'''


class GamePlan():

    def __init__(self):
        self.old_plan = ["Ball", None, None]
        self.layers = ["Ball", None, None]

        self.path = None
        self.path_lock = False




