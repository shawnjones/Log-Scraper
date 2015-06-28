#!/usr/bin/env python

# This sctipt scrapes logs from qrz.com and outputs as csv.
# It's a hack, it's my first public offering of code, it's ugly.
# Use it, modify it, just please make sure my name is mentioned. Thanks.
# Shawn Jones 2015 | shawnjones20@gmail.com

# Log Liberator v0.1

import re
import requests
from bs4 import BeautifulSoup as soup
from ADIF_log import ADIF_log

def assign_value(entry, name, value):
	if len(value.strip()):
		try:
			entry[name] = value.strip()
		except:
			try:
				entry[name] = value.strip().encode('ascii', 'replace')
			except:
				print("Failed to set value for '"+name.encode('ascii', 'replace')+"' to '"+value.strip().encode('ascii', 'replace')+"'")
				try:
					del entry[name]
				except:
					pass

def assign_call(entry, name, value):
	if value is None:
		return
	value = value.replace(u'\xd8', '0')
	assign_value(entry, name, value)

def str_or_intl(entry, name, value):
	if len(value.strip()):
		try:
			entry[name] = value.strip()
		except:
			assign_value(entry, name+'_intl', value)
			assign_value(entry, name, value)

def get_his_mine(tag):
	td = tag.find('td')
	his = td.next_sibling.next_sibling
	mine = his.next_sibling.next_sibling
	return {'his':his, 'mine':mine}

class Handler(object):
	def Serial(self, ent, tag):
		ld = tag.find('span', text='Log Date:')
		ld = ld.next_sibling.next_sibling
		ld = ld.text[0:10].replace('-','')
		assign_value(ent, 'QRZCOM_QSO_UPLOAD_DATE', ld)

	def QSO_Start(self, ent, tag):
		qs = tag.find('td')
		qs = qs.next_sibling.next_sibling
		qsd = qs.text[0:10].replace('-','')
		qst = qs.text[11:19].replace(':','')
		assign_value(ent, 'QSO_DATE', qsd)
		assign_value(ent, 'TIME_ON', qst)
		# TODO: QRZ Confirmation...

	def QSO_End(self, ent, tag):
		qe = tag.find('td')
		qe = qe.next_sibling.next_sibling
		contest = qe.next_sibling.next_sibling
		qed = qe.text[0:10].replace('-','')
		qet = qe.text[11:19].replace(':','')
		assign_value(ent, 'QSO_DATE_OFF', qed)
		assign_value(ent, 'TIME_OFF', qet)
		# TODO: Contest...

	# TODO: Exchange
	# TODO: Section

	def Station(self, ent, tag):
		st = get_his_mine(tag)
		assign_call(ent, 'call', st['his'].text)
		assign_call(ent, 'operator', st['mine'].text)

	def Op(self, ent, tag):
		op = get_his_mine(tag)
		str_or_intl(ent, 'name', op['his'].text)
		str_or_intl(ent, 'my_name', op['mine'].text)

	def QTH(self, ent, tag):
		qth = get_his_mine(tag)
		str_or_intl(ent, 'qth', qth['his'].text)
		str_or_intl(ent, 'my_city', qth['mine'].text)

	def State(self, ent, tag):
		st = get_his_mine(tag)
		assign_value(ent, 'state', st['his'].text);
		assign_value(ent, 'my_state', st['mine'].text);

	def Country(self, ent, tag):
		cnt = get_his_mine(tag)
		assign_value(ent, 'country', cnt['his'].text);
		assign_value(ent, 'my_country', cnt['mine'].text);

	def Band(self, ent, tag):
		b = get_his_mine(tag)
		band = b['his'].contents[0]
		freq = band.next_sibling.next_sibling
		mode = freq.next_sibling.next_sibling
		assign_value(ent, 'band', band)
		assign_value(ent, 'freq', freq.replace(' MHz', ''))
		assign_value(ent, 'mode', mode)
		my_band = b['mine'].contents[0]
		my_freq = band.next_sibling.next_sibling
		if (my_band != band):
			assign_value(ent, 'band_rx', my_band)
		if (my_freq != freq):
			assign_value(ent, 'freq_rx', my_freq.replace(' MHz', ''))

	def Power(self, ent, tag):
		p = get_his_mine(tag)
		po = p['his'].contents[0]
		rst = po.next_sibling.next_sibling
		if int(po.replace(' W','')) > 0:
			assign_value(ent, 'rx_pwr', po.replace(' W', ''))
		assign_value(ent, 'rst_rcvd', rst)
		po = p['mine'].contents[0]
		rst = po.next_sibling.next_sibling
		if int(po.replace(' W','')) > 0:
			assign_value(ent, 'tx_pwr', po.replace(' W', ''))
		assign_value(ent, 'rst_sent', rst)

	def Coords(self, ent, tag):
		coords = get_his_mine(tag)
		lat = coords['his'].contents[2]
		lon = coords['his'].contents[4]
		latm = re.search('([0-9]+)\.([0-9]+) ([NS])', lat)
		if latm is not None:
			mins = float('0.'+latm.group(2))*60
			assign_value(ent, 'lat', latm.group(3)+'%03u %#06.3f' % (int(latm.group(1)), mins))
		lonm = re.search('([0-9]+)\.([0-9]+) ([EW])', lon)
		if lonm is not None:
			mins = float('0.'+lonm.group(2))*60
			assign_value(ent, 'lon', lonm.group(3)+'%03u %#06.3f' % (int(lonm.group(1)), mins))
		lat = coords['mine'].contents[2]
		lon = coords['mine'].contents[4]
		latm = re.search('([0-9]+)\.([0-9]+) ([NS])', lat)
		if latm is not None:
			mins = float('0.'+latm.group(2))*60
			assign_value(ent, 'my_lat', latm.group(3)+'%03u %#06.3f' % (int(latm.group(1)), mins))
		lonm = re.search('([0-9]+)\.([0-9]+) ([EW])', lon)
		if lonm is not None:
			mins = float('0.'+lonm.group(2))*60
			assign_value(ent, 'my_lon', lonm.group(3)+'%03u %#06.3f' % (int(lonm.group(1)), mins))

	def Grid(self, ent, tag):
		gr = get_his_mine(tag)
		grid = gr['his'].contents[0]
		dist = gr['his'].contents[2]
		assign_value(ent, 'gridsquare', grid)
		km = re.search('([0-9]+) km', dist)
		if km is not None and int(km.group(1)) > 0:
			assign_value(ent, 'distance', km.group(1))
		grid = gr['mine'].contents[0]
		bear = gr['mine'].contents[4]
		assign_value(ent, 'my_gridsquare', grid)
		deg = re.search('([0-9]+)\xb0', bear)
		if deg is not None:
			assign_value(ent, 'ant_az', deg.group(1))

	# TODO: County

	def Continent(self, ent, tag):
		cont = get_his_mine(tag)
		ct = cont['his'].contents[0].strip()[0:2]
		assign_value(ent, 'cont', ct)
		cqz = re.search('[0-9]+', cont['his'].contents[2])
		if cqz is not None:
			assign_value(ent, 'cqz', cqz.group(0))
		cqz = re.search('[0-9]+', cont['mine'].contents[2])
		if cqz is not None:
			assign_value(ent, 'my_cq_zone', cqz.group(0))

	def ITU_Zone(self, ent, tag):
		iz = get_his_mine(tag)
		assign_value(ent, 'ituz', iz['his'].contents[0])
		assign_value(ent, 'iota', iz['his'].contents[2])
		assign_value(ent, 'my_itu_zone', iz['mine'].contents[0])
		assign_value(ent, 'my_iota', iz['mine'].contents[2])

	def QSL_Via(self, ent, tag):
		qsl = get_his_mine(tag)
		assign_value(ent, 'qsl_via', qsl['his'].contents[0])

	# TODO: QSL_Card
	# TODO: eQSL
	# TODO: LoTW

	def Comments(self, ent, tag):
		td = tag.find('td')
		comment = td.next_sibling.next_sibling
		str_or_intl(ent, 'comment', comment.text)

	def Notes(self, ent, tag):
		td = tag.find('td')
		comment = td.next_sibling.next_sibling
		str_or_intl(ent, 'notes', comment.text)

print("**********************************************")
print("*******     Logbook Liberator v0.1     *******")
print("**********************************************")
print("")

_username = raw_input("Username: ")
_password = raw_input("Password: ")

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

print('Getting Book ID(s)')
r = s.post('http://logbook.qrz.com', data={'page':1})
data = soup(r.text)
bookids = []
all_bookids = data.findAll('option', attrs={'id':re.compile('^booksel'),'value':re.compile('^[0-9]+$')})
for id in all_bookids:
	bookids.append(int(id['value']))
print bookids

handler = Handler()

for bookid in bookids:
	adif = ADIF_log("Radio Log Liberator")

	print('Getting total QSOs')
	r = s.post('http://logbook.qrz.com', data={'bookid':bookid})
	data = soup(r.text)
	total_qsos = data.find('input', attrs={'name':'logcount'})
	if total_qsos is None:
		print('Unable to find number of QSOs')
		system.exit(1)
	total_qsos = int(total_qsos['value'])

	print('Fetching '+str(total_qsos)+' from book '+str(bookid))

	for i in range(0, total_qsos):
		print("Working on QSO: %s" % i)
		getpages = {'op':'show', 'bookid':bookid, 'logpos':i};
		r = s.post('http://logbook.qrz.com', data=getpages)
		data = soup(r.text)
		logitem = data.find('div', id='logitem')
		if logitem is None:
			print('Unable to find log item for QSO '+str(i+1))
			continue
		rows = logitem.findAll('tr')
		if len(rows) == 0:
			print('Unable to find QSO details for QSO '+str(i+1))
			continue
		ent = adif.newEntry()
		for j in range(0, len(rows)):
			title = rows[j].find('td')
			if title is None:
				continue
			title_text = title.text.encode('ascii','replace').strip().replace(':','').replace(' ','_')
			if hasattr(handler, title_text):
				getattr(handler, title_text)(ent, rows[j])

	f = open('Logbook-'+str(bookid)+'.adi', 'w')
	f.write(str(adif))
	f.close()

print("")
print("Logbook liberated!")
print("")

