# -*- coding: utf-8 -*-

# Copyright (c) 2015, K6BSD
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import re
from xml.sax import make_parser 
from xml.sax.handler import ContentHandler
from xml.sax.saxutils import (escape, quoteattr)

_enumerations = {
	'Ant Path':	{
				 'G': 'grayline',
				 'O': 'other',
				 'S': 'short path',
				 'L': 'long path'
				},
	'ARRL Section': {
				 'AL': 	'Alabama',
				 'AK': 'Alaska',
				 'AB': 'Alberta',
				 'AR': 'Arkansas',
				 'AZ': 'Arizona',
				 'BC': 'British Columbia',
				 'CO': 'Colorado',
				 'CT': 'Connecticut',
				 'DE': 'Delaware',
				 'EB': 'East Bay',
				 'EMA': 'Eastern Massachusetts',
				 'ENY': 'Eastern New York',
				 'EPA': 'Eastern Pennsylvania',
				 'EWA': 'Eastern Washington',
				 'GA': 'Georgia',
				 'ID': 'Idaho',
				 'IL': 'Illinois',
				 'IN': 'Indiana',
				 'IA': 'Iowa',
				 'KS': 'Kansas',
				 'KY': 'Kentucky',
				 'LAX': 'Los Angeles',
				 'LA': 'Louisiana',
				 'ME': 'Maine',
				 'MB': 'Manitoba',
				 'MAR': 'Maritime',
				 'MDC': 'Maryland-DC',
				 'MI': 'Michigan',
				 'MN': 'Minnesota',
				 'MS': 'Mississippi',
				 'MO': 'Missouri',
				 'MT': 'Montana',
				 'NE': 'Nebraska',
				 'NV': 'Nevada',
				 'NH': 'New Hampshire',
				 'NM': 'New Mexico',
				 'NLI': 'New York City-Long Island',
				 'NL': 'Newfoundland/Labrador',
				 'NC': 'North Carolina',
				 'ND': 'North Dakota',
				 'NTX': 'North Texas',
				 'NFL': 'Northern Florida',
				 'NNJ': 'Northern New Jersey',
				 'NNY': 'Northern New York',
				 'NT': 'Northwest Territories/Yukon/Nunavut',
				 'NWT': 'Northwest Territories/Yukon/Nunavut (deprecated; use NT instead)',
				 'OH': 'Ohio',
				 'OK': 'Oklahoma',
				 'ON': 'Ontario',
				 'ORG': 'Orange',
				 'OR': 'Oregon',
				 'PAC': 'Pacific',
				 'PR': 'Puerto Rico',
				 'QC': 'Quebec',
				 'RI': 'Rhode Island',
				 'SV': 'Sacramento Valley',
				 'SDG': 'San Diego',
				 'SF': 'San Francisco',
				 'SJV': 'San Joaquin Valley',
				 'SB': 'Santa Barbara',
				 'SCV': 'Santa Clara Valley',
				 'SK': 'Saskatchewan',
				 'SC': 'South Carolina',
				 'SD': 'South Dakota',
				 'STX': 'South Texas',
				 'SFL': 'Southern Florida',
				 'SNJ': 'Southern New Jersey',
				 'TN': 'Tennessee',
				 'VI': 'US Virgin Islands',
				 'UT': 'Utah',
				 'VT': 'Vermont',
				 'VA': 'Virginia',
				 'WCF': 'West Central Florida',
				 'WTX': 'West Texas',
				 'WV': 'West Virginia',
				 'WMA': 'Western Massachusetts',
				 'WNY': 'Western New York',
				 'WPA': 'Western Pennsylvania',
				 'WWA': 'Western Washington',
				 'WI': 'Wisconsin',
				 'WY': 'Wyoming',
				},
	'Band': {
				 '2190M': '136KHz to 137KHz',
				 '630M': '472KHz to 479KHz',
				 '560M': '501KHz to 504KHz',
				 '160M': '1.8MHz to 2.0MHz',
				 '80M': '3.5MHz to 4.0MHz',
				 '60M': '5.102MHz to 5.4065MHz',
				 '40M': '7.0MHz to 7.3MHz',
				 '30M': '10.0MHz to 10.15MHz',
				 '20M': '14.0MHz to 14.35MHz',
				 '17M': '18.068MHz to 18.168MHz',
				 '15M': '21.0MHz to 21.45MHz',
				 '12M': '24.890MHz to 24.99MHz',
				 '10M': '28.0MHz to 29.7MHz',
				 '6M': '50MHz to 54MHz',
				 '4M': '70MHz to 71MHz',
				 '2M': '144MHz to 148MHz',
				 '1.25M': '222MHz to 225MHz',
				 '70CM': '420MHz to 450MHz',
				 '33CM': '902MHz to 928MHz',
				 '23CM': '1.240GHz to 1.300GHz',
				 '13CM': '2.300GHz to 2.450GHz',
				 '9CM': '3.300GHz to 3.500GHz',
				 '6CM': '5.650GHz to 5.925GHz',
				 '3CM': '10.0GHz to 10.5GHz',
				 '1.25CM': '24.0GHz to 24.250GHz',
				 '6MM': '47.0GHz to 47.2GHz',
				 '4MM': '75.5GHz to 81.0GHz',
				 '2.5MM': '119.98GHz to 120.02GHz',
				 '2MM': '142GHz to 149GHz',
				 '1MM': '241GHz to 250GHz',
				},
	'QSO Upload Status': {
				 'Y':	'the QSO has been uploaded to, and accepted by, the online service',
				 'N': 	'do not upload the QSO to the online service',
				 'M': 	'the QSO has been modified since being uploaded to the online service',
				},
	'Continent': {
				 'NA': 'North America',
				 'SA': 'South America',
				 'EU': 'Europe',
				 'AF': 'Africa',
				 'OC': 'Oceana',
				 'AS': 'Asia',
				 'AN': 'Antarctica',
				},
	'Contest ID': {
				 '070-PSKFEST': 'PODXS PSKFest',
				 '070-VALENTINE-SPRINT': 'PODXS Valentine Sprint',
				 '070-ST-PATS-DAY': 'PODXS St. Patricks Day',
				 '070-31-FLAVORS': 'PODXS 31 Flavors',
				 '070-3-DAY': 'PODXS Three Day Weekend',
				 '070-40M-SPRINT': 'PODXS 40m Firecracker Sprint',
				 '070-80M-SPRINT': 'PODXS 80m Jay Hudak Memorial Sprint',
				 '070-160M-SPRINT': 'PODXS Great Pumpkin Sprint',
				 '10-RTTY': 'Ten-Meter RTTY Contest (2011 onwards)',
				 '1010-OPEN-SEASON': 'Open Season Ten Meter QSO Party',
				 '7QP': '7th-Area QSO Party',
				 'AL-QSO-PARTY': 'Alabama QSO Party',
				 'ALL-ASIAN-DX-CW': 'JARL All Asian DX Contest (CW)',
				 'ALL-ASIAN-DX-PHONE': 'JARL All Asian DX Contest (PHONE)',
				 'ANARTS-RTTY': 'ANARTS WW RTTY',
				 'ANATOLIAN-RTTY': 'Anatolian WW RTTY',
				 'AP-SPRINT': 'Asia - Pacific Sprint',
				 'AR-QSO-PARTY': 'Arkansas QSO Party',
				 'ARI-DX': 'ARI DX Contest',
				 'ARRL-10': 'ARRL 10 Meter Contest',
				 'ARRL-160': 'ARRL 160 Meter Contest',
				 'ARRL-DX-CW': 'ARRL International DX Contest (CW)',
				 'ARRL-DX-SSB': 'ARRL International DX Contest (Phone)',
				 'ARRL-FIELD-DAY': 'ARRL Field Day',
				 'ARRL-RR-CW': 'ARRL Rookie Roundup (CW)',
				 'ARRL-RR-RTTY': 'ARRL Rookie Roundup (RTTY)',
				 'ARRL-RR-SSB': 'ARRL Rookie Roundup (Phone)',
				 'ARRL-RTTY': 'ARRL RTTY Round-Up',
				 'ARRL-SCR': 'ARRL School Club Roundup',
				 'ARRL-SS-CW': 'ARRL November Sweepstakes (CW)',
				 'ARRL-SS-SSB': 'ARRL November Sweepstakes (Phone)',
				 'ARRL-UHF-AUG': 'ARRL August UHF Contest',
				 'ARRL-VHF-JAN': 'ARRL January VHF Sweepstakes',
				 'ARRL-VHF-JUN': 'ARRL June VHF QSO Party',
				 'ARRL-VHF-SEP': 'ARRL September VHF QSO Party',
				 'AZ-QSO-PARTY': 'Arizona QSO Party',
				 'BARTG-RTTY': 'BARTG Spring RTTY Contest',
				 'BARTG-SPRINT': 'BARTG Sprint Contest',
				 'BC-QSO-PARTY': 'British Columbia QSO Party',
				 'CA-QSO-PARTY': 'California QSO Party',
				 'CO-QSO-PARTY': 'Colorado QSO Party',
				 'CQ-160-CW': 'CQ WW 160 Meter DX Contest (CW)',
				 'CQ-160-SSB': 'CQ WW 160 Meter DX Contest (SSB)',
				 'CQ-M': 'CQ-M International DX Contest',
				 'CQ-VHF': 'CQ World-Wide VHF Contest',
				 'CQ-WPX-CW': 'CQ WW WPX Contest (CW)',
				 'CQ-WPX-RTTY': 'CQ/RJ WW RTTY WPX Contest',
				 'CQ-WPX-SSB': 'CQ WW WPX Contest (SSB)',
				 'CQ-WW-CW': 'CQ WW DX Contest (CW)',
				 'CQ-WW-RTTY': 'CQ/RJ WW RTTY DX Contest',
				 'CQ-WW-SSB': 'CQ WW DX Contest (SSB)',
				 'CWOPS-CWT': 'CWops Mini-CWT Test',
				 'CIS-DX': 'CIS DX Contest',
				 'CT-QSO-PARTY': 'Connecticut QSO Party',
				 'CVA-DX-CW': 'Concurso Verde e Amarelo DX CW Contest',
				 'CVA-DX-SSB': 'Concurso Verde e Amarelo DX CW Contest',
				 'DARC-WAEDC-CW': 'WAE DX Contest (CW)',
				 'DARC-WAEDC-RTTY': 'WAE DX Contest (RTTY)',
				 'DARC-WAEDC-SSB': 'WAE DX Contest (SSB)',
				 'DARC-WAG': 'DARC Worked All Germany',
				 'DE-QSO-PARTY': 'Delaware QSO Party',
				 'DL-DX-RTTY': 'DL-DX RTTY Contest',
				 'DMC-RTTY': 'DMC RTTY Contest',
				 'EA-CNCW': u'Concurso Nacional de Telegrafía',
				 'EA-DME': u'Municipios Españoles',
				 'EA-PSK63': 'EA PSK63',
				 'EA-RTTY': 'Unión de Radioaficionados Españoles RTTY Contest',
				 'EA-SMRE-CW': 'Su Majestad El Rey de España - CW',
				 'EA-SMRE-SSB': 'Su Majestad El Rey de España - SSB',
				 'EA-VHF-ATLANTIC': 'Atlántico V-UHF',
				 'EA-VHF-COM': 'Combinado de V-UHF',
				 'EA-VHF-COSTA-SOL': 'Costa del Sol V-UHF',
				 'EA-VHF-EA': 'Nacional VHF',
				 'EA-VHF-EA1RCS': 'Segovia EA1RCS V-UHF',
				 'EA-VHF-QSL': 'QSL V-UHF & 50MHz',
				 'EA-VHF-SADURNI': 'Sant Sadurni V-UHF',
				 'EA-WW-RTTY': 'Unión de Radioaficionados Españoles RTTY Contest',
				 'EPC-PSK63': 'PSK63 QSO Party',
				 'EU': 'Sprint 	EU Sprint',
				 'EUCW160M': 'European CW Association 160m CW Party',
				 'EU-HF': 'EU HF Championship',
				 'EU-PSK-DX': 'EU PSK DX Contest',
				 'Fall': 'Sprint 	FISTS Fall Sprint',
				 'FL-QSO-PARTY': 'Florida QSO Party',
				 'GA-QSO-PARTY': 'Georgia QSO Party',
				 'HELVETIA': 'Helvetia Contest',
				 'HI-QSO-PARTY': 'Hawaiian QSO Party',
				 'HOLYLAND': 'IARC Holyland Contest',
				 'IARU-FIELD-DAY': 'DARC IARU Region 1 Field Day',
				 'IARU-HF': 'IARU HF World Championship',
				 'IA-QSO-PARTY': 'Iowa QSO Party',
				 'ID-QSO-PARTY': 'Idaho QSO Party',
				 'IL': 'QSO Party 	Illinois QSO Party',
				 'IN-QSO-PARTY': 'Indiana QSO Party',
				 'JARTS-WW-RTTY': 'JARTS WW RTTY',
				 'JIDX-CW': 'Japan International DX Contest (CW)',
				 'JIDX-SSB': 'Japan International DX Contest (SSB)',
				 'JT-DX-RTTY': 'Mongolian RTTY DX Contest',
				 'KS-QSO-PARTY': 'Kansas QSO Party',
				 'KY-QSO-PARTY': 'Kentucky QSO Party',
				 'LA-QSO-PARTY': 'Louisiana QSO Party',
				 'LDC-RTTY': 'DRCG Long Distance Contest (RTTY)',
				 'LZ': 'DX 	LZ DX Contest',
				 'MAR-QSO-PARTY': 'Maritimes QSO Party',
				 'MI-QSO-PARTY': 'Michigan QSO Party',
				 'MIDATLANTIC-QSO-PARTY': 'Mid-Atlantic QSO Party',
				 'MD-QSO-PARTY': 'Maryland QSO Party',
				 'ME-QSO-PARTY': 'Maine QSO Party',
				 'MI-QSO-PARTY': 'Michigan QSO Party',
				 'MN-QSO-PARTY': 'Minnesota QSO Party',
				 'MO-QSO-PARTY': 'Missouri QSO Party',
				 'MS-QSO-PARTY': 'Mississippi QSO Party',
				 'MT-QSO-PARTY': 'Montana QSO Party',
				 'NAQP-CW': 'North America QSO Party (CW)',
				 'NAQP-RTTY': 'North America QSO Party (RTTY)',
				 'NAQP-SSB': 'North America QSO Party (Phone)',
				 'NA-SPRINT-CW': 'North America Sprint (CW)',
				 'NA-SPRINT-RTTY': 'North America Sprint (RTTY)',
				 'NA-SPRINT-SSB': 'North America Sprint (Phone)',
				 'NEQP': 'New England QSO Party',
				 'NC-QSO-PARTY': 'North Carolina QSO Party',
				 'ND-QSO-PARTY': 'North Dakota QSO Party',
				 'NE-QSO-PARTY': 'Nebraska QSO Party',
				 'NH-QSO-PARTY': 'New Hampshire QSO Party',
				 'NJ-QSO-PARTY': 'New Jersey QSO Party',
				 'NM-QSO-PARTY': 'New Mexico QSO Party',
				 'NRAU-BALTIC-CW': 'NRAU-Baltic Contest (CW)',
				 'NRAU-BALTIC-SSB': 'NRAU-Baltic Contest (SSB)',
				 'NV-QSO-PARTY': 'Nevada QSO Party',
				 'NY-QSO-PARTY': 'New York QSO Party',
				 'OCEANIA-DX-CW': 'Oceania DX Contest (CW)',
				 'OCEANIA-DX-SSB': 'Oceania DX Contest (SSB)',
				 'OH-QSO-PARTY': 'Ohio QSO Party',
				 'OK-DX-RTTY': 'Czech Radio Club OK DX Contest',
				 'OK-OM-DX': 'Czech Radio Club OK-OM DX Contest',
				 'OK-QSO-PARTY': 'Oklahoma QSO Party',
				 'OMISS-QSO-PARTY': 'Old Man International Sideband Society QSO Party',
				 'ON-QSO-PARTY': 'Ontario QSO Party',
				 'OR-QSO-PARTY': 'Oregon QSO Party',
				 'PACC': 'Dutch PACC Contest',
				 'PA-QSO-PARTY': 'Pennsylvania QSO Party',
				 'PSK-DEATHMATCH': 'MDXA PSK DeathMatch (2005-2010)',
				 'QC-QSO-PARTY': 'Quebec QSO Party',
				 'RAC': 'Canadian Amateur Radio Society Contest',
				 'RAC-CANADA-DAY': 'Canadian Amateur Radio Society Canada Day Contest',
				 'RAC-CANADA-WINTER': 'Canadian Amateur Radio Society Canada Winter Contest',
				 'RDAC': 'Russian District Award Contest',
				 'RDXC': 'Russian DX Contest',
				 'REF-160M': 'Reseau des Emetteurs Francais 160m Contest',
				 'REF-CW': 'Reseau des Emetteurs Francais Contest (CW)',
				 'REF-SSB': 'Reseau des Emetteurs Francais Contest (SSB)',
				 'RI-QSO-PARTY': 'Rhode Island QSO Party',
				 'RSGB-160': '1.8Mhz Contest',
				 'RSGB-21/28-CW': '21/28 MHz Contest (CW)',
				 'RSGB-21/28-SSB': '21/28 MHz Contest (SSB)',
				 'RSGB-80M-CC': '80m Club Championships',
				 'RSGB-AFS-CW': 'Affiliated Societies Team Contest (CW)',
				 'RSGB-AFS-SSB': 'Affiliated Societies Team Contest (SSB)',
				 'RSGB-CLUB-CALLS': 'Club Calls',
				 'RSGB-COMMONWEALTH': 'Commonwealth Contest',
				 'RSGB-IOTA': 'IOTA Contest',
				 'RSGB-LOW-POWER': 'Low Power Field Day',
				 'RSGB-NFD': 'National Field Day',
				 'RSGB-ROPOCO': 'RoPoCo',
				 'RSGB-SSB-FD': 'SSB Field Day',
				 'RUSSIAN-RTTY': 'Russian Radio RTTY Worldwide Contest',
				 'SAC-CW': 'Scandinavian Activity Contest (CW)',
				 'SAC-SSB': 'Scandinavian Activity Contest (SSB)',
				 'SARTG-RTTY': 'SARTG WW RTTY',
				 'SCC-RTTY': 'SCC RTTY Championship',
				 'SC-QSO-PARTY': 'South Carolina QSO Party',
				 'SD-QSO-PARTY': 'South Dakota QSO Party',
				 'SMP-AUG': 'SSA Portabeltest',
				 'SMP-MAY': 'SSA Portabeltest',
				 'SPAR-WINTER-FD': 'SPAR Winter Field Day',
				 'SPDXContest': 'SP DX Contest',
				 'SP-DX-RTTY': 'PRC SPDX Contest (RTTY)',
				 'Spring': 'Sprint 	FISTS Spring Sprint',
				 'SR-MARATHON': 'Scottish-Russian Marathon',
				 'STEW-PERRY': 'Stew Perry Topband Distance Challenge',
				 'Summer': 'Sprint 	FISTS Summer Sprint',
				 'TARA-GRID-DIP': 'TARA Grid Dip PSK-RTTY Shindig',
				 'TARA-RTTY': 'TARA RTTY Mêlée',
				 'TARA-RUMBLE': 'TARA Rumble PSK Contest',
				 'TARA-SKIRMISH': 'TARA Skirmish Digital Prefix Contest',
				 'TEN-RTTY': 'Ten-Meter RTTY Contest (before 2011)',
				 'TMC-RTTY': 'The Makrothen Contest',
				 'TN-QSO-PARTY': 'Tennessee QSO Party',
				 'TX-QSO-PARTY': 'Texas QSO Party',
				 'UBA-DX-CW': 'UBA Contest (CW)',
				 'UBA-DX-SSB': 'UBA Contest (SSB)',
				 'UK-DX-BPSK63': 'European PSK Club BPSK63 Contest',
				 'UK-DX-RTTY': 'UK DX RTTY Contest',
				 'UKRAINIAN': 'DX 	Ukrainian DX',
				 'UKR-CHAMP-RTTY': 'Open Ukraine RTTY Championship',
				 'UKSMG-6M-MARATHON': 'UKSMG 6m Marathon',
				 'UKSMG-SUMMER-ES': 'UKSMG Summer Es Contest',
				 'URE-DX': 'Ukrainian DX Contest',
				 'US-COUNTIES-QSO': 'Mobile Amateur Awards Club',
				 'UT-QSO-PARTY': 'Utah QSO Party',
				 'VENEZ-IND-DAY': 'RCV Venezuelan Independence Day Contest',
				 'Virginia': 'QSO Party 	Virginia QSO Party',
				 'VA-QSO-PARTY': 'Virginia QSO Party',
				 'VOLTA-RTTY': 'Alessandro Volta RTTY DX Contest',
				 'WA-QSO-PARTY': 'Washington QSO Party',
				 'WI-QSO-PARTY': 'Wisconsin QSO Party',
				 'WV-QSO-PARTY': 'West Virginia QSO Party',
				 'WY-QSO-PARTY': 'Wyoming QSO Party',
				 'Winter': 'Sprint 	FISTS Winter Sprint',
				 'XE-INTL-RTTY': 'Mexico International Contest (RTTY)',
				 'YUDXC': 'YU DX Contest',
				},
	'Credit': {
				 'CQDX': 'CQDX',
				 'CQDX_BAND': 'CQDX_BAND',
				 'CQDX_MODE': 'CQDX_MODE',
				 'CQDX_MOBILE': 'CQDX_MOBILE',
				 'CQDX_QRP': 'CQDX_QRP',
				 'CQDX_SATELLITE': 'CQDX_SATELLITE',
				 'CQDXFIELD': 'CQDXFIELD',
				 'CQDXFIELD_BAND': 'CQDXFIELD_BAND',
				 'CQDXFIELD_MODE': 'CQDXFIELD_MODE',
				 'CQDXFIELD_MOBILE': 'CQDXFIELD_MOBILE',
				 'CQDXFIELD_QRP': 'CQDXFIELD_QRP',
				 'CQDXFIELD_SATELLITE': 'CQDXFIELD_SATELLITE',
				 'CQWAZ_MIXED': 'CQWAZ_MIXED',
				 'CQWAZ_BAND': 'CQWAZ_BAND',
				 'CQWAZ_MODE': 'CQWAZ_MODE',
				 'CQWAZ_SATELLITE': 'CQWAZ_SATELLITE',
				 'CQWAZ_EME': 'CQWAZ_EME',
				 'CQWAZ_MOBILE': 'CQWAZ_MOBILE',
				 'CQWAZ_QRP': 'CQWAZ_QRP',
				 'CQWPX': 'CQWPX',
				 'CQWPX_BAND': 'CQWPX_BAND',
				 'CQWPX_MODE': 'CQWPX_MODE',
				 'DXCC': 'DXCC',
				 'DXCC_BAND': 'DXCC_BAND',
				 'DXCC_MODE': 'DXCC_MODE',
				 'DXCC_SATELLITE': 'DXCC_SATELLITE',
				 'IOTA': 'IOTA',
				 'RDA': 'RDA',
				 'USACA': 'USACA',
				 'VUCC_BAND': 'VUCC_BAND',
				 'VUCC_SATELLITE': 'VUCC_SATELLITE',
				 'WAB': 'WAB',
				 'WAC': 'WAC',
				 'WAC_BAND': 'WAC_BAND',
				 'WAE': 'WAE',
				 'WAE_BAND': 'WAE_BAND',
				 'WAE_MODE': 'WAE_MODE',
				 'WAIP': 'WAIP',
				 'WAIP_BAND': 'WAIP_BAND',
				 'WAIP_MODE': 'WAIP_MODE',
				 'WAS': 'WAS',
				 'WAS_BAND': 'WAS_BAND',
				 'WAS_MODE': 'WAS_MODE',
				 'WAS_SATELLITE': 'WAS_SATELLITE',
				},
	'Country Code': {
				 '1': "CANADA",
				 '2': "ABU AIL IS (Deleted)",
				 '3': "AFGHANISTAN",
				 '4': "AGALEGA & ST BRANDON",
				 '5': "ALAND IS",
				 '6': "ALASKA",
				 '7': "ALBANIA",
				 '8': "ALDABRA (Deleted)",
				 '9': "AMERICAN SAMOA",
				 '10': "AMSTERDAM & ST PAUL",
				 '11': "ANDAMAN & NICOBAR IS",
				 '12': "ANGUILLA",
				 '13': "ANTARCTICA",
				 '14': "ARMENIA",
				 '15': "ASIATIC RUSSIA",
				 '16': "AUCKLAND & CAMPBELL",
				 '17': "AVES ISLAND",
				 '18': "AZERBAIJAN",
				 '19': "BAJO NUEVO (Deleted)",
				 '20': "BAKER, HOWLAND IS",
				 '21': "BALEARIC IS",
				 '22': "PALAU",
				 '23': "BLENHEIM REEF (Deleted)",
				 '24': "BOUVET",
				 '25': "BRITISH N. BORNEO (Deleted)",
				 '26': "BRITISH SOMALI (Deleted)",
				 '27': "BELARUS",
				 '28': "CANAL ZONE (Deleted)",
				 '29': "CANARY IS",
				 '30': "CELEBE/MOLUCCA IS (Deleted)",
				 '31': "C KIRIBATI",
				 '32': "CEUTA & MELILLA",
				 '33': "CHAGOS",
				 '34': "CHATHAM IS",
				 '35': "CHRISTMAS IS",
				 '36': "CLIPPERTON IS",
				 '37': "COCOS ISLAND",
				 '38': "COCOS-KEELING IS",
				 '39': "COMOROS (Deleted)",
				 '40': "CRETE",
				 '41': "CROZET",
				 '42': "DAMAO, DUI (Deleted)",
				 '43': "DESECHEO IS",
				 '44': "DESROCHES (Deleted)",
				 '45': "DODECANESE",
				 '46': "EAST MALAYSIA",
				 '47': "EASTER IS",
				 '48': "EASTERN KIRIBATI",
				 '49': "EQUATORIAL GUINEA",
				 '50': "MEXICO",
				 '51': "ERITREA",
				 '52': "ESTONIA",
				 '53': "ETHIOPIA",
				 '54': "EUROPEAN RUSSIA",
				 '55': "FARQUHAR (Deleted)",
				 '56': "FERNANDO DE NORONHA",
				 '57': "FRENCH EQ. AFRICA (Deleted)",
				 '58': "FRENCH INDO-CHINA (Deleted)",
				 '59': "FRENCH WEST AFRICA (Deleted)",
				 '60': "BAHAMAS",
				 '61': "FRANZ JOSEF LAND",
				 '62': "BARBADOS",
				 '63': "FRENCH GUIANA",
				 '64': "BERMUDA",
				 '65': "BRITISH VIRGIN IS",
				 '66': "BELIZE",
				 '67': "FRENCH INDIA (Deleted)",
				 '68': "SAUDI/KUWAIT N.Z. (Deleted)",
				 '69': "CAYMAN ISLANDS",
				 '70': "CUBA",
				 '71': "GALAPAGOS",
				 '72': "DOMINICAN REPUBLIC",
				 '74': "EL SALVADOR",
				 '75': "GEORGIA",
				 '76': "GUATEMALA",
				 '77': "GRENADA",
				 '78': "HAITI",
				 '79': "GUADELOUPE",
				 '80': "HONDURAS",
				 '81': "GERMANY (Deleted)",
				 '82': "JAMAICA",
				 '84': "MARTINIQUE",
				 '85': "BONAIRE,CURACAO (Deleted)",
				 '86': "NICARAGUA",
				 '88': "PANAMA",
				 '89': "TURKS & CAICOS IS",
				 '90': "TRINIDAD & TOBAGO",
				 '91': "ARUBA",
				 '93': "GEYSER REEF (Deleted)",
				 '94': "ANTIGUA & BARBUDA",
				 '95': "DOMINICA",
				 '96': "MONTSERRAT",
				 '97': "ST LUCIA",
				 '98': "ST VINCENT",
				 '99': "GLORIOSO IS",
				 '100': "ARGENTINA",
				 '101': "GOA (Deleted)",
				 '102': "GOLD COAST, TOGOLAND (Deleted)",
				 '103': "GUAM",
				 '104': "BOLIVIA",
				 '105': "GUANTANAMO BAY",
				 '106': "GUERNSEY",
				 '107': "GUINEA",
				 '108': "BRAZIL",
				 '109': "GUINEA-BISSAU",
				 '110': "HAWAII",
				 '111': "HEARD IS",
				 '112': "CHILE",
				 '113': "IFNI (Deleted)",
				 '114': "ISLE OF MAN",
				 '115': "ITALIAN SOMALI (Deleted)",
				 '116': "COLOMBIA",
				 '117': "ITU HQ",
				 '118': "JAN MAYEN",
				 '119': "JAVA (Deleted)",
				 '120': "ECUADOR",
				 '122': "JERSEY",
				 '123': "JOHNSTON IS",
				 '124': "JUAN DE NOVA",
				 '125': "JUAN FERNANDEZ",
				 '126': "KALININGRAD",
				 '127': "KAMARAN IS (Deleted)",
				 '128': "KARELO-FINN REP (Deleted)",
				 '129': "GUYANA",
				 '130': "KAZAKHSTAN",
				 '131': "KERGUELEN",
				 '132': "PARAGUAY",
				 '133': "KERMADEC",
				 '134': "KINGMAN REEF",
				 '135': "KYRGYZSTAN",
				 '136': "PERU",
				 '137': "REPUBLIC OF KOREA",
				 '138': "KURE ISLAND",
				 '139': "KURIA MURIA IS (Deleted)",
				 '140': "SURINAME",
				 '141': "FALKLAND IS",
				 '142': "LAKSHADWEEP ISLANDS",
				 '143': "LAOS",
				 '144': "URUGUAY",
				 '145': "LATVIA",
				 '146': "LITHUANIA",
				 '147': "LORD HOWE IS",
				 '148': "VENEZUELA",
				 '149': "AZORES",
				 '150': "AUSTRALIA",
				 '151': "MALYJ VYSOTSKIIS (Deleted)",
				 '152': "MACAO",
				 '153': "MACQUARIE IS",
				 '154': "YEMEN ARAB REP (Deleted)",
				 '155': "MALAYA (Deleted)",
				 '157': "NAURU",
				 '158': "VANUATU",
				 '159': "MALDIVES",
				 '160': "TONGA",
				 '161': "MALPELO IS",
				 '162': "NEW CALEDONIA",
				 '163': "PAPUA NEW GUINEA",
				 '164': "MANCHURIA (Deleted)",
				 '165': "MAURITIUS IS",
				 '166': "MARIANA IS",
				 '167': "MARKET REEF",
				 '168': "MARSHALL IS",
				 '169': "MAYOTTE",
				 '170': "NEW ZEALAND",
				 '171': "MELLISH REEF",
				 '172': "PITCAIRN IS",
				 '173': "MICRONESIA",
				 '174': "MIDWAY IS",
				 '175': "FRENCH POLYNESIA",
				 '176': "FIJI",
				 '177': "MINAMI TORISHIMA",
				 '178': "MINERVA REEF (Deleted)",
				 '179': "MOLDOVA",
				 '180': "MOUNT ATHOS",
				 '181': "MOZAMBIQUE",
				 '182': "NAVASSA IS",
				 '183': "NETHERLANDS BORNEO (Deleted)",
				 '184': "NETHERLANDS N GUINEA (Deleted)",
				 '185': "SOLOMON ISLANDS",
				 '186': "NEWFOUNDLAND, LABRADOR (Deleted)",
				 '187': "NIGER",
				 '188': "NIUE",
				 '189': "NORFOLK IS",
				 '190': "SAMOA",
				 '191': "N COOK IS",
				 '192': "OGASAWARA",
				 '193': "OKINAWA (Deleted)",
				 '194': "OKINO TORI-SHIMA (Deleted)",
				 '195': "ANNOBON I.",
				 '196': "PALESTINE (Deleted)",
				 '197': "PALMYRA & JARVIS IS",
				 '198': "PAPUA TERR (Deleted)",
				 '199': "PETER I IS",
				 '200': "PORTUGUESE TIMOR (Deleted)",
				 '201': "PRINCE EDWARD & MARION",
				 '202': "PUERTO RICO",
				 '203': "ANDORRA",
				 '204': "REVILLAGIGEDO",
				 '205': "ASCENSION ISLAND",
				 '206': "AUSTRIA",
				 '207': "RODRIGUEZ IS",
				 '208': "RUANDA-URUNDI (Deleted)",
				 '209': "BELGIUM",
				 '210': "SAAR (Deleted)",
				 '211': "SABLE ISLAND",
				 '212': "BULGARIA",
				 '213': "SAINT MARTIN",
				 '214': "CORSICA",
				 '215': "CYPRUS",
				 '216': "SAN ANDRES & PROVIDENCIA",
				 '217': "SAN FELIX",
				 '218': "CZECHOSLOVAKIA (Deleted)",
				 '219': "SAO TOME & PRINCIPE",
				 '220': "SARAWAK (Deleted)",
				 '221': "DENMARK",
				 '222': "FAROE IS",
				 '223': "ENGLAND",
				 '224': "FINLAND",
				 '225': "SARDINIA",
				 '226': "SAUDI/IRAQ N.Z. (Deleted)",
				 '227': "FRANCE",
				 '228': "SERRANA BANK & RONCADOR CAY (Deleted)",
				 '229': "GERMAN DEM. REP. (Deleted)",
				 '230': "FED REP OF GERMANY",
				 '231': "SIKKIM (Deleted)",
				 '232': "SOMALIA",
				 '233': "GIBRALTAR",
				 '234': "S COOK IS",
				 '235': "SOUTH GEORGIA IS",
				 '236': "GREECE",
				 '237': "GREENLAND",
				 '238': "SOUTH ORKNEY IS",
				 '239': "HUNGARY",
				 '240': "SOUTH SANDWICH ISLANDS",
				 '241': "SOUTH SHETLAND ISLANDS",
				 '242': "ICELAND",
				 '243': "DEM REP OF YEMEN (Deleted)",
				 '244': "SOUTHERN SUDAN (Deleted)",
				 '245': "IRELAND",
				 '246': "SOV MILITARY ORDER OF MALTA",
				 '247': "SPRATLY IS",
				 '248': "ITALY",
				 '249': "ST KITTS & NEVIS",
				 '250': "ST HELENA IS",
				 '251': "LIECHTENSTEIN",
				 '252': "ST PAUL ISLAND",
				 '253': "ST. PETER & ST. PAUL ROCKS",
				 '254': "LUXEMBOURG",
				 '255': "SINT MAARTEN, SABA, ST EUSTATIUS (Deleted)",
				 '256': "MADEIRA IS",
				 '257': "MALTA",
				 '258': "SUMATRA (Deleted)",
				 '259': "SVALBARD IS",
				 '260': "MONACO",
				 '261': "SWAN ISLAND (Deleted)",
				 '262': "TAJIKISTAN",
				 '263': "NETHERLANDS",
				 '264': "TANGIER (Deleted)",
				 '265': "NORTHERN IRELAND",
				 '266': "NORWAY",
				 '267': "TERR NEW GUINEA (Deleted)",
				 '268': "TIBET (Deleted)",
				 '269': "POLAND",
				 '270': "TOKELAU IS",
				 '271': "TRIESTE (Deleted)",
				 '272': "PORTUGAL",
				 '273': "TRINDADE & MARTIN VAZ ISLANDS",
				 '274': "TRISTAN DA CUNHA & GOUGH IS",
				 '275': "ROMANIA",
				 '276': "TROMELIN",
				 '277': "ST PIERRE & MIQUELON",
				 '278': "SAN MARINO",
				 '279': "SCOTLAND",
				 '280': "TURKMENISTAN",
				 '281': "SPAIN",
				 '282': "TUVALU",
				 '283': "UK BASES ON CYPRUS",
				 '284': "SWEDEN",
				 '285': "US VIRGIN ISLANDS",
				 '286': "UGANDA",
				 '287': "SWITZERLAND",
				 '288': "UKRAINE",
				 '289': "UNITED NATIONS HQ",
				 '291': "UNITED STATES",
				 '292': "UZBEKISTAN",
				 '293': "VIETNAM",
				 '294': "WALES",
				 '295': "VATICAN",
				 '296': "SERBIA",
				 '297': "WAKE IS",
				 '298': "WALLIS & FUTUNA",
				 '299': "WEST MALAYSIA",
				 '301': "W KIRIBATI",
				 '302': "WESTERN SAHARA",
				 '303': "WILLIS IS",
				 '304': "BAHRAIN",
				 '305': "BANGLADESH",
				 '306': "BHUTAN",
				 '307': "ZANZIBAR (Deleted)",
				 '308': "COSTA RICA",
				 '309': "MYANMAR",
				 '312': "CAMBODIA",
				 '315': "SRI LANKA",
				 '318': "CHINA",
				 '321': "HONG KONG",
				 '324': "INDIA",
				 '327': "INDONESIA",
				 '330': "IRAN",
				 '333': "IRAQ",
				 '336': "ISRAEL",
				 '339': "JAPAN",
				 '342': "JORDAN",
				 '344': "DEMOCRATIC PEOPLE'S REPUBLIC OF KOREA",
				 '345': "BRUNEI",
				 '348': "KUWAIT",
				 '354': "LEBANON",
				 '363': "MONGOLIA",
				 '369': "NEPAL",
				 '370': "OMAN",
				 '372': "PAKISTAN",
				 '375': "PHILIPPINES",
				 '376': "QATAR",
				 '378': "SAUDI ARABIA",
				 '379': "SEYCHELLES",
				 '381': "SINGAPORE",
				 '382': "DJIBOUTI",
				 '384': "SYRIA",
				 '386': "TAIWAN",
				 '387': "THAILAND",
				 '390': "TURKEY",
				 '391': "UNITED ARAB EMIRATES",
				 '400': "ALGERIA",
				 '401': "ANGOLA",
				 '402': "BOTSWANA",
				 '404': "BURUNDI",
				 '406': "CAMEROON",
				 '408': "CENTRAL AFRICAN REPUBLIC",
				 '409': "CAPE VERDE",
				 '410': "CHAD",
				 '411': "COMOROS",
				 '412': "REPUBLIC OF THE CONGO",
				 '414': "DEM. REPUBLIC OF THE CONGO",
				 '416': "BENIN",
				 '420': "GABON",
				 '422': "THE GAMBIA",
				 '424': "GHANA",
				 '428': "COTE D'IVOIRE",
				 '430': "KENYA",
				 '432': "LESOTHO",
				 '434': "LIBERIA",
				 '436': "LIBYA",
				 '438': "MADAGASCAR",
				 '440': "MALAWI",
				 '442': "MALI",
				 '444': "MAURITANIA",
				 '446': "MOROCCO",
				 '450': "NIGERIA",
				 '452': "ZIMBABWE",
				 '453': "REUNION",
				 '454': "RWANDA",
				 '456': "SENEGAL",
				 '458': "SIERRA LEONE",
				 '460': "ROTUMA IS",
				 '462': "REPUBLIC OF SOUTH AFRICA",
				 '464': "NAMIBIA",
				 '466': "SUDAN",
				 '468': "SWAZILAND",
				 '470': "TANZANIA",
				 '474': "TUNISIA",
				 '478': "EGYPT",
				 '480': "BURKINA-FASO",
				 '482': "ZAMBIA",
				 '483': "TOGO",
				 '488': "WALVIS BAY (Deleted)",
				 '489': "CONWAY REEF",
				 '490': "BANABA ISLAND",
				 '492': "YEMEN",
				 '493': "PENGUIN ISLANDS (Deleted)",
				 '497': "CROATIA",
				 '499': "SLOVENIA",
				 '501': "BOSNIA-HERZEGOVINA",
				 '502': "MACEDONIA",
				 '503': "CZECH REPUBLIC",
				 '504': "SLOVAK REPUBLIC",
				 '505': "PRATAS IS",
				 '506': "SCARBOROUGH REEF",
				 '507': "TEMOTU PROVINCE",
				 '508': "AUSTRAL IS",
				 '509': "MARQUESAS IS",
				 '510': "PALESTINE",
				 '511': "TIMOR-LESTE",
				 '512': "CHESTERFIELD IS",
				 '513': "DUCIE IS",
				 '514': "MONTENEGRO",
				 '515': "SWAINS ISLAND",
				 '516': "ST. BARTHELEMY",
				 '517': "CURACAO",
				 '518': "SINT MAARTEN",
				 '519': "ST EUSTATIUS AND SABA",
				 '520': "BONAIRE",
				 '521': "SOUTH SUDAN",
				},
	'QSL Rcvd': {
				 'Y': 'yes (confirmed)',
				 'N': 'no',
				 'R': 'requested',
				 'I': 'ignore or invalid',
				 'V': 'verified (deprecated)',
				},
	'QSL Sent': {
				 'Y': 'yes (confirmed)',
				 'N': 'no',
				 'R': 'requested',
				 'Q': 'queued',
				 'I': 'ignore or invalid',
				},
	'Mode':		{
				 'AM': 'AM',
				 'ATV': 'ATV',
				 'CHIP': 'CHIP64, CHIP128',
				 'CLO': 'CLO',
				 'CONTESTI': 'CONTESTI',
				 'CW': 'PCW',
				 'DIGITALVOICE': 'DIGITALVOICE',
				 'DOMINO': 'DOMINOEX, DOMINOF',
				 'DSTAR': 'DSTAR',
				 'FAX': 'FAX',
				 'FM': 'FM',
				 'FSK441': 'FSK441',
				 'HELL': 'FMHELL, FSKHELL, HELL80, HFSK, PSKHELL',
				 'ISCAT': 'ISCAT-A, ISCAT-B',
				 'JT4': 'JT4A, JT4B, JT4C, JT4D, JT4E, JT4F, JT4G',
				 'JT6M': 'JT6M',
				 'JT9': 'JT9-1, JT9-2, JT9-5, JT9-10, JT9-30',
				 'JT44': 'JT44',
				 'JT65': 'JT65A, JT65B, JT65B2, JT65C, JT65C2',
				 'MFSK': 'MFSK4, MFSK8, MFSK11, MFSK16, MFSK22, MFSK31, MFSK32, MFSK64, MFSK128',
				 'MT63': 'MT63',
				 'OLIVIA': 'OLIVIA 4/125, OLIVIA 4/250, OLIVIA 8/250, OLIVIA 8/500, OLIVIA 16/500, OLIVIA 16/1000, OLIVIA 32/1000',
				 'OPERA': 'OPERA-BEACON, OPERA-QSO',
				 'PAC': 'PAC2, PAC3, PAC4',
				 'PAX': 'PAX2',
				 'PKT': 'PKT',
				 'PSK': 'FSK31, PSK10, PSK31, PSK63, PSK63F, PSK125, PSK250, PSK500, PSK1000, PSKAM10, PSKAM31, PSKAM50, PSKFEC31, QPSK31, QPSK63, QPSK125, QPSK250, QPSK500',
				 'PSK2K': 'PSK2K',
				 'Q15': 'Q15',
				 'ROS': 'ROS-EME, ROS-HF, ROS-MF',
				 'RTTY': 'ASCI',
				 'RTTYM': 'RTTYM',
				 'SSB': 'LSB, USB',
				 'SSTV': 'SSTV',
				 'THOR': 'THOR',
				 'THRB': 'THRBX',
				 'TOR': 'AMTORFEC, GTOR',
				 'V4': 'V4',
				 'VOI': 'VOI',
				 'WINMOR': 'WINMOR',
				 'WSPR': 'WSPR',
				 'AMTORFEC': 'AMTORFEC (deprecated)',
				 'ASCI': 'ASCI (deprecated)',
				 'CHIP64': 'CHIP64 (deprecated)',
				 'CHIP128': 'CHIP128 (deprecated)',
				 'DOMINOF': 'DOMINOF (deprecated)',
				 'FMHELL': 'FMHELL (deprecated)',
				 'FSK31': 'FSK31 (deprecated)',
				 'GTOR': 'GTOR (deprecated)',
				 'HELL80': 'HELL80 (deprecated)',
				 'HFSK': 'HFSK (deprecated)',
				 'JT4A': 'JT4A (deprecated)',
				 'JT4B': 'JT4B (deprecated)',
				 'JT4C': 'JT4C (deprecated)',
				 'JT4D': 'JT4D (deprecated)',
				 'JT4E': 'JT4E (deprecated)',
				 'JT4F': 'JT4F (deprecated)',
				 'JT4G': 'JT4G (deprecated)',
				 'JT65A': 'JT65A (deprecated)',
				 'JT65B': 'JT65B (deprecated)',
				 'JT65C': 'JT65C (deprecated)',
				 'MFSK8': 'MFSK8 (deprecated)',
				 'MFSK16': 'MFSK16 (deprecated)',
				 'PAC2': 'PAC2 (deprecated)',
				 'PAC3': 'PAC3 (deprecated)',
				 'PAX2': 'PAX2 (deprecated)',
				 'PCW': 'PCW (deprecated)',
				 'PSK10': 'PSK10 (deprecated)',
				 'PSK31': 'PSK31 (deprecated)',
				 'PSK63': 'PSK63 (deprecated)',
				 'PSK63F': 'PSK63F (deprecated)',
				 'PSK125': 'PSK125 (deprecated)',
				 'PSKAM10': 'PSKAM10 (deprecated)',
				 'PSKAM31': 'PSKAM31 (deprecated)',
				 'PSKAM50': 'PSKAM50 (deprecated)',
				 'PSKFEC31': 'PSKFEC31 (deprecated)',
				 'PSKHELL': 'PSKHELL (deprecated)',
				 'QPSK31': 'QPSK31 (deprecated)',
				 'QPSK63': 'QPSK63 (deprecated)',
				 'QPSK125': 'QPSK125 (deprecated)',
				 'THRBX': 'THRBX (deprecated)',
				},
	'Propagation': {
				 'AUR': 'Aurora',
				 'AUE': 'Aurora-E',
				 'BS': 'Back scatter',
				 'ECH': 'EchoLink',
				 'EME': 'Earth-Moon-Earth',
				 'ES': 'Sporadic E',
				 'FAI': 'Field Aligned Irregularities',
				 'F2': 'F2 Reflection',
				 'INTERNET': 'Internet-assisted',
				 'ION': 'Ionoscatter',
				 'IRL': 'IRLP',
				 'MS': 'Meteor scatter',
				 'RPT': 'Terrestrial or atmospheric repeater or transponder',
				 'RS': 'Rain scatter',
				 'SAT': 'Satellite',
				 'TEP': 'Trans-equatorial',
				 'TR': 'Tropospheric ducting',
				},
	'QSL Via':	{
				 'B': 'bureau',
				 'D': 'direct',
				 'E': 'electronic',
				 'M': 'manager (deprecated)',
				},
	'QSL Sent':	{
				 'Y': 'yes',
				 'N': 'no',
				 'R': 'requested',
				 'Q': 'queued',
				 'I': 'ignore/invalid',
				},
	'QSO Complete': {
				 'Y': 'yes',
				 'N': 'no',
				 'NIL': 'not heard',
				 '?': 'uncertain'
				},
}

_regexes = {
	'Date':	re.compile(r'^[0-9]{8}$'),
	'Boolean': re.compile(r'^[YN]$'),
	'Number': re.compile(r'^-?[0-9]+(\.[0-9]*)?$'),
	'String': re.compile(r'^[ -~]*$'),
	'IntlString': re.compile(r'^[^\x00-\x1f]*$'),
	'MultilineString': re.compile(r'^(?:[ -~]|(?:\r\n))*$'),
	'IntlMultilineString': re.compile(r'^(?:[^\x00-\x1f]|(?:\r\n))*$'),
	'Maidenhead': re.compile(r'^[A-R]{2}[0-9]{2}(?:[A-X]{2}(?:[0-9]{2})?)?$', re.I),
	'Location': re.compile(r'^[EWNS][0-9]{3} [0-9]{2}\.[0-9]{3}$'),
}

_types = {
	'D': {'regex':_regexes['Date']},
	'B': {'regex':_regexes['Boolean']},
	'N': {'regex':_regexes['Number']},
	'S': {'regex':_regexes['String']},
	'I': {'regex':_regexes['IntlString']},
	'M': {'regex':_regexes['MultilineString']},
	'G': {'regex':_regexes['IntlMultilineString']},
	'L': {'regex':_regexes['Location']},
}

_validate_functions = {
	# CreditList
	# Date
	# Time
	# GridSquareList
}

_fieldTypes = {
	'ADDRESS':	{'type':'M', 'desc':"the contacted station's complete mailing address: full name, street address, city, postal code, and country"},
	'ADDRESS_INTL':	{'type':'G', 'desc':"the contacted station's complete mailing address: full name, street address, city, postal code, and country"},
	'AGE':	{'type':'N', 'desc':"the contacted station's operator's age in years"},
	'A_INDEX':	{'type':'N', 'desc':"the geomagnetic A index at the time of the QSO"},
	'ANT_AZ':	{'type':'N', 'desc':"the logging station's antenna azimuth, in degrees"},
	'ANT_EL':	{'type':'N', 'desc':"the logging station's antenna elevation, in degrees"},
	'ANT_PATH':	{'type':'E', 'enumeration':_enumerations['Ant Path'],'desc':"the signal path"},
	'ARRL_SECT':	{'type':'E', 'enumeration':_enumerations['ARRL Section'],'desc':"the contacted station's ARRL section"},
	'AWARD_SUBMITTED':	{'type':'P', 'desc':"the list of awards submitted to a sponsor. note that this field might not be used in a QSO record.  It might be used to convey information about a user’s “Award Account” between an award sponsor and the user.  For example, AA6YQ might submit a request for DXCC awards by sending the following: <CALL:5>AA6YQ <AWARD_SUBMITTED:64>FISTS_CENTURY_BASIC,FISTS_CENTURY_SILVER,FISTS_SPECTRUM_100-160m"},
	'AWARD_GRANTED':	{'type':'P', 'desc':"the list of awards granted by a sponsor. note that this field might not be used in a QSO record.  It might be used to convey information about a user’s “Award Account” between an award sponsor and the user.  For example, in response to a request “send me a list of the DXCC awards granted to AA6YQ”, this might be received: <CALL:5>AA6YQ <AWARD_GRANTED:64>FISTS_CENTURY_BASIC,FISTS_CENTURY_SILVER, FISTS_SPECTRUM_100-160m"},
	'BAND':	{'type':'E', 'enumeration':_enumerations['Band'],'desc':"QSO Band"},
	'BAND_RX':	{'type':'E', 'enumeration':_enumerations['Band'],'desc':"in a split frequency QSO, the logging station's receiving band"},
	'CALL':	{'type':'S', 'desc':"the contacted station's Callsign"},
	'CHECK':	{'type':'S', 'desc':"contest check (e.g. for ARRL Sweepstakes)"},
	'CLASS':	{'type':'S', 'desc':"contest class (e.g. for ARRL Field Day)"},
	'CLUBLOG_QSO_UPLOAD_DATE':	{'type':'D', 'desc':"the date the QSO was last uploaded to the Club Log online service"},
	'CLUBLOG_QSO_UPLOAD_STATUS':	{'type':'E', 'enumeration':_enumerations['QSO Upload Status'],'desc':"the upload status of the QSO on the Club Log online service"},
	'CNTY':	{'type':'E', 'desc':"the contacted station's Secondary Administrative Subdivision of contacted station (e.g. US county, JA Gun), in the specified format"},
	'COMMENT':	{'type':'S', 'desc':"comment field for QSO"},
	'COMMENT_INTL':	{'type':'I', 'desc':"comment field for QSO"},
	'CONT':	{'type':'E', 'enumeration':_enumerations['Continent'],'desc':"the contacted station's Continent"},
	'CONTACTED_OP':	{'type':'S', 'desc':"the callsign of the individual operating the contacted station"},
	'CONTEST_ID':	{'type':'S', 'enumeration':_enumerations['Contest ID'],'desc':"QSO Contest Identifier use enumeration values for interoperability"},
	'COUNTRY':	{'type':'S', 'desc':"the contacted station's DXCC entity name"},
	'COUNTRY_INTL':	{'type':'I', 'desc':"the contacted station's DXCC entity name"},
	'CQZ':	{'type':'N', 'desc':"the contacted station's CQ Zone"},
	'CREDIT_SUBMITTED':	{'type':'C', 'enumeration':_enumerations['Credit'],'desc':"the list of credits sought for this QSO"},
	'CREDIT_GRANTED':	{'type':'C', 'enumeration':_enumerations['Credit'],'desc':"the list of credits granted to this QSO"},
	'DISTANCE':	{'type':'N', 'desc':"the distance between the logging station and the contacted station in kilometers via the specified signal path"},
	'DXCC':	{'type':'E', 'enumeration':_enumerations['Country Code'],'desc':"the contacted station's Country Code"},
	'EMAIL':	{'type':'S', 'desc':"the contacted station's email address"},
	'EQ_CALL':	{'type':'S', 'desc':"the contacted station's owner's callsign"},
	'EQSL_QSLRDATE':	{'type':'D', 'desc':"date QSL received from eQSL.cc (only valid if EQSL_QSL_RCVD is Y, I, or V) (V deprecated)"},
	'EQSL_QSLSDATE':	{'type':'D', 'desc':"date QSL sent to eQSL.cc (only valid if EQSL_QSL_SENT is Y, Q, or I)"},
	'EQSL_QSL_RCVD':	{'type':'E', 'enumeration':_enumerations['QSL Rcvd'],'desc':"eQSL.cc QSL received status instead of V (deprecated) use <CREDIT_GRANTED:39>DXCC:eqsl,DXCC_BAND:eqsl,DXCC_MODE:eqsl Default Value: N"},
	'EQSL_QSL_SENT':	{'type':'E', 'enumeration':_enumerations['QSL Sent'],'desc':"eQSL.cc QSL sent status Default Value: N"},
	'FISTS':	{'type':'S', 'desc':"the contacted station's FISTS CW Club member information, which starts with a sequence of Digits giving the member's number.  For upward-compatibility, any characters after the last digit of the member number sequence must be allowed by applications."},
	'FISTS_CC':	{'type':'S', 'desc':"the contacted station's FISTS CW Club Century Certificate (CC) number, which is a sequence of Digits only (no sign and no decimal point)"},
	'FORCE_INIT':	{'type':'B', 'desc':'new EME"initial"'},
	'FREQ':	{'type':'N', 'desc':"QSO frequency in Megahertz"},
	'FREQ_RX':	{'type':'N', 'desc':"in a split frequency QSO, the logging station's receiving frequency in Megahertz"},
	'GRIDSQUARE':	{'desc':"the contacted station's 2-character, 4-character, 6-character, or 8-character Maidenhead Grid Square", 'regex':_regexes['Maidenhead']},
	'GUEST_OP':	{'type':'S', 'desc':"deprecated: use OPERATOR instead"},
	'HRDLOG_QSO_UPLOAD_DATE':	{'type':'D', 'desc':"the date the QSO was last uploaded to the HRDLog.net online service"},
	'HRDLOG_QSO_UPLOAD_STATUS':	{'type':'E', 'enumeration':_enumerations['QSO Upload Status'],'desc':"the upload status of the QSO on the HRDLog.net online service"},
	'IOTA':	{'type':'S', 'desc':"the contacted station's IOTA designator, in format CC-XXX, where CC is a member of the Continent enumeration XXX is the island designator, where 0 <= XXX ,<= 999 [use leading zeroes]"},
	'IOTA_ISLAND_ID':	{'type':'S', 'desc':"the contacted station's IOTA Island Identifier"},
	'ITUZ':	{'type':'N', 'desc':"the contacted station's ITU zone"},
	'K_INDEX':	{'type':'N', 'desc':"the geomagnetic K index at the time of the QSO"},
	'LAT':	{'type':'L', 'desc':"the contacted station's latitude"},
	'LON':	{'type':'L', 'desc':"the contacted station's longitude"},
	'LOTW_QSLRDATE':	{'type':'D', 'desc':"date QSL received from ARRL Logbook of the World (only valid if LOTW_QSL_RCVD is Y, I, or V) (V deprecated)"},
	'LOTW_QSLSDATE':	{'type':'D', 'desc':"date QSL sent to ARRL Logbook of the World (only valid if LOTW_QSL_SENT is Y, Q, or I)"},
	'LOTW_QSL_RCVD':	{'type':'E', 'enumeration':_enumerations['QSL Rcvd'],'desc':"ARRL Logbook of the World QSL received status instead of V (deprecated) use <CREDIT_GRANTED:39>DXCC:lotw,DXCC_BAND:lotw,DXCC_MODE:lotw Default Value: N"},
	'LOTW_QSL_SENT':	{'type':'E', 'enumeration':_enumerations['QSL Sent'],'desc':"ARRL Logbook of the World QSL sent status Default Value: N"},
	'MAX_BURSTS':	{'type':'N', 'desc':"maximum length of meteor scatter bursts heard by the logging station, in seconds"},
	'MODE':	{'type':'E', 'enumeration':_enumerations['Mode'],'desc':"QSO Mode"},
	'MS_SHOWER':	{'type':'S', 'desc':"For Meteor Scatter QSOs, the name of the meteor shower in progress"},
	'MY_CITY':	{'type':'S', 'desc':"the logging station's city"},
	'MY_CITY_INTL':	{'type':'I', 'desc':"the logging station's city"},
	'MY_CNTY':	{'type':'E', 'desc':"the logging station's Secondary Administrative Subdivision  (e.g. US county, JA Gun) , in the specified format"},
	'MY_COUNTRY':	{'type':'S', 'desc':"the logging station's DXCC entity name"},
	'MY_COUNTRY_INTL':	{'type':'I', 'desc':"the logging station's DXCC entity name"},
	'MY_CQ_ZONE':	{'type':'N', 'desc':"the logging station's CQ Zone"},
	'MY_DXCC':	{'type':'E', 'enumeration':_enumerations['Country Code'],'desc':"the logging station's Country Code"},
	'MY_FISTS':	{'type':'S', 'desc':"the logging station's FISTS CW Club member information, which starts with a sequence of Digits giving the member's number. For upward-compatibility, any characters after the last digit of the member number sequence must be allowed by applications."},
	'MY_GRIDSQUARE':	{'desc':"the logging station's 2-character, 4-character, 6-character, or 8-character Maidenhead Grid Square", 'regex':_regexes['Maidenhead']},
	'MY_IOTA':	{'type':'S', 'desc':"the logging station's IOTA designator, in format CC-XXX, where CC is a member of the Continent enumeration XXX is the island designator, where 0 <= XXX ,<= 999  [use leading zeroes]"},
	'MY_IOTA_ISLAND_ID':	{'type':'S', 'desc':"the logging station's IOTA Island Identifier"},
	'MY_ITU_ZONE':	{'type':'N', 'desc':"the logging station's ITU zone"},
	'MY_LAT':	{'type':'L', 'desc':"the logging station's latitude"},
	'MY_LON':	{'type':'L', 'desc':"the logging station's longitude"},
	'MY_NAME':	{'type':'S', 'desc':"the logging operator's name"},
	'MY_NAME_INTL':	{'type':'I', 'desc':"the logging operator's name"},
	'MY_POSTAL_CODE':	{'type':'S', 'desc':"the logging station's postal code"},
	'MY_POSTAL_CODE_INTL':	{'type':'I', 'desc':"the logging station's postal code"},
	'MY_RIG':	{'type':'S', 'desc':"description of the logging station's equipment"},
	'MY_RIG_INTL':	{'type':'I', 'desc':"description of the logging station's equipment"},
	'MY_SIG':	{'type':'S', 'desc':"special interest activity or event"},
	'MY_SIG_INTL':	{'type':'I', 'desc':"special interest activity or event"},
	'MY_SIG_INFO':	{'type':'S', 'desc':"special interest activity or event information"},
	'MY_SIG_INFO_INTL':	{'type':'I', 'desc':"special interest activity or event information"},
	'MY_SOTA_REF':	{'desc':"the logging station's International SOTA Reference."},
	'MY_STATE':	{'type':'E', 'desc':"the code for the logging station's Primary Administrative Subdivision (e.g. US State, JA Island, VE Province)"},
	'MY_STREET':	{'type':'S', 'desc':"the logging station's street"},
	'MY_STREET_INTL':	{'type':'I', 'desc':"the logging station's street"},
	'MY_USACA_COUNTIES':	{'desc':"two US counties in the case where the logging station is located on a border between two counties, representing counties that the contacted station may claim for the CQ Magazine USA-CA award program.  E.g. MA,Franklin:MA,Hampshire MY_VUCC_GRIDS 	GridSquareList 	  	two or four adjacent Maidenhead grid locators, each four characters long, representing the logging station's grid squares that the contacted station may claim for the ARRL VUCC award program.  E.g. EN98,FM08,EM97,FM07"},
	'NAME':	{'type':'S', 'desc':"the contacted station's operator's name"},
	'NAME_INTL':	{'type':'I', 'desc':"the contacted station's operator's name"},
	'NOTES':	{'type':'M', 'desc':"QSO notes"},
	'NOTES_INTL':	{'type':'G', 'desc':"QSO notes"},
	'NR_BURSTS':	{'type':'N', 'desc':"the number of meteor scatter bursts heard by the logging station"},
	'NR_PINGS':	{'type':'N', 'desc':"the number of meteor scatter pings heard by the logging station"},
	'OPERATOR':	{'type':'S', 'desc':"the logging operator's callsign if STATION_CALLSIGN is absent, OPERATOR shall be treated as both the logging station's callsign and the logging operator's callsign"},
	'OWNER_CALLSIGN':	{'type':'S', 'desc':"the callsign of the owner of the station used to log the contact (the callsign of the OPERATOR's host) if OWNER_CALLSIGN is absent, STATION_CALLSIGN shall be treated as both the logging station's callsign and the callsign of the owner of the station"},
	'PFX':	{'type':'S', 'desc':"the contacted station's WPX prefix"},
	'PRECEDENCE':	{'type':'S', 'desc':"contest precedence (e.g. for ARRL Sweepstakes)"},
	'PROP_MODE':	{'type':'E', 'enumeration':_enumerations['Propagation'],'desc':"QSO propagation mode"},
	'PUBLIC_KEY':	{'type':'S', 'desc':"public encryption key"},
	'QRZCOM_QSO_UPLOAD_DATE':	{'type':'D', 'desc':"the date the QSO was last uploaded to the QRZ.COM online service"},
	'QRZCOM_QSO_UPLOAD_STATUS':	{'type':'E', 'enumeration':_enumerations['QSO Upload Status'],'desc':"the upload status of the QSO on the QRZ.COM online service"},
	'QSLMSG':	{'type':'M', 'desc':"QSL card message"},
	'QSLMSG_INTL':	{'type':'G', 'desc':"QSL card message"},
	'QSLRDATE':	{'type':'D', 'desc':"QSL received date (only valid if QSL_RCVD is Y, I, or V) (V deprecated)"},
	'QSLSDATE':	{'type':'D', 'desc':"QSL sent date (only valid if QSL_SENT is Y, Q, or I)"},
	'QSL_RCVD':	{'type':'E', 'enumeration':_enumerations['QSL Rcvd'],'desc':"QSL received status instead of V (deprecated) use <CREDIT_GRANTED:39>DXCC:card,DXCC_BAND:card,DXCC_MODE:card Default Value: N"},
	'QSL_RCVD_VIA':	{'type':'E', 'enumeration':_enumerations['QSL Via'],'desc':"means by which the QSL was received by the logging station use of M (manager) is deprecated"},
	'QSL_SENT':	{'type':'E', 'enumeration':_enumerations['QSL Sent'],'desc':"QSL sent status Default Value: N"},
	'QSL_SENT_VIA':	{'type':'E', 'enumeration':_enumerations['QSL Via'],'desc':"means by which the QSL was sent by the logging station use of M (manager) is deprecated"},
	'QSL_VIA':	{'type':'S', 'desc':"the contacted station's QSL route"},
	'QSO_COMPLETE':	{'type':'E', 'enumeration':_enumerations['QSO Complete'],'desc':"indicates whether the QSO was complete from the perspective of the logging station Y - yes N - no NIL - not heard ? - uncertain"},
	'QSO_DATE':	{'type':'D', 'desc':"date on which the QSO started"},
	'QSO_DATE_OFF':	{'type':'D', 'desc':"date on which the QSO ended"},
	'QSO_RANDOM':	{'type':'B', 'desc':"indicates whether the QSO was random or scheduled"},
	'QTH':	{'type':'S', 'desc':"the contacted station's city"},
	'QTH_INTL':	{'type':'I', 'desc':"the contacted station's city"},
	'RIG':	{'type':'M', 'desc':"description of the contacted station's equipment"},
	'RIG_INTL':	{'type':'G', 'desc':"description of the contacted station's equipment"},
	'RST_RCVD':	{'type':'S', 'desc':"signal report from the contacted station"},
	'RST_SENT':	{'type':'S', 'desc':"signal report sent to the contacted station"},
	'RX_PWR':	{'type':'N', 'desc':"the contacted station's transmitter power in watts"},
	'SAT_MODE':	{'type':'S', 'desc':"satellite mode"},
	'SAT_NAME':	{'type':'S', 'desc':"name of satellite"},
	'SFI':	{'type':'N', 'desc':"the solar flux at the time of the QSO"},
	'SIG':	{'type':'S', 'desc':"the name of the contacted station's special activity or interest group"},
	'SIG_INTL':	{'type':'I', 'desc':"the name of the contacted station's special activity or interest group"},
	'SIG_INFO':	{'type':'S', 'desc':"information associated with the contacted station's activity or interest group"},
	'SIG_INFO_INTL':	{'type':'I', 'desc':"information associated with the contacted station's activity or interest group"},
	'SKCC':	{'type':'S', 'desc':"the contacted station's Straight Key Century Club (SKCC) member information"},
	'SOTA_REF':	{'desc':"the contacted station's International SOTA Reference."},
	'SRX':	{'type':'N', 'desc':"contest QSO received serial number"},
	'SRX_STRING':	{'type':'S', 'desc':"contest QSO received information use Cabrillo format to convey contest information for which ADIF fields are not specified in the event of a conflict between information in a dedicated contest field and this field, information in the dedicated contest field shall prevail"},
	'STATE':	{'type':'E', 'desc':"the code for the contacted station's Primary Administrative Subdivision (e.g. US State, JA Island, VE Province)"},
	'STATION_CALLSIGN':	{'type':'S', 'desc':"the logging station's callsign (the callsign used over the air) if STATION_CALLSIGN is absent, OPERATOR shall be treated as both the logging station's callsign and the logging operator's callsign"},
	'STX':	{'type':'N', 'desc':"contest QSO transmitted serial number"},
	'STX_STRING':	{'type':'S', 'desc':"contest QSO transmitted information use Cabrillo format to convey contest information for which ADIF fields are not specified in the event of a conflict between information in a dedicated contest field and this field, information in the dedicated contest field shall prevail"},
	'SUBMODE':	{'type':'S', 'desc':"QSO Submode use enumeration values for interoperability"},
	'SWL':	{'type':'B', 'desc':"indicates that the QSO information pertains to an SWL report"},
	'TEN_TEN':	{'type':'N', 'desc':"Ten-Ten number"},
	'TIME_OFF':	{'type':'T', 'desc':"HHMM or HHMMSS in UTC in the absence of <QSO_DATE_OFF>, the QSO duration is less than 24 hours"},
	'TIME_ON':	{'type':'T', 'desc':"HHMM or HHMMSS in UTC"},
	'TX_PWR':	{'type':'N', 'desc':"the logging station's power in watts"},
	'USACA_COUNTIES':	{'desc':"two US counties in the case where the contacted station is located on a border between two counties, representing counties credited to the QSO for the CQ Magazine USA-CA award program.  E.g. MA,Franklin:MA,Hampshire"},
	'VE_PROV':	{'type':'S', 'desc':"deprecated: use State instead"},
	'VUCC_GRIDS':	{'desc':"two or four adjacent Maidenhead grid locators, each four characters long, representing the contacted station's grid squares credited to the QSO for the ARRL VUCC award program.  E.g. EN98,FM08,EM97,FM07"},
	'WEB':	{'type':'S', 'desc':"the contacted station's URL"},
}

# Validation functions
def validate(name, value, log):
	field = log.getType(name)
	if field is None:
		raise AttributeError, name
	if 'regex' in field:
		if field['regex'].search(value) is None:
			raise ValueError, value
	if 'validate' in field:
		if not field['validate'](value):
			raise ValueError, value
	if 'enumeration' in field:
		if not str(value).upper() in field['enumeration']:
			raise ValueError, value
	if 'type' in field and field['type'] in _types:
		field = _types[field['type']]
		if 'regex' in field:
			if field['regex'].search(value) is None:
				raise ValueError, value
		if 'validate' in field:
			if not field['validate'](value):
				raise ValueError, value

# Assignment functions
# These coerce types from the obvious type to the internal one
# (ie: date/time etc)


class ADIF_logfield(object):
	def __init__(self, entry, name, value):
		ucn = str(name).upper()
		if entry.log.getType(ucn) is None:
			raise AttributeError, ucn
		self._entry = entry
		self._name = ucn
		self(value)
	def __repr__(self):
		ret = '<' + str(self._name) + ':' + str(len(str(self._value)))
		field = self._entry.log.getType(self._name)
		if 'type' in field:
			ret += ':' + field['type']
		ret += '>' + str(self._value)
		return ret
	def __str__(self):
		return str(self._value)
	def __len__(self):
		return len(str(self._value))
	def __call__(self, value):
		validate(self._name, value, self._entry.log)
		self._value = value
	def xml(self):
		if self._name in _fieldTypes:
			tag = escape(str(self._name))
			ret = '<' + tag + '>'
		else:
			field = self._entry.log.getType(self._name)
			if 'userdef' in field and field['userdef']:
				tag = 'USERDEF'
				ret = '<'+tag+' FIELDNAME=' + quoteattr(self._name) + '>'
			else:
				tag = 'APP'
				progid = self._entry.log.appName
				fname = self._name
				m = re.match(r'^APP_(.*)_(.*?)$', self._name, re.I)
				if m:
					progid=m.group(1)
					fname=m.group(2)
				ret = '<'+tag+' PROGRAMID='+quoteattr(progid)+' FIELDNAME=' + quoteattr(fname) + ' TYPE='+quoteattr(field['type'])+'>'
				end = '</APP>'
		ret += escape(self._value)
		ret += '</' + tag + '>'
		return ret

class ADIF_logentry(dict):
	def __init__(self, log):
		self.log=log
		self._old_assign = dict.__setitem__
	def __getitem__(self, index):
		li = str(index).lower()
		return dict.__getitem__(self, li)
	def __setitem__(self, index, value):
		li = str(index).lower()
		dict.__setitem__(self, li, ADIF_logfield(self, li, value))
	def __repr__(self):
		ret = ''
		for x in self:
			ret += repr(self[x]) + "\n"
		ret += '<eor>\n\n'
		return ret
	def xml(self, *indent):
		prefix = '\t'
		extra = prefix
		if len(indent) > 0:
			prefix = indent[0]
		if len(indent) > 1:
			extra = indent[1]
		ret = prefix + '<RECORD>\n'
		for x in self:
			ret += prefix + extra + self[x].xml() + "\n"
		ret += prefix + '</RECORD>\n'
		return ret

version = '3.0.4'

class ADXHandler(ContentHandler):
	def __init__(self, log):
		self._log = log
		self._inHeader = False
		self._inRecords = False
		self._inADX = False
		self._entry = None
		self._curString = ''
		self._curAttr = None
	def startElement(self, name, attrs):
		if name=='ADX' and not self._inADX:
			if self._inADX:
				raise SAXParseException, 'Nested ADX!'
			self._inADX = True
		elif name=='HEADER' and not self._inHeader:
			if not self._inADX:
				raise SAXParseException, 'Header outside of ADX!'
			self._inHeader = True
		elif name=='USERDEF' and self._inHeader:
			self._userdefType = attrs.get('TYPE');
			self._userdefEnum = attrs.get('ENUM');
			self._userdefRange = attrs.get('RANGE');
			self._curString = ''
		elif name=='RECORDS' and not self._inRecords:
			if not self._inADX:
				raise SAXParseException, 'Records outside of ADX!'
			if self._inHeader:
				raise SAXParseException, 'Records inside Header!'
			self._inRecords = True
		elif name=='RECORD':
			if not self._inRecords:
				raise SAXParseException, 'Record outside of RECORDS!'
			if not self._inADX:
				raise SAXParseException, 'Record outside of ADX!'
			if self._inHeader:
				raise SAXParseException, 'Record inside Header!'
			if self._entry is None:
				self._entry = self._log.newEntry()
				self._curString=''
				self._curAttr=None
			else:
				raise SAXParseException, 'Record inside record!'
		elif name=='USERDEF' and self._entry is not None:
			self._curString = ''
			self._curAttr = attrs.get('FIELDNAME')
		elif name=='APP' and self._entry is not None:
			fn = attrs.get('FIELDNAME')
			ft = attrs.get('TYPE')
			pn = attrs.get('PROGRAMID')
			if ft is None:
				ft = 'M'
			self._curAttr = 'APP_'+pn+'_'+fn
			self._log.setType(self._curAttr, ft)
			self._curString = ''
		else:
			if self._entry is None:
				pass
			else:
				self._curString = ''
				self._curAttr = name
	def endElement(self, name):
		if name=='ADX':
			self._inADX = False
		if name=='HEADER':
			self._inHeader = False
		if name=='RECORDS':
			self._inRecords = False
		if name=='RECORD':
			self._entry = None
		if name=='USERDEF' and self._inHeader:
			if self._userdefEnum is not None:
				range = self._userdefEnum[1:-1].split(',')
				enums = dict.fromkeys(range)
				self._log.setType(self._curString, 'E', enumeration=enums, userdef=True)
			elif self._userdefRange is not None:
				range = self._userdefRange[1:-1].split(':')
				if len(range) == 2:
					self._log.setType(self._curString, 'N', min=int(range[0]), max=int(range[1]), userdef=True)
			else:
				self._log.setType(self._curString, self._userdefType, userdef=True)
		if self._curAttr is None:
			pass
		else:
			self._entry[self._curAttr] = self._curString
			self._curString = ''
			self._curAttr = None

	def characters(self, chars):
		self._curString += chars


class ADIF_log(list):
	def getEnum(self, name):
		return _fieldTypes[name]['enumeration'] or None
	def getDesc(self, name):
		return _fieldTypes[name]['desc'] or None
	def fimport(self, file):
		f = open(file, 'rb')
		data = f.read()
		f.close()
		if data[0:5] == '<?xml':
			parser = make_parser()
			handler = ADXHandler(self)
			parser.setContentHandler(handler)
			parser.parse(file)
		else:
			tagre = re.compile(r'^<([^:>]+)(?::([0-9]+)(?::([^:>]*))?)?>')
			def skip_to_start(data):
				while len(data) and data[:1] != '<':
					data = data[1:]
				return data
			def parse_tag(data):
				data = skip_to_start(data)
				if data == '':
					return
				m = tagre.match(data)
				if not m:
					raise AttributeError, data[:80]
				tagobj = {'name':m.group(1).lower()}
				if m.group(2):
					tagobj['len']=int(m.group(2))
				if m.group(3):
					tagobj['type']=m.group(3)
				data = tagre.sub('', data)
				if 'len' in tagobj:
					tagobj['data'] = data[:tagobj['len']]
					data = data[tagobj['len']:]
				else:
					tagobj['data'] = ''
				tagobj['remainder']=data
				return tagobj
			if not data[0:1] == '<':
				# Parsing header
				while len(data):
					t = parse_tag(data)
					data = t['remainder']
					if t['name'] == 'eoh':
						break
					m = re.match(r'^USERDEF[0-9]+$',t['name'],re.I)
					if m:
						m = re.match(r'^([^,]*)(?:,{(.*)})?$', t['data'])
						if m:
							fn = m.group(1)
							ft = t['type']
							if ft is None:
								ft = 'M'
							enumeration = None
							if m.group(2):
								range = m.group(2).split(':')
								if len(range) == 2:
									self.setType(fn, 'N', min=int(range[0]), max=int(range[1]), userdef=True)
								else:
									range = m.group(2).split(',')
									enums = dict.fromkeys(range)
									self.setType(fn, 'E', enumeration=enums, userdef=True)
							else:
								self.setType(fn, ft, userdef=True)
			# Parsing entries
			r = ADIF_logentry(self)
			while len(data):
				t = parse_tag(data)
				if not t:
					break
				data = t['remainder']
				if t['name'] == 'eor':
					self.append(r)
					r = ADIF_logentry(self)
				else:
					if self.getType(t['name']) is None:
						if 'type' in t:
							type = t['type']
						else:
							type = 'M'
						self.setType(t['name'], type)
					r[t['name']]=t['data']
	def __init__(self, *args, **params):
		self.extraTypes={}
		if len(args) > 0:
			self.appName = args[0]
		else:
			self.appName='The Nameless App'
		if 'file' in params:
			self.fimport(params['file'])
	def xml(self):
		ret = '<?xml version="1.0" encoding="UTF-8"?>\n'
		ret += '<ADX>\n'
		ret += '\t<HEADER>\n'
		ret += '\t\t<ADIF_VER>'+version+'</ADIF_VER>\n'
		ret += '\t\t<PROGRAMID>' + escape(self.appName) + '</PROGRAMID>\n'
		userdef = 1
		for x in self.extraTypes:
			if 'userdef' in self.extraTypes[x]:
				fdef = '\t\t<USERDEF FIELDID="'+str(userdef)+'" TYPE='+quoteattr(self.extraTypes[x]['type'])
				if self.extraTypes[x]['type'] == 'E':
					if 'enumeration' in self.extraTypes[x]:
						edef = '{'
						for e in self.extraTypes[x]['enumeration']:
							edef += e
							edef += ','
						edef = edef[:-1] + '}'
						fdef += ' ENUM='+quoteattr(edef)
				elif self.extraTypes[x]['type'] == 'N':
					if 'min' in self.extraTypes[x] and 'max' in self.extraTypes[x]:
						fdef += ' RANGE="{'+str(self.extraTypes[x]['min'])+':'+str(self.extraTypes[x]['max'])+'}"'
				ret += fdef+'>'+x+'</USERDEF>\n'
				userdef += 1
		ret += '\t</HEADER>\n'
		ret += '\t<RECORDS>\n'
		for x in self:
			if isinstance(x, ADIF_logentry):
				ret += x.xml('\t\t')
		ret += '\t</RECORDS>\n'
		ret += '</ADX>'
		return ret
	def __repr__(self):
		ret = '\n'
		ret += '<adif_ver:'+str(len(version))+'>'+version+'\n'
		ret += '<programid:'+str(len(self.appName)) + '>' + str(self.appName) + '\n'
		userdef = 1
		for x in self.extraTypes:
			if 'userdef' in self.extraTypes[x]:
				fdef = x
				if self.extraTypes[x]['type'] == 'E':
					if 'enumeration' in self.extraTypes[x]:
						fdef += ',{'
						for e in self.extraTypes[x]['enumeration']:
							fdef += e
							fdef += ','
						fdef = fdef[:-1] + '}'
				elif self.extraTypes[x]['type'] == 'N':
					if 'min' in self.extraTypes[x] and 'max' in self.extraTypes[x]:
						fdef += ',{'+str(self.extraTypes[x]['min'])+':'+str(self.extraTypes[x]['max'])+'}'
				ret += '<userdef'+str(userdef)+':'+str(len(fdef))+':'+self.extraTypes[x]['type']+'>'+fdef+"\n"
				userdef += 1
		ret += '<eoh>\n\n'
		for x in self:
			if isinstance(x, ADIF_logentry):
				ret += repr(x)
		return ret
	def newEntry(self):
		self.append(ADIF_logentry(self))
		return self[-1]
	def getType(self, name):
		ucn = str(name).upper()
		if ucn in _fieldTypes:
			return _fieldTypes[ucn]
		if ucn in self.extraTypes:
			return self.extraTypes[ucn]
	def setType(self, name, ftype, **options):
		ucn = str(name).upper()
		self.extraTypes[ucn] = {'type':ftype}
		for x in options:
			self.extraTypes[ucn][x] = options[x]
		if 'enumeration' in self.extraTypes[ucn]:
			e = self.extraTypes[ucn]['enumeration']
			for x in e:
				if x != x.upper():
					e[x.upper()] = e[x]
					del e[x]
