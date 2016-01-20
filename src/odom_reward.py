# reward progress around track by breaking it into larg(ish) grid squares
# and giving +1 if we progress to the next square & -5 if we back a square.
# the baseline track was designed to "fit" into simple coarse squares to
# make this reward calc simpler.

# HARDCODED TO TRACK1

import rospy
from nav_msgs.msg import Odometry
import sys
import time

REWARD_MOVE_FORWARD_A_BIT = 1
REWARD_MOVE_FORWARD_ONE_GRID = 10
REWARD_MOVE_BACKWARD_ONE_GRID = -30

def close(p1, p2):
    diff = abs(p1.x-p2.x) + abs(p1.y-p2.y) + abs(p1.z-p2.z)
    return diff < 1e-6

def grid_pt_for_pos(pos):
    gx, gy = int(pos.x / 2), int(pos.y / 2)  # map ref -> grid ref is scale of 2
    return gx + 5 * gy  # bottom left (0, 0) -> 0 & top right (4, 4) -> 24

class OdomReward(object):

    # clockwise around track1 
    GRID_ORDER = [22, 23, 24, 19, 14, 9, 4, 3, 2, 7, 12, 11, 10, 15, 20, 21]
    LEN = len(GRID_ORDER)

    def __init__(self, robot_id):
        self.robot_id = robot_id
        self.reset()
        rospy.Subscriber("/robot%s/odom" % self.robot_id, Odometry, self.odom_callback)

    def reset(self):
        self.last_pos = None        # position at last reward() call
        self.latest_pos = None      # constantly updated from callback

    def odom_callback(self, msg):
        self.latest_pos = msg.pose.pose.position

    def reward(self):
        if self.latest_pos == None:
            # no callbacks yet
            return 0

        if self.last_pos == None:
            # just started, record pos for next reward() call
            self.last_pos = self.latest_pos
            return 0
                
        # check indexs of grid points in GRID_ORDER
        latest_grid_idx = OdomReward.GRID_ORDER.index(grid_pt_for_pos(self.latest_pos))
        last_grid_idx = OdomReward.GRID_ORDER.index(grid_pt_for_pos(self.last_pos))
        r = None
        wrap = len(OdomReward.GRID_ORDER)
        if latest_grid_idx == last_grid_idx:
            # have cross a grid, but at least reward if we've moved
            if close(self.latest_pos, self.last_pos):
                r = 0
            else:
                r = REWARD_MOVE_FORWARD_A_BIT
        elif latest_grid_idx == (last_grid_idx + 1) % wrap:
            r = REWARD_MOVE_FORWARD_ONE_GRID
        elif latest_grid_idx == (last_grid_idx - 1) % wrap:
            r = REWARD_MOVE_BACKWARD_ONE_GRID
        else:
            # robot has been reset?
            print >>sys.stderr, "odom reward; reset?"
            self.last_pos = None
            return 0
    
        self.last_pos = self.latest_pos
        return r
    
