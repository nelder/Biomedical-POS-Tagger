import json
from pprint import pprint
from itertools import izip
import pprint
import re
import os
import json
import operator

#Globals
#journal_root = "/Users/nick/Dropbox/School/Year Four/SE3305 Research/Codebase/TaggerCompare/MinJournals"
journal_root = "/Users/nick/Corpora"
output_file = "out.txt"
file_output_pointer= open(output_file,"w+")

#Open outcomes decesion criteria document
with open('pos_diff_outcome.json') as f:
    data = json.load(f)

#Process each POSDIFF
outcome = {}
for key in data:
	print("------processing------")
	print(key)
	#print(data[key])
	
	outcome[key]={}#define outcome
	d_proced_data = data[key].splitlines()

	#Find global_correct
	result = [i for i in d_proced_data if i.startswith('global_correct_tagger')]
	value=result[0].split("=")
	value=value[1]

	#Path for each of the global corrects
	if(value == "genia"):
		outcome[key] = {"method":"global", "tagger":"genia"}
	elif(value == "postmed"):
		outcome[key] = {"method":"global", "tagger":"postmed"} 
	else:
		outcome[key] = {"method":"mix", "rules": []}

		#If there is no global correct more complex procedure needs to be encoded
		result = [i for i in d_proced_data if i.startswith('global_tagger_default')]
		value=result[0].split("=")
		value=value[1]

		#Grab a fallback default value
		if(value == "genia" or value == "postmed"):
			outcome[key]["fallback_tagger"] = value
		else:
			raise Exception('global_tagger_default not legal value')

		#Proceed to encode rules
		counter = 0
		for i in d_proced_data: 
			if i.startswith('word_correct_tagger'):

				#We found the head of a set of rules to be parsed
				inner_counter = counter + 1
				line = d_proced_data[inner_counter]
				while("}" not in line):

					#Drop blank lines
					if(len(line)>0):

						#Process each rule
						print(">>Rule is: "+line)

						
						#Is regex or word type?
						temp = line.split("=")
						temp=temp[0]
						#print(temp)
						
						if("*" in temp):
							outcome[key]['rules'].append({"type":"regex", "expr": temp })
							print(outcome[key]['rules'][-1])

						else:
							outcome[key]['rules'].append({"type":"word", "word": temp})
							print(outcome[key]['rules'][-1])

						#Encode outcome
						if("outcome" not in outcome[key]['rules'][-1].keys()):
							temp = line.split("=")
							print(temp)
							temp=temp[1]

							#Remove comments
							if("(" in temp):
								index = temp.find("(")
								temp = temp[:index]
							
							#Direct selection outcome
							if("mix:" not in temp and "mix->" not in temp):
								outcome[key]['rules'][-1]['outcome'] = "tagger"
								outcome[key]['rules'][-1]['tagger'] = temp.strip()

							elif("mix->" in temp):
								outcome[key]['rules'][-1]['outcome'] = "map"
								mapout = temp.split("->")
								outcome[key]['rules'][-1]['tag'] = mapout[1]


							#Decesion peocedure outcome
							else:
								second_temp = temp.split("?")
								outcome[key]['rules'][-1]['outcome'] = "decide"
								outcome[key]['rules'][-1]['procedure'] = second_temp[0]
								outcome[key]['rules'][-1]['procedure_accepts'] = second_temp[1].split(",")[0]
								outcome[key]['rules'][-1]['procedure_rejects'] = second_temp[1].split(",")[1]

													

					inner_counter = inner_counter + 1
					line = d_proced_data[inner_counter]


			counter = counter + 1






pprint.pprint(outcome)
#										global, mix			go with postmed
'''outcome['G:SAMPLE|P:SAMPLE'] = {"method":"global", "tagger":"postmed"}
outcome['G:SAMPL|P:SAMPLE2'] = {
	"method":"mix", 
	"fallback_tagger":"postmed", #fallback
	"rules":[
		{"type":"word", "word": "PBS", "outcome":"tagger", "tagger": "postmed"},
		{"type":"word", "word": "PBS", "outcome":"decide", 
			"procedure":"mix:FOLLOWING_WORD_TAG@NNP|NN", "procedure_accepts":"postmed", "procedure_rejects":"genia"}, #mix:

			#FOLLOWING_WORD_TAG PRIOR_WORD_TAG PRIOR_WORD  FOLLOWING_WORD LAST_LETTER
			# can have and/or list for what it is @ or another set of checks

		{"type":"word", "word": "PBS", "outcome":"map", "tag":"VBG"}, #mix->
		{"type":"regex", "expr": "*ing", }
		# *er&~*cancer
		#*est
	]
}'''

#Process corpus (based on compare.py)
for journal in os.listdir(journal_root):

	if(journal != ".DS_Store"):

		for filename in os.listdir(journal_root+"/"+journal):
			if filename.endswith(".genia.tagged"): 
				genia_filename = filename

				#look for matching postmed
				postmed_filename = genia_filename.replace(".genia.tagged", ".postmed.tagged")

				#validate the postmed file exists
				if(os.path.isfile(journal_root+"/"+journal+"/"+postmed_filename)):

					#For both files, itterate over the lines in sync
					with open(journal_root+"/"+journal+"/"+genia_filename) as genia, open(journal_root+"/"+journal+"/"+postmed_filename) as postmed: 
						line_counter=0
						for genia_line, postmed_line in izip(genia, postmed):
							line_counter = line_counter + 1
							
							#Remove newline
							genia_line = genia_line.strip()
							postmed_line = postmed_line.strip()

							#Print both lines with tab seperator
							#print("AAA{0}\tBBB{1}".format(genia_line, postmed_line))

							#Tokenize on spaces 
							genia_line = genia_line.split()
							postmed_line = postmed_line.split()    


							line_string = []
							POS_Tag_string = []

							#Validate strings are equal len in words to proceed as spot check on tokenizer
							if(len(genia_line) == len(postmed_line)):
								word_counter = 0

								#Itterate over words in string and compare twop
								for i in range(0, len(genia_line)):

									#Pring line
									#print(genia_line[i] + " " + postmed_line[i])
									word_counter = word_counter + 1

									#Split on _ for genia
									genia_word = genia_line[i].split("_")[0];
									genia_tag = genia_line[i].split("_")[1];

									#split on / for postmed
									postmed_word = postmed_line[i].split("/")[0];
									postmed_tag = postmed_line[i].split("/")[1];
									
									if(postmed_tag != genia_tag):
										##POSDIFF ENCOUNTERED

										#Compute POSDiff
										pos_diff = "G:"+genia_tag+"|P:"+postmed_tag

										#Ensure we have a rule for this POSDiff
										if pos_diff in outcome:

											#Check rules
											if(outcome[pos_diff]['method'] == "global"):
												
												#Use global tagger we selected
												if(outcome[pos_diff]['tagger'] == "genia"):
													line_string.append(genia_word)
													POS_Tag_string.append(genia_tag)
												else:
													line_string.append(postmed_word)
													POS_Tag_string.append(postmed_tag)


											elif(outcome[pos_diff]['method'] == "mix"):
												
												#Otherwise we have to scan rules
												found_word = False

												for rule in outcome[pos_diff]['rules']:

													#Only process first match
													if(found_word == False):
														#standard word match
														if(rule['type'] == 'word' or rule['type'] == 'regex'):

															match = False
															if(rule['type'] == 'word'):
																if(rule['word'] == genia_word):
																	match = True
															
															#Else regex match
															else:
																#print(rule['expr'])

																'''NOTE: only 4 distinct cases so hard code:
																*er&~*cancer
																	*s
																	*ing
																	*est
																'''
																if(rule['expr'] == "*ing"):
																	if(genia_word.endswith("ing")):
																		match = True

																elif(rule['expr'] == "*s"):
																	if(genia_word.endswith("s")):
																		match = True

																elif(rule['expr'] == "*est"):
																	if(genia_word.endswith("est")):
																		match = True

																elif(rule['expr'] == "*er&~*cancer"):
																	if(genia_word.endswith("er") and not genia_word.endswith("cancer")):
																		match = True


															
															#check word equality
															if(match == True):

																if(rule['outcome'] == "map"):
																	line_string.append(genia_word)
																	POS_Tag_string.append(rule['tag'])
																	found_word = True

																elif(rule['outcome'] == "tagger"):

																	#Select tagger
																	if(rule['tagger']=='genia'):
																		line_string.append(genia_word)
																		POS_Tag_string.append(genia_tag)
																		found_word = True
																	else:
																		line_string.append(postmed_word)
																		POS_Tag_string.append(postmed_tag)
																		found_word = True

																else:
																	#else it is decide procedure
																	#print(rule['procedure'].split(":")[1])
																	procedure = rule['procedure'].split(":")[1]

																	#FOLLOWING_WORD_TAG PRIOR_WORD_TAG PRIOR_WORD  FOLLOWING_WORD LAST_LETTER
																	list_of_directives = ["FOLLOWING_WORD_TAG", "PRIOR_WORD_TAG", "PRIOR_WORD", "FOLLOWING_WORD", "LAST_LETTER"]
																	#Access context
																	if(len(genia_line[i-1])>4 and len(genia_line[i+1])>4):
																		#Access context window
																		genia_word_prior = genia_line[i-1].split("_")[0];
																		genia_tag_prior = genia_line[i-1].split("_")[1];

																		genia_word_following = genia_line[i+1].split("_")[0];
																		genia_tag_following = genia_line[i+1].split("_")[1];

																		if(procedure == 'FOLLOWING_WORD_TAG@NNP|NN'):
																			#Postmed if true
																			if(genia_tag_following == "NNP" or genia_tag_following == "NN"):
																				line_string.append(postmed_word)
																				POS_Tag_string.append(postmed_tag)
																				found_word = True
																			else:
																				line_string.append(genia_word)
																				POS_Tag_string.append(genia_tag)
																				found_word = True

																		elif(procedure == 'PRIOR_WORD@the&FOLLOWING_WORD_TAG@~NN&~NNS'):
																			#Postmed if true
																			if(genia_word_prior == "the" and genia_tag_following != "NN" and genia_tag_following != "NNS"):
																				line_string.append(postmed_word)
																				POS_Tag_string.append(postmed_tag)
																				found_word = True
																			else:
																				line_string.append(genia_word)
																				POS_Tag_string.append(genia_tag)
																				found_word = True

																		elif(procedure == 'PRIOR_WORD_TAG@CD'):
																			#Genia if true
																			if(genia_tag_prior == "CD"):
																				line_string.append(genia_word)
																				POS_Tag_string.append(genia_tag)
																				found_word = True
																			else:
																				line_string.append(postmed_word)
																				POS_Tag_string.append(postmed_tag)
																				found_word = True

																		elif(procedure == 'PRIOR_WORD_TAG@JJ|NN'):
																			#Postmed if true
																			if(genia_tag_prior == "JJ" or genia_tag_prior == "NN"):
																				line_string.append(postmed_word)
																				POS_Tag_string.append(postmed_tag)
																				found_word = True
																			else:
																				line_string.append(genia_word)
																				POS_Tag_string.append(genia_tag)
																				found_word = True


																		'''NOTE: it turns out we only generated 4 rules, so as opposed to building a tree parser and FSM to handle thiese,
																		I am going to hard code them. The unique values are: 

																			FOLLOWING_WORD_TAG@NNP|NN
																			PRIOR_WORD@the&FOLLOWING_WORD_TAG@~NN&~NNS
																			PRIOR_WORD_TAG@CD
																			PRIOR_WORD_TAG@JJ|NN
																		'''



																	#Else no context so we need to just fallback

												if(found_word == False):
													#No rule matched, go with fallback
													if(outcome[pos_diff]['fallback_tagger']=='genia'):
														line_string.append(genia_word)
														POS_Tag_string.append(genia_tag)
														found_word = True
													else:
														line_string.append(postmed_word)
														POS_Tag_string.append(postmed_tag)
														found_word = True



											
											else:
												raise Exception('method bad value')

										else:
											#No rule written so we go with Genia
											line_string.append(genia_word)
											POS_Tag_string.append(genia_tag)
										



									else:
										#Normal output
										line_string.append(genia_word)
										POS_Tag_string.append(genia_tag)


							#Output to file
							try:
								output_string = (" ".join(line_string))+"	"+(" ".join(POS_Tag_string)) + "\n"

							except:
								#print("warning: string collapse error for one instance")
								#print(line_string)
								#print(POS_Tag_string)
								#print("\n")
								output_string = ""
							
							#print(output_string)
							file_output_pointer.write(output_string)





file_output_pointer.close()


