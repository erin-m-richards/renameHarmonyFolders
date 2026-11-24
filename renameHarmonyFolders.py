## PART ONE: Get the plate names from the metadata and create an output file.
from os import listdir, path, rename, mkdir
import tkinter as tk
from tkinter import filedialog
import pandas as pd
from datetime import datetime
from shutil import copytree
from pathlib import Path
import sys

# Make main function to run the script:
def main():
    try:
        # Allow user to specify the hs folder.
        root = tk.Tk()
        root.withdraw()
        print("\nNote: The selection window may be hidden behind other windows.\n")
        print("\tSelect the 'hs' folder that contains your exported data.\n")
        hsFolder = filedialog.askdirectory(title="Select the 'hs' folder that contains your exported data.")

        # Make the start of the final data list.
        dataList = pd.DataFrame(columns=['FilePath', 'GUID', 'OrigPlateName', 'Time', 'NewPlateName'])
        nameList = []

        # Create a dummy for the folders that have errors.
        errorList = []

        print("Gathering platenames from metadata...")
        # Save printed details to a .txt file for investigation later.
        outputFile = "RenamePhenixFolders_output_" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".txt"
        sys.stdout = open(path.join(hsFolder, outputFile), 'w', encoding='utf-8')
        print("Gathering platename metadata from:")

        # Get all the plate names from the .xml file for each GUID folder.
        for guidFolder in listdir(hsFolder): # For each guidFolder in the hs directory...
            # Get full folder path.
            guidFolderPath = path.join(hsFolder, guidFolder)
            # Get just the GUID for that folder.
            guid = guidFolderPath.split("\\")[-1]
            # Get the name of the xml file in that GUID folder.
            xmlGUID = guid.split("-")[0:-1]
            xmlGUID = "-".join(xmlGUID)

            if path.isdir(guidFolderPath): # If that guidFolder is a folder...
                print(f"\t{guidFolder}")
                for file in listdir(guidFolderPath): # For each file in that folder...
                    if file == f"{xmlGUID}.xml": # If that file is the correct .xml file...
                        # Read the .xml file.
                        df = pd.read_xml(path.join(guidFolderPath, file))
                        # Get the user-defined plate name from the .xml file.
                        plateName = df['InitialPlateName'][4]
                        # Add the .xml file path, GUID, and original plate name to the data list.
                        newRow = pd.DataFrame({'FilePath': path.join(guidFolderPath, file), 'GUID': guid, 'OrigPlateName': plateName}, index=[0])
                        # Append each GUID folder to the final data list.
                        dataList = pd.concat([dataList, newRow], ignore_index=True)
                        nameList.append(plateName)

        # Handle the cases from automation or when there are multiple plates with the same plate name...
        for u, uName in enumerate(list(set(nameList))): # For each unique plate name in the list...
            # Get the indices of all files with that plate name.
            uNameIdx = [i for i, x in enumerate(nameList) if x == uName]

            if len(uNameIdx) > 1: # If there are multiple plates with that plate name...
                print(f"\n\tMultiple plates found with platename {uName}.")
                print("\t\tAdjusting plate names to include time information...")
                timeList = []

                for idx in uNameIdx: # For each plate with that plate name...
                    # Get the .xml file path for that plate.
                    f = dataList.iloc[int(idx), 0]
                    # Read the .xml file.
                    fDF = pd.read_xml(f)
                    # Get the GUID from the .xml file.
                    guid = fDF['MeasurementID'][0]
                    # Get the date and time that the plate was imaged from the .xml file.
                    date = fDF['Date'][1]
                    dt = date.split(".")
                    dt = dt[0].replace("T", " ")
                    time = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
                    # Save the date and time in the data list.
                    dataList.at[int(idx), 'Time'] = time
                    timeList.append(time)

                # Sort the list of different times associated with this plate name from oldest to most recent.
                orderedTimeList = sorted(timeList)

                for newTimeIdx, orderedTime in enumerate(orderedTimeList): # For each time in this ordered list...
                    # Get the index of this time in the original list.
                    oldTimeIdx = timeList.index(orderedTime)
                    # Generate the new name for the plate that includes time information so that no plate names are the same.
                    newName = f"{uName}_T{(newTimeIdx + 1):03d}"
                    # Save the new name in the data list.
                    dataList.at[int(uNameIdx[oldTimeIdx]), 'NewPlateName'] = newName

            else: # If it is a unique plate name...
                # Get the GUID from the data list.
                guid = dataList.iloc[u,1]
                # Leave the time in the data list blank.
                dataList.at[(uNameIdx)[0], 'Time'] = None
                # Save the new name (the same as the original plate name) in the data list.
                dataList.at[(uNameIdx)[0], 'NewPlateName'] = f"{uName}"

        # Generate output file name to show how the names will change.
        outputPlateNames = "RenamePhenixFolders_output_" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".csv"
        # Save the output file with old and new plate names that will become the folder names.
        dataList.to_csv(path.join(hsFolder, outputPlateNames), index=False)

        # Go back to printing to the Terminal.
        sys.stdout = sys.__stdout__

        print(f"\nProposed new folder names saved to {Path(path.join(hsFolder, outputPlateNames)).resolve()}.")
        print("\tIf you'd like, you can adjust the names now in the file in the 'NewPlateName' column and save the file, BEFORE you select the file in the next step.\n")


        ## PART TWO: Open that file (with any user changes) and rename or copy and rename the folders.
        # Allow user to specify the .csv file.
        root = tk.Tk()
        root.withdraw()
        print("\nNote: The selection window may be hidden behind other windows.\n")
        print("\tSelect the .csv file with the platenames.\n")
        plateNames = filedialog.askopenfilename(title="Select the .csv file with the platenames.")

        # Read the CSV file containing the plate names and file paths.
        dataList = pd.read_csv(plateNames)

        # Build a GUI and allow user to specify whether they want to rename the folder directly or copy and rename the folder.
        root = tk.Tk()
        print("\nNote: The selection window may be hidden behind other windows.\n")
        root.title("Rename folder(s) directly or create renamed copy?")
        root.geometry("680x200")
        for col in range(3):
            root.columnconfigure(col, weight=1)

        label = tk.Label(root, text = """Changing the folder names to human-readable names will not allow the archive to be read into Harmony with 'Read Archive'.\n
            This is only important if you intend to analyze the data in Harmony and the data is no longer in the database (was deleted).\n
            The folder names can be changed back to the original GUIDs from the .xml metadata files, if necessary.\n\n
            Would you like to rename the folder(s) directly or create a renamed copy?""")
        label.grid(row=0, column=0, columnspan=3, pady=20, sticky="nw")

        def on_click():
            global renameChoice
            renameChoice = "rename"
            root.quit()
        def on_click2():
            global renameChoice
            renameChoice = "copy"
            root.quit()
        def on_click3():
            global renameChoice
            renameChoice = "cancel"
            root.quit()
        def on_closing():
            global renameChoice
            renameChoice = "cancel"
            root.quit()
            root.destroy()
            sys.exit()
            
        renameButton = tk.Button(root, text="Rename", command=on_click, bg="#FFFFBF")
        copyButton = tk.Button(root, text="Copy", command=on_click2, bg="#D2E9B4")
        cancelButton = tk.Button(root, text="Cancel", command=on_click3, bg="#FFCFBF")

        renameButton.grid(row=1, column=0)
        copyButton.grid(row=1, column=1)
        cancelButton.grid(row=1, column=2)

        root.protocol("WM_DELETE_WINDOW", on_closing)

        root.mainloop()

        if renameChoice == "rename":
            print("Renaming folders...")
        elif renameChoice == "copy":
            print("Copying and renaming folders...")
        else:
            print("Exiting program without renaming folders...")

        # Save printed details to a .txt file for investigation later.
        sys.stdout = open(path.join(hsFolder, outputFile), 'a', encoding='utf-8')
        if renameChoice == "rename":
            print("\nRenaming folders:")
        elif renameChoice == "copy":
            print("\nCopying and renaming folders:")
        else:
            print("Exiting program without renaming folders.")

        # Get the old and new folder paths.
        for folder in dataList.itertuples(index=False): # For each folder in the set...
            # Get the xml file path from the .csv file.
            xmlPath = folder.FilePath
            # Get the old folder path from the xml file path.
            oldFolder = xmlPath.split('\\')[:-1]
            oldFolderName = "\\".join(oldFolder)
            # Get the new folder path from the old folder path and the new plate name from the .csv file.
            newFolder = oldFolder[:-1]
            newFolderName = "\\".join(newFolder)
            newFolderName = path.join(newFolderName, folder.NewPlateName)

            # Get the absolute paths for the old and new folders and fix any weirdness.
            OFNpath = Path(oldFolderName).resolve()
            NFNpath = Path(newFolderName).resolve()
            NFNpath_short = NFNpath.relative_to(Path(hsFolder).resolve())

            print(f"\t{OFNpath} --> ~\\{NFNpath_short}")

            # Based on the user's choice, copy or rename each folder.
            if renameChoice == "copy": # If the user indicated 'copy'...
                # Create the new folder if it doesn't exist already.
                NFNpath.mkdir(parents=True, exist_ok=True)
                # Copy the files from the old folder to the new folder.
                copytree(OFNpath, NFNpath, dirs_exist_ok=True)
            elif renameChoice == "rename": # If the user indicated 'rename'...
                    # Rename the old folder with the new folder name.
                    try:
                        rename(OFNpath, NFNpath)
                    except FileExistsError:
                        print(f"\t\tError: Folder {NFNpath_short} already exists in this directory. Skipping this folder.")
                        errorList.append(OFNpath)
            else:
                break

        # Go back to printing to the Terminal.
        sys.stdout = sys.__stdout__
        
        print(f"\nFinished processing folders in {Path(hsFolder).resolve()}.\n")

        if len(errorList) > 0:
            print("\tThe following folders could not be renamed because a folder with that name already exists in the directory:")
            for folder in errorList:
                print(f"\t{folder}")
        else:
            print("\tAll folders were renamed successfully.")

        print(f"\tDetails saved to {Path(path.join(hsFolder, outputFile)).resolve()}.")

    finally:
        input("\nPress Enter to close this window...\n")

if __name__ == "__main__":
    main()