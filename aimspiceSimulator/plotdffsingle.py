import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
output_dir = "../figures/aimspice"

# Helper function to process the file
def preprocess_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Replace spaces with commas
    content = content.replace(" ", ",")

    return content.splitlines()

# Helper function to generate the title based on filename
def generate_title(filename):
    corner, temp= filename.split('.')[0][:2], filename.split('.')[0][2:4]
    return f"Corner: {corner}, Temperature: {temp}°C, Simulation: Single Clock"



# List all CSV files in the current directory
csv_files = [f for f in os.listdir('.') if f.endswith('.csv') and f[:2] in ['FF', 'FS', 'SF', 'SS', 'TT'] and f[4:6] in ['SC']]

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

print("Processing completed.")

