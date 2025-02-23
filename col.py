import json
import requests
import argparse

from lane import *

def print_collection(set_name, col):
	col = ''.join([c for c in col if c in '.0123456789'])
	nums = ll_cull(col.split('.'))
	failed = []

	print('"Edition","Collector Number","Name"')
	for n in nums:
		url = f'https://api.scryfall.com/cards/{set_name.lower()}/{int(n)}'
		try:
			j = json.loads(requests.get(url).text)
			ed = set_name.upper()
			name = j['name']
			cn = int(n)
			print(f'"{ed}","{cn}","{name}"', flush=True)
		except Exception as e:
			if type(e) == KeyboardInterrupt:
				quit()
			failed.append(url)

	for f in failed:
		print(f)

def read_inp(fn):
	col_file = ll_read(fn)
	lines = ll_lines(col_file)
	set_name = lines[0]
	rest = '.'.join(lines[1:])
	while '..' in rest:
		rest = rest.replace('..', '.')
	
	return set_name, rest

def main():
	ap = argparse.ArgumentParser()
	ap.add_argument('input_file')
	args = ap.parse_args()

	print_collection(*read_inp(args.input_file))

if __name__ == '__main__':
	main()
