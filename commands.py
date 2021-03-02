import pandas as pd
import json
import argparse
import os
import subprocess
import csv
from calculations import *
from moviepy.editor import *

body_part_list = ['Nose', 'Neck', 'RShoulder', 'RElbow', 'RWrist', 'LShoulder', 'LElbow', 'LWrist', 'MidHip', 'RHip',
                     'RKnee', 'RAnkle', 'LHip', 'LKnee', 'LAnkle', 'REye', 'LEye', 'REar', 'LEar', 'LBigToe',
                     'LSmallToe', 'LHeel', 'RBigToe', 'RSmallToe', 'RHeel']
# frames = 204  # Number of frames to analyze

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


parser = argparse.ArgumentParser(description='Creates a list of body parts keypoints from a video')
parser.add_argument('input_path', help='Path of the video to analyze')
parser.add_argument('--preview', action='store_true', help='displays start frame w/ individuals numbered')  # unfinished
parser.add_argument('--process', action='store_true', help='outputs a list containing keypoints of all frames')
parser.add_argument('--start', nargs='?', type=int, default=0, help='sets a start frame')
parser.add_argument('--end', nargs='?', default='max', help='sets an end frame')
parser.add_argument('--write_csv', action='store_true', help='Indicates that you want the angles to be outputted as a CSV file')
parser.add_argument('--write_graph', action='store_true', help='return angles instead of plotting them directly')

args = parser.parse_args()
video_name = os.path.basename(args.input_path)
video_name_free = os.path.splitext(video_name)[0]  # video name w/o extension
path_free = args.input_path.replace(video_name_free, '')  # Path w/o the video name
command = 'build\\x64\\Release\\OpenPoseDemo.exe ' \
          '--video {}\\output\\processed_video_temp\\{}_processed.mp4'.format(short, video_name_free)

if args.process:
    change_wd_steps()
    if not os.path.exists('output\\processed_video_temp'):  # creates (if not pre-existent) a directory to contain
        os.makedirs('output\\processed_video_temp')         # processed videos
    clip = VideoFileClip(args.input_path)  # loads the video
    new_end = 0  # duplicate of args.end but goes from 'max' to the int max time
    if args.end == 'max': new_end = clip.duration  # sets the max time appropriately
    else:
        new_end = args.end
        args.end = int(args.end)
    clip = clip.subclip(args.start, new_end)  # trims the video
    clip.write_videofile('output\\processed_video_temp\\{}_processed.mp4'.format(video_name_free))
    command = command + " --write_json {}\\output\\keypoints\\{}".format(short, video_name_free)
    print(command)
    change_wd_open()  # changes wd to open pose to execute the openpose command
    subprocess.call(command)
    change_wd_steps()  # goes back to steps_detection to record everything
    keypoints_full, loop_range = Fetch_keypoints(start=args.start, end=args.end, rate=clip.fps, name=video_name_free,
                                                 path="output/keypoints/" + video_name_free)
    if args.write_graph: angles = Angles_over_time(keypoints_full, loop_range, save=1)
    else: angles = Angles_over_time(keypoints_full, loop_range)

    if args.write_csv: Write_csv(angles)

elif args.preview:
    # use --write_images to get a displayable image with the skeletons
    print('Function not supported yet')
