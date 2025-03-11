import argparse
import csv
import json
import os
import re
import requests
import time
import traceback

from collections import defaultdict
from io import StringIO
from lane import *
from tqdm import *

class Card:
	def __init__(self, set_name, cn, foil=False, token=False):
		self.cn = int(cn)
		self.set = set_name
		self.foil = foil
		self.token = token
		self.rarity = ''
		self.name = ''
	
	def __str__(self):
		return f'{self.set} {self.cn} {self.foil} {self.token}'
	
	def fstr(self):
		f = str(self.cn)
		if self.token:
			f += ' token'
		if self.foil:
			f += ' foil'

		return f

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
		card.rarity = j['rarity']
		card.name = name
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

def file2sets(fn):
	sets = defaultdict(list)
	set_name = ''
	set_lines = []
	for line in ll_lines(ll_read(fn)):
		# This line has cards for sure
		if '.' in line:
			set_lines.append(line)
			continue

		# This can't be a set name
		if len(line) > 3 and line != 'PLST':
			set_lines.append(line)
			continue

		# No letters? No set name...I think
		if len(set(ll_alpha.upper()).intersection(set(line))) == 0:
			set_lines.append(line)
			continue

		# OK, it's a set name. Commit the lines
		# to the last set name, if any, & reset
		if set_name:
			sets[set_name].extend(set_lines)
			set_name = ''
			set_lines = []
		set_name = line
	
	# Finish up
	if set_lines:
		sets[set_name].extend(set_lines)
	
	ret_sets = {}
	for set_name, set_lines in sets.items():
		# Combine any card lines into one line, separated by dots
		set_txt = '.'.join(set_lines)

		# Remove repeated dots
		while '..' in set_txt:
			set_txt = set_txt.replace('..', '.')
		
		# Split cards out by dot
		card_strs = set_txt.split('.')

		# Parse the cards
		cards = cardstrs2cards(set_name, card_strs)

		# Add the cards
		ret_sets[set_name] = cards

	return ret_sets

def files2sets(fns):
	sets = defaultdict(list)
	for fn in fns:
		if os.path.basename(fn).startswith('_'):
			continue
		for set_name, cards in file2sets(fn).items():
			sets[set_name].extend(cards)
	
	return sets

def cardstrs2cards(set_name, card_strs):
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

	return cards

def sets2rows(sets, delay=False):
	rows, counts = {}, {}

	set_cards = []
	for set_name in sets.keys():
		for card in sets[set_name]:
			set_cards.append((set_name, card))

	pbar = tqdm(set_cards, bar_format='{desc}{bar}')
	for i, (set_name, card) in enumerate(pbar):
		pbar.set_description_str(f'Card {i+1} of {len(set_cards)} (current set: {set_name}) ')

		if str(card) in counts:
			counts[str(card)] += 1
			continue

		try:
			if delay:
				time.sleep(0.01)
			row = scryfall_csv_row(set_name, card)
			rows[str(card)] = row
			counts[str(card)] = 1
		except:
			print(f'lookup failed on {set_name} {card.cn}', flush=True)
			print(traceback.format_exc(), flush=True)

		if i == len(set_cards)-1:
			pbar.set_description_str(f'Card {len(set_cards)} of {len(set_cards)} ')

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

def write_file(out_fn, rows, counts, append=False, card_kingdom=False, exclude_manuals=False):
	with open(out_fn, 'a+' if append else 'w+') as f:
		if not card_kingdom:
			f.write('"Count","Edition","Collector Number","Name","Foil"\n')

		for card, count in sorted(counts.items(), key=nth(1), reverse=True):
			row = f'"{count}",' + rows[card]
			write_row(f, row, count, card_kingdom=card_kingdom)

		if (not card_kingdom) and (not exclude_manuals):
			# Write the manual cards in, too
			for line in ll_lines(ll_read('in/_manual.csv', 'r'))[1:]:
				count = ll_csv_row(line)[0]
				write_row(f, line, count, card_kingdom=card_kingdom)

def main():
	ap = argparse.ArgumentParser()
	ap.add_argument('input_files', nargs='+')
	ap.add_argument('-a', '--append', action='store_true')
	ap.add_argument('-d', '--delay', action='store_true')
	ap.add_argument('-e', '--exclude-manuals', action='store_true')
	ap.add_argument('-o', '--output-set', default='')
	args = ap.parse_args()

	sets = files2sets(args.input_files)
	rows, counts = sets2rows(sets, delay=args.delay)

	if args.output_set:
		for card in sorted(sets[args.output_set], key=lambda c: c.fstr()):
			print(card.fstr())
		quit()

	write_file('out/collection.csv', rows, counts, append=args.append, exclude_manuals=args.exclude_manuals)
	write_file('out/ck_collection.csv', rows, counts, append=args.append, card_kingdom=True, exclude_manuals=True)

if __name__ == '__main__':
	main()
