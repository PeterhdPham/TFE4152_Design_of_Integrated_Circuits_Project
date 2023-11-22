import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from numpy.polynomial.polynomial import Polynomial

# Function to plot and save graphs with polynomial fit
def plot_and_save_graph_poly(data, simulation_id, output_dir, degree=5):
    plt.figure()
    for (temp, corner), group_data in data.groupby(['Temperature', 'Corner']):
        # Extract VDD and Power values
        x = group_data['VDD'].astype(float)
        y = group_data['Power'].astype(float)

        # Plot each data point
        plt.scatter(x, y, label=f"Temp: {temp}, Corner: {corner}")

        # Fit and plot a polynomial regression line
        coefs = Polynomial.fit(x, y, degree).convert().coef
        x_new = np.linspace(x.min(), x.max(), 200)  # for smooth line
        y_new = sum(coef * x_new**i for i, coef in enumerate(coefs))
        if corner == 'TT':
            plt.plot(x_new, y_new, linestyle='-', linewidth=2.5)
        else:  # For 'FF' and any other corner
            plt.plot(x_new, y_new, linestyle='--')


    plt.xlabel('VDD')
    plt.ylabel('Power')
    plt.title(f'Static power leakage vs VDD for {simulation_id}')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'static_power_leakage_graph_{simulation_id}.png'))
    plt.close()

# Main directory and simulation IDs
main_dir = 'figures/aimspice/variableVDD/CSV'
simulation_ids = ['I1', 'I2', 'I3', 'I4']

for simulation_id in simulation_ids:
    csv_filepath = os.path.join(main_dir, f'static_leakage_power_{simulation_id}.csv')
    if os.path.exists(csv_filepath):
        data = pd.read_csv(csv_filepath)
        plot_and_save_graph_poly(data, simulation_id, main_dir)
