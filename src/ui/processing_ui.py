# general imports
import tkinter as tk
from tkinter import *

# own imports
from src.utils.metadata_manager import MetadataManager
from src.utils.preprocessing import VideoPreprocessor
from setup.CoreClasses import ProcessingContainer, DataContainer


class ProcessingUI:
    def __init__(self, root):
        """
        Initialize the ProcessingUI class.
        :param root: The root Tkinter window.
        """
        self.root = root
        self.processing_container = None
        self.VideoProcessor = None
        self.metadata_manager = None

        # Set up the UI (e.g., input fields for user-provided data)
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI components."""

        # Label for subject name input
        subject_name_label = tk.Label(self.root, text="Enter the subject name:")
        subject_name_label.pack()  # Place the label above the entry field

        # Input field for subject name
        self.subject_name_entry = tk.Entry(self.root, width=100)
        self.subject_name_entry.pack()

        # Label for data path input
        data_path_label = tk.Label(self.root, text="Enter the data path:")
        data_path_label.pack()  # Place the label above the entry field

        # Input field for data path
        self.data_path_entry = tk.Entry(self.root, width=100)
        self.data_path_entry.pack()

        # Label for trail
        desired_trail_label = tk.Label(self.root, text="Enter the desired trail:")
        desired_trail_label.pack()  # Place the label above the entry field

        # Input field for trail
        self.desired_trail_entry = tk.Entry(self.root, width=100)
        self.desired_trail_entry.pack()

        # Label for output path
        output_path_label = tk.Label(self.root, text="Enter the output path:")
        output_path_label.pack()  # Place the label above the entry field

        # Input field for trail
        self.output_path_entry = tk.Entry(self.root, width=100)
        self.output_path_entry.pack()

        # Submit button
        self.submit_button = tk.Button(self.root, text="Submit", command=self.create_processing_environment)
        self.submit_button.pack()

    def create_processing_environment(self):
        """Create processing environment based on user input."""
        # Get user inputs
        data_path = self.data_path_entry.get()
        subject_name = self.subject_name_entry.get()
        output_path = self.output_path_entry.get()
        desired_trail = self.desired_trail_entry.get()

        # Initialize objects with user input
        self.metadata_manager = MetadataManager(base_directory=r'C:\Users\yotam\Desktop\Studies\year 3\CTT Project\CTT Yotam Malachi\CTT Code YM\metadata')
        # self.metadata_manager.save_metadata(subject_name)
        self.processing_container = ProcessingContainer(data_path=data_path, subject_name=subject_name)
        self.processing_container._create_out_path(output_path)
        self.video_processor = VideoPreprocessor(self.processing_container, trail=desired_trail, metadata_manager=self.metadata_manager)

        print(f"Created MetadataManager, ProcessingContainer And VideoPreprocessor for {subject_name}")

        # Navigate to the second window
        self.show_next_window(subject_name, data_path)

    def show_next_window(self, subject_name, data_path):
        """Open a new window after submission."""
        # Hide the current window
        self.root.withdraw()

        # Create a new Tkinter Toplevel window
        next_window = tk.Toplevel(self.root)
        next_window.geometry("600x480")
        next_window.title("Processing Window")

        # Display information from the first window
        tk.Label(next_window, text=f"Subject: {subject_name}").pack()
        tk.Label(next_window, text=f"Data Path: {data_path}").pack()

        # Add a back button to return to the main window
        tk.Button(next_window, text="Back", command=lambda: self.go_back(next_window)).pack()

        # Add buttons for further operations
        tk.Button(next_window, text="Trim Videos", command=self.trim_videos).pack()

    def go_back(self, current_window):
        """Return to the main window."""
        current_window.destroy()  # Close the current window
        self.root.deiconify()  # Show the main window again

    def trim_videos(self):
        """Trims videos using trim_vid_around_fixations function of VidPreprocessor class"""
        print("Trimming videos...")  # Replace with actual implementation
        fix_dict = self.video_processor._get_fixations_ts()
        merged_dict = self.video_processor._merge_neighboring_fixations(fix_dict)
        self.video_processor.create_metadata_for_subject(fix_dict, merged_dict)
        self.video_processor.trim_vid_around_fixations(merged_dict)


if __name__ == "__main__":
    root = tk.Tk()  # Creates the main window object for the application.
    root.geometry("600x480")
    app = ProcessingUI(root)  # Passes the root window to the `ProcessingUI` class.
    root.mainloop()  # Starts the main event loop for the application.
