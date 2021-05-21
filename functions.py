import os
import json
import csv
import pandas as pd

body_part_list = ['Nose', 'Neck', 'RShoulder', 'RElbow', 'RWrist', 'LShoulder', 'LElbow', 'LWrist', 'MidHip', 'RHip',
                     'RKnee', 'RAnkle', 'LHip', 'LKnee', 'LAnkle', 'REye', 'LEye', 'REar', 'LEar', 'LBigToe',
                     'LSmallToe', 'LHeel', 'RBigToe', 'RSmallToe', 'RHeel']

short = 'C:\\openpose_self_branch\\steps_detection'
temp_3d = []
df_3d = pd.DataFrame(columns=[body_part_list])  # create empty df w/ good body part names as columns
df_3d['person_id'] = []
cols = df_3d.columns.tolist()
df_3d = df_3d[cols[-1:] + cols[:-1]]  # add a column named person_id and move it in 1ast position


def change_wd_open():     # Changes wd to openpose as the commands using open pose need to be executed from there
    try:
        os.chdir('C:\\openpose')
        print('successfully changed working dir to C:\\openpose')
    except:
        print('Already in C:\\openpose directory')


def change_wd_steps():     # changes wd to steps_detection path
    try:
        os.chdir(short)
        print('successfully changed working dir to C:\\openpose')
    except:
        print('Already in C:\\openpose directory')


def Append(df_clean, df_2d):
    for i in df_clean.index:  # iterates over all individuals
        data_2d_temp = [
            df_clean.person_id[i]]  # creates a placeholder for temporary row data and places the first data in

        for j in range(int(len(df_clean.pose_keypoints_2d[i]) / 3)):  # iterates over a third of the dataframe
            body_part_temp = [df_clean.pose_keypoints_2d[i][3 * j], df_clean.pose_keypoints_2d[i][3 * j + 1],
                              df_clean.pose_keypoints_2d[i][3 * j + 2]]
            data_2d_temp.append(body_part_temp)  # then append that list to the data of one individual

        df_2d.loc[len(df_2d)] = data_2d_temp
    return df_2d


def Fetch_keypoints(start, end, rate, name, path=short+"\\output\\keypoints", pattern=df_3d):
                            # Fetches the keypoints from path
                            # and feeds them in Append, then creates one massive list containing all frames keypoints
    if end == 'max':
        end = len(os.listdir(path))
    else:
        end = int(end*rate)
    start = int(start*rate)
    loop_range = end-start

    for k in range(1, loop_range):  # iterates over the range of frames given by the user
        with open('{}/{}_{:012d}_keypoints.json'.format(path, name+'_processed', k)) as json_file:  # formats the path name
            data = json.load(json_file)  # and retrieves the keypoints

        df_clean = pd.json_normalize(data, 'people')  # formatting
        df_clean = df_clean.drop(df_clean.iloc[:, 2:9], axis=1)
        df_2d = pd.DataFrame().reindex_like(pattern)

        temp_3d.append(Append(df_clean, df_2d))
    return temp_3d, loop_range


def Write_csv(data):
    with open('test.csv', 'w+', newline='') as file:
        write = csv.writer(file)
        write.writerows(data)
