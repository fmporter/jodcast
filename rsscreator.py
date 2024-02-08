#rsscreator.py - Creates an entire RSS feed for the Jodcast.  

#Created by George J. Bendo in 2023.  This script is partially based on code 
#originally created for creating the RSS feed for George's Random Astronomical
#Object.



#To use this script, simply provide an input list of the XML files containing
#the show information and a name for the output file.
#
# > rsscreator('xmllist.txt','rss-new.xml')



#Import modules.
import calendar,numpy,os,xmltodict
from datetime import datetime
from mutagen.mp3 import MP3



#Define a module for creating the entry for a single show in an RSS feed.
def episoderssentrycreator(xmlfile):

    #Print an informational line.
    print('Working on '+xmlfile.split('/')[-1].replace('\n',''))

    #Import the xml file.
    xmlData=xmltodict.parse(open(xmlfile).read())['show']

    #Identify the location of the audio file on the local computers.  This
    #is needed for getting information about the file that is not within the
    #xml file.
    dirAudioMain='/scratch/almanas/jodcast_backup/jodcast_1/jodcast/www/'
    dirAudioEpisode=dirAudioMain+xmlData['archive']['@url'].split('www.jodcast.net/')[1]
    fileAudioEpisode=dirAudioEpisode+xmlData['media']['@src']
    
    #Get information about the file size.
    filesize=os.stat(fileAudioEpisode).st_size

    #Get information about the length of the audio file.
    audioMP3=MP3(fileAudioEpisode)
    audioLength=audioMP3.info.length
    audioLengthMin,audioLengthSec=divmod(audioLength,60)
    if int(numpy.round(audioLengthSec))==60:
      audioLengthMin+=1
      audioLengthSec=0
    audioLengthString=f'{int(audioLengthMin):02}'+':'\
      +f'{int(numpy.round(audioLengthSec)):02}'

    #Set up url based entries.  Note that many older xml entries used http 
    #instead of https.  These need to be replaces in these steps.
    urlEpisode=xmlData['archive']['@url']
    urlEpisode.replace('http:','https:')
    urlMp3=xmlData['archive']['@url']+xmlData['media']['@src']
    urlMp3.replace('http:','https:')

    #Print the first line defining the episode entry.
    output='    <item>\n'

    #Print the episode-specific information.
    output=output+'      <title>'+xmlData['title']['#text']+'</title>\n'
    output=output+'      <itunes:title>'+xmlData['title']['#text']+'</itunes:title>\n'
    output=output+'      <itunes:author>Jodrell Bank Centre for Astrophysics</itunes:author>\n'
    output=output+'      <description>'+xmlData['description']['@short']+'</description>\n'
    output=output+'      <itunes:subtitle>'+xmlData['title']['@sub']+'</itunes:subtitle>\n'
    output=output+'      <itunes:summary>'+xmlData['description']['@short']+'</itunes:summary>\n'
    output=output+'      <enclosure url="'+urlMp3+'" type="audio/mpeg" length="'+str(filesize)+'"></enclosure>\n'
    output=output+'      <guid>'+urlMp3+'</guid>\n'
    output=output+'      <link>'+urlEpisode+'</link>\n'
    output=output+'      <pubDate>'+xmlData['pubDate']+'</pubDate>\n'
    output=output+'      <itunes:duration>'+audioLengthString+'</itunes:duration>\n'
    output=output+'      <itunes:explicit>false</itunes:explicit>\n'

    #Print the line defining the end of the entry.
    output=output+'    </item>\n'
    
    #Return the output.
    return(output)



#Define the main function.
def rsscreator(xmllist,outputfile):

  #Open the rss.xml file for output.
  filerss=open(outputfile,'w+')

  #Set universal header strings.
  shortdescription='The Jodcast is an astronomy podcast created by students and staff from the Jodrell Bank Centre for Astrophysics.'
  description=shortdescription+'  The episodes include the latest astronomy news, interviews with astronomers, stargazing information, and more.'

  #Create the string for the publciation date.
  datetimedata=datetime.now()
  pubDateDayWeek=calendar.day_abbr[datetime.weekday(datetimedata)]
  pubDateDay=f'{datetimedata.day:02}'
  pubDateHour=f'{datetimedata.hour:02}'
  pubDateMinute=f'{datetimedata.minute:02}'
  pubDateSecond=f'{datetimedata.second:02}'
  pubDate=pubDateDayWeek+', '+pubDateDay+' '\
    +calendar.month_abbr[datetimedata.month]+' '\
    +str(datetimedata.year)+' '\
    +pubDateHour+':'+pubDateMinute+':'+pubDateSecond+' GMT'

  #Write the header for the RSS feed.
  filerss.write('<?xml version="1.0" encoding="UTF-8"?>\n')
  filerss.write('<rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" version="2.0">\n')
  filerss.write('  <channel>\n')
  filerss.write("    <title>The Jodcast</title>\n")
  filerss.write('    <link>https://www.jodcast.net/</link>\n')
  filerss.write('    <image>\n')
  filerss.write('      <url>https://www.jodcast.net/itunes5.jpg</url>\n')
  filerss.write("      <title>The Jodcast</title>\n")
  filerss.write('      <link>https://www.jodcast.net/</link>\n')
  filerss.write('    </image>\n')
  filerss.write('    <copyright>Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International</copyright>\n')
  filerss.write('    <description>'+description+'</description>\n')
  filerss.write('    <language>en</language>\n')
  filerss.write('    <pubDate>'+pubDate+'</pubDate>\n')
  filerss.write('    <lastBuildDate>'+pubDate+'</lastBuildDate>\n')
  filerss.write('    <itunes:subtitle>'+shortdescription+'</itunes:subtitle>\n')
  filerss.write('    <itunes:author>Jodrell Bank Centre for Astrophysics</itunes:author>\n')
  filerss.write('    <itunes:summary>'+description+'</itunes:summary>\n')
  filerss.write('    <itunes:owner>\n')
  filerss.write('      <itunes:email>jodcastfeedback@jb.man.ac.uk</itunes:email>\n')
  filerss.write('    </itunes:owner>\n')
  filerss.write('    <itunes:explicit>false</itunes:explicit>\n')
  filerss.write('    <itunes:image href="https://www.jodcast.net/itunes5.jpg" />\n')
  filerss.write('    <itunes:category text="Science">\n')
  filerss.write('      <itunes:category text="Astronomy"/>\n')
  filerss.write('      <itunes:category text="Natural Sciences"/>\n')
  filerss.write('    </itunes:category>\n')
  filerss.write('    <itunes:type>episodic</itunes:type>\n')
  filerss.write('    <itunes:keywords>astronomy, science, interviews, astronomer, stars, planets</itunes:keywords>\n')
  filerss.write('    <atom10:link xmlns:atom10="http://www.w3.org/2005/Atom" rel="self" href="https://www.jodcast.net/rss.xml" type="application/rss+xml" />\n')
  filerss.write('\n')
  filerss.write('\n')
  filerss.write('\n')

  #Read the filelist with the xml files containing the information for
  #individual episodes.
  f=open(xmllist,'r')
  filenames=f.readlines()
  f.close()

  #Loop through each filerss.
  for filename in filenames:
    
    #Call episoderssentrycreator.
    filerss.write(episoderssentrycreator(filename.rstrip('\n')))
    filerss.write('\n')

  #Write some lines to end the RSS feed.
  filerss.write('\n')
  filerss.write('\n')
  filerss.write('    </channel>\n')
  filerss.write('</rss>\n')

  #Close the file.
  filerss.close()
