from plugin import Plugin_List

import setup
import os
import subprocess
import sys
from pathlib import Path

from shared_modules.video_export.plugins.world_video_exporter import World_Video_Exporter


project_root = os.path.dirname(os.path.abspath(__file__))

class GlobalContainer: #Initation of a PL container, see PLs docs for more info
    pass

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
        import os  # Ensure os is imported if not globally

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


    def process_vid(self):

        vid_list = self.get_folders()
        g_pool = GlobalContainer()
        g_pool.rec_dir = self.input_dir()
        g_pool.user_dir = self.plugin_dir()
        g_pool.min_data_confidence = 0.5
        g_pool.plugins = Plugin_List(g_pool, plugin_initializers=)
        exporter = World_Video_Exporter(g_pool)




#עכשיו צריך להוסיף פה את כל הפלאגינים וההגדרות שלהם























#
# def process_video_dirs(dir_list, pupil_player_path, output_base_dir):
#     """
#     Processes a list of directories in Pupil Player with static parameters
#     and exports the results to a "Trail B Data" folder, with subfolders for each subject.
#
#     Parameters:
#         dir_list (list): List of directory paths to process.
#         pupil_player_path (str): Path to the Pupil Player executable.
#         output_base_dir (str): Base directory where "Trail B Data" will be created.
#     """
#     # Static parameters for the auto-fixation plugin
#     fixation_params = {
#         "min_fixation_time": 100,
#         "max_fixation_time": 600,
#         "max_dispersion": 1.5,
#     }
#
#     # Static parameters for the gaze circle
#     gaze_circle_params = {
#         "radius": 20,
#         "stroke_width": 1,
#         "red": 0,
#         "green": 0.7,
#         "blue": 0,
#         "alpha": 0.1,
#     }
#
#     # Static parameters for the visualization polyline
#     vis_polyline_params = {
#         "line_thickness": 1,
#         "red": 1,
#         "green": 0,
#         "blue": 0,
#         "gaze_history": 0,
#     }
#
#     # Ensure the base output directory exists
#     trail_b_dir = os.path.join(output_base_dir, "Trail B Data")
#     os.makedirs(trail_b_dir, exist_ok=True)
#
#     for video_dir in dir_list:
#         # Ensure the directory exists
#         if not os.path.exists(video_dir):
#             print(f"Directory not found: {video_dir}")
#             continue
#
#         # Extract the subject's folder name from three levels up
#         subject_name = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(video_dir))))
#         subject_dir = os.path.join(trail_b_dir, subject_name)
#
#         # Create a folder for this subject
#         os.makedirs(subject_dir, exist_ok=True)
#
#         # Build the command to launch Pupil Player with the specific parameters
#         command = [
#             pupil_player_path,
#             video_dir,  # Load the directory into Pupil Player
#             "--auto-fixation-plugin",
#             f"{fixation_params['min_fixation_time']} {fixation_params['max_fixation_time']} {fixation_params['max_dispersion']}",
#             "--gaze-circle",
#             f"{gaze_circle_params['radius']} {gaze_circle_params['stroke_width']} {gaze_circle_params['red']} {gaze_circle_params['green']} {gaze_circle_params['blue']} {gaze_circle_params['alpha']}",
#             "--vis-polyline",
#             f"{vis_polyline_params['line_thickness']} {vis_polyline_params['red']} {vis_polyline_params['green']} {vis_polyline_params['blue']} {vis_polyline_params['gaze_history']}",
#             "--export",  # Trigger export
#             "--export-path", subject_dir  # Ensure export to the correct subject folder
#         ]
#
#         # Print command for debugging purposes
#         print("Running command:", " ".join(command))
#
#         # Run the command to process the directory
#         try:
#             subprocess.run(command, check=True)
#             print(f"Processed and exported for subject: {subject_name}")
#         except subprocess.CalledProcessError as e:
#             print(f"Error processing {video_dir}: {e}")
#
# # Example usage
# dir_list = [
#     r'F:\YotamMalachi\data\AS970\REC_ET\PL\006'
# ]
# pupil_player_path = r"D:\CTT Project\Pupil Player v3.5.1\pupil_player.exe"
# output_base_dir = r"F:\YotamMalachi"  # Base directory where "Trail B Data" will be created
#
# process_video_dirs(dir_list, pupil_player_path, output_base_dir)
