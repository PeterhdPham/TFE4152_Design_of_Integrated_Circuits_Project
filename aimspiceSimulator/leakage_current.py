import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
output_dir = "../figures/aimspice"


leakage_data = {}
# Helper function to process the file
def preprocess_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Replace spaces with commas
    content = content.replace(" ", ",")

    return content.splitlines()
# Helper function to generate the title based on filename


# Dictionary to map filenames to descriptions
simulation_descriptions = {
    'W1': 'Datasampling and Clock Edge',
    'W2': 'Data sampling during stable clock edges.',
    'W3': 'Synchronous Reset',
}

# List all CSV files in the current directory
csv_files = [f for f in os.listdir('.') if f.endswith('.csv') and f[:2] in ['FF', 'FS', 'SF', 'SS', 'TT'] and f[4:5] in ['I']]

for filename in csv_files:
    filepath = os.path.join('.', filename)

    # Check and remove unwanted lines
    with open(filepath, 'r') as f:
        lines = f.readlines()

    if "AIM-Spice kernel Version" in lines[0]:
        with open(filepath, 'w') as f:
            f.writelines(lines[4:])

    # Preprocess and plot
    lines = preprocess_file(filepath)
    temperature = filename.split('.')[0][2:4]
    corner = filename.split('.')[0][:2]
    
    with open(filepath, 'w') as f:
        for line in lines:
            f.write(f"{line}\n")
    # Read the data
    data = pd.read_csv(filepath, delimiter=",", header=0)
    
    # Calculate the required value
    avg_current2 = np.abs(data[data.columns[1]]).mean()
    avg_current3 = np.abs(data[data.columns[2]]).mean()
    
    # Add the data to the dictionary
    if temperature not in leakage_data:
        leakage_data[temperature] = {}
    tot_current = 2*avg_current2+4*avg_current3
    leakage_data[temperature][corner] = tot_current


# Sort the leakage_data by temperature for proper plotting
sorted_temperatures = sorted(leakage_data.keys(), key=int)


corners = ['FS','SS', 'TT', 'SF',  'FF']
bar_width = 0.15
index = np.arange(len(sorted_temperatures))
colors = ['salmon', 'paleturquoise', 'palegoldenrod', 'palegreen',  'palevioletred']

fig, ax = plt.subplots()

for idx, corner in enumerate(corners):
    leakage_values = [leakage_data[temp][corner] for temp in sorted_temperatures]
    ax.bar(index + idx * bar_width, leakage_values, bar_width, label=corner, color=colors[idx])

ax.set_xlabel('Temperature')
ax.set_ylabel('Leakage Current')
# ax.set_title('Leakage Current Comparison across Temperatures and Corners')
ax.set_xticks(index + bar_width * 2)
ax.set_xticklabels(sorted_temperatures)
ax.legend()

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "leakage_current.png"))
print("Processing completed.")
