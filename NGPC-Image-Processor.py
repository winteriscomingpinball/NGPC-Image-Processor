import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import os

from PIL import Image, ImageTk

defaultPal=(0,0,0,0)

def paste_layers(layer1, layer2):
    result = Image.new("RGBA", layer1.size)
    result.paste(layer1, (0,0), layer1)
    result.paste(layer2, (0,0), layer2)
    return result
    
    
def NGPCcolors(colors):
    result = []
    for color in colors:
        r = color[0] // 16
        g = color[1] // 16
        b = color[2] // 16
        a = 0
        result.append((r, g, b, a))
    return result
    
def reduce_colors(img):
    img = img.convert("RGBA")
    pixels = img.load()
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            r, g, b, a = pixels[i, j]
            r = r // 16
            g = g // 16
            b = b // 16
            a = a // 16
            pixels[i, j] = (r * 16, g * 16, b * 16, a * 16)
    return img

def rgba_to_abgr16(rgba):
    r, g, b, a = rgba
    argb16 = (a << 12) + (b << 8) + (g << 4) + r
    return argb16
    
def process_image_tile_by_tile(img,palLookup):
    # Divide the image into 8x8 pixel tiles
    width, height = img.size
    tile_width = 8
    tile_height = 8
    
    pixelOutput=[]
    
    pixelGroup=[]

    for i in range(0, height, tile_height):
        for j in range(0, width, tile_width):
            tile = img.crop((j, i, j + tile_width, i + tile_height))

            # Iterate over each pixel in the tile
            for y in range(tile.size[1]):
                pixelGroup=[]
                for x in range(tile.size[0]):
                    pixel = tile.getpixel((x, y))
                    #print(pixel)
                    pixelGroup.append(palLookup[pixel])
                pixelOutput.append(pixelPack(pixelGroup))
                    
    return pixelOutput
   
    

def pixelPack(pixelList):
    u16 = 0
    for i in range(8):
        u16 = (u16 << 2) + pixelList[i]
    return u16
   

def outputToC(fullName,baseName, layerCount, tileWidth, tileHeight, layerPixels, layerPals):
    
    fileName = fullName + ".h"
    baseName = baseName.upper()
    totalTilesForLayer = tileWidth * tileHeight
    totalTilesUsedForAll = tileWidth * tileHeight * layerCount
    
    with open(fileName, 'w') as file:
        file.write("#define " + baseName + "_LAYER_COUNT " + str(layerCount) + "\n")
        file.write("#define " + baseName + "_WIDTH " + str(tileWidth) + "\n")
        file.write("#define " + baseName + "_HEIGHT " + str(tileHeight) + "\n")
        file.write("#define " + baseName + "_TILES_COUNT " + str(totalTilesUsedForAll) + "\n")
        
        for i in range(layerCount):
            layerNum = i + 1
            layerPixelsList = layerPixels[i]
            layerPalsList = layerPals[i]
            
            file.write("#define " + baseName + "_NPALS" + str(layerNum) + " " + str(1) + "\n")
            file.write("const u16 " + baseName + "_TILES" + str(layerNum) + "[" + str(totalTilesForLayer * 8) + "] = {\n")
            
            
            palIDArray=[]
            for j in range(totalTilesForLayer):
                palIDArray.append(0)
            
            for j in range(totalTilesForLayer):
                startIndex = j * 8
                endIndex = startIndex + 8
                tile = layerPixelsList[startIndex:endIndex]
                #tileStr = ",".join(str(x) for x in tile)
                tileStr = ",".join( "0x{:04x}".format(x) for x in tile)
                if j< totalTilesForLayer-1: 
                    file.write("\t" + tileStr + ",\n")
                else:
                    file.write("\t" + tileStr + "\n")
                
            file.write("};\n")
            
            file.write("const u16 " + baseName + "_PALS" + str(layerNum) + "[" + str(4) + "] = {\n")
            #palStr = ",".join(str(x) for x in layerPalsList)
            palStr = ",".join(  "0x{:04x}".format(x) for x in layerPalsList)
            file.write("\t" + palStr + "\n")
            file.write("};\n")
            
            file.write("const u8 " + baseName + "_PALIDX" + str(layerNum) + "[" + str(totalTilesForLayer) + "] = {\n")
            #palStr = ",".join(str(x) for x in layerPalsList)
            palIDStr = ",".join(  "0x{:02x}".format(x) for x in palIDArray)
            file.write("\t" + palIDStr + "\n")
            file.write("};\n")
            
            
def process_the_data(img, filename, layerInput, outputLayerImages, outputReducedImage):

    #img = Image.open(filename).convert("RGBA")
    base_name_full = filename.split(".")[0]

    base_name= os.path.basename(filename).split(".")[0]

    width, height = img.size
    layerInput=int(layerInput)

    # Ask for input for Layers and save it to layerInput
    #layerInput = int(input("Enter a number of layers (1-3): "))

    # Output the number of colors found in the image, including transparent
    colors = len(img.getcolors(img.size[0]*img.size[1]))
    print(f"Number of colors in the image: {colors}")
    print(img.getcolors(img.size[0]*img.size[1]))



    # Reduce the number of colors in the image to (layerInput*3) + transparent
    color_depth = (layerInput*3) + 1
    #img = img.convert("RGBA", palette=Image.ADAPTIVE, colors=color_depth)
    img = img.quantize(colors=color_depth)
    img = reduce_colors(img)
    img = img.convert("RGBA")



    pixels = img.load()

    colors = img.convert('RGBA').getcolors()
    print("color count is now: " + str(len(colors)))
    print(colors)


    pixelColors=[]
    foundTransparent=0

    for color in colors:
        counter=0;
        for item in color:
            counter+=1
            if counter==2:
                #print(item)
                pixelColors.append(item)
                if (item==(0,0,0,0)):
                    fountTransparent=1
    
    if (foundTransparent==0):
        pixelColors.append((0,0,0,0))
        

    #print("These are the colors:");
    #print(pixelColors)

    #print("These are the NGPC colors:");
    #ngpc_colors=NGPCcolors(pixelColors)


    #print(ngpc_colors)
    #for color in ngpc_colors:
    #    #print(hex(rgba_to_argb16(color)))
    #    print("0x{:04x}".format(rgba_to_argb16(color)))


    # Split the image into layers
    layers = []
    layerPals =[]
    colorIndex=0
    layerPixels=[]
    for k in range(layerInput):
        layer = Image.new("RGBA", img.size, color=(0,0,0,0) )
        for l in range(3):
            selectedColor=pixelColors[colorIndex]
            if (colorIndex<len(pixelColors)-1):
                colorIndex+=1
            else:
                break
            for i in range(img.size[0]): # for every pixel:
                for j in range(img.size[1]):
                    if pixels[i,j] == selectedColor:
                        layer.putpixel((i, j), selectedColor)
        layers.append(layer)


    # Save out a new image for each layer
    #for i, layer in enumerate(layers):
    #    layer.save(f"{filename.split('.')[0]}-Layer{i+1}.png")
    for i, layer in enumerate(layers):
        pixelColors=[]
        colors = layer.convert('RGBA').getcolors()
        
        
        
        for color in colors:
            counter=0;
            for item in color:
                counter+=1
                if counter==2:
                    #print(item)
                    pixelColors.append(item)
        ngpc_colors=NGPCcolors(pixelColors)
        #print("These are the NGPC colors for layer " + str(i+1) +" :")
        
        palMap=[0,0,0,0]
        counter=0
        
        palkey=0
        layerColorPalDict={}
        
        print("These are the colors found in layer " + str(i+1))
        print(ngpc_colors)
        for color in ngpc_colors:
            print(hex(rgba_to_abgr16(color)))
            ngpc_color=rgba_to_abgr16(color)
            
            if (ngpc_color>0):
                palkey+=1
            else:
                if pixelColors[counter][3]>0:
                    palkey+=1 #this means the color is black
                    #print("counter is: " + str(counter))
                    #print("found black...")
                    
                else:
                    palkey=0 #this means the color is transparent
                    #print("found transparent...")
            
            
            #print("Pixel color: "+ str(pixelColors[counter]) + " = NGPC color: 0x{:04x}".format(rgba_to_argb16(color)))
            #print("Pixel color: "+ str(pixelColors[counter]) + " = NGPC color pal key:" + str(palkey))
            palMap[palkey]=rgba_to_abgr16(color)
            
            layerColorPalDict[pixelColors[counter]] = palkey
            
            
            counter+=1
        #print("This is the palMap: " + str(palMap))
        #print ("This is the Dictionary..." + str(layerColorPalDict))
        layerPals.append(palMap)
        
        processedPixels=process_image_tile_by_tile(layer, layerColorPalDict)
        layerPixels.append(processedPixels)
        #print(processedPixels)
        #for processedPixel in processedPixels:
            #print("0x{:04x}".format(processedPixel))
            
            
    counter=1
    if outputLayerImages:
        for layer in layers:
            layer.save(f"{filename.split('.')[0]}-Layer{counter}.png")
            counter+=1

    #if layerInput>1:
    if outputReducedImage:
        img.save(f"{filename.split('.')[0]}-Reduced.png")
        
        #merged_layer = paste_layers(layers[0], layers[1])
        #merged_layer.save("merged_layer.png")
        #merged_layer.save(f"{filename.split('.')[0]}-Layer1-2.png")
    #else:
        #layers[0].save(f"{filename.split('.')[0]}-Layer{1}.png")
    #    pass

    #if layerInput>2:
        #layers[2].save(f"{filename.split('.')[0]}-Layer{3}.png")
     #   pass
        
    






    outputToC(base_name_full, base_name, layerInput, int(width/8), int(height/8), layerPixels, layerPals)

    return img

class GUI:
    def __init__(self, root):
        self.root = root
        
        self.img_label3=tk.Label()
        self.img_label=tk.Label()
        
        self.root.geometry("500x700")
        self.root.grid_columnconfigure(0, minsize=100)
        
        
        self.root.title("NGPC Image Processor")
        
        #self.layer_var = tk.IntVar()
        #self.layer_var.set(1)
        
        self.open_image_button = tk.Button(self.root, text="Open Image", command=self.open_image)
        #self.open_image_button.pack()
        self.open_image_button.grid(column=2, row=1)
        
        self.layerLabel=tk.Label(text="Layers:");
        #self.layerLabel.pack()
        self.layerLabel.grid(column=2, row=2)
        
        self.layer_dropdown =ttk.Combobox(values=[1,2,3])
        self.layer_dropdown.set(1)
        #self.layer_dropdown = tk.OptionMenu(self.root, self.layer_var, 1, 2, 3)
        
        #self.layer_dropdown.pack()
        self.layer_dropdown.grid(column=2, row=3)
        
        self.c1_var = tk.IntVar()
        self.c1_var.set(0)
        c1 = tk.Checkbutton(self.root, text='Output Layer Images',variable=self.c1_var, onvalue=1, offvalue=0)
        #c1.pack()
        c1.grid(column=2, row=5)
        
        self.c2_var = tk.IntVar()
        self.c2_var.set(0)
        c2 = tk.Checkbutton(self.root, text='Output Reduced Image',variable=self.c2_var, onvalue=1, offvalue=0)
        #c2.pack()
        c2.grid(column=2, row=6)
        
        self.scaleLabel=tk.Label(text="Scale Preview:");
        #self.scaleLabel.pack()
        self.scaleLabel.grid(column=2, row=8)
        
        self.scale_dropdown =ttk.Combobox(values=[1,2,3])
        self.scale_dropdown.set(1)
        #self.scale_dropdown.pack()
        self.scale_dropdown.grid(column=2, row=9)

        self.process_and_save_button = tk.Button(self.root, text="Process and Save", command=self.process_and_save)
        #self.process_and_save_button.pack()
        self.process_and_save_button.grid(column=2, row=10)
        
    def open_image(self):
        self.img_label3.destroy()
        self.img_label.destroy()
        
        self.file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        self.img = Image.open(self.file_path)
        
        width, height = self.img.size
        self.img2=self.img
        
        self.img2 = self.img2.resize((width*int(self.scale_dropdown.get()), height*int(self.scale_dropdown.get())))
        
        #self.img2 = self.img.resize((300, 300), Image.ANTIALIAS)
        
        self.img2 = ImageTk.PhotoImage(self.img2)
        self.img_label = tk.Label(self.root, image=self.img2,borderwidth=1, relief="solid")
        #self.img_label.pack()
        self.img_label.grid(column=2, row=11)
        
        self.img = Image.open(self.file_path).convert("RGBA")
        
    def process_and_save(self):
        # Add your code here to process the image and save the output
        self.img_label.destroy()
        self.img2=self.img
        
        width, height = self.img2.size
        self.img2 = self.img2.resize((width*int(self.scale_dropdown.get()), height*int(self.scale_dropdown.get())))
        
        self.img2 = ImageTk.PhotoImage(self.img2)
        self.img_label = tk.Label(self.root, image=self.img2, borderwidth=1, relief="solid")
        self.img_label.grid(column=2, row=11)
        
        self.img_label3.destroy()
        self.img3=process_the_data(self.img, self.file_path, self.layer_dropdown.get(), self.c1_var.get(), self.c2_var.get())
        width, height = self.img3.size
        
        
        
        self.img3 = self.img3.resize((width*int(self.scale_dropdown.get()), height*int(self.scale_dropdown.get())))
        self.img3 = ImageTk.PhotoImage(self.img3)
        self.img_label3 = tk.Label(self.root, image=self.img3, borderwidth=1, relief="solid")
        #self.img_label3.pack()
        self.img_label3.grid(column=4, row=11)
        
        pass


if __name__ == "__main__":
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()
    
    


# Open the PNG file
#filename = input("Enter the filename of the PNG image: ")


