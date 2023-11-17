import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import shutil 


# Helper function to process the file fo a more readable CSV file
def preprocess_file(filepath):
    
    with open(filepath, 'r') as f:
        content = f.read()
    # Check and remove unwanted lines
    if "AIM-Spice kernel Version" in content[0]:
        with open(filepath, 'w') as f:
            f.writelines(content[4:])
    elif "AIM-Spice,kernel,Version," in content[0]:
        with open(filepath, 'w') as f:
            f.writelines(content[4:])
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

# Navigate to the main directory
main_dir = 'figures/aimspice'
config_dirs = os.listdir(main_dir)

for config in config_dirs:
    csv_functionality_path = os.path.join(main_dir, config, 'CSV', 'functionality')
    output_functionality_path = os.path.join(main_dir, config, 'functionality')
    if os.path.exists(csv_functionality_path):
        if not os.path.exists(output_functionality_path):
            os.makedirs(output_functionality_path)

        csv_files = [f for f in os.listdir(csv_functionality_path) if f.endswith('.csv')]

        for filename in csv_files:
            filepath = os.path.join(csv_functionality_path, filename)
            
            # Create title
            title = generate_title(filename)

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
            plt.savefig(os.path.join(output_functionality_path, plot_filename))
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
                plt.savefig(os.path.join(output_functionality_path, plot_filename_w1))
                plt.close()

print("Processing of CSV files completed.")

