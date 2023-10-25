import pandas as pd
import matplotlib.pyplot as plt
import re

# Filename
csv_file = 'DFF.csv'


# Preprocess the CSV to ensure the first row is comma-separated
with open(csv_file, 'r') as f:
    lines = f.readlines()
    lines[0] = lines[0].replace(" ", ",")

# Write the modified content back to the file
with open(csv_file, 'w') as f:
    f.writelines(lines)
# Now read the modified CSV
df = pd.read_csv(csv_file)

# Extracting time data from the first column
time_data = df.iloc[:, 0]

# Group columns by NAND instance N"number"
nand_groups = {}
for col in df.columns[1:]:
    match = re.search(r'n(\d+):', col)
    if match:
        nand_number = "n" + match.group(1)
        if nand_number not in nand_groups:
            nand_groups[nand_number] = []
        nand_groups[nand_number].append(col)

# Define a function to convert transistor codes to labels
def transistor_label(code):
    trans_type = "NMOS" if "mn" in code else "PMOS"
    trans_number = re.search(r'(\d+)', code).group(1)
    return f"{trans_type}{trans_number}"

def plot_voltages_on_secondary_axis(time_data, voltages, ax):
    ax2 = ax.twinx()  # Create a second y-axis
    for voltage in voltages:
        ax2.plot(time_data, df[voltage], label=voltage, linestyle='--')
    ax2.set_ylabel('Voltage (V)')
    ax2.legend(loc="upper right")

# Plotting
# voltages = ['v(out)']
voltages = ['v(clk)', 'v(data)', 'v(out)']
for nand_name, cols in nand_groups.items():
    fig, ax = plt.subplots()
    for col in cols:
        label = transistor_label(col.split(':')[-2])  # Extract transistor code and convert to label
        ax.plot(time_data, df[col], label=label)
    ax.set_title(f"NAND{nand_name[1:]}")  # Set title as NAND"number"
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Current (A)')
    ax.legend(loc="upper left")
    
    # Plot voltages on a secondary axis
    plot_voltages_on_secondary_axis(time_data, voltages, ax)

    plt.tight_layout()
    plt.show()