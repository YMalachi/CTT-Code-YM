# General imports
import os
from shared_modules.plugin import Plugin_List
import logging


# Pupil imports
from video_capture import File_Source

# Project imports (written by us)
from utils.preprocessing import Preprocessor
from setup.CoreClasses import GlobalContainer
from utils.gpool_initializers import (initialize_basic_gpool,
                                      add_capture_to_gpool,
                                      initialize_plugins,
                                      initialize_data_for_pre_computation
                                      )

# Defining params
plugin_initializers = [
        {
            "name": "Offline_Fixation_Detector",
            "args": {
                "max_dispersion": 1.50,
                "min_duration": 80,
                "max_duration": 600,
                "show_fixations": True,
            },
        },
        {
            "name": "vis_circle",
            "args": {
                "color": (0.0, 0.7, 0.0, 0.1),
            },
        },
        {
            "name": "raw_data_exporter",
            "args": {},
        },
    ]
#
# class GlobalContainer:
#     def __init__(self):
#         self.plugin_by_name = {}
#         self.plugins = None  # Plugins initialized dynamically
#         self.rec_dir = None
#         self.user_dir = None
#         self.min_data_confidence = 0.5
#         self.topics = (
#             "notify.eye_process.",
#             "notify.player_process.",
#             "notify.world_process.",
#             "notify.service_process",
#             "notify.clear_settings_process.",
#             "notify.player_drop_process.",
#             "notify.launcher_process.",
#             "notify.meta.should_doc",
#             "notify.circle_detector_process.should_start",
#             "notify.ipc_startup",
#         )
#
# # Initialize g_pool function
# def initialize_g_pool(input_dir, plugin_dir):
#     """
#     Initializes and returns a GlobalContainer object.
#     :param input_dir: The input directory for recordings.
#     :param plugin_dir: The directory for user plugins.
#     :return: A configured GlobalContainer object.
#     """
#     g_pool = GlobalContainer()
#     g_pool.rec_dir = input_dir
#     g_pool.user_dir = plugin_dir
#     g_pool.plugins = None  # Plugins will be initialized dynamically
#     g_pool.min_data_confidence = 0.5
#     return g_pool
#
# from shared_modules.plugin import Plugin_List
#
# def initialize_plugins(g_pool):
#     """
#     Initializes and populates g_pool.plugins with the required plugins.
#     :param g_pool: The GlobalContainer object.
#     """
#     plugin_initializers = [
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
#     # Initialize the plugins
#     g_pool.plugins = Plugin_List(g_pool, plugin_initializers=plugin_initializers)

# Main workflow
def main():
    # Paths for input data and plugins
    input_dir = r'C:\Users\yotam\Desktop\Studies\year 3\CTT Project\CTT Yotam Malachi\YotamMalachi\data\AN755\REC_ET\PL\005'
    plugin_dir = os.path.abspath(r'..\setup\custom_plugins')
    output_dir = os.path.abspath(r'..\test')

    # Initialize g_pool and attributes
    g_pool = initialize_basic_gpool(input_dir, plugin_dir)
    add_capture_to_gpool(g_pool)
    initialize_data_for_pre_computation(g_pool)
    initialize_plugins(g_pool, plugin_initializers)

    # Initialize Preprocessor
    preprocessor = Preprocessor(g_pool=g_pool, output_dir=output_dir)

    # Run export for a single subject
    try:
        print("Starting export process...")
        preprocessor.export_vid_for_subject(plugin_initializers)
        print("Export process completed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Entry point
if __name__ == "__main__":
    main()
