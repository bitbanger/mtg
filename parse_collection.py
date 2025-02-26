import argparse
import csv
import json
import os
import re
import requests
import traceback

from io import StringIO
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

	if not os.path.exists('cache'):
		os.mkdir('cache')

	cache_fn = f'{ll_md5(url)}.json'
	if (cache_fn := f'{ll_md5(url)}.json') in os.listdir('cache'):
		j = json.loads(ll_read(f'cache/{cache_fn}'))
	else:
		j = json.loads(jt := requests.get(url).text)
		ll_write(f'cache/{cache_fn}', jt)

	try:
		name = j['name']
	except:
		print(set_name)
		print(card.cn)
		print(url, flush=True)
		print(f'{card} {j}', flush=True)
		quit()
		return ''
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

def fetch_card_data(input_files):
	rows = {}
	counts = {}
	pbar_1 = tqdm(input_files, bar_format='{desc}{bar}')
	for i, fn in enumerate(pbar_1):
		set_name = fn.split(".")[0].split("/")[-1].upper()
		pbar_1.set_description(f'Set {i+1} of {len(input_files)} ({set_name})')
		if not fn.endswith('.txt'):
			continue
		set_name, cards = parse_cards(fn)
		pbar_2 = tqdm(cards, bar_format='{desc}{bar}', leave=False)
		for j, card in enumerate(pbar_2):
			pbar_2.set_description(f'Card {j+1} of {len(cards)}')
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

	return rows, counts

def write_row(file, row, count, card_kingdom=False):
	if not card_kingdom:
		file.write(row + '\n')
	else:
		c, ed, cn, n, f = next(csv.reader(StringIO(row)))
		n = n.split(' // ')[0]
		if n in ['Island', 'Mountain', 'Forest', 'Plains', 'Swamp']:
			n = '%s (%04d)' % (n, int(cn))
		file.write(f'"{count}","{ed}","{n}","{f}"\n')

def write_file(out_fn, rows, counts, append=False, card_kingdom=False):
	with open(out_fn, 'a+' if append else 'w+') as f:
		if not card_kingdom:
			f.write('"Count","Edition","Collector Number","Name","Foil"\n')

		for card, count in sorted(counts.items(), key=nth(1), reverse=True):
			row = f'"{count}",' + rows[card]
			write_row(f, row, count, card_kingdom=card_kingdom)

		# Write the manual cards in, too
		for line in ll_lines(ll_read('in/_manual.csv', 'r'))[1:]:
			count = ll_csv_row(line)[0]
			write_row(f, line, count, card_kingdom=card_kingdom)

def main():
	ap = argparse.ArgumentParser()
	ap.add_argument('input_files', nargs='+')
	ap.add_argument('-a', '--append', action='store_true')
	args = ap.parse_args()

	rows, counts = fetch_card_data(args.input_files)
	write_file('out/collection.csv', rows, counts, append=args.append)
	write_file('out/ck_collection.csv', rows, counts, append=args.append, card_kingdom=True)

if __name__ == '__main__':
	main()
