I used ChatGPT to aid in putting this python script with GUI together.  It takes a png file as input and outputs a C header file for use in C programming for the Neo Geo Pocket Color.

Open the image with the Open Image button.

Select how many layers you want to use for processing.  Note that it allows for selecting up to 3 layers.  I have some use-cases for displaying an image that is 3 layers where 2 layers are scroll planes and the 3rd layer is made up of sprites.

The assumption for the images is that they are limited to 3 colors plus transparent per layer.  The script will attempt to reduce the colors as needed, but it is best to create images that follow this assumption.

Select Output Layer Images to get an individual png image file per layer.  These can be used in other image processors as needed.

Select Output Reduced Image to save a png file that looks the way it will on the NGPC with reduced(if needed) and modified colors.

Choose an option for Scale Preview.  This affects only the display on the GUI when processing.

Select Choose Palette Order to bring up a new popup during processing that allows you to change the order of the palette.

Click Process and Save to save the header file and other image ouputs if the options are selected.

All saved files have the same base name as the input image.

All variables defined in the header file have the same base name as the input image in uppercase.