
import subprocess
import os
from sys import platform
import sys
import argparse
import ntpath
from pathlib import Path

user_os = None
if platform == "Linux" or platform == "linux":
    print("Operating on Linux")
    user_os = "lin"

    import cv2
    import numpy as np
    from tqdm import tqdm
    import matplotlib.pyplot as plt
    from os.path import isfile, join
    import random

    ## Import OpenPose in Python 
    try:
        # Change these variables to point to the correct folder (Release/x64 etc.)
        #sys.path.append('../../python');
        # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
        if '/usr/local/python' not in sys.path :
            sys.path.append('/usr/local/python')
        import pyopenpose as op

    except ImportError as e:
        print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
        raise e

if platform == "win32" or platform == "win64" :
    print("Operating on Windows")
    user_os = "win"


def detect_skeleton_in_video(args):
    print("Launching OpenPose")
    params= dict()
    params["model_folder"] = "models"
    file_no_extension = ntpath.basename(os.path.splitext(args.input_path)[0])
    if args.write_images or args.write_video:
        params["write_images"] = "output/images/"+file_no_extension
        Path(params["write_images"]).mkdir(parents=True, exist_ok=True)

    if args.write_keypoints :
        params["write_json"] = "output/keypoints/"+file_no_extension+"/"
        Path(params["write_json"]).mkdir(parents=True, exist_ok=True)

    # Starting OpenPose
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()
    cap = cv2.VideoCapture(args.input_path)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print("Starting frame by frame detection")
    frames_keypoints = []
    for i in tqdm(range(0,length)):
        _, frame = cap.read()
        # Process Image
        datum = op.Datum()
        datum.cvInputData = frame
        opWrapper.emplaceAndPop([datum])
        frames_keypoints.append(datum.poseKeypoints)
    cap.release()

    print("Detection Done !")

    if args.write_video :
        print("Starting writing video")
        Path("output/video/").mkdir(parents=True, exist_ok=True)
        create_output_video_from_frames(f"output/images/{file_no_extension}",f"output/video/{file_no_extension}.mp4")
        print(f"Video created at output/video/{file_no_extension}.mp4 !")

    return frames_keypoints


def create_output_video_from_frames(pathIn, pathOut, fps = 24):
    frame_array = []
    files = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))]  # makes files = pathIn
    # for sorting the file names properly
    files_number = [int(x[0:-13]) for x in files]
    files_number.sort()
    frame_array = []
    files = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))]  # makes files = pathIn in original order
    # for sorting the file names properly according to files_number
    files.sort(key = lambda x: x[5:-4])
    for i in tqdm(range(len(files))): # tqdm is a progress meter
        filename=pathIn+"/" + str(files_number[i])+"_rendered.png"
        # reading each files
        img = cv2.imread(filename) # imports the image as a matrix of pixels
        height, width, _ = img.shape
        size = (width,height)

        # inserting the frames into an image array
        frame_array.append(img)

    out = cv2.VideoWriter(pathOut,cv2.VideoWriter_fourcc(*'DIVX'), fps, size)
    for i in tqdm(range(len(frame_array))):
        # writing to an image array
        out.write(frame_array[i])
    out.release()  # releases the video writer


parser = argparse.ArgumentParser(description='Count steps in video')  # creates a function that can be used in terminal
parser.add_argument('input_path', help='Path of the video to analyze') #adds arguments the user can specify
parser.add_argument('--write_video', action='store_true', help='Rewrite the intput video with the skeletons (will also create one image per frame), this will considerably slow the process')
parser.add_argument('--write_images', action='store_true',  help='Same every frame of the video with detected skeletons, this will considerably slow the process')
parser.add_argument('--write_keypoints', action='store_true' , help='Store keypoints in a folder. JSON format')

args = parser.parse_args()

if user_os == "lin":
    keypoints = detect_skeleton_in_video(args)

if user_os == 'win':
    filename = args.input_path
    ##--display 0 --render_pose 0 pour enlever la fenêtre
    command = "bin\\OpenPoseDemo.exe --video " + filename
    file_no_extension = ntpath.basename(os.path.splitext(args.input_path)[0])
    if args.write_video :
        Path("output\\processed_video\\").mkdir(parents=True, exist_ok=True)
        command =  command + " --write_video output\\processed_video\\"+ntpath.basename(args.input_path)
    if args.write_images :
        Path("output\\images\\").mkdir(parents=True, exist_ok=True)
        command = command + " --write_images output\\images\\"+file_no_extension
    if args.write_keypoints :
        Path("output\\keypoints\\").mkdir(parents=True, exist_ok=True)
        command = command + " --write_json output\\keypoints\\"+file_no_extension

    res = subprocess.check_call(command, shell=False)

    print("Done")
