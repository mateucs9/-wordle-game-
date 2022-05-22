import re
import tkinter as tk
from random import random, sample
import fnmatch
import unidecode
from string import ascii_uppercase
from PIL import Image, ImageTk


class Wordle(tk.Tk):
	def __init__(self):
		tk.Tk.__init__(self)
		self.geometry('900x900')
		self.title('Wordle')
		self.resizable(0, 0)
		self.bg_color = 'white'
		self.config(bg=self.bg_color, padx=20, pady=20)
		self.bind('<Any-KeyPress>', self.on_key_press)
		self.max_length = 8
		self.initial_cell = 3
		self.attempts = 6
		self.large_font = ('Calbri', 48, 'bold')
		self.medium_font = ('Calbri', 24, 'bold')
		self.small_font = ('Calbri', 12)
		self.get_playing_screen()

	def get_playing_screen(self):
		# Clearing the screen just in case and we create a new frame
		for widget in self.winfo_children():
			widget.destroy()
		self.main_frame = tk.Frame(self, bg=self.bg_color)
		self.main_frame.pack(fill='both', expand='true')

		self.word = self.get_word()
		self.cell = self.initial_cell
		self.available_row = self.initial_cell
		self.guessed_word = ''

		# This will make all the rows and columns with the same size
		[self.main_frame.rowconfigure(i, weight=1) for i in range(100)]
		[self.main_frame.columnconfigure(i, weight=1)
		 for i in range(self.word_len)]

		# Game header
		tk.Label(self.main_frame, text='WORDLE', font=self.large_font,
				 bg=self.bg_color).grid(row=0, columnspan=self.word_len)

		# Creating label that we will use to display errors and additional info
		self.info_lbl = tk.Label(self.main_frame, text='',
								 font=self.small_font, bg=self.bg_color, wraplength=700)
		self.info_lbl.grid(row=1, column=0, rowspan=2,
						   columnspan=self.word_len, sticky='nsew', pady=10)
		self.update_info_label()

		# Creating grid with labels where game will be played and characters will be inserted into
		for row in range(self.initial_cell, self.attempts+3):
			for col in range(self.word_len):
				tk.Label(self.main_frame, text='A', relief='solid', borderwidth=1, font=self.large_font,
						 bg=self.bg_color, fg=self.bg_color).grid(row=row, column=col, sticky='ew', padx=2, pady=5)

		# Creating letters frame where where we will show the status of each letter (green if right position, orange for right character, gray for not in the word)
		self.letters_frame = tk.Frame(self.main_frame, bg=self.bg_color)
		self.letters_frame.grid(row=self.attempts+3, column=0,
								rowspan=2, columnspan=self.word_len, sticky='nsew', pady=5)
		row = 0
		col = 0
		[self.letters_frame.rowconfigure(i, weight=1) for i in range(100)]
		[self.letters_frame.columnconfigure(i, weight=1)
		 for i in range(int(len(list(ascii_uppercase))/2))]
		for ch in list(ascii_uppercase):
			tk.Label(self.letters_frame, text=ch, font=self.medium_font, bg=self.bg_color,
					 borderwidth=1, relief='solid').grid(row=row, column=col, sticky='nsew')
			if col == len(list(ascii_uppercase))/2-1:
				col = 0
				row += 1
			else:
				col += 1

		# Button to submit each guess, but the key button "Return" does the same
		buttons_frame = tk.Frame(self.main_frame, bg=self.bg_color)
		buttons_frame.grid(row=self.attempts+5, column=0,
						   columnspan=100, sticky='nsew', pady=20)
		tk.Button(buttons_frame, text='Check Word', command=self.return_pressed,
				  font=self.medium_font).grid(row=0, column=0, sticky='ew', padx=(200, 0))

		# Button to get hint
		image = Image.open("hint.png").resize((30, 30), Image.ANTIALIAS)
		self.photo = ImageTk.PhotoImage(image)
		tk.Button(buttons_frame, text='  Get hint', command=self.get_hint, font=self.medium_font,
				  image=self.photo, compound='left').grid(row=0, column=1, padx=20, ipadx=20, sticky='ew')

	def on_key_press(self, event):
		key_pressed = event.keysym
		self.update_label_ref()

		if key_pressed == 'Return':
			self.return_pressed()
		else:
			if re.match('^[a-zA-Z]$', key_pressed) != None:
				if self.cur_row != self.available_row:
					self.info_lbl.configure(
						text='Try to check first if the word is valid', fg='red')
				else:
					self.add_cell(key_pressed)

			elif key_pressed == 'BackSpace':
				if self.prev_row == self.available_row:
					self.delete_cell()

			elif key_pressed == 'Return':
				print(key_pressed)

		# This will update the cell reference regarding current cell and previous cell
	def update_label_ref(self):
		prev_cell = 3 if self.cell == 3 else self.cell - 1

		if self.check_label_exists(prev_cell):
			self.previous_lbl = self.main_frame.children['!label{}'.format(
				prev_cell)]
			self.prev_row = self.previous_lbl.grid_info()['row']

		if self.check_label_exists(self.cell):
			self.current_lbl = self.main_frame.children['!label{}'.format(
				self.cell)]
			self.cur_row = self.current_lbl.grid_info()['row']

		# This will validate if the guessed word is right
	def return_pressed(self):
		if len(self.guessed_word) != self.word_len:
			self.info_lbl.configure(text='You are still missing {} characters'.format(
				self.word_len-len(self.guessed_word)), fg='red')
		else:
			if self.guessed_word.upper() == self.word.upper() or self.attempts == self.available_row-2:
				self.end_game()
				return

			self.check_word()

			self.available_row += 1
			self.guessed_word = ''

		# We will get all words and we will randomly pick one
	def get_word(self):
		self.all_words = self.get_all_words()

		# We take a random word out of the of all the available words
		self.word = self.all_words[int(random()*len(self.all_words))]
		self.word_len = len(self.word)

		# We get the first filter out of all the words, by filtering those with same length as desired word
		self.possible_words = list(
			filter(lambda x: len(x) == len(self.word), self.all_words))
		self.possibilities = len(self.possible_words)

		return self.word

		# This will add the character from the key pressed into the current label and it will move onto the next one
	def add_cell(self, letter):
		self.current_lbl.configure(text=letter.upper(), fg='black')

		self.cell += 1
		self.guessed_word += letter.upper()
		self.update_info_label()

		# This will delete the character from the previous label, so we can write again in that cell
	def delete_cell(self):
		if self.cell > self.initial_cell:
			self.previous_lbl.configure(text='', fg='black')

			self.cell -= 1
			self.guessed_word = self.guessed_word[:-1]
			self.update_info_label()

		# It will check if the character matches any of the logic and it will apply the corresponding color.
	def check_word(self):
		for index, char in enumerate(self.guessed_word):
			# Right character and position
			if char == self.word[index].upper():
				self.color_character(char, 'green')
				self.main_frame.children['!label{}'.format(
					(self.available_row-3)*(self.word_len)+(index+1)+2)].configure(bg='green')
			# Right character but wrong position
			elif char in self.word.upper():
				self.color_character(char, 'orange')
				self.main_frame.children['!label{}'.format(
					(self.available_row-3)*(self.word_len)+(index+1)+2)].configure(bg='orange')
			# Character not found in word
			else:
				self.color_character(char, 'gray')
				self.main_frame.children['!label{}'.format(
					(self.available_row-3)*(self.word_len)+(index+1)+2)].configure(bg='gray')
		
		# This will narrow the possibilities, so we can get better hints
		self.filter_possibilities()
		
		# It will update the message label to show the current guess
		self.update_info_label()

	def update_info_label(self):
		self.info_lbl.configure(text='Try to guess the word. Your current guess is: {}'.format(
			self.guessed_word), fg='black')

	def get_all_words(self):
		# We get all the words from the txt
		all_words = list(open('rae.txt', encoding='utf-8'))

		# We remove all the line breaks
		all_words = list(map(lambda x: x.strip('\n'), all_words))

		# We remove all the words with non alphabet characters
		all_words = list(filter(lambda x: x.isalpha(), all_words))

		# To simplify the game, we remove all the words above certain length
		# all_words = list(filter(lambda x: len(x) <= self.max_length, all_words))
		all_words = list(filter(lambda x: len(x) == 5, all_words))

		# We remove the ñ, since not everybody would have access to it
		all_words = list(
			filter(lambda x: not re.compile('ñ').findall(x), all_words))

		# We remove all the accents
		all_words = list(map(lambda x: unidecode.unidecode(x), all_words))

		return all_words

	def check_label_exists(self, cell):
		return '!label{}'.format(cell) in self.main_frame.children.keys()

	def filter_possibilities(self):
		hit_list = []
		maybe_list = []
		not_list = []
		guess = list(self.guessed_word.lower())

		for index, ch in enumerate(self.guessed_word):
			if ch == self.word.upper()[index]:
				hit_list.append(ch.lower())
				guess.remove(ch.lower())
			else:
				hit_list.append('?')

		for ch in guess:
			if ch in self.word:
				maybe_list.append(ch)
			else:
				not_list.append(ch)

		# This will filter based those characters for which, we know both the character and the position
		self.possible_words = fnmatch.filter(
			self.possible_words, ''.join(hit_list))

		# This will filter based on characters on the word but not in the exact position
		for ch in maybe_list:
			self.possible_words = list(
				filter(lambda x: re.compile(ch).findall(x), self.possible_words))

		# This will filter out the characters we know that are not in the word
		for ch in not_list:
			self.possible_words = list(
				filter(lambda x: not re.compile(ch).findall(x), self.possible_words))

		self.possibilities = len(self.possible_words)

	def end_game(self):
		# This will clear out the screen
		for widget in self.main_frame.winfo_children():
			widget.destroy()

		# If the guessed word matches the desired word, it will display a message or other
		if self.guessed_word.upper() == self.word.upper():
			tk.Label(self.main_frame, text='You won!!', font=self.large_font,
					 fg='green', bg=self.bg_color).pack(expand=True)
		else:
			tk.Label(self.main_frame, text='Game Over - It was {}'.format(self.word),
					 font=self.large_font, fg='red', bg=self.bg_color, wraplength=700).pack(expand=True)

		tk.Button(self.main_frame, text='Play Again', font=self.medium_font,
				  relief='groove', command=self.get_playing_screen).pack()

	# This will add color into the alphabet summary, so you can avoid to place wrong characters again
	def color_character(self, char, color):
		for widget in self.letters_frame.winfo_children():
			if widget['text'] == char and widget['background'] == self.bg_color:
				print(widget['background'])
				widget.configure(bg=color)

	def get_hint(self):
		possible_options = self.possibilities if self.possibilities < 10 else 10
		self.info_lbl.configure(text='There are still {:,.0f} possibilities. {} random possibilites are: {}'.format(
			self.possibilities, possible_options, sample(self.possible_words, possible_options), fg='black'))


app = Wordle()
app.mainloop()
