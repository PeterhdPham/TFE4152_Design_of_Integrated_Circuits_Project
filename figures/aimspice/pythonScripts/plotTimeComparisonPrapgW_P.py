import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from numpy.polynomial.polynomial import Polynomial

# Function to plot and save graphs with polynomial fit for multiple parameters
def plot_and_save_graph_multi(data, output_dir, parameters, title, file_suffix, degree=5):
    plt.figure(figsize=(10, 8))
    for param in parameters:
        # Filter data to remove outliers
        filtered_data = data[data[param] >= 0]
        for (temp, corner), group_data in filtered_data.groupby(['Temperature', 'Corner']):
            # Extract P_W and Power values
            x = group_data['P_W'].str.replace('u', '').astype(float) 
            y = group_data[param].astype(float)

            # Plot each data point
            plt.scatter(x, y, label=f"{param} - Temp: {temp}, Corner: {corner}")

            # Fit and plot a polynomial regression line
            coefs = Polynomial.fit(x, y, degree).convert().coef
            x_new = np.linspace(x.min(), x.max(), 200)  # for smooth line
            y_new = sum(coef * x_new**i for i, coef in enumerate(coefs))
            if corner == 'TT':
                plt.plot(x_new, y_new, linestyle='-', linewidth=2.5)
            else:  # For 'FF' and any other corner
                plt.plot(x_new, y_new, linestyle='--')

    plt.xlabel('P_W')
    plt.ylabel('Time (s)')
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'{file_suffix}.png'))
    plt.close()
# Function to plot and save individual graphs for tPLH and tPHL for each temperature and corner
def plot_and_save_individual_graphs(data, output_dir, degree=5):
    # Filter out rows where tPLH or tPHL are below zero
    data = data[(data['tPLH'] >= 0) & (data['tPHL'] >= 0)]

    # Get unique combinations of Temperature and Corner
    unique_combinations = data[['Temperature', 'Corner']].drop_duplicates()

    for index, row in unique_combinations.iterrows():
        temp = row['Temperature']
        corner = row['Corner']

        # Filter data for the specific Temperature and Corner
        group_data = data[(data['Temperature'] == temp) & (data['Corner'] == corner)]
        
        plt.figure(figsize=(10, 8))  # Set a larger figure size for clarity
        # Extract VDD and the parameters
        x = group_data['P_W'].str.replace('u', '').astype(float) 
        y_tPLH = group_data['tPLH'].astype(float)
        y_tPHL = group_data['tPHL'].astype(float)

        # Plot tPLH and tPHL data points
        plt.scatter(x, y_tPLH, label='tPLH', color='blue')
        plt.scatter(x, y_tPHL, label='tPHL', color='orange')

        # Fit and plot polynomial regression lines
        coefs_tPLH = Polynomial.fit(x, y_tPLH, degree).convert().coef
        coefs_tPHL = Polynomial.fit(x, y_tPHL, degree).convert().coef
        x_new = np.linspace(x.min(), x.max(), 200)
        y_new_tPLH = sum(coef * x_new**i for i, coef in enumerate(coefs_tPLH))
        y_new_tPHL = sum(coef * x_new**i for i, coef in enumerate(coefs_tPHL))
        plt.plot(x_new, y_new_tPLH, label='tPLH - Poly Fit', color='blue', linestyle='-', linewidth=1.5)
        plt.plot(x_new, y_new_tPHL, label='tPHL - Poly Fit', color='orange', linestyle='--', linewidth=1.5)

        plt.xlabel('P_W', fontsize=14)
        plt.ylabel('Propagation Delay (s)', fontsize=14)
        plt.title(f'Propagation Delays vs P_W - Temp: {temp}, Corner: {corner}', fontsize=16)
        plt.legend(fontsize=12)
        plt.grid(True)
        plt.tight_layout()
        # Define the file name based on Temperature and Corner
        file_name = f'propagation_delays_Temp_{temp}_Corner_{corner}.png'
        plt.savefig(os.path.join(output_dir, file_name))
        plt.close()
        
        
# Function to plot and save individual graphs for tr and tf for each temperature and corner
def plot_and_save_individual_graphs_tr_tf(data, output_dir, degree=5):
    # Filter out rows where tr or tf are below zero
    data = data[(data['tr'] >= 0) & (data['tf'] >= 0)]

    # Get unique combinations of Temperature and Corner
    unique_combinations = data[['Temperature', 'Corner']].drop_duplicates()

    for index, row in unique_combinations.iterrows():
        temp = row['Temperature']
        corner = row['Corner']

        # Filter data for the specific Temperature and Corner
        group_data = data[(data['Temperature'] == temp) & (data['Corner'] == corner)]
        
        plt.figure(figsize=(10, 8))  # Set a larger figure size for clarity
        # Extract VDD and the parameters
        x = group_data['P_W'].str.replace('u', '').astype(float) 
        y_tr = group_data['tr'].astype(float)
        y_tf = group_data['tf'].astype(float)

        # Plot tr and tf data points
        plt.scatter(x, y_tr, label='tr', color='blue')
        plt.scatter(x, y_tf, label='tf', color='orange')

        # Fit and plot polynomial regression lines
        coefs_tr = Polynomial.fit(x, y_tr, degree).convert().coef
        coefs_tf = Polynomial.fit(x, y_tf, degree).convert().coef
        x_new = np.linspace(x.min(), x.max(), 200)
        y_new_tr = sum(coef * x_new**i for i, coef in enumerate(coefs_tr))
        y_new_tf = sum(coef * x_new**i for i, coef in enumerate(coefs_tf))
        plt.plot(x_new, y_new_tr, label='tr - Poly Fit', color='blue', linestyle='-', linewidth=1.5)
        plt.plot(x_new, y_new_tf, label='tf - Poly Fit', color='orange', linestyle='--', linewidth=1.5)

        plt.xlabel('P_W', fontsize=14)
        plt.ylabel('Time (s)', fontsize=14)
        plt.title(f'Rise and Fall Times vs P_W - Temp: {temp}, Corner: {corner}', fontsize=16)
        plt.legend(fontsize=12)
        plt.grid(True)
        plt.tight_layout()
        # Define the file name based on Temperature and Corner
        file_name = f'rise_fall_times_Temp_{temp}_Corner_{corner}.png'
        plt.savefig(os.path.join(output_dir, file_name))
        plt.close()        
        
# Main directory and simulation IDs
main_dir = 'figures/aimspice/variableParam/CSV_time'


csv_filepath = os.path.join(main_dir, f'speed.csv')
if os.path.exists(csv_filepath):
    data = pd.read_csv(csv_filepath)
    # Plot and save graphs for different combinations of parameters
    plot_and_save_graph_multi(data, main_dir, ['tPLH', 'tPHL'], 'Propagation Delays vs VDD', 'propagation_delays_graph')
    plot_and_save_graph_multi(data, main_dir, ['tr', 'tf'], 'Rise and Fall Times vs VDD', 'rise_fall_times_graph')
    plot_and_save_graph_multi(data, main_dir, ['tPLH', 'tPHL', 'tr', 'tf'], 'All Parameters vs VDD', 'all_parameters_graph')

plot_and_save_individual_graphs(data, main_dir)
plot_and_save_individual_graphs_tr_tf(data, main_dir)
