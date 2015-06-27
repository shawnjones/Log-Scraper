#!/usr/bin/env python

# This sctipt scrapes logs from qrz.com and outputs as csv.
# It's a hack, it's my first public offering of code, it's ugly.
# Use it, modify it, just please make sure my name is mentioned. Thanks.
# Shawn Jones 2015 | shawnjones20@gmail.com

# Log Liberator v0.1

import unicodecsv
import requests
from bs4 import BeautifulSoup as soup
from ADIF_log import ADIF_log

print"**********************************************"
print"*******     Logbook Liberator v0.1     *******"
print"**********************************************"
print""

_username = raw_input("Username: ")
_password = raw_input("Password: ")
_maxPagesStr = raw_input("Pages: ")

_maxPages = int(_maxPagesStr)

f = open('Logbook.csv', 'w')
adif = ADIF_log("Radio Log Liberator")

payload = {
	'username': _username,
	'password': _password
	}

print""
print"Here we go. Viva la Logbook!!"
print""
	
with requests.Session() as s:
	p = s.post('https://www.qrz.com/login', data=payload)
	#r = s.get('http://logbook.qrz.com')

for i in range(1, _maxPages+1):
    print"Working on page: %s" % i
    getpages = {'page': i }
    r = s.post('http://logbook.qrz.com', data=getpages)		
    data = soup(r.text)
    writer = unicodecsv.writer(f)
    
    table = data.findAll('tr', {'class':'lrow'})
    for i in range(0, len(table)):
        sheet = []
        for row in table[i].findAll("td", {'class':['lpos', 'ldt', 'ltm', 'lde', 'lba', 'lfr', 'lmo', 'lgr', 'lcc', 'lop']}):
            x = row.text
            sheet.append(x)
            
        writer.writerows([sheet])
        ent = adif.newEntry()
        if len(sheet[1].strip()):
          try:
            ent['qso_date'] = sheet[1].strip().replace('-','')
          except:
            pass
        if len(sheet[2].strip()):
          try:
            ent['time_on'] = sheet[2].strip().replace(':','')
          except:
            pass
        if len(sheet[3].strip()):
          try:
            ent['call'] = sheet[3].strip().replace(u'\xd8','0')
          except:
            pass
        if len(sheet[4].strip()):
          try:
            ent['band'] = sheet[4].strip()
          except:
            pass
        if len(sheet[5].strip()):
          try:
            ent['freq'] = sheet[5].strip()
          except:
            pass
        if len(sheet[6].strip()):
          try:
            ent['mode'] = sheet[6].strip()
          except:
            pass
        if len(sheet[7].strip()):
          try:
            ent['gridsquare'] = sheet[7].strip()
          except:
            pass
        if len(sheet[9].strip()):
          try:
            ent['country'] = sheet[9].strip()
          except:
            pass
        if len(sheet[10].strip()):
          try:
            ent['name'] = sheet[10].strip()
          except:
            pass
        if len(sheet[11].strip()):
          try:
            ent['notes'] = sheet[11].strip()
          except:
            try:
              ent['notes_intl'] = sheet[11].strip()
            except:
              pass
f.close()

f = open('Logbook.adf', 'w')
f.write(str(adif))
f.close()

print""
print"Logbook liberated!"
print""
