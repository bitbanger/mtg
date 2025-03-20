import json
import os
import requests

from lane import *

class Card:
	def __init__(self, set_code, cn, foil=False, token=False, name=''):
		self.cn = int(cn)

		self.set_code = set_code
		self.token = token
		if len(set_code) == 4 and set_code[0].lower() == 't':
			self.token = True
			self.set_code = set_code[1:]

		self.foil = foil
		self.rarity = ''
		self._name = name

		self.json = self.scryfall_json()
	
	def __str__(self):
		return f'{self.set_code} {self.cn} {self.foil} {self.token}'
	
	def mox_csv_row(self):
		# return f'"{self.set_code.upper()}","{self.cn}","{self.name()}","{\'foil\' if self.foil else \'\'}"'
		return '"' + '","'.join([self.set_code.upper(), self.cn, self.name(), 'foil'*self.foil]) + '"'
	
	@ll_cache
	def scryfall_json(self):
		url = f'https://api.scryfall.com/cards/{self.fixed_sc()}/{self.cn}'
		self.json = json.loads(requests.get(url).text)
		return self.json
	
	def fixed_sc(self):
		fixed_sc = self.set_code.lower()
		if self.token:
			fixed_sc = 't'+fixed_sc
		return fixed_sc
	
	def name(self):
		if not self._name:
			self._name = self.json.get('name')
		return self._name
	
	def price(self):
		if self.token:
			return 0.0

		j = self.json
		price = 0.0

		ps = j.get('prices')
		if ps is None:
			print(f'Card ({self}) had null prices')
			return 0.0

		ps = {k: v for k, v in ps.items()
						if 'usd' in k
							and v is not None}

		k = 'usd'
		if self.foil:
			if ('usd_foil' not in ps) and ('usd_etched' in ps):
				k = 'usd_etched'
			else:
				k = 'usd_foil'
		else:
			if 'usd' not in ps:
				k = 'usd_etched'

		if len(ps) == 1:
			r = ps[nth(0)(ps.keys())]
			return float(r)

		price = ps.get(k)
		if price is None:
			print(f'Card ({self}) tried invalid price "{k}" ({ps})')
			return 0.0

		return float(price)

	def fstr(self):
		f = str(self.cn)
		if self.token:
			f += ' token'
		if self.foil:
			f += ' foil'

		return f
