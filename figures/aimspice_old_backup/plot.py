import os
import pandas as pd
import matplotlib
import numpy as np

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
            print(f"Detected CSV file: {filepath}")  # Debugging print

            # Step 2: Check for unwanted lines
            with open(filepath, 'r') as f:
                lines = f.readlines()

            # Check if the unwanted lines are present
            if "AIM-Spice kernel Version" in lines[0]:
                print(f"Removing lines for file: {filepath}")  # Debugging print
                with open(filepath, 'w') as f:
                    f.writelines(lines[4:])

            # Now, preprocess and plot
            lines = preprocess_file(filepath)
            print(f"First few lines of {filepath}:\n{lines[:5]}")  # Debugging print
            
            with open(filepath, 'w') as f:
                for line in lines:
                    f.write(f"{line}\n")

            # Plotting
            data = pd.read_csv(filepath, delimiter=",", header=0)  # Assuming the first row contains the headers

            fig, ax = plt.subplots(figsize=(10, 6))

            fig.suptitle(f"Data from {file}", fontsize=16)

            time = data[data.columns[0]].astype(float)  # Ensure that the time data is in float format

            # Define a dictionary for specific styles for each signal
            styles = {
                "v(clk)": {"linestyle": "--", "color": "lightblue"},
                "v(data)": {"linestyle": "--", "color": "lightgreen"},
                "v(out)": {}  # Default style for other signals
            }

            for i in range(1, data.shape[1]):
                col_name = data.columns[i]
                ax.plot(time, data[col_name], label=col_name, **styles.get(col_name, {}))
                
            ax.set_xlabel('Time')
            ax.set_ylabel('Voltage (V)')
            ax.legend()
            ax.set_xticks(np.linspace(time.min(), time.max(), 10))  # Adjusting the X-axis

            plt.tight_layout()
            plt.savefig(f"{filepath}.png")
            plt.close()


print("Processing completed.")
