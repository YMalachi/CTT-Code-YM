[//]: # (# CTT Project: Eye-Tracking and Gaze Analysis in VR)

[//]: # (## Project Overview)

[//]: # ()
[//]: # (This project involves analyzing gaze and fixation data collected using Pupil Labs' eye-tracking system in a virtual reality &#40;VR&#41; environment. The study explores how gaze behavior affects task performance, specifically focusing on the Color Trail Test &#40;CTT&#41;. The main objective is to determine whether participants who fixate on specific balls in the VR environment can later locate them faster when prompted.)

[//]: # (## Folder and File Structure)

[//]: # (### Project folder)

[//]: # (- **src/**: Contains the main project files.)

[//]: # (  - `main.py`: The entry point of the project.)

[//]: # (  - **utils/**: Includes helper scripts and preprocessing functions.)

[//]: # (    - `preprocessing.py`: Handles cleaning, filtering, and preprocessing of gaze and fixation data.)

[//]: # (  - **custom_plugins/**: A directory to store custom plugins for Pupil Labs &#40;default: empty&#41;)

[//]: # (- **setup/** : Contains GlobalContainer and other core classes)

[//]: # (- **data/**: Directory for raw and processed data.)

[//]: # (- **results/**: Output files such as visualizations and analysis summaries.)

[//]: # (- `README.md`: Documentation for the project.)

[//]: # (### Pupil folder &#40;after pupil is installed&#41;)

[//]: # (- **pupil_src/**: Pupil Labs' source code.)

[//]: # (- **pupil_env/**: Virtual environment containing all dependencies &#40;if you've decided to go with venv&#41;.)

[//]: # (## Setup Instructions)

[//]: # (Note 1: I strongly recommend checking out pupil labs' documentation first, this project relies on their open-source code.)

[//]: # ()
[//]: # (Note 2: I recommend creating a virtual environment for this &#40;step 2&#41;.)

[//]: # ()
[//]: # (Note 3: Python 3.10.11 is used to develop this project, I recommend you use the same.)

[//]: # ()
[//]: # (1. Clone pupil's repository to your local machine &#40;while in a preferred folder&#41;.)

[//]: # (   ```bash)

[//]: # (   git clone https://github.com/pupil-labs/pupil.git)

[//]: # (   cd pupil)

[//]: # (   git checkout develop)

[//]: # (2. Create a virtual environment &#40;optional&#41;:)

[//]: # (   ```bash)

[//]: # (   python -m venv pupil_env)

[//]: # (3. Install dependencies:)

[//]: # (   ```bash)

[//]: # (   cd pupil)

[//]: # (   python -m pip install -r requirements.txt)

[//]: # (4. Make sure you have pupil_env in your interpreter path.)

[//]: # (## Data Description)
[//]: # ()
[//]: # (### Input Data)

[//]: # (- The raw data collected using Pupil Labs' eye-tracking system is stored in the `data/` folder.)

[//]: # (- Input files are typically:)

[//]: # (  - **World video recordings**: `.mp4` files of the VR environment.)

[//]: # (  - **Fixation files**: `.csv` files containing gaze and fixation data.)

[//]: # ()
[//]: # (### Output Data)

[//]: # (- Processed results, such as visualizations or aggregated statistics, are saved in the `results/` folder.)

[//]: # (- Output formats include:)

[//]: # (  - **Plots and Graphs**: Visualizations of gaze behavior.)

[//]: # (  - **Summaries**: CSV or text files with aggregated metrics.)

# Video Processing for Fixation-Based Neural Network Input

## **Project Overview**
This project provides a framework for processing video data around fixations in a structured and automated manner. It is designed to facilitate the preparation of trimmed and padded video snippets that align with neural network input requirements.

### **Core Features**
1. **Data Validation and Management**:
   - Validate directory structures and file existence for data integrity.
   - Synchronize data between Pupil Labs and Unity files.
2. **Fixation-Based Video Trimming**:
   - Trim video snippets around fixations with precise frame control.
   - Pad video snippets to a fixed length for uniformity.
3. **Error Handling and Logging**:
   - Extensive logging to trace execution and debug efficiently.
   - Robust exception handling to manage unexpected errors.

---

## **Directory Structure**
```
Project Directory
├── CoreClasses.py
├── Preprocessing.py
├── Data
│   ├── Subject_Folder
│   │   ├── REC_ET
│   │   │   ├── PL
│   │   │   └── UNI
│   └── Outputs
└── README.md
```

---

## **Code Organization**

### **CoreClasses.py**
Defines the foundational classes for managing and validating data.

#### **Classes**

1. **`DataContainer`**
   - Represents the base structure for data manipulations.
   - Validates the root directory containing subject data.

   **Key Methods**:
   - `__init__(data_path)`: Initializes with the root data path.
   - `__repr__()`: Provides a string representation.

2. **`ProcessingContainer`**
   - Extends `DataContainer` to handle processing-specific attributes.
   - Constructs paths to Pupil Labs and Unity data, validating their existence.

   **Key Methods**:
   - `_create_out_path(output_path)`: Creates an output directory for video snippets.

---

### **Preprocessing.py**
Implements video processing logic for fixation-based tasks.

#### **Classes**

1. **`VideoPreprocessor`**
   - Handles video trimming, synchronization, and fixation processing.

   **Key Attributes**:
   - `subject_name`: Name of the subject.
   - `data_path`: Root data directory.
   - `pl_path`: Path to Pupil Labs data.
   - `uni_path`: Path to Unity data.
   - `out_path`: Path for storing processed outputs.

   **Key Methods**:

   - **`match_pl_uni()`**:
     - Synchronizes Unity files and Pupil Labs directories using timestamps.
     - Returns a dictionary mapping Unity files to Pupil Labs directories.

   - **`_get_fixations_ts()`**:
     - Extracts fixation start and end frames from Pupil Labs CSV data.
     - Returns a dictionary: `{fixation_id: (start_frame, end_frame)}`.

   - **`_merge_neighboring_fixations(fixation_dict, threshold=5)`**:
     - Merges consecutive fixations close in time.
     - Ensures consistent snippet length of 180 frames.
     - Returns a dictionary: `{group_id: (start_frame, end_frame)}`.

   - **`trim_vid_around_fixations(merged_fixations_dict)`**:
     - Trims video around fixation groups.
     - Pads snippets to 180 frames using black frames.
     - Saves snippets in the output directory.

   - **`_create_out_path_for_video_snippets()`**:
     - Creates a folder for storing video snippets.

---

## **How to Use**

### **Setup**
1. Clone the repository or download the code files.
2. Ensure the directory structure follows the format:
   - **`data_path/subject_name/REC_ET/PL`**
   - **`data_path/subject_name/REC_ET/UNI`**
3. Install dependencies:
   ```bash
   pip install opencv-python numpy pandas av
   ```

### **Steps to Process Data**

#### **Initialization**
```python
from CoreClasses import DataContainer, ProcessingContainer
from Preprocessing import VideoPreprocessor

# Define paths
DATA_PATH = "path_to_data_directory"
SUBJECT_NAME = "Subject_Name"

# Initialize containers
data = DataContainer(data_path=DATA_PATH)
processing = ProcessingContainer(data_path=data.data_path, subject_name=SUBJECT_NAME)
processing._create_out_path("path_to_outputs")
```

#### **Video Preprocessing**
```python
# Initialize video preprocessor
vid_pro = VideoPreprocessor(processing, trail="T2")

# Match Unity and Pupil Labs data
vid_pro.match_pl_uni()

# Extract and merge fixations
fix_dict = vid_pro._get_fixations_ts()
merged_dict = vid_pro._merge_neighboring_fixations(fix_dict)

# Trim videos around fixations
vid_pro.trim_vid_around_fixations(merged_dict)

print(f"Processed {len(merged_dict)} snippets.")
```

---

## **Important Notes**

1. **Validation**:
   - Ensure the directory structure matches the expected format before processing.
2. **Padding**:
   - Video snippets are padded to 180 frames using black frames for consistency.
3. **Error Handling**:
   - Logs errors and warnings for missing files or directory mismatches.
4. **Future Enhancements**:
   - Add a mask file to identify padded frames.
   - Build a user-friendly interface (CLI or GUI).

---

## **Dependencies**
- Python 3.8+
- OpenCV
- NumPy
- Pandas
- Logging

---

## Contact
For any questions or support, please contact:
- **Yotam**: yotammalachi@mail.tau.ac.il