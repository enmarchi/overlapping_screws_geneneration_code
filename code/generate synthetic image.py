import blenderproc as bproc
import blenderproc
import blenderproc.python
import blenderproc.python.types
import blenderproc.python.types.MeshObjectUtility
import numpy as np
import argparse
import os
import sys
import random
import bpy


parser = argparse.ArgumentParser(description="Generate synthetic data using BlenderProc.")
parser.add_argument('base_path', help="Path to working directory")
args = parser.parse_args()
cwd = args.base_path

np.random.seed(42)

def generate_random_light_position():
    x = np.random.uniform(-1, 1)
    y = np.random.uniform(-1, 1)
    z = np.random.uniform(3, 5)
    return [x, y, z]

output_dir = os.path.join(cwd, fr"output")
# Initialize BlenderProc
bproc.init()

# Define and configure a point light
light = bproc.types.Light()
light.set_type("POINT")
light_position = generate_random_light_position()
light.set_location(light_position)

light.set_energy(np.random.uniform(100, 300))

# Set camera resolution and position
bproc.camera.set_resolution(1024, 1024)
position_camera = [0, 0, 9]
euler_rotation_camera = [0, 0, 0]
matrix_world = bproc.math.build_transformation_mat(position_camera, euler_rotation_camera)
bproc.camera.add_camera_pose(matrix_world)

# Load textures
grid_texture = bproc.loader.load_texture(path=os.path.join(cwd, fr"resources\textures\metallic_grid.jpg"))
bolt_texture = bproc.loader.load_texture(path=os.path.join(cwd, fr"resources\textures\black_metal.jpg"))
screw_texture = bproc.loader.load_texture(path=os.path.join(cwd, fr"resources\textures\brushed-metal-texture.jpg"))

# Create and configure the ground plane
background_size = 5
background = bproc.object.create_primitive(shape="PLANE")
ground_material = background.new_material("ground_material")
ground_material.infuse_texture(grid_texture[0], mode="set", connection="Base Color", texture_scale=0.05)
background.set_scale([background_size+1, background_size+1, 0])
background.set_location([0, 0, 0])
background.set_cp("category_id", 0)
background.enable_rigidbody(active=False, collision_shape="MESH")
wall_height = 20
wall_thickness = 0.5
walls = []
background_size = 3
for i in range(4):
    wall = bproc.object.create_primitive(shape="CUBE")
    if i == 0:  
        wall.set_scale([background_size + wall_thickness, wall_thickness/2, wall_height])
        wall.set_location([0, -1 * (background_size + wall_thickness / 2), wall_height / 2])
    elif i ==1:  
        wall.set_scale([wall_thickness/2, background_size + wall_thickness, wall_height])
        wall.set_location([-1 * (background_size + wall_thickness / 2), 0, wall_height / 2])
    elif i == 2: 
        wall.set_scale([background_size + wall_thickness, wall_thickness/2, wall_height])
        wall.set_location([0, (background_size + wall_thickness / 2), wall_height / 2])
    elif i ==3:  
        wall.set_scale([wall_thickness/2, background_size + wall_thickness, wall_height])
        wall.set_location([(background_size + wall_thickness / 2), 0, wall_height / 2])
    
    wall_material = wall.new_material(f"wall_material_{i}")
    wall_material.set_principled_shader_value("Base Color", [1.0, 0.0, 0.0, 1.0])
    wall.set_cp("category_id", 0)
    wall.enable_rigidbody(active=False, collision_shape="BOX")
    walls.append(wall)
# Load and configure screws
elements = []
loaded_bolts = bproc.loader.load_obj(os.path.join(cwd, fr"resources\models\1701623.obj"))
loaded_screws = bproc.loader.load_obj(os.path.join(cwd, fr"resources\models\screw.obj"))
loaded_screws[1].delete()
loaded_screws[2].delete()
loaded_screws[3].delete()
loaded_screws[4].delete()
loaded_screws[5].delete()
for _ in range(2):
    num_elements = random.randint(1,15)
    for i in range(num_elements):
        x = np.random.normal(0, 1)
        y = np.random.normal(0, 1)
        z = np.random.uniform(2, 7)
        random_value = random.random()
        if random_value >= 0.50:
            element : blenderproc.python.types.MeshObjectUtility.MeshObject
            element = loaded_screws[0].duplicate()
            element.set_cp("category_id", 1)
            element.set_scale([0.5, 0.5, 0.5])
            location = [x,y,z+2]
            epsilon =0.0
            rotation = np.random.uniform([0, np.pi/2-epsilon, -np.pi], [0, np.pi/2 + epsilon, np.pi])
            element.clear_materials()
            material = element.new_material("material")
            material.infuse_texture(screw_texture[0], mode="set", connection="Base Color", texture_scale=0.5)
        else:
            element = loaded_bolts[0].duplicate()
            element.set_cp("category_id", 2)
            element.set_scale([0.02, 0.02, 0.02])
            location = [x,y,z]
            rotation = np.random.uniform([0, 0, -np.pi], [0, 0, np.pi])
            element.clear_materials()
            material = element.new_material("material")
            material.infuse_texture(bolt_texture[0], mode="set", connection="Base Color", texture_scale=0.05)
        element.enable_rigidbody(active=True)    
        element.set_location(location)
        element.set_rotation_euler(rotation)
        elements.append(element)
loaded_screws[0].delete()
loaded_bolts[0].delete()
# Simulate physics
bproc.object.simulate_physics_and_fix_final_poses(min_simulation_time=4, max_simulation_time=20, check_object_interval=1)

# Enable rendering outputs
bproc.renderer.enable_depth_output(activate_antialiasing=True)
bproc.renderer.set_output_format(enable_transparency=True)
bproc.renderer.enable_segmentation_output(map_by=["category_id", "instance", "name"])

for wall in walls:
    wall.delete()

data_without_walls = bproc.renderer.render()
bproc.writer.write_coco_annotations(os.path.join(output_dir, 'coco_data'),
                                    instance_segmaps=data_without_walls["instance_segmaps"],
                                    instance_attribute_maps=data_without_walls["instance_attribute_maps"],
                                    colors=data_without_walls["colors"],
                                    append_to_existing_output=True)

bproc.writer.write_hdf5(os.path.join(output_dir, "hdf5"), data_without_walls, append_to_existing_output=True)