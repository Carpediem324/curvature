import os
import glob
import shutil
import numpy as np
import matplotlib.pyplot as plt

username = os.getlogin()
input_dir = '/home/' + username + '/curve/input/'
output_dir = '/home/' + username + '/curve/output/'

input_files = glob.glob(os.path.join(input_dir, '*.txt'))

for input_path in input_files:
    with open(input_path, 'r') as f:
        lines = f.readlines()

    points = [list(map(float, line.strip().split(','))) for line in lines]
    points = np.array(points)

    vectors = np.diff(points, axis=0)
    
    norms = np.linalg.norm(vectors, axis=1)
    
    # Check if any norm is zero to prevent ZeroDivisionError
    if np.any(norms == 0):
        print("Warning: Division by zero detected. Replacing zeros with a small number.")
        norms[norms == 0] += 1e-10

    vectors /= norms[:, None]

    dot_products = np.sum(vectors[:-1] * vectors[1:], axis=1)

    distances =(norms[:-1] + norms[1:]) / 2
    
    # Ensure dot_products is within the valid range for arccos.
    dot_products=np.clip(dot_products,-1.0 ,1.0)

    angles=np.arccos(dot_products)
    if np.any(distances == 0):
        print("Warning: Division by zero detected. Replacing zeros with a small number.")
        # Replace zeros with a very small number (you can choose this number as per your requirements)
        distances[distances == 0] = 1e-10

    curvature = np.divide(2*np.sin(angles), distances)

	# Check if curvature values are valid.
    if not (np.all(np.isfinite(curvature)) and (curvature >= 0).all()):
        print(f"Warning: Invalid curvature values detected in {input_path}.")

    output_filename_base=os.path.splitext(os.path.basename(input_path))[0]
    output_filename=output_filename_base+'_curvature.txt'
    output_path=os.path.join(output_dir,output_filename)

    png_output_filename=output_filename_base+'_curvature.png'
    png_output_path=os.path.join(output_dir,png_output_filename)

    if os.path.exists(output_path) or os.path.exists(png_output_path):
        backup_dir_base_name ='backup'
        i= 0

        while True:
            i += 1
            backup_dir_name=f'{output_dir}/{backup_dir_base_name}{i}'
            
            if not os.path.exists(backup_dir_name):
                break
		
        os.makedirs(backup_dir_name)

    if os.path.exists(output_path):
            shutil.move(output_path,os.path.join(backup_dir_name,output_filename))

    if os.path.exists(png_output_path):
            shutil.move(png_output_path,os.path.join(backup_dir_name,png_output_filename))

    with open(output_path,'w') as f:
        f.write('NaN\n')
        for value in curvature:
            rounded_value=np.round(value, decimals=10)
            f.write(str(rounded_value)+'\n')
        f.write('NaN\n')

    plt.figure(figsize=(10,5))
    plt.plot([np.nan]+list(curvature)+[np.nan])
    plt.title('Curvature values')
    plt.xlabel('Index')
    plt.ylabel('Curvature')
    plt.grid(True)

    png_rounded_output_filepath=os.path.join(output_dir,png_output_filename)

    # save the figure here.
    plt.savefig(png_rounded_output_filepath)

    print(f"Processing completed for {input_path}!")
