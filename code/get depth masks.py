import h5py
import os
import numpy as np
import cv2

output_dir = fr"path to \output"
hdf5_dir = os.path.join(output_dir, "hdf5")
output_image_dir = os.path.join(output_dir, "normalized depth maps")
os.makedirs(output_image_dir, exist_ok=True)

def normalize_and_save_depth_map(i, path_hdf5, output_path):
    with h5py.File(path_hdf5, 'r') as hdf5_file:
        depth_map = np.array(hdf5_file['depth'])
        semantic_map = np.array(hdf5_file['category_id_segmaps'])

        # Create a mask for the background (semantic_map == 0)
        background_mask = semantic_map == 0
        # Filter and process the depth map
        filtered_depth = depth_map.copy()
        filtered_depth = 9.1 - filtered_depth
        filtered_depth = np.clip(filtered_depth, 0, 1)
        filtered_depth[background_mask] = 0  # Remove background
        # Normalize the filtered depth map to [0, 255]
        if filtered_depth.max() > 0:
            filtered_depth_normalized = (filtered_depth * 255).astype(np.uint8)

            output_file = os.path.join(output_path, f"{i:06d}.png")
            cv2.imwrite(output_file, filtered_depth_normalized)
            print(f"Saved normalized image: {output_file}")

for i in range(100):
    path_hdf5 = os.path.join(hdf5_dir, f"{i}.hdf5")
    if os.path.exists(path_hdf5):
        normalize_and_save_depth_map(i, path_hdf5, output_image_dir)
    else:
        print(f"File not found: {path_hdf5}")
