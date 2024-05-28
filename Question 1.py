#Write a function to calculate and return the volume of a PyramidI or Cone. In main, get the area
#and height of the Pyramid or Cone from user, call the function anad display the result. Make sure
#to include the area and height as arguments in the function call.
#The formula to calculate the volume of a Pyramid or Cone is V = (1/3)Ah
#*A is the area of the base,h is the height.

def calculate_volume_pyramid_or_cone(base_area,height):
    volume = (1 / 3) * base_area * height
    return volume

def main():
    Shape = input("Enter Shape(pyramid or cone):").lower()

    if Shape == "pyramid" or Shape == "cone":
       base_area = float(input("Enter the area:"))
       height = float(input("Enter the height:"))
       volume = calculate_volume_pyramid_or_cone(base_area,height)
       print("The volume of pyramid is:", Shape, "is:{:.2f}".format(volume))

    else:
       print ("invalid shape entered. Please enter 'pyramid' or 'cone'.")

if __name__ == "__main__":
   main()