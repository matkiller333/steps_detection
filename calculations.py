import math
import matplotlib.pyplot as plt
import numpy as np
import os


def Check_wd():     # Makes sure that the working dir is correct before proceeding
    try:
        os.chdir('steps_detection')
        print('successfully changed working directory')
    except:
        print('Already in steps_detection directory')


def Angles_over_time(temp_3d, duration, save=0):
    Check_wd()
    angles = [[], [], [], [], []]
    for joint in range(5):
        side = Get_best_overall(temp_3d, joint, duration-1)
        for t in range(duration-1):
            angles[joint].append(Get_angle(temp_3d[t], joint, side))

    x = np.linspace(0, duration-1, duration-1)
    for i in range(5):
        plt.subplot(2, 3, (i + 1)).plot(x, angles[i])
    if save:
        plt.savefig('output\\matplotlib\\temp_graph.png', transparent=True)
        for i in range(5):
            plt.clf()
            plt.plot(x, angles[i])
            name = 'output\\matplotlib\\temp_graph_'+str(i)+'.png'
            plt.savefig(name, transparent=True)
    else:
        plt.show()
    return angles


def Get_angle(keypoints, joint, side):
    point_a, point_b, point_c = Get_points(keypoints, joint, side)
    if point_a[2] == 0 or point_b[2] == 0 or point_c[2] == 0:
        angle_b = np.nan
    else:
        # uses the pythagorean theorem to find lines in the triangle formed by the 3 important keypoints
        line_a = math.sqrt((point_c[0] - point_b[0])**2 + (point_c[1] - point_b[1])**2)
        line_b = math.sqrt((point_a[0] - point_c[0])**2 + (point_a[1] - point_c[1])**2)
        line_c = math.sqrt((point_a[0] - point_b[0])**2 + (point_a[1] - point_b[1])**2)
        # uses the cos law to find the angle of interest in the triangle
        # angle_a = math.acos(((line_b**2 + line_c**2 - line_a**2)/(2*line_b*line_c))*math.pi/180)
        angle_b = math.acos(((line_a ** 2 + line_c ** 2 - line_b ** 2) / (2 * line_a * line_c)))
    return angle_b * 180 / np.pi


def Get_points(keypoints, joint, side):
    person = 0  # place holder until I figure out a way to get a specific person in the video. For now takes the 1st one
    key_0 = []
    key_1 = []
    if joint == 'ankle' or joint == 0:  # angle from knee, heel, toe
        set_0 = keypoints.iloc[person, 11], keypoints.iloc[person, 25], keypoints.iloc[person, 23]  # right side
        set_1 = keypoints.iloc[person, 14], keypoints.iloc[person, 22], keypoints.iloc[person, 20]  # left side

    elif joint == 'knee' or joint == 1:  # angle from heel, knee, hip
        set_0 = keypoints.iloc[person, 25], keypoints.iloc[person, 11], keypoints.iloc[person, 10]  # right side
        set_1 = keypoints.iloc[person, 22], keypoints.iloc[person, 14], keypoints.iloc[person, 13]  # left side

    elif joint == 'hip' or joint == 2:  # angle from knee, hip, shoulder
        set_0 = keypoints.iloc[person, 11], keypoints.iloc[person, 10], keypoints.iloc[person, 3]  # right side
        set_1 = keypoints.iloc[person, 14], keypoints.iloc[person, 13], keypoints.iloc[person, 6]  # left side

    elif joint == 'shoulder' or joint == 3:  # angle from hip, shoulder, elbow
        set_0 = keypoints.iloc[person, 10], keypoints.iloc[person, 3], keypoints.iloc[person, 4]  # right side
        set_1 = keypoints.iloc[person, 13], keypoints.iloc[person, 6], keypoints.iloc[person, 7]  # left side

    elif joint == 'elbow' or joint == 4:  # angle from shoulder, elbow, wrist
        set_0 = keypoints.iloc[person, 3], keypoints.iloc[person, 4], keypoints.iloc[person, 5]  # right side
        set_1 = keypoints.iloc[person, 6], keypoints.iloc[person, 7], keypoints.iloc[person, 8]  # left side

    if side == 'right':
        point_a, point_b, point_c = set_0
    elif side == 'left':
        point_a, point_b, point_c = set_1
    elif side == 'get':
        key_0 = set_0
        key_1 = set_1

    if side == 'get': return key_0, key_1
    return point_a, point_b, point_c


def Get_quality(points):
    quality = points[0][2] * 0.25 + points[1][2] * 0.5 + points[2][2] * 0.25
    if points[0][2] == 0 or points[1][2] == 0 or points[2][2] ==0: quality = 0
    return quality


def Get_best_quality(set_0, set_1):
    if Get_quality(set_0) > Get_quality(set_1):
        return set_0
    elif Get_quality(set_0) < Get_quality(set_1):
        return set_1
    elif Get_quality(set_0) == Get_quality(set_1):
        return set_0


def Get_best_overall(keypoints_all, joint, length):
    overall_0, overall_1 = 0, 0
    for i in range(length):
        keypoints_both = Get_points(keypoints_all[i], joint, side='get')
        if Get_quality(keypoints_both[0]) == 0: overall_0 -= 1
        else:
            overall_0 = overall_0 + Get_quality(keypoints_both[0])
        if Get_quality(keypoints_both[1]) == 0: overall_1 -= 1
        else:
            overall_1 = overall_1 + Get_quality(keypoints_both[1])
    if overall_1 > overall_0: return 'left'
    elif overall_0 > overall_1: return 'right'
    else: return 'left'
