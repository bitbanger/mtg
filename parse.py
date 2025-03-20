from card import Card
from collections import defaultdict
from lane import *
from tqdm import tqdm
from typing import List, Dict

# e.g., parse_card('FDN', '7 token foil')
# 				-> Card('TFDN', '7', token=True, foil=True)
def parse_card(sc: str, s: str) -> Card:
	spl = ll_split(s)
	cn = spl[0]
	token = 'token' in spl
	foil = 'foil' in spl

	return Card(sc, cn, token=token, foil=foil)


def _line2set(sc: str, l: str) -> List[Card]:
	return [parse_card(sc, c) for c in ll_split(l, delim='.')]


def load_input(fn: str) -> Dict[str, List[Card]]:
	sets = dict()
	for i, line in enumerate(ls:=ll_lines(fn)):
		if len(line) == 3 and not line.isnumeric():
			sets[line] = _line2set(line, ls[i+1])
	
	return sets

def load_output(fn: str) -> Dict[str, List[Card]]:
	sets = defaultdict(list)
	if len(ls:=ll_lines(fn)) > 100:
		ls = tqdm(ls)
	for i, l in enumerate(ls):
		if i == 0:
			continue
		count, sc, cn, name, foil = ll_csv_row(l)
		if cn.isnumeric():
			sets[sc].append(Card(sc, int(cn), foil=foil, name=name))
	
	return sets
