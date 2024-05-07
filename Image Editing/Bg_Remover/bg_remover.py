# Importing Required Modules 
from rembg import remove 
from PIL import Image 

# Store image name in the variable image_name
image_name = 'chicken burger.png'

# Store path of the image in the variable input_path 
input_path = 'before/' + image_name

# Store path of the output image in the variable output_path 
output_path = 'after/'

# Processing the image 
input = Image.open(input_path) 

# Removing the background from the given Image 
output = remove(input) 

#Saving the image in the given path 
output.save(output_path + image_name, 'png') 
