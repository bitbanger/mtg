import argparse
import os

from card import Card
from lane import *
from parse import *
from tqdm import tqdm

def color(price):
	price_min = 0.01
	price_max = 20.0
	col_min = (100,100,100)
	col_max = (0,255,0)

	scale = (price-price_min)/(price_max-price_min)
	r, g, b = [int(col_min[i] + (col_max[i]-col_min[i]) * scale) for i in range(3)]
	def cap(f):
		return max(0, min(255, f))
	return (cap(r), cap(g), cap(b))


def process(sets):
	cards = [c for s in sets.values() for c in s]
	cards = sorted(cards, key=lambda c: c.price())
	total = sum(c.price() for c in cards)
	for i, card in enumerate(cards):
		if i > 0:
			print('')
		col = color(card.price())
		r,g,b=col
		zeroes = max(0, 4-len(str(card.cn))) * f'\033[38;2;50;50;50m0\033[38;2;{r};{g};{b}m'
		cprint(col, '$%.2f\t(%s %s%d)\t%s%s' % (card.price(), card.set_code, zeroes, card.cn, "(foil) " if card.foil else '', card.name()))
		pass
	print('')
	print('$%.2f\tTOTAL' % total)

def main():
	ap = argparse.ArgumentParser()
	ap.add_argument('file')
	args = ap.parse_args()
	process(load_input(args.file))

	try:
		process(load_output(args.file))
	except:
		try:
			process(load_input(args.file))
		except:
			print('Sorry, invalid file :(')


if __name__ == '__main__':
	main()
