import json
import requests
import sys

from lane import *

def price(sc, cn, foil=False):
	if not os.path.exists('cache'):
		os.mkdir('cache')

	url = f'https://api.scryfall.com/cards/{sc.lower()}/{cn}'

	cache_fn = f'{ll_md5(url)}.json'
	if False and (cache_fn := f'{ll_md5(url)}.json') in os.listdir('cache'):
		j = json.loads(ll_read(f'cache/{cache_fn}'))
	else:
		j = json.loads(jt := requests.get(url).text)
		ll_write(f'cache/{cache_fn}', jt)

	return float(j['prices']['usd_foil']) if foil else float(j['prices']['usd']), j['name']


def main():
	total = 0.0
	for p, _ in (ps:=[price(*ll_split(line)) for line in ll_lines(sys.stdin.read())]):
		total += p
	print('TOTAL: $%.2f\n' % total)
	for t in sorted(ps, key=nth(0), reverse=True):
		print('\t$%.2f\t\t%s' % t)

if __name__ == '__main__':
	main()
