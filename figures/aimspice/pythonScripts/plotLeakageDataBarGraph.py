import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Felper functionto preprocess the CSV file for easier plotting
def preprocess_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Check and remove unwanted lines
    if "AIM-Spice kernel Version" in lines[0] or "AIM-Spice,kernel,Version," in lines[0]:
        lines = lines[4:]

    # Join the lines back into a single string and replace spaces with commas
    content = ''.join(lines).replace(" ", ",")

    return content.splitlines()

# Helper function to generate the title based on filename
def generate_title(filename):
    corner, temp, static = filename.split('.')[0][:2], filename.split('.')[0][2:4], filename.split('.')[0][4:]
    return f"Corner: {corner}, Temperature: {temp}°C, Simulation: {simulation_descriptions[static]}"

# Dictionary to map simulation identifiers to descriptions
simulation_descriptions = {
    'I01': 'Static power leakage when D:0, Clk:0, Res:0, Q:0',
    'I02': 'Static power leakage when D:0, Clk:1, Res:0, Q:0',
    'I03': 'Static power leakage when D:1, Clk:0, Res:0, Q:0',
    'I04': 'Static power leakage when D:1, Clk:1, Res:0, Q:0',
    'I05': 'Static power leakage when D:0, Clk:0, Res:1, Q:0',
    'I06': 'Static power leakage when D:0, Clk:1, Res:1, Q:0',
    'I07': 'Static power leakage when D:1, Clk:0, Res:1, Q:0',
    'I08': 'Static power leakage when D:1, Clk:1, Res:1, Q:0',
    'I09': 'Static power leakage when D:0, Clk:0, Res:1, Q:1',
    'I10': 'Static power leakage when D:0, Clk:1, Res:1, Q:1',
    'I11': 'Static power leakage when D:1, Clk:0, Res:1, Q:1',
    'I12': 'Static power leakage when D:1, Clk:1, Res:1, Q:1',}

corners = ['TT', 'FF'] 

# Function to calculate leakage power
def calculate_leakage_power(leakage_current, vdd_value):
    return leakage_current * float(vdd_value)

# Helper function to extract parameters from foldername
def extract_params_from_config_name(config_name):
    parts = config_name.split('_')
    if len(parts) != 5:
        raise ValueError(f"Invalid configuration name format: {config_name}")

    params = {
        'vdd_value': parts[0],
        'N_Width': parts[1],
        'N_Length': parts[2],
        'P_Width': parts[3],
        'P_Length': parts[4]
    }
    return params

def plot_leakage_data(leakage_data, ylabel, output_filename, output_leakage_current_path, corners):
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
    plt.savefig(os.path.join(output_leakage_current_path, output_filename))
    plt.close(fig)

def append_to_csv(data, csv_filepath):
    if os.path.exists(csv_filepath):
        existing_data = pd.read_csv(csv_filepath)
        # Check if the entry with the same VDD, corner, and temperature already exists
        if not existing_data[(existing_data['VDD'] == data['VDD']) & 
                             (existing_data['Corner'] == data['Corner']) & 
                             (existing_data['Temperature'] == data['Temperature'])].empty:
            return  # Entry exists, do nothing
    else:
        existing_data = pd.DataFrame(columns=['VDD', 'Corner', 'Temperature', 'Power'])

    # Append new data
    existing_data = pd.concat([existing_data, pd.DataFrame([data])], ignore_index=True)
    existing_data.to_csv(csv_filepath, index=False)


# Navigate to the main directory
main_dir = 'figures/aimspice'
config_dirs = [os.path.join(main_dir, d) for d in os.listdir(main_dir) if os.path.isdir(os.path.join(main_dir, d))]
for config in config_dirs:
    try:
        params = extract_params_from_config_name(os.path.basename(config))
    except ValueError as e:
        print(e)
        continue

    csv_leakage_current_path = os.path.join(config, 'CSV', 'leakage_current')
    output_leakage_data_path = os.path.join(config, 'leakage_data')
    
    if not os.path.exists(output_leakage_data_path):
        os.makedirs(output_leakage_data_path)

    csv_files = [f for f in os.listdir(csv_leakage_current_path) if f.endswith('.csv')]
    
    for simulation_id, description in simulation_descriptions.items():
        leakage_current_data = {}
        leakage_power_data = {}
        
        for filename in csv_files:
            if simulation_id in filename:
                filepath = os.path.join(csv_leakage_current_path, filename)
                lines = preprocess_file(filepath)
                with open(filepath, 'w') as f:
                    for line in lines:
                        f.write(f"{line}\n")

                data = pd.read_csv(filepath, delimiter=",", header=0)
                temperature = filename.split('.')[0][2:4]
                corner = filename.split('.')[0][:2]
                current = np.abs((data[data.columns[1]]).mean())
                leakage_power = calculate_leakage_power(current, params['vdd_value'])

                if temperature not in leakage_current_data:
                    leakage_current_data[temperature] = {}
                leakage_current_data[temperature][corner] = current
                
                if temperature not in leakage_power_data:
                    leakage_power_data[temperature] = {}
                leakage_power_data[temperature][corner] = leakage_power
                
                if params['N_Width'] == '0.1u' and params['N_Length'] == '0.1u' and params['P_Width'] == '0.2u' and params['P_Length'] == '0.1u':
                    variable_vdd_csv_path = os.path.join(main_dir, 'variableVDD', 'CSV')
                    os.makedirs(variable_vdd_csv_path, exist_ok=True)
                    csv_filename = f'static_leakage_power_{simulation_id}.csv'  # Unique filename for each simulation
                    csv_filepath = os.path.join(variable_vdd_csv_path, csv_filename)
                    data = {
                        'VDD': params['vdd_value'],
                        'Corner': corner,
                        'Temperature': temperature,
                        'Power': leakage_power
                    }
                    append_to_csv(data, csv_filepath)
                if params['vdd_value'] == '0.6': 
                    os.makedirs(variable_vdd_csv_path, exist_ok=True)
                    csv_filename = f'static_leakage_power_{simulation_id}.csv'  # Unique filename for each simulation
                    csv_filepath = os.path.join(variable_vdd_csv_path, csv_filename)
                    data = {
                        'VDD': params['vdd_value'],
                        'Corner': corner,
                        'Temperature': temperature,
                        'Power': leakage_power
                    }
                    append_to_csv(data, csv_filepath)                

        sorted_temperatures = sorted(leakage_current_data.keys(), key=int)
        plot_leakage_data(leakage_current_data, 'Leakage Current (A)', f"leakage_current_{simulation_id}.png", output_leakage_data_path, corners)
        plot_leakage_data(leakage_power_data, 'Leakage Power (W)', f"leakage_power_{simulation_id}.png", output_leakage_data_path, corners)





