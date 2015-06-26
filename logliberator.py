#!/usr/bin/env python

# This sctipt scrapes logs from qrz.com and outputs as csv.
# It's a hack, it's my first public offering of code, it's ugly.
# Use it, modify it, just please make sure my name is mentioned. Thanks.
# Shawn Jones 2015 | shawnjones20@gmail.com

# Log Liberator v0.1

import unicodecsv
import requests
from bs4 import BeautifulSoup as soup

print"**********************************************"
print"*******     Logbook Liberator v0.1     *******"
print"**********************************************"
print""

_username = raw_input("Username: ")
_password = raw_input("Password: ")
_maxPagesStr = raw_input("Pages: ")

_maxPages = int(_maxPagesStr)

f = open('Logbook.csv', 'w')

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
f.close()

print""
print"Logbook liberated!"
print""
