# CTT Project: Eye-Tracking and Gaze Analysis in VR
## Project Overview

This project involves analyzing gaze and fixation data collected using Pupil Labs' eye-tracking system in a virtual reality (VR) environment. The study explores how gaze behavior affects task performance, specifically focusing on the Color Trail Test (CTT). The main objective is to determine whether participants who fixate on specific balls in the VR environment can later locate them faster when prompted.
## Folder and File Structure
### Project folder
- **src/**: Contains the main project files.
  - `main.py`: The entry point of the project.
  - `utils/`: Includes helper scripts and preprocessing functions.
    - `preprocessing.py`: Handles cleaning, filtering, and preprocessing of gaze and fixation data.
- **data/**: Directory for raw and processed data.
- **results/**: Output files such as visualizations and analysis summaries.
- `README.md`: Documentation for the project.
### Pupil folder (after pupil is installed)
- **pupil_src/**: Pupil Labs' source code.
- **pupil_env/**: Virtual environment containing all dependencies (if you've decided to go with venv).
## Setup Instructions
Note 1: I strongly recommend checking out pupil labs' documentation first, this project relies on their open-source code.

Note 2: I recommend creating a virtual environment for this (step 2).
1. Clone this repository to your local machine.
   ```bash
   git clone https://github.com/pupil-labs/pupil.git
   cd pupil
   git checkout develop
2. Create a virtual environment (optional):
   ```bash
   cd pupil
   python -m venv pupil_env
3. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
4. Make sure you have pupil_env in your interpreter path.
## Data Description

### Input Data
- The raw data collected using Pupil Labs' eye-tracking system is stored in the `data/` folder.
- Input files are typically:
  - **World video recordings**: `.mp4` files of the VR environment.
  - **Fixation files**: `.csv` files containing gaze and fixation data.

### Output Data
- Processed results, such as visualizations or aggregated statistics, are saved in the `results/` folder.
- Output formats include:
  - **Plots and Graphs**: Visualizations of gaze behavior.
  - **Summaries**: CSV or text files with aggregated metrics.


## Contact

For any questions or support, please contact:
- **Yotam**: yotammalachi@mail.tau.ac.il
