#!/usr/bin/env python3
import os
import h5py
import csv 

def read_h5_files(base_dir):    
    # List to store results [aval, bval, path]
    results = []
    
    # Get list of all outer directories matching sim_XXXX pattern
    outer_dirs = [d for d in os.listdir(base_dir) 
                 if os.path.isdir(os.path.join(base_dir, d)) and d.startswith('sim_')]
    
    # Sort them numerically
    outer_dirs.sort()
    
    for outer_dir in outer_dirs:
        outer_path = os.path.join(base_dir, outer_dir)
        
        # Get list of all inner directories matching sim_XX pattern
        inner_dirs = [d for d in os.listdir(outer_path) 
                     if os.path.isdir(os.path.join(outer_path, d)) and d.startswith('sim_')]
        
        # Sort them numerically
        inner_dirs.sort()
        
        for inner_dir in inner_dirs:
            inner_path = os.path.join(outer_path, inner_dir)
            h5_path = os.path.join(inner_path, "database.h5")
            
            # Check if database.h5 exists
            if os.path.exists(h5_path):
                print(f"Reading {h5_path}")
                try:
                    with h5py.File(h5_path, 'r') as f:
                        aval = f['particles'].attrs['aval']
                        bval = f['particles'].attrs['bval']
                        # Store absolute path instead of relative path
                        abs_path = os.path.abspath(h5_path)
                        results.append([aval, bval, abs_path])
                except Exception as e:
                    print(f"  Error reading {h5_path}: {e}")
    # Write results to CSV
    with open('h5_database_list.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(['a', 'b', 'path'])
        # Write data
        writer.writerows(results)
    
    print(f"Results saved to h5_database_list.csv with {len(results)} entries")
    return results

if __name__ == "__main__":
    # Use current directory as base
    base_dir = "."
    read_h5_files(base_dir)
