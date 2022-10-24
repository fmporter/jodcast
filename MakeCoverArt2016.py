#These functions create a Jodcast cover image. The default image size, as has
#been used since 2006 is 300x300, however this can now be changed at will.
#Any complaints should go to charles.walker@postgrad.manchester.ac.uk
#If you are reading this and he has left Manchester already (they are
#very militant about destroying your email address when you leave)
#then complain to walker.mbcxqcw2@gmail.com

#Import packages.
import math,os
from subprocess import PIPE,Popen
from Params import *

def ConvertColorSpace(image,desired_colorspace,new_image_name=None):
    if new_image_name != None:
        os.system('/usr/bin/convert  '+image+' -colorspace '+desired_colorspace+' '+new_image_name)
    else:
        os.system('/usr/bin/convert  '+image+' -colorspace '+desired_colorspace+' '+image)


def GetImageWidthHeight(inpic):
    """
    does what it says on the tin
    """
    print "Image width"
    print Popen(args='/usr/bin/convert '+inpic+' -print "%w" /dev/null',stdout=PIPE,shell=True).communicate()[0]
    print ""
    image_width=float(Popen(args='/usr/bin/convert '+inpic+' -print "%w" /dev/null',stdout=PIPE,shell=True).communicate()[0])
    image_height=float(Popen(args='/usr/bin/convert '+inpic+' -print "%h" /dev/null',stdout=PIPE,shell=True).communicate()[0])

    return image_width,image_height

def GetResizeCall(image_width,image_height,image_dimension):
    """
    creates the cmd line call which will resize an input image
    """

    if image_width>=image_height:
        excess=`int( round( (image_width/image_height*image_dimension-image_dimension)/2 ) )`
        resizecall='-resize x'+str(image_dimension)+' -crop -'+excess+'+0 -crop +'+excess+'+0'
    if image_width<image_height:
        excess=`int( round( (image_height/image_width*image_dimension-image_dimension)/2 ) )`
        resizecall='-resize '+str(image_dimension)+' -crop +0-'+excess+' -crop +0+'+excess

    return resizecall

def DoResize(inpic,resizecall,outname='tmp.jpg'):
    """
    uses a resize call on an input image, storing the output in a temporary file
    this is important. don't fiddle with the real files. you can delete temps afterwards.
    """

    os.system('/usr/bin/convert '+inpic+' '+resizecall+' '+outname)

    return

def GetTextParams(cover_dimension,valign):
    """
    the text must be rescaled and translated accordingly 
    from the reference we have (600*600 pixel cover)
    """

    #reference dimensions and locations *NEVER CHANGE*
    #edition text
    ref_dims = 600.
    ref_loc_1 = 109.

    if valign == 'top':
        ref_loc_2 = 360.
    else:
        ref_loc_2 = 42.

    ref_textsize = 35.
    #credit text
    ref_loc_3 = 5.
    ref_loc_4 = 5.
    ref_textsize_2 = 18.
    
    #get scaling factor
    in_dims = cover_dimension
    rescale_factor = in_dims/ref_dims

    #rescale numbers
    loc_1 = int(rescale_factor * ref_loc_1)
    loc_2 = int(rescale_factor * ref_loc_2)
    textsize = int(rescale_factor * ref_textsize)
    loc_3 = int(rescale_factor * ref_loc_3)
    loc_4 = int(rescale_factor * ref_loc_4)
    textsize_2 = int(rescale_factor * ref_textsize_2)

    return loc_1,loc_2,loc_3,loc_4,textsize,textsize_2

def MakeCoverArt(inpic,valign='bottom',outpic='cover.jpg',edition='INSERT EDITION Edition',credit='INSERT THE CREDIT!!!',cover_dimension=300,colour='white'):
    """
    creates jodcast cover art from an input image, the logo template (cover_template_fade.png) for use on the website.
    default and used cover size is 300x300. can be scaled with cover_dimension for higher quality images.
    valign puts logo at top or bottom of image.
    Remember to add the edition information (eg July 2016 or July Extra 2016) and credits.
    """

    #choose template picture based on alignment option
    if valign == 'top':
        cover_template_pic = cover_template_top
    else:
        cover_template_pic = cover_template

    #get height and width of input picture
    print '\nMaking cover art using: '+str(inpic)+'\n'
    print 'Obtaining picture dimensions...'
    cover_width,cover_height = GetImageWidthHeight(inpic)

    #get height and width of template logo
    print 'Obtaining template dimensions...'
    logo_width,logo_height = GetImageWidthHeight(cover_template_pic)

    #set resize parameters so smaller dimension = cover_dimension [pixels]
    print 'Obtaining picture resize parameters...'
    resizecall = GetResizeCall(cover_width,cover_height,cover_dimension)

    #set resize parameters for template logo
    print 'Obtaining template resize parameters...'
    logo_dimension = cover_dimension
    logo_resizecall = GetResizeCall(logo_width,logo_height,logo_dimension)

    #create temporary image
    print 'Resizing picture...'
    imag_temp_name = 'tmp.jpg'
    DoResize(inpic,resizecall)

    #create temporary logo image
    print 'Resizing template...'
    logo_temp_name = 'tmp_logo.png'
    DoResize(cover_template_pic,logo_resizecall,logo_temp_name)

    #Convert image to correct colorspace (RGB rather than CMYK)
    ConvertColorSpace(imag_temp_name,'rgb')

    #Recolour Jodcast logo if required
    if colour!='white':
        os.system('/usr/bin/convert '+logo_temp_name+' -fill '+colour+' -opaque white '+logo_temp_name)
    
    #rescale text locations and sizes
    print 'Getting rescaled parameters...'
    loc_1,loc_2,loc_3,loc_4,textsize,textsize_2 = GetTextParams(cover_dimension,valign)

    #create cover art
    print 'Making cover art...'

    os.system('/usr/bin/convert '+imag_temp_name+' -thumbnail '+str(cover_dimension)+'x'+str(cover_dimension)+'^ -gravity center -extent '+str(cover_dimension)+'x'+str(cover_dimension)+' '+str(logo_temp_name)+' -font Bitstream-Vera-Sans-Bold -fill "'+str(colour)+'" -pointsize '+str(textsize)+' -gravity SouthEast -draw "text '+str(loc_1)+','+str(loc_2)+' \''+str(edition)+'\'" -composite -thumbnail '+str(cover_dimension)+'x'+str(cover_dimension)+'^ -fill "'+str(colour)+'" -font Helvetica -gravity NorthWest -kerning -0 -pointsize '+str(textsize_2)+' -draw "text '+str(loc_3)+','+str(loc_4)+' \'CREDIT: '+str(credit)+'\'" '+str(outpic))

    #remove temporary images
    os.system('rm '+str(imag_temp_name))
    os.system('rm '+str(logo_temp_name))
    print 'Cover art complete.\n'

    return

def MakeWebArt(inpic,credit,outpic='cover_big.jpg',colour='white',width=600,height=360):
    """
    Makes the 600x360 widescreen website image. You should never have to change
    width or height.
    """

    #get height and width of input picture
    print '\nMaking website art using: '+str(inpic)+'\n'
    print 'Obtaining picture dimensions...'
    cover_width,cover_height = GetImageWidthHeight(inpic)

    #set resize parameters so smaller dimension = 600 pixels
    print 'Obtaining picture resize parameters...'
    resizecall = GetResizeCall(cover_width,cover_height,width)

    #create temporary image
    print 'Resizing picture...'
    web_temp_name = 'tmp3.jpg'
    DoResize(inpic,resizecall,web_temp_name)

    #Convert to correct colorspace (RGB rather CMYK)
    ConvertColorSpace(web_temp_name,'rgb',web_temp_name)
    #create image
    print 'Making widescreen website art...'
    os.system('/usr/bin/convert tmp3.jpg -thumbnail '+str(width)+'x'+str(height)+'^ -gravity center -extent '+str(width)+'x'+str(height)+' -fill '+str(colour)+' -font Helvetica -gravity SouthWest -kerning 0 -pointsize 10 -draw "text 5,5 \'CREDIT: '+str(credit)+'\'" '+str(outpic))

    #remove temporary image
    os.system('rm '+str(web_temp_name))
    print 'Website art complete.\n'

    return


