#!/usr/bin/python

import math
import spidev as SPI                # where the display connects
from PIL import Image, ImageDraw, ImageFont  # PIL - PythonImageLibrary
import subprocess # for getting the up time.
import time, datetime, sys, signal, urllib, requests, random
from StringIO import StringIO

from EPD_driver import EPD_driver

##################################################################################################

# draw a 12h analog clock
def drawclock(drw):
	centerx = 60
	centery = 70

	# draw hour markers
	r = 3
	rc = 50
	for i in range(12):
		theta =math.radians(i*30)
		x = centerx+rc*math.cos(theta)
		y = centery+rc*math.sin(theta)
		drw.ellipse((x-r, y-r, x+r,y+r), fill=0)

	time = datetime.datetime.now()

	# get hour and convert it to 12h
	hour = time.hour
	if(hour>12):
		hour = hour - 12
	hourAngle = (30 * hour) + (0.5 * time.minute) # 360/12 = 30
	#draw the hour
	drawHand(drw, hourAngle, 35, centerx, centery)

	# get minute
	minuteAngle = 360/60 * time.minute
	drawHand(drw, minuteAngle, 55, centerx, centery)

# draw a hand of the clock
def drawHand(drw, angle, length, centerx, centery):
	rad = math.radians(angle)
	# long end point
	hex = centerx + (math.sin(rad)*length)
	hey = centery - (math.cos(rad)*length)
	#short end points at center
	hepx = centerx+(math.cos(rad)*2)
	hemx = centerx-(math.cos(rad)*2)
	# and vice versa
	hepy = centery+(math.sin(rad)*2)
	hemy = centery-(math.sin(rad)*2)
	# draw the polygon
	drw.polygon((hepx, hepy, hemx, hemy,hex, hey),fill=0)

##################################################################################################

# get the system uptime
def getServerUpTime():
	upminutes = 0
	uphours = 0
	updays = 0

	uptime = subprocess.check_output(['cat', '/proc/uptime']).decode('utf-8').split()[0]
	uptime = long(float(uptime)) # convert to float, then to long int
	upseconds = uptime % 60 # "subtract" the seconds from the time
	uptime = int(uptime - upseconds) # ...
	if(uptime>=60):
		upminutes = uptime/60 # convert uptime to minutes
		uptime = upminutes # ...
		upminutes = uptime%60 # subtract the minutes from the uptime
		uptime = uptime - upminutes # ...
		if(uptime>=60):
			uphours = uptime / 60 # get the hours
			uptime = uphours
			uphours=uptime%24
			uptime=uptime-uphours
			if(uptime>=24):
				updays=uptime/24
	upstring = str(updays)+"d"+str(uphours)+"h"+str(upminutes)+"m" # +":"+str(upseconds)
	return upstring

##################################################################################################

# ending handler
def handler(signum, frame):
    print('SIGTERM')
    sys.exit(0)
signal.signal(signal.SIGTERM, handler)
random.seed(time.time())

# put the main image (mainimg) to the display
def imageToDisplay():
	im = mainimg.transpose(Image.ROTATE_90)
	listim = list(im.getdata())
	listim2 = []
	for y in range(0, im.size[1]):
		for x in range(0, im.size[0]/8):
			val = 0
			for x8 in range(0,8):
				if listim[(im.size[1]-y-1)*im.size[0] + x*8 + (7-x8)] > 128:
					val = val | 0x01 << x8
				else:
					pass
			listim2.append(val)
	for x in range(0,1000):
		listim2.append(0)
	ypos = 0
	xpos = 0
	disp.EPD_Dis_Part(xpos, xpos+im.size[0]-1, ypos, ypos+im.size[1]-1, listim2)
	uploadtime = time.time()

##################################################################################################

bus = 0
device = 0
disp = EPD_driver(spi = SPI.SpiDev(bus, device))
print('ben0bi server display script.')
print("by beni @ 19")
print("ben0bi.dlinkddns.com")
print("--> disp size : %dx%d"%(disp.xDot, disp.yDot))

print('------------init and clear full screen------------')
disp.Dis_Clear_full()
disp.delay()

# display part
disp.EPD_init_Part()
disp.delay()
print("..done")

# font for drawing within PIL
myfont10 = ImageFont.truetype("amiga_forever/amiga4ever.ttf", 10)
myfont18 = ImageFont.truetype("amiga_forever/amiga4ever.ttf", 18)
myfont28 = ImageFont.truetype("amiga_forever/amiga4ever.ttf", 28)

# mainimg is used as screen buffer, all image composing/drawing is done in PIL,
# the mainimg is then copied to the display (drawing on the disp itself is no fun)
mainimg = Image.new("1", (296,128))
draw = ImageDraw.Draw(mainimg)

# main loop

actualmin = -1
absoluterefresh = 0

while(1):
	now = datetime.datetime.now()
	# refresh all 10 minutes completely
	if(absoluterefresh > 10):
		absoluterefresh = 0
		disp.Dis_Clear_full()
		disp.delay()
		disp.EPD_init_Part()
		disp.delay()
		actualmin = -1
		print "..done"

	# redraw if minute changes
	if(actualmin != now.minute):
		getServerUpTime()
		print("minute changed %2d:%2d",now.hour, now.minute)
		actualmin = now.minute
		absoluterefresh += 1
		draw.rectangle([0,0,296,128], fill=255)
		drawclock(draw)

		#draw time
		#tstr = "%02d:%02d%02d"%(now.hour,now.minute, now.second)
		# draw the time (digital)
		#tpx = 120
		#tpy = 96
		#draw.text((tpx  , tpy  ), tstr, fill=0, font=myfont28)

		# draw the uptime
		tpx = 120
		tpy = 10
		beserv="Webserver"
		beserv2 = "by beni in 19"
		tup = "Uptime:"

		draw.text((tpx-10, tpy+5), beserv, fill = 0, font = myfont18)
		draw.text((tpx, tpy+25), beserv2, fill = 0, font = myfont10)
		draw.text((tpx+40, tpy+50), tup, fill = 0, font = myfont10)
		draw.text((tpx+40, tpy+70), getServerUpTime(), fill = 0, font = myfont10)

		ref = str(10-absoluterefresh)
		tpx = 260
		tpy = 105
		# draw the refresh count with an outline.
		draw.text((tpx+2, tpy), ref, fill = 0, font = myfont18)
		draw.text((tpx-2, tpy), ref, fill = 0, font = myfont18)
		draw.text((tpx, tpy-2), ref, fill = 0, font = myfont18)
		draw.text((tpx, tpy+2), ref, fill = 0, font = myfont18)

		draw.text((tpx+2, tpy+2), ref, fill = 0, font = myfont18)
		draw.text((tpx+2, tpy-2), ref, fill = 0, font = myfont18)
		draw.text((tpx-2, tpy-2), ref, fill = 0, font = myfont18)
		draw.text((tpx-2, tpy+2), ref, fill = 0, font = myfont18)

		draw.text((tpx, tpy), ref, fill = 255, font = myfont18)

		# double the fun so it is more visible (?)
		imageToDisplay()
		disp.delay()
		imageToDisplay()
		disp.delay()
