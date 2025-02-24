import argparse
import re
import requests
import json

from lane import *
from tqdm import *

class Card:
	def __init__(self, cn, foil=False, token=False, emblem=False):
		self.cn = int(cn)
		self.foil = foil
		self.token = token
		self.emblem = emblem

def scryfall_csv_row(set_name, card):
	if card.token:
		set_name = 'T' + set_name
	if card.emblem:
		set_name = 'E' + set_name

	url = f'https://api.scryfall.com/cards/{set_name.lower()}/{card.cn}'
	j = json.loads(requests.get(url).text)
	name = j['name']
	f = 'foil' if card.foil else ''
	return f'"{set_name.upper()}","{card.cn}","{name}","{f}"'

def parse_cards(fn):
	txt = ll_read(fn)
	lines = ll_lines(txt)
	set_name = lines[0]
	card_strs = lines[1].split('.')

	cards = []
	for cs in card_strs:
		cn = ll_only_nums(cs)
		card = Card(cn)
		if ll_only_alpha(cs):
			tags = ll_split(ll_only_alpha(cs, also=' '), delim=' ')
			if 'foil' in tags:
				card.foil = True
			if 'token' in tags:
				card.token = True
			if 'emblem' in tags:
				card.emblem = True
		cards.append(card)

	return set_name, cards

def main():
	ap = argparse.ArgumentParser()
	ap.add_argument('input_files', nargs='+')
	args = ap.parse_args()

	with open('out/collection.csv', 'w+') as f:
		headers = '"Edition","Collector Number","Name","Foil"'
		f.write(headers + '\n')

		for fn in tqdm(args.input_files):
			set_name, cards = parse_cards(fn)
			for card in tqdm(cards, leave=False):
				row = scryfall_csv_row(set_name, card)
				f.write(row + '\n')

if __name__ == '__main__':
	main()
