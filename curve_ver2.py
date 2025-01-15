import os
import glob
import shutil
import numpy as np
import matplotlib.pyplot as plt

# ROS2 library import and Node creation
import rclpy
from rclpy.node import Node


path_dir='/home/'+os.getlogin()+'/ros2_ws/src/local_pkg/map/'
output_dir='/home/'+os.getlogin()+'/ros2_ws/src/local_pkg/curve_map/'

class CurvatureCalculationNode(Node):
    def __init__(self):
        super().__init__('curvature_calculation')
        # 소수점 자릿수 설정
        self.decimals = 16
        self.small_number_threshold = 0.0000000000000001   # 최소치
        
        username = os.getlogin()
        self.input_dir = path_dir
        self.output_dir = output_dir

    def calculate_curvature(self):
        input_files = glob.glob(os.path.join(self.input_dir, 'result_*.txt'))

        for input_path in input_files:
            with open(input_path, 'r') as f:
                lines = f.readlines()

            points_and_yaw = [list(map(float, line.strip().split(','))) for line in lines]
            points_and_yaw_array = np.array(points_and_yaw)

            points = points_and_yaw_array[:, :2]  
            pathyaw_values = points_and_yaw_array[:, 2] 

            vectors = np.diff(points, axis=0)

            norms = np.linalg.norm(vectors, axis=1)

            if np.any(norms < 1e-16):
                print("Warning: Small norms detected. Replacing small norms with a small number.")
                norms[norms < 1e-16] += 1e-16

            vectors /= norms[:, None]

            dot_products=np.sum(vectors[:-1]*vectors[1:],axis=1)
            
            distances=(norms[:-1]+norms[1:])/2

            
            dot_products=np.clip(dot_products,-1.0 ,1.0)

            
            angles=np.arccos(dot_products)

            
            if np.any(distances < self.small_number_threshold):
                print("Warning: Small distances detected. Replacing small distances with a small number.")
                distances[distances < self.small_number_threshold] += self.small_number_threshold

        
            curvature=np.divide(2*np.sin(angles),distances)


            curvature[curvature < self.small_number_threshold]=0


            output_filename_base=os.path.splitext(os.path.basename(input_path))[0]
            output_filename=output_filename_base+'_curvature.txt'
            output_path=os.path.join(self.output_dir,output_filename)
            
            
            #백업용코드
            if os.path.exists(output_path) :
                backup_dir_base_name ='Backup'
                i= 0

                while True:
                    i += 1
                    backup_dir_name=f'{output_dir}/{backup_dir_base_name}{i}'
                    
                    if not os.path.exists(backup_dir_name):
                        break
                os.makedirs(backup_dir_name)


            if os.path.exists(output_path):
                    shutil.move(output_path,os.path.join(backup_dir_name,output_filename))


            with open(output_path,'w') as f:
                for point,pathyaw_value,value in zip(points,pathyaw_values,[0]+list(curvature)+[0]):
                    rounded_value=np.round(value, self.decimals)
                    if rounded_value < self.small_number_threshold:
                        rounded_value=0  

                    # Use string formatting to control how the number is displayed.
                    f.write(','.join(map(str,list(point)+[pathyaw_value]+["{:.{}f}".format(rounded_value, self.decimals)]))+'\n')

            self.get_logger().info(f"Processing completed for {input_path}!")


def main(args=None):
    rclpy.init(args=args)

    node = CurvatureCalculationNode()
    node.calculate_curvature()

    rclpy.shutdown()

if __name__ == '__main__':
    main()
