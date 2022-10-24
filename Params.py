print_output=True
bitrate_dict={"-high":128,"":64,"-low":24}

#Base directory for recordings
base_dir="/scratch/almanas/jodcast_backup/jodcast_1/jodcast/raw/"
#Base directory for websites
web_dir="/home/www/public_html/jodcast/"
#Location of convert program (for creating cover art)
convert = "/scratch/almanas/jodcast_backup/jodcast_1/im/bin/convert"
#Name of lame program (for converting wav to mp3)
lame="lame"
#sox="scratch/almanas/jodcast_backup/jodcast_1/jodcast/sox-14.4.2/src/sox"
sox="sox"
#404 webpage in case the real webpage hasn"t been creating yet
url_404_page=web_dir+"/404b.html"

#set manual options for cover art text
colour = "white" #text colour
valign = "bottom" #logo location

#Name of music for intro and outro
intro="./audio/intro_mike_peel.wav" #Can we create a folder for regularly used audio clips? 
#intro="./audio/test/intro_mike_mono.wav" 
#intro="./audio/intro_fionashow_mono.wav" 

outro="./audio/outro-tess.wav"
#outro="./audio/test/outro_mono.wav"

#Template images with jodcast logo
cover_template_top='./images/cover_template_fade_top.png'
cover_template='./images/cover_template_fade.png'
#cover_template='./images/fiona_fade.png'




#Shouldn't need to change anything below this line. 
#Proceed with extreme caution
import os
if 'LD_LIBRARY_PATH' in os.environ.keys():
   os.environ['LD_LIBRARY_PATH']+=':/scratch/almanas/jodcast_backup/jodcast_1/im/lib'
else:
   os.environ['LD_LIBRARY_PATH']='/scratch/almanas/jodcast_backup/jodcast_1/im/lib'
