# overlapping_screws_geneneration_code
Please, install blenderproc 2.7.0.
The script "generate synthetic image.py" contains the pipeline to generate one single snapshot.
To generate the whole dataset, simply run the script multiple times throught the "execute generation pipeline.bat" script.
Edit "execute generation pipeline.bat" to match the directory containing the scripts and the resources. 
Use the script "get depth masks.py" to reconstruct the depth images from the "hdf5" files after having updated the path
inside the script. The path cwd is the path of the folder containing the whole project.
