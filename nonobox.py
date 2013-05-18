#!/usr/bin/python
# -*- coding: utf-8 -*-
# python version of stool (originally written for bash and sed)

""" 
Nonobox 0.4.6: companion tool for searches in SIL Toolbox-formatted databases
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

def nl_dos_linux(line): 
	""" for converting a line that ends \r\n into a line that ends in \n """
	dos_line_find = re.compile(r'\r', re.UNICODE)
	out_line = dos_line_find.sub('', line)
	return out_line

def fix_toolbox(lines): 
	""" for aligning toolbox databases (defined over lists of strings) """
	tx_find = re.compile(r'\\tx', re.UNICODE)
	mb_find = re.compile(r'\\mb', re.UNICODE)
	desaligned_find = re.compile(r'\\(mb|gn|ps)', re.UNICODE)
	dos_line_find = re.compile(r'\r', re.UNICODE)

	out_lines = [] # initializes the lines to be returned
	for line_number in range(len(lines)):
		lines[line_number] = nl_dos_linux(lines[line_number])
		if tx_find.search(lines[line_number]) and mb_find.search(lines[line_number+1]):
			out_lines.append(align_line(lines[line_number]))
		elif desaligned_find.search(lines[line_number]):
			out_lines.append(align_line(lines[line_number]))
		else:
			out_lines.append(lines[line_number])
	return out_lines

def align_line(line):
	""" for aligning a single line that has been identified as desaligned """
	one_space_find = re.compile(u'[ãâáôóõêéũĩíç]', re.UNICODE|re.IGNORECASE)
	two_space_find = re.compile(u'[ẽỹ]', re.UNICODE|re.IGNORECASE)
	space_find = re.compile(r' ', re.UNICODE)
	word_separation_pattern = re.compile(ur'(\S+)', re.UNICODE)
	chunked_line = word_separation_pattern.split(line)

	out_line = ''
	for i in range(len(chunked_line)-1):
		if space_find.match(chunked_line[i+1]):
			extra_spaces = len(one_space_find.findall(chunked_line[i])) + len(two_space_find.findall(chunked_line[i])) * 2
			chunked_line[i+1] += ' ' * extra_spaces
		out_line += chunked_line[i] 
	return out_line + '\n'

def open_database(filename):
	""" opens the database and returns a list of lines (I'm not closing the file. 
	 Though I don't know if I actually need to) """
	with codecs.open(filename, encoding = 'utf-8') as openfile:
		lines = fix_toolbox(openfile.readlines())
	return lines

def search_database(lines, register_separator, pattern): 
	""" for searching and printing fields that match """
	# creates the search objects
	register_find = re.compile(register_separator, re.UNICODE)
	pattern_find = re.compile(pattern, re.UNICODE)

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
				output += field
		else:
			line_number += 1

	return output

def search_aligned(lines, register_separator, pattern1, pattern2): 
	""" for searching and printing fields that match """
	# creates the search objects
	register = re.compile(register_separator, re.UNICODE)
	pattern1 = re.compile(pattern1, re.UNICODE)
	pattern2 = re.compile(pattern2, re.UNICODE)

	output = '' # initializes the output
	line_number = 0 
	while line_number < len(lines): # goes through all the lines 
		if register.search(lines[line_number]): # found for the beginning of a field
			field = [] # initializes the field
			field.append(lines[line_number]) 
			line_number += 1
			while line_number < len(lines) and not register.search(lines[line_number]): # builds the rest of field
				field.append(lines[line_number])
				line_number += 1
			found_pattern1 = set()
			for match_object_list in { pattern1.finditer(field_line) for field_line in field }:
				for match_object in match_object_list:
					found_pattern1.add(match_object)
			found_pattern2 = set()
			for match_object_list in { pattern2.finditer(field_line) for field_line in field }:
				for match_object in match_object_list:
					found_pattern2.add(match_object)
			if found_pattern1:
				positions_pattern1 = { x.start() for x in found_pattern1 }
				if found_pattern2:
					positions_pattern2 = { x.start() for x in found_pattern2 }
					if positions_pattern1 & positions_pattern2:
						output += ''.join(field)
		else:
			line_number += 1

	return output

root = Tk()
root.title('Nonobox')
icon = Image("photo", file="nonobox.gif")
root.tk.call('wm', 'iconphoto', root._w, icon)

# sets up the upper bar, with the fields
topFrame = Frame(root)

Label(topFrame, text='Field Marker:').pack(side=LEFT)
fieldMarker = Entry(topFrame,)
fieldMarker.insert(END, r'\\ref')
fieldMarker.pack(side=LEFT, fill=BOTH)

Label(topFrame, text='Regex:').pack(side=LEFT)
regex1 = Entry(topFrame)
regex1.pack(side=LEFT, fill=BOTH)
regex1.focus_set()

Label(topFrame, text='Aligned Regex:').pack(side=LEFT)
alignedregex = Entry(topFrame)
alignedregex.pack(side=LEFT, fill=BOTH)

topFrame.pack(side=TOP, anchor=S, expand=YES, fill=BOTH) #, anchor=W, expand=YES, fill=BOTH)

# sets the lower bar, with the buttons
interFrame = Frame(root)

buttonFind1 = Button(interFrame, text='Find Regex')
buttonFind1.pack(side=LEFT)

buttonFindAligned = Button(interFrame, text='Find Regex + Aligned Regex')
buttonFindAligned.pack(side=LEFT)

checkInResults = IntVar()
Checkbutton(interFrame, text = 'Search in results', variable = checkInResults).pack(side=LEFT, padx=5)

buttonLatex = Button(interFrame, text='Latexize')
buttonLatex.pack(side=LEFT)

buttonHighlight = Button(interFrame, text='Highlight')
buttonHighlight.pack(side=LEFT)

buttonOpen = Button(interFrame, text='Open other file...')
buttonOpen.pack(side=LEFT)

interFrame.pack(side=TOP, anchor=S, expand=YES, fill=BOTH) #, anchor=W, expand=YES, fill=BOTH)

#sets up the lower part, where the text is
bottomFrame = Frame(root)
scroll = Scrollbar(bottomFrame)
text = Text(bottomFrame)

scroll.pack(side=RIGHT, fill=Y)
text.config(width=90, height=30, tabs=30)
text.pack(side=LEFT, expand=YES, fill=BOTH)
bottomFrame.pack(side=TOP, expand=YES, fill=BOTH)

# sets up the scrolling things
scroll.config(command=text.yview)
text.config(yscrollcommand=scroll.set)

class onscreen(object):
	""" this class is for storing the text on the screen for delatexizing """
	text = ''
	tags = []

def get_field_marker():
	""" this gets the field marker, obvious, huh? """
	register_separator = fieldMarker.get()
	return register_separator

def resize(result, text_widget):
	""" resizes the a text widget to fit all lines without wrapping """
	max_size = 180 # maximum window size
	line_separation_pattern = re.compile('\n', re.UNICODE)
	lines_result = line_separation_pattern.split(result)
	if result: 
		width_widest_line = min(max_size, max({len(line_result) for line_result in lines_result}))
		text_widget.config(width = width_widest_line)

def find(*ignore): 
	""" for getting the entry and doing a search """
	pattern = regex1.get()
	register_separator = get_field_marker()
	if pattern:
		if not checkInResults.get():
			lines = open_database(filename)
		else:
			lines = text.get(0.0, END).splitlines(True)
		result = search_database(lines, register_separator, pattern)

		text.delete(0.0, END)
		text.insert(END, result)
		resize(result, text)

		# this far I only got the matches and put them in the text box. Now I'll count the matches and highlight them 
		text.tag_remove('found', '1.0', END)
		idx = '1.0'
		num_matches = 0
		length_match = IntVar()
		while True:
			idx = text.search(pattern, idx, stopindex=END, regexp=True, count=length_match)
			if not idx: break
			lastidx = '%s+%dc' % (idx, length_match.get())
			text.tag_add('found', idx, lastidx)
			idx = lastidx
			num_matches += 1
		text.tag_config('found', foreground='red')
		root.title('Nonobox - ' + filename + ' (' + str(num_matches) + ' matches)')

		regex1.focus_set()

def find_aligned(*ignore): 
	""" for getting the entry and doing a search """
	register_separator = get_field_marker()
	pattern1 = regex1.get()
	pattern2 = alignedregex.get()
	if pattern1 and pattern2:
		if not checkInResults.get():
			lines = open_database(filename)
		else:
			lines = text.get(0.0, END).splitlines(True)

		result = search_aligned(lines, register_separator, pattern1, pattern2)

		text.delete(0.0, END)
		text.insert(END, result)
		resize(result, text)

		# this far I only got the matches and put them in the text box. Now I'll find where they are
		text.tag_remove('found', '1.0', END)
		index = [ '1.0', '1.0' ]
		indexes = [ [ ], [ ] ]
		length_match = [ IntVar(), IntVar() ]
		length_matches = [ [ ], [ ] ]
		while True:
			index[0] = text.search(pattern1, index[0], stopindex=END, regexp=True, count=length_match[0])
			if index[0]:
				indexes[0].append(index[0])
				length_matches[0].append(length_match[0].get())
				if length_match[0].get():
					index[0] = '%s + %d char' % (index[0], length_match[0].get())
				else:
					index[0] = '%s + 1 char' % (index[0])
			else: 
				break
		while True:
			index[1] = text.search(pattern2, index[1], stopindex=END, regexp=True, count=length_match[1])
			if index[1]:
				indexes[1].append(index[1])
				length_matches[1].append(length_match[1].get())
				if length_match[1].get():
					index[1] = '%s + %d char' % (index[1], length_match[1].get())
				else:
					index[1] = '%s + 1 char' % (index[1])
			else:
				break

		# and here I will find which ones are aligned and mark them, and also count the matches
		num_matches = 0
		for idx in indexes[0]:
			for num in range(1,4):
				tentative_line = int(idx.split('.')[0]) + num
				idx_column = idx.split('.')[1]
				tentative_index = '%s.%s' % (tentative_line, idx_column)
				if tentative_index in indexes[1]:
					lastidx0 = '%s + %d chars' % (idx, length_matches[0][indexes[0].index(idx)])
					lastidx1 = '%s + %d chars' % (tentative_index, length_matches[1][indexes[1].index(tentative_index)])
					text.tag_add('found', idx, lastidx0)
					text.tag_add('found', tentative_index, lastidx1)
					num_matches += 1

		text.tag_config('found', foreground='red')
		root.title('Nonobox - ' + filename + ' (' + str(num_matches) + ' matches)')

		regex1.focus_set()

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
	buttonLatex.config(text = 'Delatexize', command=delatexize)

def delatexize():
	""" brings the original text back, after having converted to latex """
	text.delete(0.0, END)
	text.insert(END, onscreen.text)
	tags_begin = onscreen.tags[0::2]
	tags_end = onscreen.tags[1::2]
	for tag_begin, tag_end in zip(tags_begin,tags_end):
		text.tag_add('found',tag_begin,tag_end)
	resize(onscreen.text, text)
	buttonLatex.config(text = 'Latexize', command=latexize)

def highlight():
	pattern1 = regex1.get()
	pattern2 = alignedregex.get()
	if pattern1 and not pattern2:
		idx = '1.0'
		length_match = IntVar()
		while True:
			idx = text.search(pattern1, idx, stopindex=END, regexp=True, count=length_match)
			if not idx: break
			lastidx = '%s+%dc' % (idx, length_match.get())
			text.tag_add('found', idx, lastidx)
			idx = lastidx
	elif pattern1 and pattern2:
		# Here I'll find where the matches are
		index = [ '1.0', '1.0' ]
		indexes = [ [ ], [ ] ]
		length_match = [ IntVar(), IntVar() ]
		length_matches = [ [ ], [ ] ]
		while True:
			index[0] = text.search(pattern1, index[0], stopindex=END, regexp=True, count=length_match[0])
			if index[0]:
				indexes[0].append(index[0])
				length_matches[0].append(length_match[0].get())
				if length_match[0].get():
					index[0] = '%s + %d char' % (index[0], length_match[0].get())
				else:
					index[0] = '%s + 1 char' % (index[0])
			else: 
				break
		while True:
			index[1] = text.search(pattern2, index[1], stopindex=END, regexp=True, count=length_match[1])
			if index[1]:
				indexes[1].append(index[1])
				length_matches[1].append(length_match[1].get())
				if length_match[1].get():
					index[1] = '%s + %d char' % (index[1], length_match[1].get())
				else:
					index[1] = '%s + 1 char' % (index[1])
			else:
				break
		# and here I will find which ones are aligned and mark them
		for idx in indexes[0]:
			for num in range(1,4):
				tentative_line = int(idx.split('.')[0]) + num
				idx_column = idx.split('.')[1]
				tentative_index = '%s.%s' % (tentative_line, idx_column)
				if tentative_index in indexes[1]:
					lastidx0 = '%s + %d chars' % (idx, length_matches[0][indexes[0].index(idx)])
					lastidx1 = '%s + %d chars' % (tentative_index, length_matches[1][indexes[1].index(tentative_index)])
					text.tag_add('found', idx, lastidx0)
					text.tag_add('found', tentative_index, lastidx1)
	text.tag_config('found', foreground='red')
		
buttonFind1.config(command=find)
regex1.bind('<Return>', find)

buttonFindAligned.config(command=find_aligned)
alignedregex.bind('<Return>', find_aligned)

buttonOpen.config(command=dialog_file)
buttonLatex.config(command=latexize)
buttonHighlight.config(command=highlight)

dialog_file()

root.mainloop()
