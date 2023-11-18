import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Function to calculate leakage power
def calculate_leakage_power(leakage_current, vdd_value):
    return leakage_current * float(vdd_value)

# Function to extract parameters from the .cir file
def extract_params_from_cir(filepath):
    params = {}
    with open(filepath, 'r') as file:
        for line in file:
            if line.startswith('.param'):
                key, value = line.split('=')[0].strip().split()[-1], line.split('=')[1].strip()
                params[key] = value
    return params

# Read the param.cir file and extract parameters
param_file_path = './param.cir'
params = extract_params_from_cir(param_file_path)

# Construct folder name from parameters
folder_name = f"{params['vdd_value']}V_{params['N_Width']}x{params['N_Length']}_{params['P_Width']}x{params['P_Length']}".replace("u", "")
output_dir = f"../figures/aimspice/{folder_name}"

# Ensure the output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# New: Define and ensure the existence of the CSV subfolder
csv_output_dir = os.path.join(output_dir, "CSV")
if not os.path.exists(csv_output_dir):
    os.makedirs(csv_output_dir)

# Additional data structure for leakage power and leakage current
leakage_power_data = {}
leakage_current_data = {}

# Helper function to process the file
def preprocess_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Replace spaces with commas
    content = content.replace(" ", ",")

    return content.splitlines()
# Helper function to generate the title based on filename

# Global Variables
corners = ['FS', 'SS', 'TT', 'SF', 'FF']

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
    
    output_csv_filepath = os.path.join(csv_output_dir, filename)
    # Calculate the required value
    avg_current2 = np.abs(data[data.columns[1]]).mean()
    avg_current3 = np.abs(data[data.columns[2]]).mean()
    
    # Add the data to the dictionary
    if temperature not in leakage_current_data:
        leakage_current_data[temperature] = {}
    tot_current = 2*avg_current2+4*avg_current3
    leakage_current_data[temperature][corner] = tot_current
    # Calculate leakage power
    leakage_power = calculate_leakage_power(tot_current, params['vdd_value'])
    if temperature not in leakage_power_data:
        leakage_power_data[temperature] = {}
    leakage_power_data[temperature][corner] = leakage_power

sorted_temperatures = sorted(leakage_current_data.keys(), key=int)

def plot_leakage_data(leakage_data, ylabel, output_filename):
    bar_width = 0.15
    index = np.arange(len(sorted_temperatures))
    colors = ['salmon', 'paleturquoise', 'palegoldenrod', 'palegreen', 'palevioletred']

    fig, ax = plt.subplots()

    for idx, corner in enumerate(corners):
        leakage_values = [leakage_data[temp][corner] for temp in sorted_temperatures]
        ax.bar(index + idx * bar_width, leakage_values, bar_width, label=corner, color=colors[idx])

    ax.set_xlabel('Temperature')
    ax.set_ylabel(ylabel)
    ax.set_xticks(index + bar_width * 2)
    ax.set_xticklabels(sorted_temperatures)
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, output_filename))

# Plotting leakage current
plot_leakage_data(leakage_current_data, 'Leakage Current (A)', "leakage_current.png")

# Plotting leakage power
plot_leakage_data(leakage_power_data, 'Leakage Power (W)', "leakage_power.png")

# Function to add or update data in the CSV
def add_or_update_csv(csv_file, folder_name, leakage_power_data):
    if os.path.exists(csv_file):
        # Read existing data
        df = pd.read_csv(csv_file, index_col='parameters')
    else:
        # Create a new DataFrame if the file doesn't exist
        df = pd.DataFrame(columns=['parameters', 'FS', 'SS', 'TT', 'SF', 'FF'])
        df.set_index('parameters', inplace=True)

    if folder_name not in df.index:
        # Add new data
        data = [leakage_power_data[temp]['FS'] for temp in ['27']]
        data += [leakage_power_data[temp]['SS'] for temp in ['27']]
        data += [leakage_power_data[temp]['TT'] for temp in ['27']]
        data += [leakage_power_data[temp]['SF'] for temp in ['27']]
        data += [leakage_power_data[temp]['FF'] for temp in ['27']]
        df.loc[folder_name] = data

    # Save the updated dataframe
    df.to_csv(csv_file)

# File path
power_param_file = './power_param.csv'

# Call the function to add or update the CSV
add_or_update_csv(power_param_file, folder_name, leakage_power_data)

print("Processing and saving completed.")
