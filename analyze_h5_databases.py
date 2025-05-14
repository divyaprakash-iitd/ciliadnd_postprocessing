import numpy as np
import h5py
import pandas as pd
from pathlib import Path

def is_cilium_vertical(cx, cy, threshold_deg=10):
    """Determine if a cilium is vertical (closed) based on its principal axis angle."""
    # Compute the principal axis using PCA
    points = np.vstack((cx, cy)).T
    centroid = points.mean(axis=0)
    centered_points = points - centroid
    cov_matrix = np.cov(centered_points.T)
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
    principal_axis = eigenvectors[:, np.argmax(eigenvalues)]
    
    # Calculate angle in degrees
    angle = np.degrees(np.arctan2(principal_axis[1], principal_axis[0]))
    # Normalize angle to [0, 360)
    angle = angle % 360
    # Check if angle is close to 90° or 270° (vertical)
    return abs(angle - 90) < threshold_deg or abs(angle - 270) < threshold_deg

def analyze_h5_file(h5_path, a, b):
    """Analyze a single HDF5 file and return required metrics."""
    with h5py.File(h5_path, 'r') as f:
        # Load cilia data
        cx_data = f['cilia/cx'][:]
        cy_data = f['cilia/cy'][:]
        lcilia = f['cilia'].attrs['lcilia']
        ncilia = f['cilia'].attrs['ncilia']
        
        # Load particle data
        px_data = f['particles/px'][:]
        py_data = f['particles/py'][:]
        thetacum = f['particles/thetacum'][:]
        
        # Get final time step data
        last_cx = cx_data[-1]  # Shape: (ncilia, ncp)
        last_cy = cy_data[-1]
        last_px = px_data[-1]  # Shape: (nparticle, npp)
        last_py = py_data[-1]
        
        # Analyze last two cilia (assuming last two are top and bottom)
        top_cilium_vertical = is_cilium_vertical(last_cx[-1], last_cy[-1])
        bottom_cilium_vertical = is_cilium_vertical(last_cx[-2], last_cy[-2])
        
        # Determine gate configuration
        if top_cilium_vertical and not bottom_cilium_vertical:
            gate_config = 'sort_top'
            designated_half = 'top'
        elif not top_cilium_vertical and bottom_cilium_vertical:
            gate_config = 'sort_bottom'
            designated_half = 'bottom'
        else:
            gate_config = 'undefined'
            designated_half = None
        
        # Calculate percentage of particle in designated half
        percentage = 0.0
        if designated_half:
            # Normalize y-coordinates by lcilia
            Ly = lcilia * 2.75  # From generate_data.py: lcilia = Ly / 2.75
            y_normalized = last_py / Ly  # Shape: (nparticle, npp)
            midpoint = 0.5  # Midpoint of channel in normalized coordinates
            
            # Count nodes in designated half
            total_nodes = y_normalized.size
            if designated_half == 'top':
                in_designated = np.sum(y_normalized > midpoint)
            else:  # bottom
                in_designated = np.sum(y_normalized <= midpoint)
            
            percentage = (in_designated / total_nodes) * 100
        
        # Calculate full rotations
        final_thetacum = thetacum[-1] if len(thetacum) > 0 else 0.0
        full_rotations = abs(final_thetacum) / 360.0
        
        return {
            'a': a,
            'b': b,
            'gate_configuration': gate_config,
            'percentage_in_designated_half': percentage,
            'full_rotations': full_rotations
        }

def main():
    """Read CSV, process HDF5 files, and save results."""
    # Read CSV file
    csv_path = 'h5_database_list.csv'
    df = pd.read_csv(csv_path)
    
    # Initialize results list
    results = []
    
    # Process each HDF5 file
    for _, row in df.iterrows():
        a = row['a']
        b = row['b']
        h5_path = row['path']
        
        if not Path(h5_path).exists():
            print(f"Warning: File {h5_path} does not exist. Skipping.")
            continue
        
        print(f"Processing {h5_path}")
        result = analyze_h5_file(h5_path, a, b)
        results.append(result)
    
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    
    # Save results to CSV
    output_path = 'analysis_results.csv'
    results_df.to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    main()
