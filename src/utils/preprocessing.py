import os
from pathlib import Path
import numpy as np

from video_export.plugins.world_video_exporter import World_Video_Exporter


class Preprocessor:
    def __init__(self, g_pool, output_dir=None):
        """
        Initializes the Preprocessor with a shared g_pool object and output directory.
        :param g_pool: The GlobalContainer object holding global paths and state.
        :param output_dir: The directory to store processed data. Defaults to 'data' inside the project's directory.
        """
        self.g_pool = g_pool
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



    def export_vid_for_subject(self, subject_folder, subject_output_dir):
        """
        Exports the world video for a specific subject to their output directory.
        :param subject_folder: The input folder for the subject's data.
        :param subject_output_dir: The output folder for the subject's data.
        """
        # Set the recording directory to the subject folder
        self.g_pool.rec_dir = subject_folder

        # Ensure world_timestamps.npy exists
        timestamps_path = os.path.join(self.g_pool.rec_dir, "world_timestamps.npy")
        if not os.path.exists(timestamps_path):
            raise FileNotFoundError(f"Timestamps file not found: {timestamps_path}")

        # Load timestamps and calculate total frames
        timestamps = np.load(timestamps_path)
        total_frames = len(timestamps)
        export_range = (0, total_frames)

        # Ensure the output directory exists
        os.makedirs(subject_output_dir, exist_ok=True)

        # Create an instance of World_Video_Exporter
        exporter = World_Video_Exporter(self.g_pool)

        # Use the export_data function
        try:
            export_dir = subject_output_dir
            exporter.export_data(export_range, export_dir)
            print(f"Video successfully exported to {export_dir}")
        except Exception as e:
            print(f"An error occurred during export: {e}")

    def export_all(self):
        """
        Exports videos for all subjects in g_pool.rec_dir.
        """
        output_structure = self.create_output_structure()
        for subject_id, subject_output_dir in output_structure.items():
            subject_folder = os.path.join(self.g_pool.rec_dir, subject_id)
            print(f"Starting export for subject: {subject_id}")
            try:
                self.export_vid_for_subject(subject_folder, subject_output_dir)
            except Exception as e:
                print(f"An error occurred while exporting for subject {subject_id}: {e}")
            else:
                print(f"Successfully exported data for subject: {subject_id}")
