import argparse
import json
import re
import requests
import traceback

from lane import *
from tqdm import *

class Card:
	def __init__(self, set_name, cn, foil=False, token=False):
		self.cn = int(cn)
		self.set = set_name
		self.foil = foil
		self.token = token
	
	def __str__(self):
		return f'{self.set} {self.cn} {self.foil} {self.token}'

def scryfall_csv_row(set_name, card):
	if card.token:
		set_name = 'T' + set_name

	url = f'https://api.scryfall.com/cards/{set_name.lower()}/{card.cn}'
	j = json.loads(requests.get(url).text)
	try:
		name = j['name']
	except:
		print(url, flush=True)
		print(f'{card} {j}', flush=True)
	f = 'foil' if card.foil else ''

	res = f'"{set_name.upper()}","{card.cn}","{name}","{f}"'
	return res

def parse_cards(fn):
	txt = ll_read(fn)
	lines = ll_lines(txt)
	set_name = lines[0]
	card_strs = lines[1].split('.')

	cards = []
	for cs in card_strs:
		cn = ll_only_nums(cs)
		card = Card(set_name, cn)
		if ll_only_alpha(cs):
			tags = ll_split(ll_only_alpha(cs, also=' '), delim=' ')
			if 'foil' in tags:
				card.foil = True
			if 'token' in tags:
				card.token = True
			if 'emblem' in tags:
				card.token = True
		cards.append(card)

	return set_name, cards

def main():
	ap = argparse.ArgumentParser()
	ap.add_argument('input_files', nargs='+')
	ap.add_argument('-a', '--append', action='store_true')
	args = ap.parse_args()

	counts = {}
	rows = {}

	with open('out/collection.csv', 'a+' if args.append else 'w+') as f:
		for fn in tqdm(args.input_files):
			set_name, cards = parse_cards(fn)
			for card in tqdm(cards, leave=False):
				if str(card) in counts:
					counts[str(card)] += 1
					continue

				try:
					row = scryfall_csv_row(set_name, card)
					rows[str(card)] = row
					counts[str(card)] = 1
				except:
					f.write(f'lookup failed on {set_name} {card.cn}' + '\n')
					print(f'lookup failed on {set_name} {card.cn}', flush=True)
					print(traceback.format_exc(), flush=True)

		f.write('"Count","Edition","Collector Number","Name","Foil"\n')
		for card, count in sorted(counts.items(), key=nth(1), reverse=True):
			row = rows[card]
			row = f'"{count}",' + row
			f.write(row + '\n')

		# Write the manual cards in, too
		for line in ll_lines(ll_read('in/_manual.csv', 'r'))[1:]:
			f.write(line + '\n')

if __name__ == '__main__':
	main()
