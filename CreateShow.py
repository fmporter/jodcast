#!/usr/bin/env python
"""
This is a script to:
- Read XML file for show
- Compress episode to mp3
- Make cover art
- Extract show segments and compress to mp3
- Add tags to mp3 files
- Copy all mp3s and jpegs to the web directory

Written by Monique Henson, Charlie Walker and George Bendo
moniquehenson13@gmail.com
walker.mbcxqcw2@gmail.com
October 2016
"""
#Quick and dirty script to replace addtags5.pl
#Not yet finished
#Still needs to create cover art, add tags to mp3, convert entire episode from wav to mp3 (segments already done) and sort out a load of permissions
#Complain to Monique (monique.henson@manchester.ac.uk) if you"d like to complain
#Have been testing on /local/scratch/jodcast_backup/jodcast_1/jodcast/raw/201612/

#cover art stuff is done, import from MakeCoverArt2016.py

import sys
#Add anaconda to pythonpath 
sys.path.append('/scratch/almanas/jodcast_backup/jodcast_1/jodcast/anaconda2/lib/python2.7/site-packages')
import argparse #To parse command line arguments
import os
import grp #To get id of jodcast group
import string
from shutil import copyfile 
import subprocess #for executing lame
from datetime import datetime #calculating time between two time intervals
import eyed3

from MakeCoverArt2016 import MakeCoverArt
from MakeCoverArt2016 import MakeWebArt
from Params import *
from ProcessAudio import *
   


#Parse command line arguments
parser=argparse.ArgumentParser()
parser.add_argument("episode",type=str,help="String with name of episode")
arguments=parser.parse_args()
episode=arguments.episode


#Location of shownotes directory
episode_dir=base_dir+"/"+episode+"/"
#Log files for all subprocesses called in this script (lame, sox etc.)
log_err_file=episode_dir+'/createshow_err.txt'
log_out_file=episode_dir+'/createshow_output.txt'

#Assume shownotes file has same name as directory
xml_filename=episode_dir+episode+".xml"

#Can get rid of this once we are sure we don"t need any of Stuarts scripts. We should 
#just be able to call the Extra episodes Extra!
if "Extra" in episode:
    audio_file_label=episode[:-1*len('Extra')]+"15"+"-jodcast"
else:
    audio_file_label=episode+"01"+"-jodcast"



#Tell user what script does (do later once things work)
print "This is a script to:"
print "- Read XML file for show"
print "- XML file name should match episode directory name"
print "- Compress episode to mp3"
print "- Make cover art"
print "- Extract show segments and compress to mp3"
print "- Add tags to mp3 files"
print "- Copy all mp3s and jpegs to the web directory"
print "The script can be configured by changing Params.py"
print "Current settings are..."
print "Intro audio:",intro
print "Outro audio:",outro
print "Logo alignment:",valign
print "Logo colour:",colour
print "Script beginning now!"

#Check if show directory exists, if not, create a random temporary directory
show_web_dir=web_dir+"/archive/"+episode
if os.path.exists(show_web_dir) is False:
    if os.path.isfile(episode_dir+'/web_directory_location.txt'):
        with open(episode_dir+'/web_directory_location.txt','r') as f:
            show_web_dir=f.read()
            
    else:
        show_web_dir_temp=web_dir+"/archive/"+GetRandomString(5)+'/'
        os.makedirs(show_web_dir_temp)
        os.chmod(show_web_dir_temp,0775)
        group_id=grp.getgrnam("jodcast").gr_gid
        os.chown(show_web_dir_temp,-1,group_id)
        #Store this somewhere. Where do they store it normally? Can"t find it
        show_web_dir=show_web_dir_temp
        #Store name of new directory in episode file

        with open(episode_dir+'/web_directory_location.txt','w') as f:
            f.write(show_web_dir)
else:
    with open(episode_dir+'/web_directory_location.txt','w') as f:
        f.write(show_web_dir) 

show_web_dir = show_web_dir.rstrip() #Added to avoid a newline bug in the temp directory name
#  This is the equivalent of 'chomp' in perl - Ben Shaw. May 22 2017

        
#Create dictionary to store show info from XML file
xml_data_dict={}
#Read XML file
ReadXMLFile(xml_filename,xml_data_dict)  
#Check if the index.html file exists. If now, create a 404 not found and set permissions
if os.path.isfile(show_web_dir+"/index.html") is False:
        copyfile(url_404_page,show_web_dir+"/index.html")
     
#################################################

#Check if cover art exists 
#If it doesn"t then make it
#get metadata from xml
inpic = episode_dir+"/"+str(xml_data_dict["cover"]["src"])    #cover art filename
credit = str(xml_data_dict["cover"]["credit"])    #cover art credit
edition=xml_data_dict["title"]["text"] #cover art episode edition

#make the 300x300 version for the mp3
if os.path.isfile(episode_dir+'cover.jpg') is False:
    MakeCoverArt(inpic,valign,episode_dir+"cover.jpg",edition,credit,300,colour)
CopyAndSetPermissions(episode_dir+"cover.jpg",show_web_dir+"cover.jpg")
               
#make the 190x190 version for the website
if os.path.isfile(episode_dir+'cover_mp3.jpg') is False:
    MakeCoverArt(inpic,valign,episode_dir+"cover_mp3.jpg",edition,credit,190,colour)
CopyAndSetPermissions(episode_dir+"cover_mp3.jpg",show_web_dir+str("cover_mp3.jpg"))
#Save cover image data to xml_data_dict for adding to mp3 tags later
with open(episode_dir+"cover_mp3.jpg",'rb') as f:
    xml_data_dict['coverimage']=f.read()
                
#make the 600x360 website art
if os.path.isfile(episode_dir+'cover_big.jpg') is False:
    MakeWebArt(inpic,credit,episode_dir+"cover_big.jpg",colour)
CopyAndSetPermissions(episode_dir+"cover_big.jpg",show_web_dir+"cover_big.jpg")
if print_output: print "Cover art created successfully"
            
            
###############################################
# Process audio and ID3 tags for each episode #
###############################################
if print_output: 
   print "Processing main show audio. This may take a while..."
   print "If you want to see how it's progressing, look at ",log_out_file,' and ',log_err_file
   print "in the show directory."
   print "Use less +F <filename> so that they automatically update"

#Compress whole show to mp3
full_show_wav=episode_dir+"/"+audio_file_label+".wav"
print full_show_wav,'!!!'
#sys.exit(9)
for quality in bitrate_dict.keys():
   full_show_mp3=episode_dir+'/'+audio_file_label+quality+'.mp3'
   #print full_show_mp3 ; sys.exit(9)
   bitrate=str(bitrate_dict[quality])
   #Convert WAV segment to mp3
   if os.path.isfile(full_show_mp3) is False:
       ConvertWavToMP3(lame,full_show_wav,full_show_mp3,bitrate,log_out_file,log_err_file)     
       SetMP3Tags(full_show_mp3,xml_data_dict)
   
       
   full_show_mp3_web_dir=show_web_dir+"/"+audio_file_label+quality+'.mp3'
   if os.path.isfile(full_show_mp3_web_dir) is False:
       #Copy show to web directory
       CopyAndSetPermissions(full_show_mp3,full_show_mp3_web_dir)
   if print_output: print "Main show with bitrate ",bitrate,"completed"
           
if print_output: print "Main show converted to mp3 successfully"

#Process each segment for the show
for segment in xml_data_dict["segments"]:
   print "\nSegment:"+str(segment)
   #Find out segment length
   start_time=xml_data_dict[segment]["starttime"]["text"]
   end_time=xml_data_dict[segment]["endtime"]["text"]
   duration=GetSegmentDuration(start_time,end_time)
   
   uncompressed_segment=episode_dir+"/"+audio_file_label+'-'+segment+".wav" 
   #Extract segment from main audio file
   TrimToSegment(sox,full_show_wav,start_time,duration,uncompressed_segment,log_out_file,log_err_file)
   #Add intro and outro to segment file
   try:
      AddIntroOutro(sox,uncompressed_segment,intro,outro,log_out_file,log_err_file)
   except IOError:
      print "Error encountered whilst adding segment voice file"
      print "It looks like your main wav file is in mono and the segment file you're trying to add is in stereo"
      print "See/edit lines 22-28 in Params.py and all should become clear"
      sys.exit(9)

   #Covert segment file to mp3 (for 3 different bitrates)
   for quality in bitrate_dict.keys():     
       segment_file=episode_dir+"/"+audio_file_label+'-'+segment+quality+".mp3"
       bitrate=str(bitrate_dict[quality])
       #Convert WAV segment to mp3
       if os.path.isfile(segment_file) is False:       
           ConvertWavToMP3(lame,uncompressed_segment,segment_file,bitrate,log_out_file,log_err_file)
       #Add tags to segment
           SetMP3Tags(segment_file,xml_data_dict,segment)
       segment_file_web_dir=show_web_dir+"/"+audio_file_label+'-'+segment+quality+".mp3"
       if os.path.isfile(segment_file_web_dir) is False:
           #Copy segment to show directory
           CopyAndSetPermissions(segment_file,segment_file_web_dir)          
   if print_output: print "Segment:",segment,"extracted and compressed successfully."

   




