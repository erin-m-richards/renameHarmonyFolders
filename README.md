# renameHarmonyFolders
When using 'Write Archive' to export images from the Revvity Opera Phenix and Harmony 5.2/5.3, TIFs export in folders with GUID names rather than with user-given platenames.

<img width="405" height="471" alt="Screenshot 2026-11-24 123419" src="https://github.com/user-attachments/assets/4182d5ba-05ac-4639-9aef-2d2a0645b9e3" />

&emsp;

The user-given platenames for these folders are in an .html file inside of each folder.

&emsp;&emsp;hs\ → folder named for GUID\ → html file named for GUID

This package is a Python script to rename each folder from its original GUID name to the user-given platename (to make them more human-readable).

_Note: Renaming the folders does not allow these data to be read back into Harmony using 'Read Archive'. Folders must be renamed to their original GUID name before trying 'Read Archive'._

______________________________________________________________________________

## Inputs:
  - Pop-up window that asks the user to select the 'hs' Archive file that was created using 'Write Archive' to export data from Harmony 5.2/5.3.

## Outputs:
  - .csv file with old folder names (GUIDs) and new folder names (user-given platenames)
  - Directly renamed folders _or_ renamed copies of the folders, depending on user input

______________________________________________________________________________

## Required packages (may work with lower, but has not been tested)
  - python 3.13 and dependencies
  - pandas 3.1 and dependencies
  - lxml 6.1 and dependencies

All packages are contained in the env.yml file.

______________________________________________________________________________

## Installation instructions (conda environment and python script)
1. (Install) Download env.yml and renameHarmonyFolders.py or install the latest "Script_" Release to your computer.
2. (Install) In Terminal, create necessary conda environment with ``conda env create -f full\path\to\env.yml``.
3. (Run) Activate conda environment with ``conda activate renameHarmonyFolders``.
4. (Run) Run python script with ``python full\path\to\renameHarmonyFolders.py``.
5. (Run) A pop-up window will appear asking you to select the 'hs' archive folder that contains your exported images.
6. (Run) A .csv file is created with the old folder names (GUIDs) and the new folder names (user-given platenames). If you'd like, you can edit the .csv file _now_ and save it BEFORE you choose the .csv file in the next pop-up window.
7. (Run) A new pop-up window will ask if you'd like to rename the folders directly or if you'd like to rename copies of those folders.
8. (Run) Any issues with folders will appear in the Terminal as a printed message.
9. (Run) Close the Terminal.
