import vobject

with open('/Users/phildini/Desktop/sort_me/all.vcf', 'r') as f:
    count = 0
    cards = []
    current_lines = []
    possible_keys = set()
    for line in f:
        if line.strip() == 'END:VCARD':
            current_lines.append(line)
            card = ''.join(current_lines)
            cards.append(card)
            count += 1
            current_lines = []
        else:
            current_lines.append(line)
    for card in cards:
        v = vobject.readOne(card)
        possible_keys.update(v.contents.keys())
        try:
            print(str(v.adr.value))
        except:
            pass
        try:
            print(str(v.email.value))
        except:
            pass
        try:
            print(str(v.n.value))
        except:
            pass
        try:
            print(str(v.url.value))
        except:
            pass
        try:
            print(str(v.bday.value))
        except:
            pass
print(possible_keys)