# General imports
import numpy as np
import os
import msgpack
import pandas as pd

# Pupil imports
from video_capture import File_Source
from player_methods import Bisector, Affiliator, PupilDataBisector
from file_methods import load_pldata_file
from video_export.plugins.world_video_exporter import World_Video_Exporter, _export_world_video

# Project imports (written by us)
from setup.CoreClasses import GlobalContainer


def load_timestamps(file_path):
    """
    Load a .npy file containing timestamps and return it as a NumPy array.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Missing timestamps file: {file_path}")

    return np.load(file_path)




def load_precomputed_eye_data(rec_dir):
    """
    Load gaze, pupil, and fixation data for precomputation.
    """
    # Load data using PupilDataBisector
    gaze_data = PupilDataBisector.load_from_file(rec_dir, "gaze")
    fixations_data = PupilDataBisector.load_from_file(rec_dir, "fixations")
    pupil_data = PupilDataBisector.load_from_file(rec_dir, "pupil")

    return {
        "gaze": gaze_data,
        "fixations": fixations_data,
        "pupil": pupil_data,
    }

# def load_data_for_precomputation(rec_dir):
#     """
#     Load raw data (pupil, gaze, fixations) into PupilDataBisector or similar objects for precomputation.
#
#     :param rec_dir: Path to the recording directory.
#     :return: Dictionary containing Bisector/Affiliator objects for pupil, gaze, and fixations.
#     """
#     raw_eye_data = {}
#
#     # Load Pupil Data
#     try:
#         raw_eye_data["pupil"] = PupilDataBisector.load_from_file(rec_dir, "pupil")
#     except FileNotFoundError:
#         print(f"Pupil data not found in {rec_dir}.")
#         raw_eye_data["pupil"] = None
#
#     # Load Gaze Data
#     try:
#         raw_eye_data["gaze"] = PupilDataBisector.load_from_file(rec_dir, "gaze")
#     except FileNotFoundError:
#         print(f"Gaze data not found in {rec_dir}.")
#         raw_eye_data["gaze"] = None
#
#     # Load Fixation Data
#     try:
#         raw_eye_data["fixations"] = PupilDataBisector.load_from_file(rec_dir, "fixations")
#     except FileNotFoundError:
#         print(f"Fixation data not found in {rec_dir}.")
#         raw_eye_data["fixations"] = None
#
#     return raw_eye_data
#
#
# def compute_precomputed_eye_data(raw_eye_data, timestamps, export_range):
#     """
#     Compute precomputed eye data for a specific range using raw data.
#
#     :param raw_eye_data: Dictionary of Bisector/Affiliator objects for pupil, gaze, and fixations.
#     :param timestamps: Full list of timestamps.
#     :param export_range: Tuple (start_index, end_index) defining the export range.
#     :return: Precomputed eye data compatible with _export_world_video.
#     """
#     export_window = (timestamps[export_range[0]], timestamps[export_range[1]])
#     precomputed_eye_data = {}
#
#     for key, data_bisector in raw_eye_data.items():
#         if data_bisector is not None:
#             init_dict = data_bisector.init_dict_for_window(export_window)
#             # Serialize data for compatibility with _export_world_video
#             init_dict["data"] = [datum.serialized for datum in init_dict["data"]]
#             precomputed_eye_data[key] = init_dict
#         else:
#             precomputed_eye_data[key] = None
#
#     return precomputed_eye_data
#
# #test
#
# plugin_initializers = [
#         {
#             "name": "Offline_Fixation_Detector",
#             "args": {
#                 "max_dispersion": 1.50,
#                 "min_duration": 80,
#                 "max_duration": 600,
#                 "show_fixations": True,
#             },
#         },
#         {
#             "name": "vis_circle",
#             "args": {
#                 "color": (0.0, 0.7, 0.0, 0.1),
#             },
#         },
#         {
#             "name": "raw_data_exporter",
#             "args": {},
#         },
#     ]
#
# rec_dir = r"C:\Users\yotam\Desktop\Studies\year 3\CTT Project\CTT Yotam Malachi\YotamMalachi\data\AN755\REC_ET\PL\005"
# raw_eye_data = load_precomputed_eye_data(rec_dir)
# timestamps = load_timestamps(r"C:\Users\yotam\Desktop\Studies\year 3\CTT Project\CTT Yotam Malachi\YotamMalachi\data\AN755\REC_ET\PL\005\world_timestamps.npy")
# export_range = (0, 100)
# precomputed_eye_data = compute_precomputed_eye_data(raw_eye_data, timestamps, export_range)
# _export_world_video(
#     rec_dir=rec_dir,
#     user_dir=r"C:\Users\yotam\Desktop\Studies\year 3\CTT Project\CTT Yotam Malachi\CTT Code YM\setup\custom_plugins",
#     min_data_confidence=0.5,
#     start_frame=export_range[0],
#     end_frame=export_range[1],
#     plugin_initializers=plugin_initializers,
#     out_file_path=r"C:\Users\yotam\Desktop\Studies\year 3\CTT Project\CTT Yotam Malachi\CTT Code YM\test",
#     pre_computed_eye_data=precomputed_eye_data,
# )













def initialize_basic_gpool(input_dir, plugin_dir):
    """
    Initializes a basic g_pool with essential attributes.
    :param input_dir: a subject directory
    :param plugin_dir: additional plugins directory
    """
    g_pool = GlobalContainer()
    g_pool.rec_dir = input_dir
    g_pool.user_dir = plugin_dir
    return g_pool

def add_capture_to_gpool(g_pool):
    """
    Adds capture (video source) and timestamps to g_pool.
    """
    video_path = os.path.join(g_pool.rec_dir, "world.mp4")
    timestamps_path = os.path.join(g_pool.rec_dir, "world_timestamps.npy")

    g_pool.capture = File_Source(
        g_pool,
        timing="external",
        source_path=video_path,
        buffered_decoding=False,
        fill_gaps=True,
    )

    if os.path.exists(timestamps_path):
        g_pool.timestamps = np.load(timestamps_path)
    else:
        raise FileNotFoundError(f"Timestamps file not found: {timestamps_path}")


def initialize_plugins(g_pool, plugin_initializers):
    """
    Initializes plugins for g_pool.
    """
    from shared_modules.plugin import Plugin_List

    g_pool.plugins = Plugin_List(g_pool, plugin_initializers=plugin_initializers)
#
#
#
#
# def load_pldata(file_path):
#     """
#     Load a .pldata file, unpack its rows without altering the original format.
#
#     :param file_path: Path to the .pldata file.
#     :return: A list of unpacked dictionaries.
#     """
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"Missing .pldata file: {file_path}")
#
#     unpacked_data = []
#     with open(file_path, "rb") as f:
#         unpacker = msgpack.Unpacker(f, raw=False, strict_map_key=False)
#         for row in unpacker:
#             if isinstance(row, (list, tuple)) and len(row) > 1:
#                 try:
#                     # Unpack the serialized data in the second element
#                     unpacked_data.append({
#                         "topic": row[0],
#                         **msgpack.unpackb(row[1], raw=False, strict_map_key=False)
#                     })
#                 except Exception as e:
#                     print(f"Failed to unpack binary data: {e}")
#             else:
#                 unpacked_data.append(row)
#
#     return unpacked_data
#
#
# def load_timestamps(file_path):
#     """
#     Load a .npy file containing timestamps and return it as a NumPy array.
#     """
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"Missing timestamps file: {file_path}")
#
#     return np.load(file_path)
#
#
# def initialize_fixations(g_pool):
#     """
#     Initializes fixation data for g_pool by loading precomputed fixations and timestamps.
#     """
#     # File paths
#     fixation_data_path = os.path.join(g_pool.rec_dir, "fixations.pldata")
#     fixation_timestamps_path = os.path.join(g_pool.rec_dir, "fixation_timestamps.npy")
#
#     # Load fixation data and timestamps
#     fixations = load_pldata(fixation_data_path)
#     fixation_timestamps = load_timestamps(fixation_timestamps_path)
#
#     # Extract fixation properties
#     data = []
#     start_ts = []
#     stop_ts = []
#
#     for fixation in fixations:
#         # Ensure required fields are present
#         if "norm_pos" in fixation and "timestamp" in fixation:
#             data.append(fixation["norm_pos"])
#             start_ts.append(fixation["timestamp"])
#             stop_ts.append(fixation["timestamp"] + (fixation["duration"] / 1000.0))
#
#     # Create Affiliator object for fixations
#     g_pool.fixations = Affiliator(data=data, start_ts=start_ts, stop_ts=stop_ts)
#
#
#
# def initialize_data_for_pre_computation(g_pool):
#     """
#     Initialize pre-computed data (gaze, pupil, fixations) for use in g_pool.
#     This function ensures alignment between data and timestamps.
#     """
#     # Initialize gaze data
#     try:
#         gaze_data_path = os.path.join(g_pool.rec_dir, "gaze.pldata")
#         gaze_timestamps_path = os.path.join(g_pool.rec_dir, "gaze_timestamps.npy")
#         gaze_data = load_pldata(gaze_data_path)
#         gaze_timestamps = load_timestamps(gaze_timestamps_path)
#         df = pd.DataFrame(gaze_data) #testing
#         print(df.head())
#         print(df.info())
#
#         if len(gaze_data) != len(gaze_timestamps):
#             raise ValueError("Mismatch between gaze data and timestamps.")
#
#         g_pool.gaze_positions = Bisector(
#             data=[datum["norm_pos"] for datum in gaze_data],
#             data_ts=gaze_timestamps
#         )
#     except FileNotFoundError as e:
#         print(f"Gaze data initialization skipped: {e}")
#         g_pool.gaze_positions = None
#
#     # Initialize pupil data
#     try:
#         pupil_data_path = os.path.join(g_pool.rec_dir, "pupil.pldata")
#         pupil_timestamps_path = os.path.join(g_pool.rec_dir, "pupil_timestamps.npy")
#         pupil_data = load_pldata(pupil_data_path)
#         pupil_timestamps = load_timestamps(pupil_timestamps_path)
#
#         if len(pupil_data) != len(pupil_timestamps):
#             raise ValueError("Mismatch between pupil data and timestamps.")
#
#         g_pool.pupil_positions = Bisector(
#             data=[datum["norm_pos"] for datum in pupil_data],
#             data_ts=pupil_timestamps
#         )
#     except FileNotFoundError as e:
#         print(f"Pupil data initialization skipped: {e}")
#         g_pool.pupil_positions = None
#
#     # Initialize fixation data
#     try:
#         fixation_data_path = os.path.join(g_pool.rec_dir, "fixations.pldata")
#         fixation_timestamps_path = os.path.join(g_pool.rec_dir, "fixation_timestamps.npy")
#         fixation_data = load_pldata(fixation_data_path)
#         fixation_timestamps = load_timestamps(fixation_timestamps_path)
#
#         if len(fixation_data) != len(fixation_timestamps):
#             raise ValueError("Mismatch between fixation data and timestamps.")
#
#         g_pool.fixations = Affiliator(
#             data=fixation_data,
#             start_ts=fixation_timestamps[:, 0],
#             stop_ts=fixation_timestamps[:, 1]
#         )
#     except FileNotFoundError as e:
#         print(f"Fixation data initialization skipped: {e}")
#         g_pool.fixations = None
