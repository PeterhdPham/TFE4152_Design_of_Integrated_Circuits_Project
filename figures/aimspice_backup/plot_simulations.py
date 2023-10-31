import os
import pandas as pd
import matplotlib
import numpy as np

import matplotlib.pyplot as plt

root_dir = "figures/aimspice"
base_dir = "figures/aimspice"
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

# Dictionary to map filenames to descriptions
simulation_descriptions = {
    'W1': 'Datasampling and Clock Edge',
    'W2': 'Asynchronous Reset',
    'W3': 'Data sampling during stable clock edges.',
    'W4': 'Synchronous Reset',
    'I': 'Leakage current'
}


# Walk through directories
for dirpath, dirnames, filenames in os.walk(base_dir):
    for filename in filenames:
        if filename.endswith('.csv'):
            filepath = os.path.join(dirpath, filename)

            # Extract corner, temperature, and simulation type
            corner = os.path.basename(os.path.dirname(os.path.dirname(filepath)))
            temperature = os.path.basename(os.path.dirname(filepath))
            simulation_type = filename.split('.')[0]

            # Create title
            title = f"Corner: {corner}, Temperature: {temperature}°C, Simulation: {simulation_descriptions[simulation_type]}"
            
            # Check and remove unwanted lines
            with open(filepath, 'r') as f:
                lines = f.readlines()

            if "AIM-Spice kernel Version" in lines[0]:
                with open(filepath, 'w') as f:
                    f.writelines(lines[4:])

            # Preprocess and plot
            lines = preprocess_file(filepath)
            
            with open(filepath, 'w') as f:
                for line in lines:
                    f.write(f"{line}\n")

            # Plotting
            data = pd.read_csv(filepath, delimiter=",", header=0)  # Assuming the first row contains the headers
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.suptitle(title, fontsize=16)

            time = data[data.columns[0]].astype(float)
            styles = {
                "v(clk)": {"linestyle": "--", "color": "lightblue"},
                "v(data)": {"linestyle": "--", "color": "lightgreen"},
                "v(out)": {}
            }

            for i in range(1, data.shape[1]):
                col_name = data.columns[i]
                ax.plot(time, data[col_name], label=col_name, **styles.get(col_name, {}))
                
            ax.set_xlabel('Time')
            ax.set_ylabel('Voltage (V)')
            ax.legend()
            ax.set_xticks(np.linspace(time.min(), time.max(), 10))
            plt.tight_layout()
            plt.savefig(f"{filepath}.png")
            plt.close()

print("Processing completed.")