#!/usr/bin/env python3
import pandas as pd
import h5py
import numpy as np
import pickle
from generate_signatures import find_extreme_window, find_threshold_crossing

# Constants
Lx = 0.01


def process_h5_files(csv_path):
    """
    Load the CSV file containing a, b values and database paths,
    then process each database.h5 file one by one.
    
    Args:
        csv_path (str): Path to the CSV file
    """
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_path)
    
    # Read the base values
    base_values = np.loadtxt('base_values.txt', delimiter=',')
    
    # Print info about the loaded data
    print(f"Loaded {len(df)} entries from {csv_path}")
    
    # Process each entry
    # Create a list to store the tip deflections of all 6 cilia
    simdata_tip = []
   
    for index, row in df.iterrows():
        # Extract data from row
        a_val = row['a']
        b_val = row['b']
        file_path = row['path']
       
        try:
            # Open and process the H5 file
            with h5py.File(file_path, 'r') as f:
                # Find the time index when the particle crosses xlim_val = 0.7*Lx
                xlim_val_1 = 0.1*Lx
                time_index_1 = find_threshold_crossing(f['particles/px'],xlim_val_1)
                xlim_val_2 = 0.7*Lx
                time_index_2 = find_threshold_crossing(f['particles/px'],xlim_val_2)
                
                # Here you can process each H5 file as needed
                # For example, you might want to:
               
                # Create a container for storing the cilia tip deflection data
                ntime = f['cilia']['cx'].shape[0]
                ncilia = 6
                ctip = np.zeros((ntime,ncilia,4)) # 4 each for x, y, maskx and masky
                # The cilia shape: [Time Steps, No. of cilia, No. of nodes]
                for icilia in range(0,ncilia): 
                    node = -1 * (icilia%2 == 0)
                    signal_x = f['cilia']['cx'][:,icilia,node]
                    signal_y = f['cilia']['cy'][:,icilia,node]
                    
                    # Select the base value for every cilia and component
                    datum = base_values[icilia,:].squeeze()
                    
                    # Prepare signal with nan to exclude time-series data after particle crossing the threshold 
                    signal_x_input = signal_x.copy()
                    signal_y_input = signal_y.copy()
                    signal_x_input[0:time_index_1] = np.nan
                    signal_x_input[time_index_2:] = np.nan
                    signal_y_input[0:time_index_1:] = np.nan
                    signal_y_input[time_index_2:] = np.nan

                    mask_x = find_extreme_window(signal_x_input, datum[0], peak_detection_params=None)
                    mask_y = find_extreme_window(signal_y_input, datum[1], peak_detection_params=None)
                    
                    ctip[:,icilia,0] = signal_x 
                    ctip[:,icilia,1] = signal_y  
                    ctip[:,icilia,2] = mask_x 
                    ctip[:,icilia,3] = mask_y  
 
                # This is just a placeholder that prints basic info
                print(f"Processing file with a={a_val}, b={b_val}")
                print(f"File: {file_path}")
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        simdata_tip.append(ctip)

    with open('simdata_tip.pkl', 'wb') as f2:
        pickle.dump(simdata_tip, f2)

    return simdata_tip

if __name__ == "__main__":
    # Path to the CSV file
    csv_path = "h5_database_list.csv"
    simdata_tip = process_h5_files(csv_path)
