# CTT-Code-YM
 CTT project code and documentation
 Legend:
1.	Functions:
 1.1.	Pre Processing Functions
  1.1.1.	get_video_folders – line TBD
  1.1.2.	process_video_dirs - line TBD



























**get_video_folders(subjects_dir):**
This function retrieves the directories for the "Trail B" test recordings for each subject.
It traverses the given directory structure, which is expected to contain subject folders.
Each subject folder should have a `REC_ET` folder, and inside that, a `PL` folder with test 
video directories. The function identifies the latest folder (e.g., `003`, `001`) for each 
subject and collects them into a list.
    Input:
***IMPORTANT: USE RAW STRING OR REPLACE DIRECTORY PATH'S " \ " WITH " / " OTHERWISE IT WON'T WORK***
subjects_dir (raw str): The path to the root directory containing all subject data and recordings. 
Example: 'C:/Data' or '/home/user/Data'.
    Output:
list: A list of full paths to the "Trail B" test directories (as strings), one for each subject. 
Each path corresponds to the latest numbered directory inside the `PL` folder for each subject.
    Example:
If the input is `C:/Data`, the output might look like:
C:/Data/YM109/REC_ET/PL/003',
C:/Data/YM110/REC_ET/PL/002',
C:/Data/YM111/REC_ET/PL/004'
**********************************************************************************************************

**process_video_dirs(dir_list, pupil_player_path, output_base_dir):**
Processes a list of directories in Pupil Player with static parameters
and exports the results to a "Trail B Data" folder, with subfolders for each subject containing the
exported data from Pupil Player (world video, fixation txt and gaze info only).
    
    Input:
dir_list (list): List of directory paths to process.
pupil_player_path (str): Path to the Pupil Player **executable**.
output_base_dir (str): Base directory where "Trail B Data" will be created.
    Output:
"Trail B Data" directory in output_base_dir containing a folder for each test
subject with it's exported data from Pupil Player
    Example:
If the input is:
                dir_list: [r'C:/Data/YM109/REC_ET/PL/003',
                           r'C:/Data/YM110/REC_ET/PL/002',
                           r'C:/Data/YM111/REC_ET/PL/004']
                pupil_player_path: r'C:/pupil_player.exe'
                output_base_dir: r'C:/folder'
The output will be a new directory inside C:/folder that will look like:
                C:/folder/Trail B Data/YM109/...(exported data)
                C:/folder/Trail B Data/YM110/...(exported data)
                C:/folder/Trail B Data/YM111/...(exported data)
**********************************************************************************************************

