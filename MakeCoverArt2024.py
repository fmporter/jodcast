#MakeCoverArt.py - Two python classes (MakeCoverArt and MakeWebArt) designed
#  to create the cover art for the Jodcast audio file and an image for the 
#  Jodcast webpage.

#Written in 2016 by Charlie Walker (walker.mbcxqcw2@gmail.com).  Modified 
#  in 2024 by George J. Bendo.



#To create the Jodcast cover art, use MakeCoverArt.  See the example below.
#
# > MakeCoverArt('input.jpg',credit='J. Doe et al.',
#     edition='January 2000 Edition')
#
#The default settings will create an output file names "cover.jpg".
#
#The mandatory input are the following:
#  - inpic: The name of the input image.
#
#The options are the following:
#  - colour: The colour of the logo.  The default is 'white'.  Only
#      'white' and 'black' are recommended, and 'white' has generally been
#      used for most episodes.
#  - cover_dimension: Sets the dimensions of the (square) cover in pixels.
#      The default is 600, but current podcast recommendations are to use 
#      values greater than 1400.
#  - credit: The image credits.  This should be set.  The default is 
#      'INSERT THE CREDIT!!!'.
#  - edition: Specifies the edition name placed underneath the logo.
#      This should be set.  The default is 'INSERT EDITION Edition'.
#  - outpic: Specifies the name of the output file.  The default is 
#      'cover.jpg'.
#  - valign: Places the Jodcast logo at either the bottom (default) or top
#      of the cover art.  The options are 'top' and 'bottom'; the detault
#      is 'bottom'. 



#To create the image associated with a specific episode for the Jodcast 
#  webpages, use MakeWebArt.  See the example below.
#
# > MakeWebArt('input.jpg','J. Doe et al.')
#
#The default settings will create an output file names "cover_big.jpg".
#
#The mandatory input are the following:
#  - inpic: The name of the input image.
#  - credit: The image credits.
#
#The options are the following:
#  - colour: The colour of the logo.  The default is 'white'.  Only
#      'white' and 'black' are recommended, and 'white' has generally been
#      used for most episodes.
#  - height: The height of the output image in pixels.  The default is 360. 
#      Since this size has been used for other images on the website since
#      the inception of the Jodcast, it should not be changed.
#  - outpic: Specifies the name of the output file.  The default is 
#      'cover_big.jpg'.
#  - width: The width of the output image in pixels.  The default is 600. 
#      Since this size has been used for other images on the website since
#      the inception of the Jodcast, it should not be changed.



#Import packages.
import math,os
from subprocess import PIPE,Popen
from Params import *



#Utility to get the height and width of an image.
def GetImageWidthHeight(inpic):

    image_width=float(Popen(args='/usr/bin/convert '+inpic+' -print "%w" /dev/null',stdout=PIPE,shell=True).communicate()[0])
    image_height=float(Popen(args='/usr/bin/convert '+inpic+' -print "%h" /dev/null',stdout=PIPE,shell=True).communicate()[0])

    return image_width,image_height



#Utility to crete parameters for /usr/bin/convert.
def GetResizeCall(image_width,image_height,image_dimension):

    if image_width>=image_height:
        excess=str(int( round( (image_width/image_height*image_dimension-image_dimension)/2 ) ))
        resizecall='-resize x'+str(image_dimension)+' -crop -'+excess+'+0 -crop +'+excess+'+0'
    if image_width<image_height:
        excess=str(int( round( (image_height/image_width*image_dimension-image_dimension)/2 ) ))
        resizecall='-resize '+str(image_dimension)+' -crop +0-'+excess+' -crop +0+'+excess

    return resizecall



#Utility for calling /usr/bin/convert, which resizes the images.
def DoResize(inpic,resizecall,outname='tmp.jpg'):

    os.system('/usr/bin/convert '+inpic+' '+resizecall+' '+outname)

    return



#Utility for determining the scale of the text to be added to the cover art.
def GetTextParams(cover_dimension,valign):

    #Reference dimensions and locations.  This is based on a reference 
    #image with dimensions of 600x600 pixels.  DO NOT CHANGE THESE LINES.
    
    #Reference dimensions for edition text.
    ref_dims = 600.
    ref_loc_1 = 109.

    if valign == 'top':
        ref_loc_2 = 360.
    else:
        ref_loc_2 = 42.
    ref_textsize = 35.
    
    #Reference dimensions for credit text.
    ref_loc_3 = 8.
    ref_loc_4 = 590.
    ref_textsize_2 = 18.
    
    #Get the scaling factor.
    in_dims = cover_dimension
    rescale_factor = in_dims/ref_dims

    #Rescale the numbers.
    loc_1 = int(rescale_factor * ref_loc_1)
    loc_2 = int(rescale_factor * ref_loc_2)
    textsize = int(rescale_factor * ref_textsize)
    loc_3 = int(rescale_factor * ref_loc_3)
    loc_4 = int(rescale_factor * ref_loc_4)
    textsize_2 = int(rescale_factor * ref_textsize_2)

    return loc_1,loc_2,loc_3,loc_4,textsize,textsize_2



#The definition of MakeCoverArt, which makes the cover art that is attached
#  to the Jodcast audio file.  See the instructions at the top of this file
#  to understand how to use this.
def MakeCoverArt(inpic,valign='bottom',outpic='cover.jpg',
    edition='INSERT EDITION Edition',credit='INSERT THE CREDIT!!!',
    cover_dimension=600,colour='white'):

    #Choose a template picture based on the alignment option.
    if valign == 'top':
        cover_template_pic = cover_template_top
    else:
        cover_template_pic = 'cover_template.png'

    #Get the height and width of the input picture.
    print('\nMaking cover art using: '+str(inpic)+'\n')
    print('Obtaining picture dimensions...')
    cover_width,cover_height = GetImageWidthHeight(inpic)

    #Get the height and width of the template logo.
    print('Obtaining template dimensions...')
    logo_width,logo_height = GetImageWidthHeight(cover_template_pic)

    #Set the resize parameters for the image.
    print('Obtaining picture resize parameters...')
    resizecall = GetResizeCall(cover_width,cover_height,cover_dimension)

    #Set the resize parameters for the logo template.
    print('Obtaining template resize parameters...')
    logo_dimension = cover_dimension
    logo_resizecall = GetResizeCall(logo_width,logo_height,logo_dimension)

    #Create a temporary resized image.
    print('Resizing picture...')
    imag_temp_name = 'tmp.jpg'
    DoResize(inpic,resizecall)

    #Create a temporary resized logo.
    print('Resizing template...')
    logo_temp_name = 'tmp_logo.png'
    DoResize(cover_template_pic,logo_resizecall,logo_temp_name)

    #Recolour the Jodcast logo if required.
    if colour!='white':
        os.system('/usr/bin/convert '+logo_temp_name+' -fill '+colour+' -opaque white '+logo_temp_name)
    
    #Rescale the text locations and sizes.
    print('Getting rescaled parameters...')
    loc_1,loc_2,loc_3,loc_4,textsize,textsize_2 = GetTextParams(cover_dimension,valign)

    #Create the cover art.
    print('Making cover art...')
    os.system('/usr/bin/convert tmp.jpg -thumbnail '+str(cover_dimension)+'x'+str(cover_dimension)+'^ -gravity center -extent '+str(cover_dimension)+'x'+str(cover_dimension)+' '+str(logo_temp_name)+' -font Bitstream-Vera-Sans-Bold -fill "'+str(colour)+'" -pointsize '+str(textsize)+' -gravity SouthEast -draw "text '+str(loc_1)+','+str(loc_2)+' \''+str(edition)+'\'" -composite -thumbnail '+str(cover_dimension)+'x'+str(cover_dimension)+'^ -fill "'+str(colour)+'" -font Helvetica -gravity NorthWest -kerning -0 -pointsize '+str(textsize_2)+' -draw "text '+str(loc_3)+','+str(loc_4)+' \'Image credit: '+str(credit)+'\'" '+str(outpic))

    #Remove the temporary images.
    os.system('rm '+str(imag_temp_name))
    os.system('rm '+str(logo_temp_name))
    print('Cover art complete.\n')

    return



#The definition of MakeWebArt, which makes the image associated with an
#  episode that is placed on a website.  See the instructions at the top of 
#  this file to understand how to use this.
def MakeWebArt(inpic,credit,outpic='cover_big.jpg',colour='white',
    width=600,height=360):

    #Get the height and width of the input picture.
    print('\nMaking website art using: '+str(inpic)+'\n')
    print('Obtaining picture dimensions...')
    cover_width,cover_height = GetImageWidthHeight(inpic)

    #Set the resize parameters so that the smaller dimension equals 600 
    #pixels.
    print('Obtaining picture resize parameters...')
    resizecall = GetResizeCall(cover_width,cover_height,width)

    #Create a temporary resized image.
    print('Resizing picture...')
    web_temp_name = 'tmp3.jpg'
    DoResize(inpic,resizecall,web_temp_name)

    #create the final image.
    print('Making widescreen website art...')
    os.system('/usr/bin/convert tmp3.jpg -thumbnail '+str(width)+'x'+str(height)+'^ -gravity center -extent '+str(width)+'x'+str(height)+' -fill '+str(colour)+' -font Helvetica -gravity SouthWest -kerning 0 -pointsize 8 -draw "text 5,5 \'Image credit: '+str(credit)+'\'" '+str(outpic))

    #Remove the temporary image.
    os.system('rm '+str(web_temp_name))
    print('Website art complete.\n')

    return
