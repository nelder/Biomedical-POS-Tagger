import json
from pprint import pprint
import linecache


#Read in the JSON data object and parse into Python structure
with open('data.json') as f:
    data = json.load(f)

#Generate output data struct
output = {}

#For each of the POSDiff objects (NOTE: redefining dict of len 1 for small sample)
pos_diff = 'G:VB|P:VBP'
for key in {pos_diff:data[pos_diff]}:

	output[pos_diff] = {"pos_context_postmed": [], "pos_context_genia": [], "word_context":[]}

	#print(key)
	#parse out the POSs
	if(len(key.split("|"))==2): #this is to remove the 1-2 buggy cases in the data
		genia_pos = key.split("|")[0].split(":")[1]
		postmed_pos = key.split("|")[1].split(":")[1]
		
		#Define the combined POSDiff object key which helps us identify the POSDiff and the complement
		diff_identifier = ""
		a=""
		b=""
		if(genia_pos < postmed_pos):
			diff_identifier = genia_pos + "|" + postmed_pos
			a=genia_pos
			b=postmed_pos
		else:
			diff_identifier = postmed_pos + "|" + genia_pos
			a=postmed_pos
			b=genia_pos

		#print(key, genia_pos, postmed_pos)
		#print(diff_identifier+"\n")


		#print("> "+genia_pos+" "+postmed_pos)

		for word_instance in data[key]['words']:

			#Output
			pos_context = ["context_obj", "address"]

			#Read 2 lines in
			genia = word_instance[1];
			postmed = word_instance[2]	
					
			genia_file = genia.split("|")[0]
			genia_line = (genia.split("|")[1]).split("/")[0]
			genia_word = (genia.split("|")[1]).split("/")[1]

			postmed_file = postmed.split("|")[0]
			postmed_line = (postmed.split("|")[1]).split("/")[0]
			postmed_word = (postmed.split("|")[1]).split("/")[1]

			#print(word_instance)
			#print(postmed_file)
			#print(genia_file)

			corpus_root = "/Users/nick/Corpora/"
			
			try:
				postmed_line_data = linecache.getline(corpus_root+postmed_file, int(genia_line))
				genia_line_data = linecache.getline(corpus_root+genia_file, int(postmed_line))

				postmed_line_data = postmed_line_data.split(" ")
				genia_line_data = genia_line_data.split(" ")

				if(postmed_line_data[int(postmed_word)-1].split("/")[0] == "have"):
					output[key]['pos_context_postmed'].append([postmed_line_data[int(postmed_word)-1-1].split("/")[1]+"_"+postmed_line_data[int(postmed_word)-1+1].split("/")[1] , postmed])
					output[key]['pos_context_genia'].append([genia_line_data[int(genia_word)-1-1].split("_")[1]+"_"+genia_line_data[int(genia_word)-1+1].split("_")[1] , genia])
					output[key]['word_context'].append([postmed_line_data[int(postmed_word)-1-1].split("/")[0]+"_"+postmed_line_data[int(postmed_word)-1+1].split("/")[0] , postmed])

				#Summarize the data
				continue


			except:
				continue
			







summary_output = {}

for key in output:

	summary_output[key] = {"pos_context_postmed": {}, "pos_context_genia": {}, "word_context":{}}


	for genia in output[key]['pos_context_genia']:
		if genia[0] in summary_output[key]['pos_context_genia'].keys():
			summary_output[key]['pos_context_genia'][genia[0]] += 1
		else:
			summary_output[key]['pos_context_genia'][genia[0]] = 1

	for postmed in output[key]['pos_context_postmed']:
		if postmed[0] in summary_output[key]['pos_context_postmed'].keys():
			summary_output[key]['pos_context_postmed'][postmed[0]] += 1
		else:
			summary_output[key]['pos_context_postmed'][postmed[0]] = 1

	for word in output[key]['word_context']:
		if word[0] in summary_output[key]['word_context'].keys():
			summary_output[key]['word_context'][word[0]] += 1
		else:
			summary_output[key]['word_context'][word[0]] = 1















###CODE FROM ELSEWHERE FOR REF
#Generte an output summary
'''
output_detail = {}
for key in output:

	output_detail[key] = {'both': 0, 'one': 0, 'oneComp': 0}
	for word in output[key]['both']:
		output_detail[key]["both"] = output_detail[key]["both"] + output[key]['both'][word]

	for word in output[key]['one']:
		output_detail[key]["one"] = output_detail[key]["one"] + output[key]['one'][word]

	for word in output[key]['oneComp']:
		output_detail[key]["oneComp"] = output_detail[key]["oneComp"] + output[key]['oneComp'][word]
'''
#print(json.dumps(summary_output, indent=4, sort_keys=True))
new = {}
new['detail'] = output
new['summary'] = summary_output 

print(json.dumps(new, indent=4, sort_keys=True))



#Generate CSV output
'''
csv_blob = "Part of Speech Diff,Both,One,OneComplement\n"
for key, value in output_detail.iteritems():
	csv_blob += key+","+str(value['both'])+","+str(value['one'])+","+str(value['oneComp'])+"\n"

f = open("wordInPDC_summary.csv", "w")
f.write(csv_blob)
'''

