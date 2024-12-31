# Here I define core classes of the project like the GlobalContainer class.
# It will be dynamically adjusted and passed whenever needed.
# This is used to stimulate a g_pool instance which is used by many pupil labs' plugins
# and core utilities.

class GlobalContainer:
    def __init__(self):
        self.plugin_by_name = {}
        self.plugins = None
        self.rec_dir = None
        self.user_dir = None
        self.min_data_confidence = 0.6
        self.timestamps = None
        self.camera_render_size = None
        self.gaze_positions = None
        self.pupil_positions = None
        self.fixations = None
        self.topics = (
            "notify.world_process.",
                       )

