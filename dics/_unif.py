import os

text = ''
with open('rae.txt', 'w', encoding='utf-8') as file:
	for doc in os.listdir('dics'):
		if doc[-4:] == '.txt':
			with open('dics/'+doc, encoding='utf-8') as file_read:
				for row in file_read:
					if ',' in row:
						row = ''.join([i for i in row if not i.isdigit()]).split(',')[0][:-1]
						text += (row+'o\n')
						text += (row+'a\n')
					else:
						text += ''.join([i for i in row if not i.isdigit()])
		
	file.write(text)

print(os.listdir('dics'))