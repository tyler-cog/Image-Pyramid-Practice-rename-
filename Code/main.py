# Import required libraries
import numpy as np
from matplotlib import pyplot as plt
from skimage.transform import resize
from skimage.metrics import mean_squared_error
import sys

# Function to retrieve r, g, b planes from Prokudin-Gorskii glass plate images
def read_strip(path):
    image = plt.imread(path) # read the input image
    info = np.iinfo(image.dtype) # get information about the image type (min max values)
    image = image.astype(np.float) / info.max # normalize the image into range 0 and 1

    height = int(image.shape[0] / 3)

    # For images with different bit depth
    scalingFactor = 255 if (np.max(image) <= 255) else 65535
    
    # Separating the glass image into R, G, and B channels
    b = image[: height, :]
    g = image[height: 2 * height, :]
    r = image[2 * height: 3 * height, :]
    return r, g, b

# circshift implementation similar to matlab
def circ_shift(channel, shift):
    shifted = np.roll(channel, shift[0], axis = 0)
    shifted = np.roll(shifted, shift[1], axis = 1)
    return shifted

# The main part of the code. Implement the FindShift function
def find_shift_smallest(im1, im2):
    max_shift = 20
    best_shift = None
    best_score = float("inf")

    for row_shift in range(-max_shift, max_shift+1):
        for col_shift in range(-max_shift, max_shift+1):
            shifted_im1 = np.roll(np.roll(im1, row_shift, axis=0), col_shift, axis=1)
            score = np.sum((shifted_im1 - im2) ** 2)
            if score < best_score:
                best_score = score
                best_shift = [row_shift, col_shift]

    return best_shift
    # return best_shift[0], best_shift[1]

def find_shift(im1, im2, shiftX, shiftY):
    max_shift = shiftX
    min_shift = shiftY
    best_shift = None
    best_score = float("inf")

    for row_shift in range(min_shift, max_shift+1):
        for col_shift in range(min_shift, max_shift+1):
            shifted_im1 = np.roll(np.roll(im1, row_shift, axis=0), col_shift, axis=1)
            score = np.sum((shifted_im1 - im2) ** 2)
            if score < best_score:
                best_score = score
                best_shift = [row_shift, col_shift]

    return best_shift

    # return best_shift[0], best_shift[1]

def multi_scale(r, g , b):
    rHeight, rWidth = r.shape
    gHeight, gWidth = g.shape
    bHeight, bWidth = b.shape
    levelCounter = 3
    scale = 2
    smallestCheck = True


    for i in range(4):
        if (levelCounter == 0):
            levelCounter = 1
            scale = 1

        newRHeight = rHeight / (levelCounter * scale)
        newRWidth = rWidth / (levelCounter * scale)
        newRShape = (newRHeight, newRWidth)
        rResize = resize(r, newRShape)
        print("rResize", rResize.shape)

        newGHeight = gHeight / (levelCounter * scale)
        newGWidth = gWidth / (levelCounter * scale)
        newGShape = (newGHeight, newGWidth)
        gResize = resize(g, newGShape)

        newBHeight = bHeight / (levelCounter * scale)
        newBWidth = bWidth / (levelCounter * scale)
        newBShape = (newBHeight, newBWidth)
        bResize = resize(b, newBShape)

        if (smallestCheck == True):
            rShift = find_shift_smallest(rResize, bResize)
            gShift = find_shift_smallest(gResize, bResize)
            print("rshift", rShift)
            print("gshift", gShift)
            smallestCheck = False
        else:
            rShift = find_shift(rResize, bResize, max(rShift[0] * 2, 20), max(rShift[1] * 2, 20))
            gShift = find_shift(gResize, bResize, max(gShift[0] * 2, 20), max(gShift[1] * 2, 20))
            print("rshiftelse", rShift)
            print("gshiftelse", gShift)

        levelCounter -= 1

    return rShift, gShift
#how do I use skimage.transform.resize in order to resize an image to half its size?
if __name__ == '__main__':
    # Setting the input output file path
    imageDir = '../Images/'
    # imageName = 'three_generations.tif'
    imageName = sys.argv[1]
    # print(sys.argv[0])
    outDir = '../Results/'
    # multiscale = True
    multiscale = sys.argv[2]
    # Get r, g, b channels from image strip
    r, g, b = read_strip(imageDir + imageName)
    print("rsize", r.shape)
   
    if (multiscale == True):
        rShift, gShift = multi_scale(r, g ,b)
    # Calculate shift
    else:
        rShift = find_shift_smallest(r, b)
        gShift = find_shift_smallest(g, b)
    
    print("rShift is:", rShift)
    print("gShift is:", gShift)
    # Shifting the images using the obtained shift values
    finalB = b
    finalG = circ_shift(g, gShift)
    finalR = circ_shift(r, rShift)

    # Putting together the aligned channels to form the color image
    finalImage = np.stack((finalR, finalG, finalB), axis = 2)

    # Writing the image to the Results folder
    # plt.imsave(outDir + "cathedral5" + '.jpg', finalImage)
    plt.imsave(outDir + imageName[:-4] + '.jpg', finalImage)
