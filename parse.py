import json
from collections import defaultdict

board = None
with open('trello.json', 'r') as file:
    board = json.loads(file.read())

cards = board['cards']
lists = board['lists']

list_id_to_name = {}
list_names_to_pos = {}
for _list in lists:
    if _list['closed']:
        continue
    list_id_to_name[_list['id']] = _list['name']
    list_names_to_pos[_list['name']] = _list['pos']

keyset = set(str())
cards_cleaned = []
for card in cards:
    votes = 0
    if 'votes' in card['badges']:
        votes = card['badges']['votes']

    if votes == 0:
        continue

    cards_cleaned.append(
        {
            'name': card['name'],
            'list': list_id_to_name[card['idList']],
            'votes': votes
        }
    )

# separate by list
list_to_cards = defaultdict(list)
for card in cards_cleaned:
    list_to_cards[card['list']].append(card)

for list_name in list(list_to_cards.keys()):
    list_to_cards[list_name] = sorted(
        list_to_cards[list_name],
        key=lambda x: x['votes'],
        reverse=True
    )

with open('trello.csv', 'w') as file:
    list_names = list(list_to_cards.keys())
    list_names = sorted(list_names, key=lambda x: int(list_names_to_pos[x]))

    header = ''
    for list_name in list_names:
        header += 'votes,{},'.format(list_name.encode('utf-8'))
    header = header[:-1] + '\n'

    file.write(header)

    row_index = 0
    rows = []
    while True:
        row = []
        none_counter = 0
        for list_name in list_names:
            list_cards = list_to_cards[list_name]
            if row_index < len(list_cards):
                card = list_cards[row_index]
            else:
                card = None
                none_counter += 1
            row.append(card)

        if none_counter == len(list_names):
            break
        else:
            rows.append(row)

        row_index += 1

    for row in rows:
        row_str = ''
        for item in row:
            if item is None:
                row_str += ',,'
            else:
                row_str += '{},"{}",'.format(
                    item['votes'],
                    item['name'].encode('utf-8').replace('"', '\'')
                )

        row_str = row_str[:-1] + '\n'
        file.write(row_str)
