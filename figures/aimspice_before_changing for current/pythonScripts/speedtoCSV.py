import pandas as pd
import os
data=0
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

def find_time_at_threshold(signal, time, threshold):
    """
    Find the time at which the signal crosses a specific threshold.

    :param signal: Pandas Series of signal values
    :param time: Pandas Series of time values corresponding to the signal
    :param threshold: Threshold value to find
    :return: Time at which the signal crosses the threshold
    """
    for i in range(len(signal) - 1):
        if (signal.iloc[i] < threshold <= signal.iloc[i + 1]) or (signal.iloc[i] > threshold >= signal.iloc[i + 1]):
            delta_t = time.iloc[i + 1] - time.iloc[i]
            delta_v = signal.iloc[i + 1] - signal.iloc[i]
            return time.iloc[i] + ((threshold - signal.iloc[i]) / delta_v) * delta_t
    return None

def calculate_rise_fall_times(data, start_time, end_time, percent_low, percent_high):
    """
    Calculate the rise and fall times of a signal between specified time interval.

    :param data: DataFrame containing the time and signal data
    :param start_time: Start time of the interval
    :param end_time: End time of the interval
    :param percent_low: Lower percentage threshold (e.g., 10%)
    :param percent_high: Higher percentage threshold (e.g., 90%)
    :return: Rise time and fall time
    """
    interval_data = data[(data['Time'] >= start_time) & (data['Time'] <= end_time)]
    min_signal = interval_data['v(out)'].min()
    max_signal = interval_data['v(out)'].max()
    low_threshold = min_signal + percent_low * (max_signal - min_signal)
    high_threshold = min_signal + percent_high * (max_signal - min_signal)
    time_low_to_high = find_time_at_threshold(interval_data['v(out)'], interval_data['Time'], low_threshold)
    time_high_to_low = find_time_at_threshold(interval_data['v(out)'], interval_data['Time'], high_threshold)
    rise_time = time_high_to_low - time_low_to_high if time_low_to_high and time_high_to_low else None
    return rise_time

def calculate_propagation_delay(input_signal, output_signal, time, start_time, end_time, threshold):
    """
    Calculate the propagation delay between the input signal and output signal.

    :param input_signal: Pandas Series of input signal values
    :param output_signal: Pandas Series of output signal values
    :param time: Pandas Series of time values
    :param start_time: Start time of the interval for analysis
    :param end_time: End time of the interval for analysis
    :param threshold: Threshold value for determining the transition point
    :return: Propagation delay
    """
    interval_data = data[(data['Time'] >= start_time) & (data['Time'] <= end_time)]
    input_cross_time = find_time_at_threshold(interval_data['v(clk)'], interval_data['Time'], threshold)
    output_cross_time = find_time_at_threshold(interval_data['v(out)'], interval_data['Time'], threshold)
    return output_cross_time - input_cross_time if input_cross_time and output_cross_time else None

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
def append_to_csv(data, csv_filepath):
    # Define the two possible sets of required keys
    required_keys = ['VDD','N_W','N_L','P_W','P_L','Corner','Temperature','tr','tf','tPLH','tPHL']

    if os.path.exists(csv_filepath):
        existing_data = pd.read_csv(csv_filepath)

        if not existing_data[(existing_data['VDD'] == data['VDD']) & 
                                (existing_data['N_W'] == data['N_W']) &
                                (existing_data['N_L'] == data['N_L']) &
                                (existing_data['P_W'] == data['P_W']) &
                                (existing_data['P_L'] == data['P_L']) &
                                (existing_data['Corner'] == data['Corner']) &
                                (existing_data['Temperature'] == data['Temperature'])].empty:
            return  # Entry exists, do nothing
    else:
        # Initialize DataFrame with required columns if file doesn't exist
        existing_data = pd.DataFrame(columns=required_keys)

    # Append new data
    new_data = pd.DataFrame([data])
    existing_data = pd.concat([existing_data, new_data], ignore_index=True)
    existing_data.to_csv(csv_filepath, index=False)
    print(csv_filepath)
# Define the time intervals and thresholds for analysis
low_to_high_interval = (1.01e-7, 1.11e-7)
high_to_low_interval = (1.23e-7, 1.36e-7)
# Navigate to the main directory
main_dir = 'figures/aimspice'
config_dirs = os.listdir(main_dir)
total_files = 0
for config in config_dirs:
    csv_functionality_path = os.path.join(main_dir, config, 'CSV', 'functionality')
    if os.path.exists(csv_functionality_path):
        total_files += len([f for f in os.listdir(csv_functionality_path) if f.endswith('.csv')])

# Initialize a counter for processed files
processed_files = 0
for config in config_dirs:
    try:
        params = extract_params_from_config_name(os.path.basename(config))
    except ValueError as e:
        print(e)
        continue
    csv_functionality_path = os.path.join(main_dir, config, 'CSV', 'functionality')
    output_functionality_path = os.path.join(main_dir, config, 'functionality')
    if os.path.exists(csv_functionality_path):
        if not os.path.exists(output_functionality_path):
            os.makedirs(output_functionality_path)

        csv_files = [f for f in os.listdir(csv_functionality_path) if f.endswith('.csv')]

        for filename in csv_files:
            processed_files += 1
            filepath = os.path.join(csv_functionality_path, filename)
            
            # Preprocess
            lines = preprocess_file(filepath)
            data = pd.read_csv(filepath)
            temperature = filename.split('.')[0][2:4]
            corner = filename.split('.')[0][:2]
            input_signal_max = data['v(clk)'].max()
            threshold = input_signal_max / 2

            # Calculate rise and fall times
            rise_time = calculate_rise_fall_times(data, *low_to_high_interval, 0.1, 0.9)
            fall_time = calculate_rise_fall_times(data, *high_to_low_interval, 0.9, 0.1)

            # Calculate propagation delays
            propagation_delay_low_to_high = calculate_propagation_delay(data['v(clk)'], data['v(out)'], data['Time'], *low_to_high_interval, threshold)
            propagation_delay_high_to_low = calculate_propagation_delay(data['v(clk)'], data['v(out)'], data['Time'], *high_to_low_interval, threshold)
            if params['N_Width'] == '0.1u' and params['N_Length'] == '0.1u' and params['P_Width'] == '0.3u' and params['P_Length'] == '0.1u':
                variable_vdd_csv_path = os.path.join(main_dir, 'variableVDD', 'CSV_time')
                os.makedirs(variable_vdd_csv_path, exist_ok=True)
                csv_filename = f'speed.csv'  # Unique filename for each simulation
                csv_filepath = os.path.join(variable_vdd_csv_path, csv_filename)
                data = {
                    'VDD': params['vdd_value'],
                    'N_W': params['N_Width'],
                    'N_L': params['N_Length'],
                    'P_W': params['P_Width'],
                    'P_L': params['P_Length'],
                    'Corner': corner,
                    'Temperature': temperature,
                    'tr':rise_time,
                    'tf':fall_time,
                    'tPLH':propagation_delay_low_to_high,
                    'tPHL':propagation_delay_high_to_low,
                }
                append_to_csv(data, csv_filepath)
            if params['vdd_value'] == '0.600': 
                variable_param_csv_path = os.path.join(main_dir, 'variableParam', 'CSV_time')
                os.makedirs(variable_param_csv_path, exist_ok=True)
                csv_filename = f'speed.csv'  # Unique filename for each simulation
                csv_filepath = os.path.join(variable_param_csv_path, csv_filename)
                data = {
                    'VDD': params['vdd_value'],
                    'N_W': params['N_Width'],
                    'N_L': params['N_Length'],
                    'P_W': params['P_Width'],
                    'P_L': params['P_Length'],
                    'Corner': corner,
                    'Temperature': temperature,
                    'tr':rise_time,
                    'tf':fall_time,
                    'tPLH':propagation_delay_low_to_high,
                    'tPHL':propagation_delay_high_to_low,
                }
                append_to_csv(data, csv_filepath) 
            # Calculate and display the remaining percentage
            # Print results
            print(f"Rise Time: {rise_time} seconds")
            print(f"Fall Time: {fall_time} seconds")
            print(f"Propagation Delay (Low to High): {propagation_delay_low_to_high} seconds")
            print(f"Propagation Delay (High to Low): {propagation_delay_high_to_low} seconds")
            remaining_percentage = ((processed_files) / total_files) * 100 if total_files > 0 else 0
            print(f"Status: {remaining_percentage:.2f}%")     
            print(f"{processed_files}/{total_files}")
            print(params)
            print(csv_filepath)

