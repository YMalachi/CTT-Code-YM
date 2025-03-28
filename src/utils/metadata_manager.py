import json
import os
import logging
from pathlib import Path

class MetadataManager:
    def __init__(self, base_directory="..\metadata"):
        """
        Initializes the MetadataManager.
        :param base_directory: Directory where all metadata files will be stored.
        """
        self.base_directory = base_directory
        Path(self.base_directory).mkdir(parents=True, exist_ok=True)
        logging.info(f"MetadataManager initialized. Metadata directory: {self.base_directory}")

    def _get_subject_metadata_path(self, subject_name):
        """
        Returns the file path for a specific subject's metadata.
        """
        return os.path.join(self.base_directory, f"{subject_name}.json")

    def load_metadata(self, subject_name):
        """
        Loads the metadata for a specific subject.
        """
        metadata_path = self._get_subject_metadata_path(subject_name)
        try:
            with open(metadata_path, "r") as file:
                logging.debug(f"Loaded metadata for subject: {subject_name}")
                return json.load(file)
        except FileNotFoundError:
            logging.warning(f"No metadata file found for subject: {subject_name}. Creating new metadata.")
            return {"name": subject_name, "videos": []}

    def save_metadata(self, subject_name, metadata):
        """
        Saves the metadata for a specific subject safely.
        """
        metadata_path = self._get_subject_metadata_path(subject_name)
        temp_path = f"{metadata_path}.tmp"
        try:
            # Write to a temporary file first
            with open(temp_path, "w") as temp_file:
                json.dump(metadata, temp_file, indent=4)

            # Replace the original file
            os.replace(temp_path, metadata_path)
            logging.info(f"Metadata saved for subject: {subject_name} in {metadata_path}")

        except Exception as e:
            logging.error(f"Failed to save metadata for subject: {subject_name}. Error: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    def add_video_snippet(self, subject_name, group_data):
        """
        Adds a video snippet and its associated group fixation data to a subject's metadata.
        :param subject_name: The name of the subject.
        :param group_data: A dictionary containing group-level and nested fixation data.
        """
        try:
            metadata = self.load_metadata(subject_name)
            # Add the snippet with its group data
            metadata["videos"].append({
                "snippet_path": None,
                **group_data  # Unpack the group-level and nested fixations
            })
            group_id = group_data["group_id"]
            logging.info(f"Added video snippet with fixations for subject {subject_name}, snippet {group_id}")
            self.save_metadata(subject_name, metadata)
        except WindowsError as e:
            logging.warning(f"Metadata for subject {subject_name} already exists in the metadata folder. Delete if you wish to define new metadata")

    def update_fixation_snippet_path(self, subject_name, snippet_path, idx):
        """
        Updates the snippet path of a fixation group in the subject's metadata.\
        :param subject_name: Subject's name.
        :param snippet_path: A path to the snippet video.
        :param idx: Number of group (int).
        """
        metadata = self.load_metadata(subject_name)
        vid_lst = metadata["videos"]
        L = len(vid_lst)
        for group_id in range(L):
            if vid_lst[group_id]["group_id"] == f"group_{idx}":
                metadata["videos"][group_id]["snippet_path"] = snippet_path
                break
        try:
            self.save_metadata(subject_name, metadata)
            logging.debug(f"Updated snippet path for subject: {subject_name} successfully, snippet_{idx}")
        except Exception as e:
            logging.error(f"There was a problem with updating the video snippet path for subject: {subject_name}, snippet_{idx}. error: {e}")
            raise e
    def update_fixation_tag(self, subject_name, group_id, fixation_id, tag):
        """
        Updates the tag of a fixation in the subject's metadata.
        :param subject_name: The name of the subject.
        :param group_id: The group ID where the fixation resides.
        :param fixation_id: The ID of the fixation to update.
        :param tag: The new tag value to assign.
        """
        metadata = self.load_metadata(subject_name)
        for video in metadata["videos"]:
            if video["group_id"] == group_id:
                if fixation_id in video["fixations"]:  # Check if the fixation exists in the group
                    video["fixations"][fixation_id]["tag"] = tag  # Update the tag
                    logging.debug(
                        f"Updated fixation {fixation_id} for subject {subject_name} in {group_id} with tag: {tag}")
                    self.save_metadata(subject_name, metadata)
                    return
                else:
                    logging.warning(f"Fixation {fixation_id} not found in group {group_id} for subject {subject_name}.")
                    return
        # in case group_id isn't found:
        logging.error(f"{group_id} not found for subject {subject_name}. No changes made.")

