from PIL import Image
import re
import glob
import pytesseract
from pytesseract import image_to_string
pytesseract.pytesseract.tesseract_cmd = '' #PATH TO TESSERACT FOLDER

def getCoords(text): #Search text for coordinates and ask for user input
    coords  = []
    strictcoords = []
    permcoordpattern = '[EW]\d{1,9}.*?\s.*?\s.*?\..*?[NS]\d{1,9}.*?\s.*?\s.*?\.\d{0,9}' #Permissive coord regex
    strictcoordpattern = 'W[0-9l][0-9l][0-9]\s[0-9][0-9]\s[0-9][0-9]\W..\/N[0-9][0-9]\s[0-9][0-9]\s[0-9][0-9]\W..|S[0-9][0-9]\s[0-9][0-9]\s[0-9][0-9]\W..|E[0-9][0-9][0-9]\s[0-9][0-9]\s[0-9][0-9]\W..\/N[0-9][0-9]\s[0-9][0-9]\s[0-9][0-9]\W..|S[0-9][0-9]\s[0-9][0-9]\s[0-9][0-9]\W..' #Strict coord regex

    #Detect coordinates permissively
    x = 0
    for match in re.findall(permcoordpattern, text):
        coords.append(match)
        x += 1

    #Detect coordinates strictly
    z = 0
    for match in re.findall(strictcoordpattern, text):
        strictcoords.append(match)
        z += 1

    #List to remember pre-repaired coords
    repaired = []

    #loop through coords running pruneN
    y = 0
    for i in coords:
        cord = pruneN(i)
        if cord != '' and len(cord) <= 26: #blank cords didn't require repair, cords longer than 26 characters are otherwise malformed
            del coords[y] #prune now good coords from coords
            repaired.append(i) #pre-repaired
            strictcoords.append(cord) #add repaired coords to strictcoords
        y+=1

    #Begin interactive portion
    print "Tesseract found " + str(x) + " coordinates in permissive mode and " + str(len(strictcoords)) + " in strict mode."
    print "There are " + str(x - len(strictcoords)) + " malformed coordinates that should be corrected."
    YN = raw_input("Correct now? (Y/N): ")
    print YN
    if YN.upper() == "Y":
        #loop through permissive coords
        y = 0
        for coord in coords:
            if coord not in strictcoords and coord not in repaired: #only look at coords that are bad(not in strict coords) and weren't repaired(not in repaired coords)
                response = editCoords(coord) #see editCoords
                if response == "D": #delete
                    del coords[y]
                elif response == "S": #skip
                    continue
                else: #insert the corrected coordinate into strictcoords
                    strictcoords.insert(y, response)
            y+=1
    return strictcoords

def editCoords(coord):
    print "The malformed coord: " + coord
    repair = raw_input("(E)dit/(D)elete/(S)kip: ")
    if repair.upper() == "E":
        print "Enter the correct coord"
        print "Format should be (E/W)XXX XX XX.XX/(N/S)XXX XX XX.XX"
        goodcoord = raw_input()
    if repair.upper() == "D":
        print "Deleting..."
        goodcoord = "D"
    if repair.upper() == "S":
        print "Skipping..."
        goodcoord = "S"
    return goodcoord

def pruneN(coord): #Repair common error in text detection(double Ns)
    x = 0
    newcoord = ""
    for i in coord: #loop through characters in coord
        if i == "N" and coord[x+1] == "N": #two consecutive Ns
            newcoord = (coord[:x] + coord[(x+1):]) #slice string to remove second N
        x+=1
    return newcoord


files = glob.glob('*.png') #list of PNG in folder

for file in files: #loop through images
    input = file
    print "File: " + file
    text = image_to_string(Image.open(input), lang='geo') #run dictionary text detection on input image
    coords = getCoords(text)

    #create CSV output
    output = input + '.csv'
    f = open(output, 'w')
    for i in coords:
        f.write(i + "\n")
    f.close()




