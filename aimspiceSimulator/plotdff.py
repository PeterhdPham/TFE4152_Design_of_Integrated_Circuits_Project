import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re


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

# Helper function to process the file
def preprocess_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Replace spaces with commas
    content = content.replace(" ", ",")
    return content.splitlines()

# Helper function to generate the title based on filename
def generate_title(filename):
    corner, temp, wave = filename.split('.')[0][:2], filename.split('.')[0][2:4], filename.split('.')[0][4:]
    return f"Corner: {corner}, Temperature: {temp}°C, Simulation: {simulation_descriptions[wave]}"

# Dictionary to map filenames to descriptions
simulation_descriptions = {
    'W1': 'Datasampling and Clock Edge',
    'W2': 'Data sampling during stable clock edges.',
    'W3': 'Synchronous Reset',
}

# List all CSV files in the current directory
csv_files = [f for f in os.listdir('.') if f.endswith('.csv') and f[:2] in ['FF', 'FS', 'SF', 'SS', 'TT'] and f[4:6] in ['W1', 'W2', 'W3']]

for filename in csv_files:
    filepath = os.path.join('.', filename)

    # Create title
    title = generate_title(filename)

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
    plot_filename = os.path.splitext(filename)[0] + ".png"
    plt.savefig(os.path.join(output_dir, plot_filename))
    plt.close()

    # Additional Plotting for W1 from 100ns to 130ns
    if 'W1' in filename:
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.suptitle(f"{title} (100ns - 130ns)", fontsize=16)

        time_w1 = time[(time >= 100e-9) & (time <= 130e-9)]
        for i in range(1, data.shape[1]):
            col_name = data.columns[i]
            ax.plot(time_w1, data.loc[(time >= 100e-9) & (time <= 130e-9), col_name], label=col_name, **styles.get(col_name, {}))

        ax.set_xlabel('Time')
        ax.set_ylabel('Voltage (V)')
        ax.legend()
        ax.set_xticks(np.linspace(time_w1.min(), time_w1.max(), 10))
        plt.tight_layout()
        plot_filename_w1 = os.path.splitext(filename)[0] + "SC.png"
        plt.savefig(os.path.join(output_dir, plot_filename_w1))
        plt.close()

print("Processing of CSV files completed.")

