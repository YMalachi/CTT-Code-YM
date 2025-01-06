import os
from ctypes import pythonapi
from pathlib import Path
import numpy as np
import pandas as pd
import av
import time
import logging
import cv2
from pandas.core.indexing import convert_from_missing_indexer_tuple

# Our own libraries
from CoreClasses import DataContainer,ProcessingContainer

# Initializing log
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class Preprocessor:
    def __init__(self, input_dir, output_dir=None):
        """
        Initializes the Preprocessor with a shared g_pool object and output directory.
        :param g_pool: The GlobalContainer object holding global paths and state.
        :param output_dir: The directory to store processed data. Defaults to 'data' inside the project's directory.
        """
        self.input_dir = input_dir
        self.output_dir = output_dir or os.path.join(os.getcwd(), 'data')

    def get_subject_folders(self):
        """
        Retrieves subject folders from the input directory (g_pool.rec_dir).

        Output:
            list: A list of subject folder paths.
        """
        if not os.path.exists(self.g_pool.rec_dir) or not os.path.isdir(self.g_pool.rec_dir):
            raise ValueError(f"Invalid input directory: {self.g_pool.rec_dir}")

        return [
            os.path.join(self.g_pool.rec_dir, subject_folder)
            for subject_folder in os.listdir(self.g_pool.rec_dir)
            if os.path.isdir(os.path.join(self.g_pool.rec_dir, subject_folder))
        ]

    def create_output_structure(self):
        """
        Creates an output directory structure for each subject folder in g_pool.rec_dir.

        Output:
            dict: A mapping of subject IDs to their corresponding output directories.
        """
        subject_folders = self.get_subject_folders()
        output_structure = {}

        for subject_folder in subject_folders:
            subject_id = os.path.basename(subject_folder)
            subject_output_dir = os.path.join(self.output_dir, subject_id)
            Path(subject_output_dir).mkdir(parents=True, exist_ok=True)
            output_structure[subject_id] = subject_output_dir

        return output_structure

def validate_path(path, error_message):
    if not os.path.exists(path):
        logging.error(error_message)
        raise FileNotFoundError(error_message)

class VideoPreprocessor: # instead of inheriting ProcessingContainer im passing its attributes directly
    def __init__(self, parent, trail):
        """
        This class holds and utilize data for video processing.
        :param trail: Trail type (e.g. trail B)
        """
        # Creating the paths
        self.subject_name = parent.subject_name
        self.data_path = parent.data_path
        self.pl_path = parent.pl_path
        self.uni_path = parent.uni_path
        self.uni_trail_name = self.subject_name + '_' + trail + '.txt'
        self.uni_trail_path = os.path.join(self.uni_path, self.uni_trail_name) # this is the path to unity's trail file
        # Creating a synchronized dict of matching Unity files and PL directory (for each trail there is one of each)
        uni_pl_sync_dict = self.match_pl_uni()
        self.pl_trail_name = uni_pl_sync_dict.get(self.uni_trail_name, None)
        if not self.pl_trail_name:
            logging.error(f"No matching PL directory found for {self.uni_trail_name} in Unity files {self.uni_path}.")
            raise KeyError(f"No matching PL directory found for {self.uni_trail_name} in Unity files {self.uni_path}.")

        # More paths
        self.trail_path = os.path.join(parent.pl_path, self.pl_trail_name) #this is the path to the trail's directory, e.g. /005/
        self.pl_exports_path = os.path.join(self.trail_path, 'exports') # path to exports directory inside each trail. this only exists of you've already exported via Pupil Labs' software
        if not os.path.isdir(self.pl_exports_path): # checking if you've exported the vid...
            raise FileNotFoundError(f"There is no exports directory in this path {self.trail_path}. Double check if you went through export process before.")

        specific_export = max(os.listdir(self.pl_exports_path))

        # Creating paths and checking if they exist
        try:
            self.specific_export_path = os.path.join(self.pl_exports_path, specific_export) # path to export 000 for example
            validate_path(self.specific_export_path, f"The required directory does not exist: {self.specific_export_path}")

            self.vid_path = os.path.join(self.specific_export_path, 'world.mp4') # path to the world video
            validate_path(self.vid_path, f"Video not found in: {self.specific_export_path}")

            self.pl_timestamps = os.path.join(self.specific_export_path, 'world_timestamps.csv') # path to the world timestamps
            validate_path(self.pl_timestamps, f"Timestamps csv file not found in: {self.specific_export_path}")

            self.pl_fixations = os.path.join(self.specific_export_path, 'fixations.csv') # path to Pupil Labs' fixations
            validate_path(self.pl_fixations, f"Fixations csv file not found in: {self.specific_export_path}")

            self.export_info = os.path.join(self.specific_export_path, 'export_info.csv') # path to Pupil Labs' export_info txt file
            validate_path(self.export_info, f"Export_info csv file not found in: {self.specific_export_path}")

        except FileNotFoundError as e:
            raise e
        except Exception as e:
            raise e

    def match_pl_uni(self):
        """
        Matches the names of folders and files of Pupil Labs and Unity so that
        we know which PL folder matches which trial, using the "file modification timestamp" attribute.
        :return: A dict consisting of: (key : value) = (unity_txt_file_name : corresponding PL folder)
        """

        # I first create the file name lists, then check if everything is as expected and only then match the files.
        unity_file_check_list = [self.subject_name + "_Reference_Calibration_1.txt", self.subject_name + "_P1.txt", self.subject_name + "_P1A.txt", self.subject_name + "_T1.txt", self.subject_name + "_P2.txt", self.subject_name + "_P2A.txt", self.subject_name + "_T2.txt"] # these are the expected names
        unity_file_list = os.listdir(self.uni_path)
        if len(unity_file_list) >= len(unity_file_check_list):
            logging.info(f"There are more files in {self.uni_path} than expected.")
        for file in unity_file_check_list[:]:  # iterate over a copied list
            if file not in unity_file_list:
                unity_file_check_list.remove(file)  # modify the original list
                logging.error(f"There is a missing file or a file with unexpected name in {self.uni_path}, file name: {file}")

        # Checking if everything is as expected!
        # First checking for missing files
        for file in unity_file_check_list: # checking in unity folder
            try:
                if file not in unity_file_list: # check for missing files
                    unity_file_check_list.remove(file)
                    raise UserWarning(f"There is a missing file or a file with unexpected name in {self.uni_path}, file name: {file}")
            except UserWarning as w:
                logging.warning(f"There is a missing file or a file with unexpected name in {self.uni_path}, file name: {file}")
                logging.info(f"{file} have been removed from the Unity files list")

        # Now checking if there are enough video dirs in PL's data
        pl_dir_list = os.listdir(self.pl_path)
        try:
            if len(unity_file_list) > len(pl_dir_list):
                raise Warning(f"There are not enough video directories in {self.pl_path}. Check for mismatches.")
            else:
                pass
        except Warning:
            logging.warning(f"There are not enough video directories in {self.pl_path}. Check for mismatches.")

        # Extracting the creation timestamp
        uni_file_dict = {} # a dictionary to save file modification timestamps (key:value)=(file_name:timestamp)
        for file in unity_file_check_list:
            file_path = os.path.join(self.uni_path, file)
            uni_file_dict[file] = os.path.getmtime(file_path)


        pl_dir_dict = {} # same but (dir_name:timestamps)
        for _dir in pl_dir_list:
            pl_file_path = os.path.join(self.pl_path, _dir)
            ts_path = os.path.join(pl_file_path, 'world_timestamps.npy') # using the timestamps is ideal because it is created in the same exact moment as the UNI files
            pl_dir_dict[_dir] = os.path.getmtime(ts_path)

        # Now creating a dict where (key:value) = (UNI file name:matching PL dir)
        # I also make sure the dictionaries are sorted by keys (this condition should be satisfied already, but it's kept for better readability
        uni_file_dict_list = sorted(uni_file_dict.items(), key= lambda item: item[1])
        pl_dir_dict_list = sorted(pl_dir_dict.items(), key= lambda item: item[1])

        # Creating the synchronized dict:
        sync_dict = {}
        try:
            if len(pl_dir_dict_list) == len(uni_file_dict_list):
                for i in range(len(uni_file_dict_list)):
                    sync_dict[uni_file_dict_list[i][0]] = pl_dir_dict_list[i][0]
            else:
                raise ValueError(f"Mismatch between Unity files ({len(uni_file_dict_list)}) and PL directories ({len(pl_dir_dict_list)}).")
        except ValueError:
            logging.error(f"Mismatch between Unity files ({len(uni_file_dict_list)}) and PL directories ({len(pl_dir_dict_list)}).")
        except Exception as e:
            logging.error(f"An error occurred: {e}")
        return sync_dict



    def _get_fixations_ts(self):
        """
        This function is an internal function. It is called within the video trimming function and possibly others in the future.
        :return: A fixations dictionary that contains data in the form of {"fixation id" : (start frame of fixation,end frame of fixation)}.
        """
        fixations_dict = {}
        df = pd.read_csv(self.pl_fixations)
        df = df.iloc[:-3] # idk if this is good for all test subjects but it is for AN755
        print("remember to check the df iloc slicing with other subjects as well (if cutting out 3 rows is good)")
        fixations_id = df['id'].astype(int)
        fixation_start = df['start_frame_index']
        fixations_end = df['end_frame_index']

        for _id in fixations_id: # saving for each fixation id (key) its start and end time as a tuple (start, end)
            fixations_dict[_id] = (fixation_start.iloc[_id].astype(int), fixations_end.iloc[_id].astype(int))

        return fixations_dict

    def _merge_neighboring_fixations(self, fixation_dict, threshold=5):
        """
        This is an internal function designed to merge consecutive fixations that are close in time, based on the following logic:
        If the end of fixation(i) is within a specified threshold (in frames) from the start of fixation(i+1), the fixations are merged.
        The grouping process continues until:
        The total duration of the grouped fixations reaches exactly 180 frames, or
        Adding another fixation causes the total duration to exceed the 180 frames limit.
        If adding a fixation exceeds the 180 frames mark, it will not be included in the group. The remaining frames required to reach 180 will be padded with black frames later. This ensures a consistent snippet length of 180 frames across the entire project.
        :param fixation_dict: fixation dictionary in the correct format
        :param threshold: the frame threshold that below it fixations will be grouped.
        :return: merged fixations dictionary of {group id : (start frame, end frame).
        """
        merged_fixations_dict = {}
        snippet_fixed_length = 180
        current_snippet_length = 0
        fixations_amount = 0
        group_id = 0
        idx = 0
        print(len(fixation_dict.keys())-1)
        while idx < len(fixation_dict.keys())-1:
            # current fixation data
            start_frame_current_fixation = fixation_dict[idx][0]
            end_frame_current_fixation = fixation_dict[idx][1]
            # next fixation data
            start_frame_next_fixation = fixation_dict[idx+1][0]
            end_frame_next_fixation = fixation_dict[idx+1][1]

            delta_frames = start_frame_next_fixation - end_frame_current_fixation

            if current_snippet_length == 0: # add the first fixation to the length
                fixation_length = end_frame_current_fixation - start_frame_current_fixation # unit is frames
                merged_fixations_dict[group_id] = (start_frame_current_fixation, end_frame_current_fixation)
                current_snippet_length += fixation_length
                fixations_amount += 1
                idx += 1
            elif delta_frames <= threshold: # add fixations within the threshold
                fixation_length = end_frame_next_fixation - end_frame_current_fixation
                snippet_length_if_grouped = current_snippet_length + fixation_length
                if snippet_length_if_grouped <= snippet_fixed_length:
                    merged_fixations_dict[group_id] = (merged_fixations_dict[group_id][0], fixation_dict[idx+1][1])
                    current_snippet_length += fixation_length
                    fixations_amount += 1
                    idx += 1
                elif snippet_length_if_grouped > snippet_fixed_length and idx+1 == len(fixation_dict.keys()):
                    # this handles the case in which the fixation group would be longer than 180 frames, but the next fixation would be the last fixation
                    group_id += 1
                    fixations_amount = 1
                    merged_fixations_dict[group_id] = (start_frame_next_fixation, end_frame_next_fixation)
                    idx += 1
                else: # (if this snippet length exceeds 180 frames and is not the last fixation)
                    group_id += 1 # creates key for the next fixations group in the merged dictionary
                    fixations_amount = 0
                    current_snippet_length = 0
                    idx += 1
                    continue
            else: # (this code block is accessed only if there are no temporal close fixations)
                group_id += 1
                fixations_amount = 0
                current_snippet_length = 0
                continue
        return merged_fixations_dict





# #test laptop
# data = DataContainer(data_path=r'C:\Users\yotam\Desktop\Studies\year 3\CTT Project\CTT Yotam Malachi\YotamMalachi\data')
# subject_name = 'AN755'
# processing = ProcessingContainer(data_path=data.data_path, subject_name=subject_name)
# vid_pro = VideoPreprocessor(processing, trail='T2')
# vid_pro.match_pl_uni()
#test home
data = DataContainer(data_path=r'F:\YotamMalachi\data')
subject_name = 'AN755'
processing = ProcessingContainer(data_path=data.data_path, subject_name=subject_name)
vid_pro = VideoPreprocessor(processing, trail='T2')
#vid_pro.match_pl_uni()
fix_dict = vid_pro._get_fixations_ts()
vid_pro._merge_neighboring_fixations(fix_dict)