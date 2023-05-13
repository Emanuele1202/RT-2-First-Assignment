#!/usr/bin/env python
"""
## \file
# \brief A node that moves a robot to a desired position and performs wall following
#
# This node moves a robot to a desired position using a go-to-point service
# and performs wall following using a wall follower service. The node subscribes
# to odometry and laser scan topics, and uses the TF package to obtain the yaw angle.
#
# \author Author Name <author_email>
#
# \date Date created
#
# \version 1.0.0
#
# \license License information
The purpose of this module is to navigate a mobile robot to a specified point in a 2D space using ROS.
"""
import rospy
from geometry_msgs.msg import Point, Pose, Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
import math
import actionlib
import actionlib.msg
import assignment_2_2022.msg
from tf import transformations
from std_srvs.srv import *
import time

# Service clients
srv_client_go_to_point_ = None
srv_client_wall_follower_ = None

# Robot position and orientation
yaw_ = 0
yaw_error_allowed_ = 5 * (math.pi / 180)  # 5 degrees
position_ = Point()
pose_ = Pose()

# Target position
desired_position_ = Point()
desired_position_.z = 0

# Laser scan data
regions_ = None

# State machine
state_desc_ = ['Go to point', 'wall following', 'done']
state_ = 0  # 0 - go to point, 1 - wall following, 2 - done, 3 - canceled

def clbk_odom(msg):
    """
    Callback function for the robot's odometry data.
    
    Parameters:
        msg: An Odometry message containing the robot's odometry data.
    """
    global position_, yaw_, pose_

    # position
    position_ = msg.pose.pose.position
    pose_ = msg.pose.pose

    # yaw
    quaternion = (
        msg.pose.pose.orientation.x,
        msg.pose.pose.orientation.y,
        msg.pose.pose.orientation.z,
        msg.pose.pose.orientation.w)
    euler = transformations.euler_from_quaternion(quaternion)
    yaw_ = euler[2]

def clbk_laser(msg):
    """
    Callback function for the laser scan data.
    
    Parameters:
        msg: A LaserScan message containing the laser scan data.
    """
    global regions_
    regions_ = {
        'right':  min(min(msg.ranges[0:143]), 10),
        'fright': min(min(msg.ranges[144:287]), 10),
        'front':  min(min(msg.ranges[288:431]), 10),
        'fleft':  min(min(msg.ranges[432:575]), 10),
        'left':   min(min(msg.ranges[576:719]), 10),
    }

def change_state(state):
    """
    Change the state of the state machine.
    
    Parameters:
        state: An integer representing the new state of the state machine.
    """
    global state_, state_desc_
    global srv_client_wall_follower_, srv_client_go_to_point_
    state_ = state
    log = "state changed: %s" % state_desc_[state]
    rospy.loginfo(log)
    if state_ == 0:
        resp = srv_client_go_to_point_(True)
        resp = srv_client_wall_follower_(False)
    if state_ == 1:
        resp = srv_client_go_to_point_(False)
        resp = srv_client_wall_follower_(True)
    if state_ == 2:
        resp = srv_client_go_to_point_(False)
        resp = srv_client_wall_follower_(False)

def normalize_angle(angle):
    """
    Normalize an angle to be in the range [-pi, pi].
    
    Parameters:
        angle: A float representing the angle to be normalized.
        
    Returns:
        The normalized angle.
    """
    if(math.fabs(angle) > math.pi):
        angle = angle - (2 * math.pi
