################################################################################
#
# xPL interface for Boxee
#
# Version 1.0
#
# Copyright (C) 2010 by Sam Steele
# http://www.c99.org/
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# Linking this library statically or dynamically with other modules is
# making a combined work based on this library. Thus, the terms and
# conditions of the GNU General Public License cover the whole
# combination.
# As a special exception, the copyright holders of this library give you
# permission to link this library with independent modules to produce an
# executable, regardless of the license terms of these independent
# modules, and to copy and distribute the resulting executable under
# terms of your choice, provided that you also meet, for each linked
# independent module, the terms and conditions of the license of that
# module. An independent module is a module which is not derived from
# or based on this library. If you modify this library, you may extend
# this exception to your version of the library, but you are not
# obligated to do so. If you do not wish to do so, delete this
# exception statement from your version.
#
################################################################################
import sys, string, select, threading, os.path
import xbmc
from socket import *

# Define maximum xPL message size
buff = 1500

# Define xPL base port
port = 3865

# Send out a heartbeat message periodically
def HeartBeat():
	global port
	
	SendBroadcast("xpl-stat", "*","hbeat.app", "interval=1\nport=" + str(port) + "\nremote-ip=" + xbmc.getIPAddress())
	heartbeat_timer = threading.Timer(60, HeartBeat)
	heartbeat_timer.start()

heartbeat_timer = threading.Timer(1, HeartBeat)
heartbeat_timer.start()

# xPL source name
source = "c99org-boxee." + gethostname().split(".")[0]

# Sub routine for sending a broadcast
def SendBroadcast(type, target, schema, body) :
  hbSock = socket(AF_INET,SOCK_DGRAM)
  hbSock.setsockopt(SOL_SOCKET,SO_BROADCAST,1)
  msg = "xpl-stat\n{\nhop=1\nsource=" + source + "\ntarget="+target+"\n}\n"+schema+"\n{\n"+ body + "\n}\n"
  hbSock.sendto(msg,("255.255.255.255",3865))

def ParseBroadcast(data):
	parts = data.split("\n")
	msgtype = parts[0].lower()
	offset = 2
	values = dict()
	if parts[offset-1] == "{":
		while parts[offset] != "}":
			part = parts[offset]
			if part != "}":
				value=part.split("=")
				if len(value) == 2:
					values[value[0].lower()]=value[1].lower()
				offset = offset + 1
			else:
				break
	offset = offset + 1
	schema = parts[offset].lower()
	offset = offset + 2
	if parts[offset-1] == "{":
		while parts[offset] != "}":
			part = parts[offset]
			if part != "}":
				value=part.split("=")
				if len(value) == 2:
					values[value[0].lower()]=value[1].lower()
				offset = offset + 1
			else:
				break

	if (values['target'] != "*" and values['target'] != "c99org-boxee.*" and values['target'] != source) or values['source'] == source:
		return

	if msgtype == "xpl-cmnd":
		if schema == "media.basic":
			print "Got media command:" + values['command']
			if values['command'].lower() == "stop":
				xbmc.executebuiltin('PlayerControl(Stop)')
			if values['command'].lower() == "play":
				xbmc.executebuiltin('PlayerControl(Play)')
			if values['command'].lower() == "pause":
				if xbmc.Player().isPlaying():
					xbmc.executebuiltin('PlayerControl(Play)')
			if values['command'].lower() == "skip":
				xbmc.executebuiltin('PlayerControl(Next)')
				
		if schema == "media.request":
			if values['request'].lower() == "devinfo":
				SendBroadcast("xpl-stat", values['source'],"media.devinfo", "name=Boxee xPL Interface\nversion=1.0\nauthor=Sam Steele\ninfo-url=http://www.c99.org/\nmp-list=boxee\n")
			
			if values['request'].lower() == "devstate":
				SendBroadcast("xpl-stat", values['source'],"media.devstate", "power=on\nconnected=true\n")

			if values['request'].lower() == "mpinfo":
				SendBroadcast("xpl-stat", values['source'],"media.mpinfo", "mp=boxee\nname=Boxee\ncommand-list=play,stop,pause,skip\naudio=true\nvideo=true\n")

			if values['request'].lower() == "mptrnspt":
				SendBroadcast("xpl-stat", values['source'],"media.mptrnspt", "mp=boxee\ncommand="+lastState+"\n")

			if values['request'].lower() == "mpmedia":
				media = "mp=boxee\n"
				if xbmc.Player().isPlaying():
					if xbmc.Player().isPlayingAudio():
						tag = xbmc.Player().getMusicInfoTag();
						media = "mp=boxee\n"
						media = media + "kind=audio\n"
						media = media + "title=" + tag.getTitle() + "\n"
						media = media + "album=" + tag.getAlbum() + "\n"
						media = media + "artist=" + tag.getArtist() + "\n"
						media = media + "duration=" + str(xbmc.Player().getTotalTime()) + "\n"
						media = media + "format=" + os.path.splitext(xbmc.Player().getPlayingFile())[1][1:] + "\n"
					else:
						tag = xbmc.Player().getVideoInfoTag();
						media = "mp=boxee\n"
						media = media + "kind=video\n"
						media = media + "title=" + tag.getTitle() + "\n"
						media = media + "album=" + "\n"
						media = media + "artist=" + "\n"
						media = media + "duration=" + str(xbmc.Player().getTotalTime()) + "\n"
						media = media + "format=" + os.path.splitext(xbmc.Player().getPlayingFile())[1][1:] + "\n"
						
				SendBroadcast("xpl-stat", values['source'],"media.mpmedia", media)

lastState = "stop"
lastAudioTag = None
lastVideoTag = None

def MonitorXbmc():
	global lastState, lastAudioTag, lastVideoTag
	
	if xbmc.Player().isPlaying():
		try:
			if mc.Player().IsPaused():
				state = "pause"
			else:
				state = "play"
		except:
			state = "play"
		if xbmc.Player().isPlayingAudio():
			tag = xbmc.Player().getMusicInfoTag();
			if lastAudioTag is None or lastAudioTag.getTitle() != tag.getTitle() or lastAudioTag.getArtist() != tag.getArtist() or lastAudioTag.getAlbum() != tag.getAlbum():
				media = "mp=boxee\n"
				media = media + "kind=audio\n"
				media = media + "title=" + tag.getTitle() + "\n"
				media = media + "album=" + tag.getAlbum() + "\n"
				media = media + "artist=" + tag.getArtist() + "\n"
				media = media + "duration=" + str(xbmc.Player().getTotalTime()) + "\n"
				media = media + "format=" + os.path.splitext(xbmc.Player().getPlayingFile())[1][1:] + "\n"
				SendBroadcast("xpl-trig", "*","media.mpmedia", media)
				lastAudioTag = tag
		else:
			tag = xbmc.Player().getVideoInfoTag();
			if lastVideoTag is None or lastVideoTag.getTitle() != tag.getTitle():
				media = "mp=boxee\n"
				media = media + "kind=video\n"
				media = media + "title=" + tag.getTitle() + "\n"
				media = media + "album=" + "\n"
				media = media + "artist=" + "\n"
				media = media + "duration=" + str(xbmc.Player().getTotalTime()) + "\n"
				media = media + "format=" + os.path.splitext(xbmc.Player().getPlayingFile())[1][1:] + "\n"
				SendBroadcast("xpl-trig", "*","media.mpmedia", media)
				lastVideoTag = tag

	else:
		state = "stop"
		lastAudioTag = None
		lastVideoTag = None
		
	if state != lastState:
		lastState = state
		SendBroadcast("xpl-trig", "*","media.mptrnspt", "mp=boxee\ncommand="+lastState+"\n")
		
	monitor_timer = threading.Timer(1, MonitorXbmc)
	monitor_timer.start()

monitor_timer = threading.Timer(1, MonitorXbmc)
monitor_timer.start()

# Initialise the socket
UDPSock = socket(AF_INET,SOCK_DGRAM)
addr = ("0.0.0.0",port)

# Try and bind to the base port
try :
  UDPSock.bind(addr)
except :
  # A hub is running, so bind to a high port
  port = 50000

  addr = ("127.0.0.1",port)
  try :
    UDPSock.bind(addr)
  except :
    port += 1

print "xPL source " + source + " now listening on port " + str(port)

try:
	while 1==1:
	  readable, writeable, errored = select.select([UDPSock],[],[],60)

	  if len(readable) == 1 :
	    data,addr = UDPSock.recvfrom(buff)
	    ParseBroadcast(data)
	
	  xbmc.sleep(3000)
except (KeyboardInterrupt, SystemExit):
	print "Shutting down xPL listener"
	SendBroadcast("xpl-stat", "*","hbeat.end", "")
	heartbeat_interval = -1
	heartbeat_timer.cancel()
	
