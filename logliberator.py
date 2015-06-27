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

def assign_value(entry, name, value):
    if len(value.strip()):
        try:
            entry[name] = value.strip()
        except:
            try:
                entry[name] = value.encode('ascii', 'replace')
            except:
                try:
                    del entry[name]
                except:
                    pass

def str_or_intl(entry, name, value):
    if len(value.strip()):
        try:
            entry[name] = value.strip()
        except:
            assign_value(entry, name+'_intl', value)
            assign_value(entry, name, value)

print("**********************************************")
print("*******     Logbook Liberator v0.1     *******")
print("**********************************************")
print("")

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

print("")
print("Here we go. Viva la Logbook!!")
print("")
	
with requests.Session() as s:
	p = s.post('https://www.qrz.com/login', data=payload)
	#r = s.get('http://logbook.qrz.com')

for i in range(1, _maxPages+1):
    print("Working on page: %s" % i)
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
        assign_value(ent, 'qso_date', sheet[1].replace('-',''))
        assign_value(ent, 'time_on', sheet[2].replace(':',''))
        assign_value(ent, 'call', sheet[3].replace(u'\xd8','0'))
        assign_value(ent, 'band', sheet[4])
        if sheet[5].strip() != '0.000':
            assign_value(ent, 'freq', sheet[5])
        assign_value(ent, 'mode', sheet[6])
        assign_value(ent, 'gridsquare', sheet[7])
        str_or_intl(ent, 'country', sheet[9])
        str_or_intl(ent, 'name', sheet[10])
        str_or_intl(ent, 'notes', sheet[11])
f.close()

f = open('Logbook.adf', 'w')
f.write(str(adif))
f.close()

print("")
print("Logbook liberated!")
print("")
