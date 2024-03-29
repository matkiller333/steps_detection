import pandas as pd
import argparse
import subprocess
from calculations import *
from moviepy.editor import *
from functions import *


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

    if args.write_csv:
        angles = Angles_over_time(keypoints_full, loop_range)
        Write_csv(angles)

elif args.preview:
    # use --write_images to get a displayable image with the skeletons
    print('Function not supported yet')
