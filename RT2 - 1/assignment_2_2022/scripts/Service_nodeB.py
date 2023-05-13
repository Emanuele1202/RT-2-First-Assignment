"""
.. module:: Service_nodeB
    :platform: Unix
    :synopsis: Python module The node provides a service called "/goals_n" that tracks the number of goals reached  

.. moduleauthor:: *Emanuele Buzzurro* S5147474@studenti.unige.it

This is a Python script that defines a ROS node called "n_goal_rc_server". 
The node provides a service called "/goals_n" that tracks the number of goals reached and 
canceled by subscribing to the "/reaching_goal/result" topic, which publishes the status of a
robot's movement to a desired position. The script also defines two functions, "callback()" and "track_goal_n()",
which are used to handle callbacks and service requests, respectively. Finally, the script contains a main function that 
initializes the node and sets up the subscriber and service.

Subscriber: 
	/reaching_goal/result


Publisher: 
	/goals_n

Action:
	/reaching_goal
"""
import rospy
import math
import actionlib
import actionlib.msg
import assignment_2_2022.msg
import time
import sys
import select
from tf import transformations
from std_srvs.srv import *
from geometry_msgs.msg import Point, Pose, Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from assignment_2_2022.msg import Robot_pos_vel
from assignment_2_2022.srv import RC_Goal_num, RC_Goal_numResponse



# Variables initialization
canceled_goal_n = 0;
reached_goal_n = 0;



def callback(msg):
    """
    Callback function for the robot's odometry data.

    Parameters:
        msg: An Odometry message containing the robot's odometry data.
    """

    global canceled_goal_n, reached_goal_n 

    # Get the status 
    status = msg.status.status

    # If status is 2 the goal is canceled
    if status == 2:
        canceled_goal_n = canceled_goal_n + 1

    # If status is 3 the goal is reached
    elif status == 3:
        reached_goal_n  = reached_goal_n  + 1
		


def track_goal_n(req):
    """
    Service callback function.

    Parameters:
        req: A request of type RC_Goal_num.

    Returns:
        A response of type RC_Goal_numResponse.
    """
    
    return  RC_Goal_numResponse(reached_goal_n , canceled_goal_n)



def main():
    """
    Main function.
    """
	
    # Initialize the node
    rospy.init_node('n_goal_rc_server')
	
    # Subscriber to /reaching_goal/result topic to get status
    sub = rospy.Subscriber('/reaching_goal/result', assignment_2_2022.msg.PlanningActionResult, callback)
    
    # Provide the service /n_goal
    s = rospy.Service('/goals_n', RC_Goal_num, track_goal_n)
    
    # Wait
    rospy.spin()
    
    

if __name__ == "__main__":
    main()
