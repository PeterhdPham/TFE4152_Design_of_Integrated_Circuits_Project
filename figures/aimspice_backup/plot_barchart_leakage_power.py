import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

base_dir = "figures/aimspice"

# Dictionary to store leakage currents
leakage_data = {}  # Structure: {temperature: {corner: leakage_value}}
# Helper function to process the file
def preprocess_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Replace spaces with commas
    content = content.replace(" ", ",")

    return content.splitlines()
# Walk through directories
for dirpath, dirnames, filenames in os.walk(base_dir):
    for filename in filenames:
        if filename == 'I.csv':
            filepath = os.path.join(dirpath, filename)
            
            # Extract corner and temperature
            corner = os.path.basename(os.path.dirname(os.path.dirname(filepath)))
            temperature = os.path.basename(os.path.dirname(filepath))
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
            # Read the data
            data = pd.read_csv(filepath, delimiter=",", header=0)
            
            # Calculate the required value
            avg_current = np.abs(data[data.columns[1]]).mean() 
            
            # Add the data to the dictionary
            if temperature not in leakage_data:
                leakage_data[temperature] = {}
            leakage_data[temperature][corner] = avg_current

# Sort the leakage_data by temperature for proper plotting
sorted_temperatures = sorted(leakage_data.keys(), key=int)

corners = ['FS','SS', 'TT', 'SF',  'FF']
bar_width = 0.15
index = np.arange(len(sorted_temperatures))
colors = ['red', 'blue', 'green', 'yellow', 'purple']

fig, ax = plt.subplots()

for idx, corner in enumerate(corners):
    leakage_values = [leakage_data[temp][corner] for temp in sorted_temperatures]
    ax.bar(index + idx * bar_width, leakage_values, bar_width, label=corner, color=colors[idx])

ax.set_xlabel('Temperature')
ax.set_ylabel('Adjusted Leakage Current')
# ax.set_title('Leakage Current Comparison across Temperatures and Corners')
ax.set_xticks(index + bar_width * 2)
ax.set_xticklabels(sorted_temperatures)
ax.legend()

plt.tight_layout()
plt.show()
