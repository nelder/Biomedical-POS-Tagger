#Nick Elder, December 2 2018
from itertools import izip
import pprint
import re
import os
import json
import operator

match_list = []
differ_list = []
differ_freq = {}

journal_root = "50Journals"

#print("Processing folder: " +journal_root)

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

						        	#Validate that tag is read (to remove things like puncuation which have no tag)
						        	if(re.match("\w",postmed_tag) and re.match("\w",genia_tag)):

						        		#Generate an address for each "Journal/Paper/Line/Word object"
						        		item_address_genia = journal+"/"+genia_filename+"|"+str(line_counter)+"/"+str(word_counter)
						        		item_address_postmed = journal+"/"+postmed_filename+"|"+str(line_counter)+"/"+str(word_counter)


							        	#Validate the words are the same
							        	if(genia_word == postmed_word):
							        		#Check if word tags match
							        		if(genia_tag == postmed_tag):
							        			#Maintain a list of the word and tag pairs that are the same
							        			same_summary = {"word" : genia_word, "tag" : genia_tag}
							        			match_list.append(same_summary)
							        		else:	
							        			#Maintain a list of the word and tag pairs that differ, repetitions happen
							        			diff_summary = {"word" : genia_word, "genia_tag" : genia_tag, "postmed_tag" : postmed_tag}
							        			differ_list.append(diff_summary)

							        			#track differences in meaningful way
							        			diff_vector = "G:"+ genia_tag + "|P:"+postmed_tag

							        			#If we already have seen this different, add to it's object
							        			if(diff_vector in differ_freq):
							        				differ_freq[diff_vector]['pos_frequency'] = differ_freq[diff_vector]['pos_frequency'] + 1;
							        				differ_freq[diff_vector]['words'].append((genia_word, item_address_genia, item_address_postmed))

							        				#If the word frequency pair is already existing we increment, else we add
							        				if(genia_word in differ_freq[diff_vector]['words_freq_alpha']):
							        					differ_freq[diff_vector]['words_freq_alpha'][genia_word] = differ_freq[diff_vector]['words_freq_alpha'][genia_word] + 1
							        				else:
							        					differ_freq[diff_vector]['words_freq_alpha'][genia_word] = 1

							        			#Else create because its the first time we've seen this difference
							        			else:
							        				item = {"words":[(genia_word, item_address_genia, item_address_postmed)],"words_freq_alpha":{genia_word:1}, "pos_frequency":1}
							        				differ_freq[diff_vector] = item

							        	else:
							        		continue
							        		#print("ERROR: Word mismatch. Tokenizer fault. (GENIA:"+genia_word+"[VS]POSTMED:"+postmed_word+")")


					        else:
					        	continue
					        	#print("ERROR: String line tokenization mismatch (GENIA:"+json.dumps(genia_line)+"[VS]POSTMED:"+json.dumps(postmed_line)+").")


#Add a second data object that is sorted by the frequency of words for a given POS difference vector, there already exists an alpha list with the frequency keys so we will now provide a diff sorting option
for item in differ_freq:
	words_sorted = sorted(differ_freq[item]["words_freq_alpha"].items(), key=operator.itemgetter(1), reverse=True)
	differ_freq[item]["words_freq"] = words_sorted



##Print out summary data stats
#print("Total instances: "+str(len(match_list)+len(differ_list)))

#print("Same Summary")
#print(len(match_list))
#print(float(len(match_list))/(len(match_list)+len(differ_list)))

#print("\nDiff List")
#print(len(differ_list))
#print(float(len(differ_list))/(len(match_list)+len(differ_list)))

#print("\nDiff Freq")
#print(len(differ_freq))


##Print out the data objects
#pprint.pprint(match_list)
#pprint.pprint(differ_list)
#pprint.pprint(differ_freq)



##Generate a JSON dump of the diff object
print(json.dumps(differ_freq, indent=4, sort_keys=True))

##Generate Summary CSV
'''
csv_blob = "Part of Speech Diff,Frequency,Num of Words\n"
for key, value in differ_freq.iteritems():
	csv_blob += key+","+str(value['frequency'])+","+str(len(set(value['word'])))+"\n"

f = open("out.csv", "w")
f.write(csv_blob)
'''





