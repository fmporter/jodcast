from Params import *
import sys
import subprocess
sys.path.append('/scratch/almanas/jodcast_backup/jodcast_1/jodcast/anaconda2/lib/python2.7/site-packages/eyed3/__init__.pyc')

def GetRandomString(length):
    import string
    import random
    chars=string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for x in range(length)).lower()


def ReadXMLFile(xml_filename,data_dict):
        import xml.etree.cElementTree as ElementTree
        #print xml_filename ; sys.exit(9)
        xml_file_tree=ElementTree.parse(xml_filename).getroot()
        data_dict["segments"]=[]
        counter=1
        for child in xml_file_tree:            
            if type(child.attrib)==dict and child.tag=="segment":
               segment_name=str(child.attrib['type'])
               if segment_name in data_dict.keys():
                   if counter==1:
                       data_dict[segment_name+'1']=data_dict[segment_name]
                       del data_dict[segment_name]
                       data_dict['segments'].remove(segment_name)
                       data_dict['segments'].append(segment_name+'1')
                   counter+=1
                   segment_name+=str(counter)
                   
               data_dict[segment_name]={}
               segment_dict=data_dict[segment_name]
               data_dict["segments"].append(segment_name)
               for grandchild in child:
                    segment_dict[grandchild.tag]={}
                   
                    #Grandchild attrib should be a dictionary. If it"s empty (returns False), don"t read it
                    if bool(grandchild.attrib) is True:
                        segment_dict[grandchild.tag]=grandchild.attrib

                    if grandchild.text != None: 
                        segment_dict[grandchild.tag]["text"]=grandchild.text
                                           
            else:

                if "item" in child.attrib.keys():
                    data_dict[child.attrib["item"]]=child.attrib["name"]
                else:
                    data_dict[child.tag]=child.attrib
                    data_dict[child.tag]["text"]=child.text


def PadTimeString(time_string):
   if time_string.count(":")<2:
       return "00:"+time_string
   else: return time_string
     
       
def GetSegmentDuration(start_time,end_time):
   import datetime as dt 
   time_format="%H:%M:%S.%f"
   start_time=PadTimeString(start_time) #To ensure consistent formatting for recordings <1 hour
   start_time_dt=dt.datetime.strptime(start_time,time_format)  
   end_time=PadTimeString(end_time) #To ensure consistent formatting for recordings <1 hour
   end_time_dt=dt.datetime.strptime(end_time,time_format)
   duration=end_time_dt-start_time_dt
   duration=duration.seconds+(duration.microseconds/1e6)
   return duration
   

def TrimToSegment(sox,full_show_wav,start_time,duration,segment_wav,log_out_file,log_err_file):
   from subprocess import Popen #for executing sox
   start_time=str(start_time)
   duration=str(duration)
   with open(log_out_file,'a') as out:
        with open(log_err_file,'a') as err:
           Popen([sox,full_show_wav,segment_wav,"trim",start_time,duration],stdout=out, stderr=err).wait()

   


def AddIntroOutro(sox,segment_file,intro,outro,log_out_file,log_err_file,newfile=None):
   from subprocess import Popen #for executing sox
   import os
   import shutil
   #print segment_file, intro, outro ; sys.exit(9)
   with open(log_out_file,'a') as out:
        with open(log_err_file,'a') as err:
           Popen([sox,intro,segment_file,outro,'dummy_segment_file.wav'],stdout=out, stderr=err).wait()
   if newfile==None:
#      os.rename('dummy_segment_file.wav',segment_file)
       shutil.move('dummy_segment_file.wav',segment_file)
   else:
      shutil.move('dummy_segment_file.wav',newfile)
#      os.rename('dummy_segment_file.wav',newfile)

def ConvertWavToMP3(lame,audio_wav,audio_mp3,bitrate,log_out_file,log_err_file):

   import subprocess
   with open(log_out_file,'a') as out:
       with open(log_err_file,'a') as err:
           subprocess.Popen([lame,"-b",bitrate,"-m","j","-h",audio_wav,audio_mp3],stdout=out, stderr=err).wait()

                  
                  

def SetMP3Tags(audiofile,xml_data_dict,segment=None):
   import eyed3
   audiofile_eyed3=eyed3.load(audiofile)
   audiofile_eyed3.initTag()
   if segment==None: #assume it's full episode
       audiofile_eyed3.tag.title=unicode(xml_data_dict["title"]["text"])
       audiofile_eyed3.tag.artist=unicode("The Jodcast Astronomers")
   else:
       audiofile_eyed3.tag.title=unicode(xml_data_dict[segment]['title']['text'])
       audiofile_eyed3.tag.artist=unicode(xml_data_dict[segment]['author']['name'])
        
        
   audiofile_eyed3.tag.album=unicode("The Jodcast")
   audiofile_eyed3.tag.year=unicode(xml_data_dict['pubDate']['text'][-4:])
   audiofile_eyed3.tag.copyright_url=unicode(xml_data_dict['copyright']['text'])
   audiofile_eyed3.tag.audio_file_url=unicode(xml_data_dict['archive']['url'])
   audiofile_eyed3.tag.genre=unicode('Speech')
   coverimage=xml_data_dict['coverimage']
   audiofile_eyed3.tag.images.set(3,coverimage,'image/jpeg')
   audiofile_eyed3.tag.save()   


def CopyAndSetPermissions(original_file,new_file):
#Copy file to new directory and ensure both files have 775 permissions 
#and are in the jodcast group
   from shutil import copyfile 
   import os
   import grp #To get id of jodcast group
   copyfile(original_file,new_file)
   os.chmod(new_file,0775)
   group_id=grp.getgrnam("jodcast").gr_gid
   os.chown(new_file,-1,group_id)
