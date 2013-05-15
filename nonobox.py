#!/usr/bin/python
# -*- coding: utf-8 -*-
# python version of stool (originally written for bash and sed)

""" 
Nonobox 0.3: companion tool for searches in SIL Toolbox-formatted databases
Copyright (C) 2013 Rafael Bezerra Nonato [rafaeln@gmail.com]

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# to do list
#		search from multiple sources

import re
import codecs
from Tkinter import *
from tkFileDialog import askopenfilename

standard_directory = "~/Dropbox/linguistica/kisedje/ks-toolbox"

def nl_dos_linux(lines): 
	""" for converting \r\n into \n """
	dos_line_find = re.compile(r'\r', re.UNICODE)
	output = []
	for line in lines:
		output.append(dos_line_find.sub('', line))
	return output

def align_toolbox(field): 
	""" for aligning glossed toolbox entries """
	one_space_chars = u'[ãâáôóõêéũĩíç]' # if a word has one of those letters, one space will be added after it 
	one_space_find = re.compile(one_space_chars, re.UNICODE|re.IGNORECASE)
	two_space_chars = u'[ẽỹ]' # if a word has one of those letters, two spaces will be added after it
	two_space_find = re.compile(two_space_chars, re.UNICODE|re.IGNORECASE)
	space_chars = r' ' # spaces 
	space_find = re.compile(space_chars, re.UNICODE)

	word_separation_pattern = re.compile(ur'(\S+)', re.UNICODE)
	chunked_field = word_separation_pattern.split(field)
	
	out_field = '' # initializes the field to be returned
	for i in range(len(chunked_field)-1):
		if space_find.match(chunked_field[i+1]):
			extra_spaces = len(one_space_find.findall(chunked_field[i])) + len(two_space_find.findall(chunked_field[i])) * 2
			chunked_field[i+1] += ' ' * extra_spaces
		out_field += chunked_field[i] 

	return out_field

def open_database(filename):
	""" opens the database and returns a list of (linux) lines (I'm not closing the file. 
	 Though I don't know if I actually need to) """
	with codecs.open(filename, encoding = 'utf-8') as openfile:
		lines = openfile.readlines()
	return lines

def search_database(lines, register_separator, pattern): 
	""" for searching and printing fields that match """
	# creates the search objects
	register_find = re.compile(register_separator, re.UNICODE)
	pattern_find = re.compile(pattern, re.UNICODE)
	glossed_find = re.compile(r'\\mb')

	output = '' # initializes the output
	line_number = 0 
	while line_number < len(lines): # goes through all the lines 
		if register_find.search(lines[line_number]): # found for the beginning of a field
			field = lines[line_number] # initializes the field
			line_number += 1
			while line_number < len(lines) and not register_find.search(lines[line_number]):
				field += lines[line_number]
				line_number += 1
			if pattern_find.search(field):
				if glossed_find.search(field):
					output += align_toolbox(field) + '\n\n'
				else:
					output += field
		else:
			line_number += 1

	return output

def search_aligned(lines, register_separator, pattern1, pattern2): 
	""" for searching and printing fields that match """
	# creates the search objects
	register_find = re.compile(register_separator, re.UNICODE)
	pattern1_find = re.compile(pattern1, re.UNICODE)
	pattern2_find = re.compile(pattern2, re.UNICODE)
	glossed_find = re.compile(r'\\mb', re.UNICODE)
	nl_find = re.compile(r'(\n)', re.UNICODE)

	output = '' # initializes the output
	line_number = 0 
	while line_number < len(lines): # goes through all the lines 
		if register_find.search(lines[line_number]): # found for the beginning of a field
			field = lines[line_number] # initializes the field
			line_number += 1
			while line_number < len(lines) and not register_find.search(lines[line_number]):
				field += lines[line_number]
				line_number += 1
			if glossed_find.search(field):
				field = align_toolbox(field) + '\n\n'
			field = nl_find.split(field)
			field_line = 0
			while field_line < len(field):
				found_pattern1 = pattern1_find.search(field[field_line])
				if found_pattern1:
					position_pattern1 = found_pattern1.start()
					for embedded_field_line in range(field_line+1,len(field)):
						found_pattern2 = pattern2_find.search(field[embedded_field_line])
						if found_pattern2:
							position_pattern2 = found_pattern2.start()
							if position_pattern1 == position_pattern2:
								break
					if found_pattern1 and found_pattern2 and position_pattern1 == position_pattern2: 
						output += ''.join(field)
						break
				field_line += 2
		else:
			line_number += 1

	return output

root = Tk()
root.title('Nonobox')
icon = Image("photo", file="nonobox.gif")
root.tk.call('wm', 'iconphoto', root._w, icon)

# sets up the upper part, where the search field is
topFrame = Frame(root)

Label(topFrame, text='Field Marker:').pack(side=LEFT)
edit3 = Entry(topFrame,)
edit3.insert(END, r'\\ref')
edit3.pack(side=LEFT, fill=BOTH)

Label(topFrame, text='Primary Regex:').pack(side=LEFT)
edit1 = Entry(topFrame)
edit1.pack(side=LEFT, fill=BOTH)
edit1.focus_set()

Label(topFrame, text='Aligned Regex:').pack(side=LEFT)
edit2 = Entry(topFrame)
edit2.pack(side=LEFT, fill=BOTH)

button1 = Button(topFrame, text='Find Primary')
button1.pack(side=LEFT)

button2 = Button(topFrame, text='Find Primary + Aligned')
button2.pack(side=LEFT)

button3 = Button(topFrame, text='Open other file...')
button3.pack(side=LEFT)

button4 = Button(topFrame, text='Latexize')
button4.pack(side=LEFT)

topFrame.pack(side=TOP, anchor=W, expand=YES, fill=BOTH) #, anchor=W, expand=YES, fill=BOTH)

#sets up the lower part, where the text is
bottomFrame = Frame(root)
scroll = Scrollbar(bottomFrame)
text = Text(bottomFrame)

scroll.pack(side=RIGHT, fill=Y)
text.config(width=180, height=50, tabs=30)
text.pack(side=LEFT, expand=YES, fill=BOTH)
bottomFrame.pack(side=BOTTOM, expand=YES, fill=BOTH)

# sets up the scrolling things
scroll.config(command=text.yview)
text.config(yscrollcommand=scroll.set)

class onscreen(object):
	""" this class is for storing the text on the screen for delatexizing """
	text = ''
	tags = []

def get_field_marker():
	""" this gets the field marker, obvious, huh? """
	register_separator = edit3.get()
	return register_separator

def resize(result, text_widget):
	""" resizes the a text widget to fit all lines without wrapping """
	max_size = 180 # maximum window size
	line_separation_pattern = re.compile('\n', re.UNICODE)
	lines_result = line_separation_pattern.split(result)
	if result: 
		width_widest_line = min(max_size, max([len(line_result) for line_result in lines_result]))
		text_widget.config(width = width_widest_line)

def find(*ignore): 
	""" for getting the entry and doing a search """
	pattern = edit1.get()
	register_separator = get_field_marker()
	if pattern:
		lines = nl_dos_linux(open_database(filename))
		result = search_database(lines, register_separator, pattern)

		text.delete(0.0, END)
		text.insert(END, result)
		resize(result, text)

		# this far I only got the matches and put them in the text box. Now I'll count the matches and highlight them 
		text.tag_remove('found', '1.0', END)
		idx = '1.0'
		num_matches = 0
		count = IntVar()
		while True:
			idx = text.search(pattern, idx, nocase=True, stopindex=END, regexp=True, count=count)
			if not idx: break
			lastidx = '%s+%dc' % (idx, count.get())
			text.tag_add('found', idx, lastidx)
			idx = lastidx
			num_matches += 1
		text.tag_config('found', foreground='red')
		root.title('Nonobox - ' + filename + ' (' + str(num_matches) + ' matches)')

		edit1.focus_set()

def find_aligned(*ignore): 
	""" for getting the entry and doing a search """
	register_separator = get_field_marker()
	pattern1 = edit1.get()
	pattern2 = edit2.get()
	if pattern1 and pattern2:
		lines = nl_dos_linux(open_database(filename))
		result = search_aligned(lines, register_separator, pattern1, pattern2)

		text.delete(0.0, END)
		text.insert(END, result)
		resize(result, text)

		# this far I only got the matches and put them in the text box. Now I'll count the matches and highlight them.
		text.tag_remove('found', '1.0', END)
		idx = '1.0'
		num_matches = 0
		count = IntVar()
		count2 = IntVar()
		while True:
			idx = text.search(pattern1, idx, nocase=True, stopindex=END, regexp=True, count=count)
			if idx:
				idx2 = idx + ' + 1 char' 
				idx2 = text.search(pattern2, idx2, nocase=True, stopindex=END, regexp=True, count=count2)
				num_matches += 1
			else: 
				break
			lastidx = '%s+%dc' % (idx, count.get())
			lastidx2 = '%s+%dc' % (idx2, count2.get())
			idx_column = idx.split('.')[1]
			idx2_column = idx2.split('.')[1]
				
			if idx2_column == idx_column:
				text.tag_add('found', idx, lastidx)
				text.tag_add('found', idx2, lastidx2)
			idx = lastidx
		text.tag_config('found', foreground='red')
		root.title('Nonobox - ' + filename + ' (' + str(num_matches) + ' matches)')

		edit1.focus_set()

def dialog_file():
	""" opens the file selection dialogue """
	global filename 
	new_file = False
	while not new_file:
		new_file = askopenfilename(title='Open your database file', initialdir=standard_directory)
	filename = new_file
	root.title('Nonobox - ' + filename)

def latexize():
	"""	converts the text on the screen for latex use """
	global onscreen
	onscreen.text = text.get(0.0,END)
	onscreen.tags = text.tag_ranges('found')
	latex_text = re.sub(r' +', ' ', onscreen.text)
	latex_text = re.sub(r'^(\\ref)', r'%\1', latex_text, flags=re.MULTILINE)
	latex_text = re.sub(r'^(\\nt)', r'%\1', latex_text, flags=re.MULTILINE)
	latex_text = re.sub(r'^\\tx(.*)', r'\\ex.\1', latex_text, flags=re.MULTILINE)
	latex_text = re.sub(r'^\\mb (.*)', r'\\glll \1 \\\\', latex_text, flags=re.MULTILINE)
	latex_text = re.sub(r'^\\gn (.*)', r'\t\1 \\\\', latex_text, flags=re.MULTILINE)
	latex_text = re.sub(r'^\\ps (.*)', r'\t\1 \\\\', latex_text, flags=re.MULTILINE)
	latex_text = re.sub(r'\n\n(\\tn.*)', r'\n\1', latex_text, flags=re.MULTILINE)
	latex_text = re.sub(r'^\\tn(.*)', r'\\glt\1', latex_text, flags=re.MULTILINE)
	text.delete(0.0, END)
	text.insert(END, latex_text)
	resize(latex_text, text)
	button4.config(text = 'Delatexize', command=delatexize)

def delatexize():
	""" brings the original text back, after having converted to latex """
	text.delete(0.0, END)
	text.insert(END, onscreen.text)
	tags_begin = onscreen.tags[0::2]
	tags_end = onscreen.tags[1::2]
	for tag_begin, tag_end in zip(tags_begin,tags_end):
		text.tag_add('found',tag_begin,tag_end)
	resize(onscreen.text, text)
	button4.config(text = 'Latexize', command=latexize)

button1.config(command=find)
edit1.bind('<Return>', find)

button2.config(command=find_aligned)
edit2.bind('<Return>', find_aligned)

button3.config(command=dialog_file)
button4.config(command=latexize)

dialog_file()

root.mainloop()