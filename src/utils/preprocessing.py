import setup
import os
import subprocess
import sys
from pathlib import Path
import numpy as np

from shared_modules.plugin import Plugin_List
from shared_modules.video_export.plugins.world_video_exporter import World_Video_Exporter
from shared_modules.video_export.plugins.world_video_exporter import _export_world_video

project_root = os.path.dirname(os.path.abspath(__file__)) # This is the path to the project directory

class GlobalContainer: #Initation of a PL container, see PLs docs for more info
    def __init__(self):
        self.plugin_by_name = {}  # Initialize as empty
        self.plugins = None  # To be set later by Plugin_List
        self.rec_dir = None  # Path to the recording directory
        self.user_dir = None  # Path to the user directory
        self.min_data_confidence = 0.5  # Default confidence threshold
        self.topics = {}  # Add topics as an empty dictionary

class Preprocessor:
    def __init__(self, input_dir, output_dir=None, plugin_dir = None):
        """
              Initializes the Preprocessor.
              :param input_dir: The input directory containing the raw data.
              :param output_dir: The directory to store processed data. Defaults to 'data' inside the project's directory.
        """
        self.input_dir = input_dir
        if output_dir is None: # Default to a 'data' folder in the project's directory
            self.output_dir = os.path.join(project_root, 'data')
        else:
            self.output_dir = output_dir

        if plugin_dir is None:
            self.plugin_dir = os.path.join(project_root, 'custom_plugins')
        else:
            self.plugin_dir = plugin_dir

    def get_folders(self):
        """
        Retrieves the directories for the "Trail B" test recordings for each subject.

        It traverses the given directory structure, which is expected to contain subject folders.
        Each subject folder should have a `REC_ET` folder, and inside that, a `PL` folder with test
        video directories. The function identifies the latest numbered folder (e.g., `003`, `001`) for each
        subject and collects them into a list.

        Output:
            list: A list of full paths to the "Trail B" test directories, one for each subject.
                  Each path corresponds to the latest numbered directory inside the `PL` folder for each subject.

        Raises:
            ValueError: If the input directory is invalid or inaccessible.

        Example:
            If the input is `/data`, the output might look like:
            [
                '/data/ZS109/REC_ET/PL/003',
                '/data/ZS110/REC_ET/PL/002',
                '/data/ZS111/REC_ET/PL/004'
            ]
        """

        if not os.path.exists(self.input_dir) or not os.path.isdir(self.input_dir):
            raise ValueError(f"Invalid input directory: {self.input_dir}")

        video_folders = []
        # Traverse each subject folder
        for subject_folder in os.listdir(self.input_dir):
            subject_path = os.path.join(self.input_dir, subject_folder)

            if os.path.isdir(subject_path):
                # Look for the 'PL' folder inside the subject folder
                pl_folder = os.path.join(subject_path, 'REC_ET', 'PL')

                if os.path.isdir(pl_folder):
                    # Get all folder names inside the PL folder (these are the video folders)
                    video_folders_in_pl = [
                        f for f in os.listdir(pl_folder)
                        if os.path.isdir(os.path.join(pl_folder, f))
                    ]

                    # Filter numeric folders (e.g., "001", "003")
                    numeric_video_folders = [
                        folder for folder in video_folders_in_pl if folder.isdigit()
                    ]

                    if numeric_video_folders:
                        # Sort the folder names as integers to get the highest numbered folder
                        highest_video_folder = max(numeric_video_folders, key=lambda x: int(x))

                        # Get the full path to the folder and append to the list
                        video_folder_path = os.path.join(pl_folder, highest_video_folder)
                        video_folders.append(video_folder_path)

        return video_folders




    def export_vid(self, vid_dir):
        """
        Replaces the existing export_vid function to utilize _export_world_video
        for a comprehensive export process.
        """
        # Paths and directories
        rec_dir = self.input_dir  # Directory containing the recording
        user_dir = self.plugin_dir  # Directory for user plugins
        out_file_path = os.path.join(vid_dir, "exported_world.mp4")  # Exported video path
        min_data_confidence = 0.5  # Minimum confidence threshold

        # Ensure world_timestamps.npy exists and calculate total frames
        timestamps_path = os.path.join(rec_dir, "world_timestamps.npy")
        if not os.path.exists(timestamps_path):
            raise FileNotFoundError(f"Timestamps file not found: {timestamps_path}")

        timestamps = np.load(timestamps_path)
        total_frames = len(timestamps)
        export_range = (0, total_frames)  # Export entire video range

        # Plugin initializers
        plugin_initializers = [
            {
                "name": "Offline_Fixation_Detector",
                "args": {
                    "max_dispersion": 1.50,  # angle, degrees
                    "min_duration": 80,  # ms
                    "max_duration": 600,  # ms
                    "show_fixations": True,
                },
            },
            {
                "name": "vis_circle",
                "args": {
                    "color": (0.0, 0.7, 0.0, 0.1),  # RGBA color for visualizations
                },
            },
            {
                "name": "raw_data_exporter",
                "args": {},
            },
        ]

        # Pre-computed eye data (can be extended if necessary)
        pre_computed_eye_data = {
            "pupil": {
                "data": [],
                "bisector_class": "PupilDataBisector",
                "data_ts": []  # Add this key
            },
            "gaze": {
                "data": [],
                "bisector_class": "Bisector",
                "data_ts": []  # Add this key
            },
            "fixations": {
                "data": [],
                "affiliator_class": "Affiliator",
                "data_ts": []  # Add this key
            },
        }

        # Call the _export_world_video function
        export_gen = _export_world_video(
            rec_dir=rec_dir,
            user_dir=user_dir,
            min_data_confidence=min_data_confidence,
            start_frame=export_range[0],
            end_frame=export_range[1],
            plugin_initializers=plugin_initializers,
            out_file_path=out_file_path,
            pre_computed_eye_data=pre_computed_eye_data,
        )

        # Handle the generator output (progress updates)
        try:
            for status, progress in export_gen:
                print(f"Status: {status}, Progress: {progress}")
        except Exception as e:
            print(f"An error occurred during export: {e}")
        else:
            print(f"Video successfully exported to {out_file_path}")


# Example setup
input_directory = r'C:\Users\yotam\Desktop\Studies\year 3\CTT Project\CTT Yotam Malachi\YotamMalachi\data\YY404\REC_ET\PL\007'
output_directory = r'C:\Users\yotam\Desktop\Studies\year 3\CTT Project\CTT Yotam Malachi\CTT Code YM\test'
vid_directory = r'C:\Users\yotam\Desktop\Studies\year 3\CTT Project\CTT Code YM\test'

# Create an instance of Preprocessor
preprocessor = Preprocessor(input_dir=input_directory, output_dir=output_directory)

# Call the export_vid function
try:
    preprocessor.export_vid(vid_dir=vid_directory)
    print(f"Video successfully exported to {vid_directory}")
except Exception as e:
    print(f"An error occurred: {e}")


#     def export_vid(self, vid_dir):
#
#         g_pool = GlobalContainer()
#         g_pool.rec_dir = self.input_dir
#         g_pool.user_dir = self.plugin_dir
#         g_pool.min_data_confidence = 0.5
#
#         # Retrieve total frames using world_timestamps.npy
#         timestamps_path = os.path.join(g_pool.rec_dir, 'world_timestamps.npy')
#         if not os.path.exists(timestamps_path):
#             raise FileNotFoundError(f"Timestamps file not found: {timestamps_path}")
#
#         total_frames = len(np.load(timestamps_path))
#         export_range = (0, total_frames)  # Entire video range
#
#         # Define plugin initializers
#         initializers = [
#             {
#                 "name": "Offline_Fixation_Detector",
#                 "args": {"max_dispersion": 1.50, # angle, degrees
#                          "min_duration": 80, # ms
#                          "max_duration": 600, # ms
#                          "show_fixations": True
#                          }
#             },
#
#             {
#                 "name": "raw_data_exporter",
#                 "args": {"g_pool": g_pool}
#             },
#
#             {
#                 "name": "vis_circle",
#                 "args": {"g_pool": g_pool,
#                          "color": (0.0, 0.7, 0.0, 0.1)
#                          }
#             }
#         ]
#         g_pool.plugins = Plugin_List(g_pool, plugin_initializers= initializers)
#         exporter = World_Video_Exporter(g_pool)
#         exporter.export_data(export_range, vid_dir)
#
#
# # Example setup
# input_directory = r'C:\Users\yotam\Desktop\Studies\year 3\CTT Project\CTT Yotam Malachi\YotamMalachi\data\YY404\REC_ET\PL\007'  # Replace with your actual input directory
# output_directory = r'C:\Users\yotam\Desktop\Studies\year 3\CTT Project\CTT Yotam Malachi\CTT Code YM\test'  # Replace with your desired output directory
# vid_directory = r'C:\Users\yotam\Desktop\Studies\year 3\CTT Project\CTT Yotam Malachi\YotamMalachi\data\YY404\REC_ET\PL\007'  # Replace with your desired export directory






# # Create an instance of Preprocessor
# preprocessor = Preprocessor(input_dir=input_directory, output_dir=output_directory)
#
# # Call the export_vid function
# try:
#     preprocessor.export_vid(vid_dir=vid_directory)
#     print(f"Video successfully exported to {vid_directory}")
# except Exception as e:
#     print(f"An error occurred: {e}")
