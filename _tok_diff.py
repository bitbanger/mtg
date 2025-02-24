from lane import *

fdn = ll_lines(ll_read('fdn.txt'))[1].split('.')
toks = ll_lines(ll_read('toks.txt'))[0].split('.')

for tok in toks:
	fdn.remove(tok)

print('.'.join(fdn))
quit()
print('.'.join(fdn) + '.' + '.'.join([f'{cn} tok' for cn in toks]))
