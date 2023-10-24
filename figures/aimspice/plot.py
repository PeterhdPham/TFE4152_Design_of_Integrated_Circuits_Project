import os
import pandas as pd
import matplotlib.pyplot as plt

root_dir = "figures/aimspice"
# Helper function to process the file
def preprocess_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Replace spaces with commas
    content = content.replace(" ", ",")

    return content.splitlines()
# Helper function to generate the title based on filepath
def generate_title(filepath):
    parts = filepath.split(os.sep)  # Split the path into folders
    corner, temp, file = parts[-3], parts[-2], parts[-1]
    
    if 'W' in file:
        return f"Voltage for {corner} corner at {temp} degrees"
    elif 'I' in file:
        return f"Leakage current for {corner} corner at {temp} degrees"

# Step 1: Recursively go through all folders
for root, dirs, files in os.walk(root_dir):
    print(f"Traversing directory: {root}")

    for file in files:
        if file.endswith('.csv'):
            filepath = os.path.join(root, file)
            print(f"Detected CSV file: {filepath}") # Debugging print

            # Step 2: Remove unwanted lines
            with open(filepath, 'r') as f:
                lines = preprocess_file(filepath)
                print(f"First few lines of {filepath}:\n{lines[:5]}")  # Debugging print

            # Check if the unwanted lines are present
            if "AIM-Spice kernel Version" in lines[0]:
                print(f"Removing lines for file: {filepath}")  # Debugging print
                with open(filepath, 'w') as f:
                    f.writelines(lines[4:])

            # Step 3: Plot the data
            data = pd.read_csv(filepath, delimiter=",", header=None)
            time = data[0].values
            y_data = data[1].values

            if "W" in file:
                y_label = "Voltage (V)"
            elif "I" in file:
                y_label = "Current (A)"
            else:
                continue  # ignore other files

            plt.figure()
            plt.plot(time, y_data)
            plt.xlabel('Time')
            plt.ylabel(y_label)
            plt.title(generate_title(filepath))  # Use the helper function to get the title
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(os.path.join(root, f"{file}.png"))  # save the plot in the same directory as the CSV
            print(f"Saved plot for {filepath}")  # Debugging print
            plt.close()  # close the current plot

print("Processing completed.")
