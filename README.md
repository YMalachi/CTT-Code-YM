# CTT-Code-YM
 CTT project code and documentation </br>
 Legend: </br>
1.	Functions: </br>
 1.1.	Pre Processing Functions</br>
  1.1.1.	get_video_folders 
  1.1.2.	process_video_dirs 
</br>
</br>

**1.1.1 get_video_folders(subjects_dir):** </br>
This function retrieves the directories for the "Trail B" test recordings for each subject. </br>
It traverses the given directory structure, which is expected to contain subject folders. </br>
Each subject folder should have a `REC_ET` folder, and inside that, a `PL` folder with test </br>
video directories. The function identifies the latest folder (e.g., `003`, `001`) for each </br>
subject and collects them into a list.</br>
</br>
    **Input:**</br>
***IMPORTANT: USE RAW STRING OR REPLACE DIRECTORY PATH'S " \ " WITH " / " OTHERWISE IT WON'T WORK***</br>
subjects_dir (raw str): The path to the root directory containing all subject data and recordings. </br>
Example: 'C:/Data' or '/home/user/Data'.</br>
</br>
    **Output:**</br>
list: A list of full paths to the "Trail B" test directories (as strings), one for each subject. </br>
Each path corresponds to the latest numbered directory inside the `PL` folder for each subject.</br>
</br>
    **Example:**</br>
If the input is `C:/Data`, the output might look like:</br>
- [
C:/Data/YM109/REC_ET/PL/003',</br>
C:/Data/YM110/REC_ET/PL/002',</br>
C:/Data/YM111/REC_ET/PL/004'
] </br>

**********************************************************************************************************</br>

**1.1.2 process_video_dirs(dir_list, pupil_player_path, output_base_dir):**</br>
Processes a list of directories in Pupil Player with static parameters</br>
and exports the results to a "Trail B Data" folder, with subfolders for each subject containing the</br>
exported data from Pupil Player (world video, fixation txt and gaze info only).</br>
</br>
    **Input:**</br>
dir_list (list): List of directory paths to process.</br>
pupil_player_path (str): Path to the Pupil Player **executable**.</br>
output_base_dir (str): Base directory where "Trail B Data" will be created.</br>
</br>
    **Output:**</br>
"Trail B Data" directory in output_base_dir containing a folder for each test</br>
subject with it's exported data from Pupil Player</br>
</br>
    **Example:**</br>
If the input is:</br>
- dir_list: [r'C:/Data/YM109/REC_ET/PL/003', </br>
r'C:/Data/YM110/REC_ET/PL/002', </br>
r'C:/Data/YM111/REC_ET/PL/004'] </br>
- pupil_player_path: r'C:/pupil_player.exe'</br>
- output_base_dir: r'C:/folder'</br>

The output will be a new directory inside C:/folder that will look like:</br>
- [
C:/folder/Trail B Data/YM109/...(exported data)</br>
C:/folder/Trail B Data/YM110/...(exported data)</br>
C:/folder/Trail B Data/YM111/...(exported data)
]</br>

**********************************************************************************************************</br>

