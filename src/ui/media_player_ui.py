# Complete and updated media player with:
# - Fixed window size
# - Metadata input first, then main UI
# - Horizontal layout (video on right, controls on left)
# - Video selection dropdown
# - Fixation tagging with dropdown (no popup)
# - Playback speed control

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import time
import os
from src.utils.metadata_manager import MetadataManager


class MediaPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Player App")
        self.root.geometry("1000x550")
        self.root.resizable(False, False)

        self.metadata_path = None
        self.subject_name = None

        self.collect_user_inputs()

    def collect_user_inputs(self):
        self.root.withdraw()

        input_window = tk.Toplevel(self.root)
        input_window.title("Enter Metadata Information")
        input_window.geometry("400x300")

        tk.Label(input_window, text="Enter Metadata Path:").pack(pady=5)
        metadata_path_entry = tk.Entry(input_window, width=50)
        metadata_path_entry.pack()

        tk.Label(input_window, text="Enter Subject Name:").pack(pady=5)
        subject_name_entry = tk.Entry(input_window, width=50)
        subject_name_entry.pack()

        def on_submit():
            self.metadata_path = metadata_path_entry.get()
            self.subject_name = subject_name_entry.get()

            if not self.metadata_path or not self.subject_name:
                messagebox.showerror("Input Error", "Both fields are required!")
                return

            input_window.destroy()
            self.root.deiconify()
            self.launch_media_player_ui()

        tk.Button(input_window, text="Submit", command=on_submit).pack(pady=20)

    def launch_media_player_ui(self):
        MediaPlayerUI(self.root, self.metadata_path, self.subject_name)


class MediaPlayerUI:
    def __init__(self, root, metadata_path, subject_name):
        self.root = root
        self.metadata_path = metadata_path
        self.subject_name = subject_name

        self.metadata_manager = MetadataManager(base_directory=metadata_path)
        self.metadata = self.metadata_manager.load_metadata(subject_name)
        self.videos = self.metadata.get("videos", [])

        self.cap = None
        self.current_frame = None
        self.current_video_index = 0
        self.current_fixation_index = 0
        self.selected_video = None
        self.playback_speed = tk.DoubleVar(value=1.0)
        self.selected_tag = tk.StringVar(value="Relevant")
        self.tag_controls_frame = None # Will create it only when needed
        self.next_video_button = None  # Will create it only when needed

        self.setup_ui()

    def setup_ui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        control_frame = tk.Frame(main_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

        tk.Label(control_frame, text="Media Player", font=("Helvetica", 16, "bold")).pack(pady=10)
        tk.Label(control_frame, text=f"Subject: {self.subject_name}", font=("Helvetica", 12)).pack(pady=5)
        tk.Label(control_frame, text=f"Metadata Path:", font=("Helvetica", 12)).pack(pady=5)
        tk.Label(control_frame, text=f"{self.metadata_path}", wraplength=180, justify="left").pack(pady=5)

        tk.Label(control_frame, text="Select Video:").pack(pady=(20, 0))
        self.video_selector = ttk.Combobox(control_frame, values=[v["group_id"] for v in self.videos], state="readonly")
        self.video_selector.pack()
        self.video_selector.bind("<<ComboboxSelected>>", self.on_video_selected)

        tk.Label(control_frame, text="Playback Speed:").pack(pady=(20, 0))
        tk.OptionMenu(control_frame, self.playback_speed, 0.5, 1.0, 1.5, 2.0).pack()

        tk.Button(control_frame, text="Play Fixations", command=self.play_next_fixation).pack(pady=10)
        tk.Button(control_frame, text="Pause Video", command=self.pause_video).pack(pady=5)

        self.tag_controls_frame = tk.Frame(control_frame)
        self.tag_controls_frame.pack(pady=30)
        tk.Label(self.tag_controls_frame, text="Tag this fixation:").pack()
        tag_options = ["-- Choose --", "Relevant", "Irrelevant"]
        self.selected_tag.set(tag_options[0])  # Default value
        tk.OptionMenu(self.tag_controls_frame, self.selected_tag, *tag_options).pack(pady=5)
        tk.Button(self.tag_controls_frame, text="Submit Tag", command=self.submit_tag).pack()
        self.tag_controls_frame.pack_forget()

        self.video_canvas = tk.Canvas(main_frame, width=640, height=480, bg="black")
        self.video_canvas.pack(side=tk.RIGHT)

    def on_video_selected(self, event):
        group_id = self.video_selector.get()
        for index, video in enumerate(self.videos):
            if video["group_id"] == group_id:
                self.current_video_index = index
                self.current_fixation_index = 0
                self.selected_video = video
                break

    def play_next_fixation(self):
        fixations = self.selected_video["fixations"]
        fixation_keys = list(fixations.keys())
        if self.current_fixation_index >= len(fixation_keys):
            messagebox.showinfo("Video Finished", "You have finished all fixations in this video.")

            # Show 'Continue to Next Video' button
            if self.next_video_button is None:
                self.next_video_button = tk.Button(
                    self.tag_controls_frame,
                    text="Continue to Next Video",
                    command=self.load_next_video
                )
                self.next_video_button.pack(pady=10)
            return

        if self.current_fixation_index >= len(fixation_keys):
            messagebox.showinfo("Info", "All fixations in this video are completed!")
            return

        fixation = fixations[fixation_keys[self.current_fixation_index]]
        start_frame = fixation["start_frame"]
        end_frame = fixation["end_frame"]

        if not self.cap or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.selected_video["snippet_path"])
            if not self.cap.isOpened():
                messagebox.showerror("Error", f"Cannot open video: {self.selected_video['snippet_path']}")
                return

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        self.play_fixation(start_frame, end_frame)

    def play_fixation(self, start_frame, end_frame):
        while True:
            ret, frame = self.cap.read()
            if not ret or self.cap.get(cv2.CAP_PROP_POS_FRAMES) > end_frame:
                self.cap.release()
                self.cap = None
                self.tag_controls_frame.pack()
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            self.video_canvas.image = imgtk

            self.root.update()
            time.sleep(0.03 / self.playback_speed.get())

    def submit_tag(self):
        tag = self.selected_tag.get().strip()

        if tag == "-- Choose --":
            proceed = messagebox.askyesno(
                "Skip Fixation?",
                "You didn't tag this fixation. Are you sure you want to skip it?"
            )
            if not proceed:
                return  # Go back to tagging

        else:
            fixation_id = f"fixation_{self.current_fixation_index}"
            self.metadata_manager.update_fixation_tag(
                subject_name=self.subject_name,
                group_id=self.selected_video["group_id"],
                fixation_id=fixation_id,
                tag=tag
            )

        self.current_fixation_index += 1
        self.tag_controls_frame.pack_forget()
        self.play_next_fixation()

    def pause_video(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
            messagebox.showinfo("Pause", "Video playback paused.")

    def load_next_video(self):
        self.current_video_index += 1
        if self.current_video_index >= len(self.videos):
            messagebox.showinfo("Done", "You have completed all videos!")
            self.video_selector.set("")
            self.selected_video = None
            if self.next_video_button:
                self.next_video_button.destroy()
                self.next_video_button = None
            return

        # Set the next video
        self.selected_video = self.videos[self.current_video_index]
        self.current_fixation_index = 0
        self.video_selector.set(self.selected_video["group_id"])

        if self.next_video_button:
            self.next_video_button.destroy()
            self.next_video_button = None

        self.play_next_fixation()


if __name__ == "__main__":
    root = tk.Tk()
    MediaPlayerApp(root)
    root.mainloop()
