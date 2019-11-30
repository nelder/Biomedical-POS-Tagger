import json
from pprint import pprint

#Read in the JSON data object and parse into Python structure
with open('data50.json') as f:
    data = json.load(f)

#Generate output data struct
output = {}
#SAMPLE DATA: output['JJ|VBN'] = {'both': [['word', 12], ['word2', 15]], 'one': [['word', 12]], 'oneComp': [['word', 12]]}
# Both is in both POSDiff and POSDiff-comlement, one is when it is in just G:AAA|P:BBB, (note this is always alphabetized), the complement is this of the same structure in reverse order

#For each of the POSDiff objects
for key in data:

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


		#if we have not processed this object yet (note we will skip the flip object as we process both directions at once)
		if diff_identifier in output:
			#Existing Key
			continue
		else:
			#New Key, process
			#print "new"
			output[diff_identifier] = {'both': {}, 'one': {}, 'oneComp': {}}

			#Put all words in set one
			if "G:"+a+"|P:"+b in data:
				output[diff_identifier]["one"] = data["G:"+a+"|P:"+b]["words_freq_alpha"]
			else:
				#Does not exist
				output[diff_identifier]["one"] = {}

			#For every word in set two, if it is in set one, move word to both set, else, put in set b set
			if "G:"+b+"|P:"+a in data:
				for word in data["G:"+b+"|P:"+a]["words_freq_alpha"]:
					if word in output[diff_identifier]["one"]:
						#Move to both set 
						output[diff_identifier]["one"].pop(word)
						output[diff_identifier]["both"][word] = data["G:"+b+"|P:"+a]["words_freq_alpha"][word] #NOTE!!!!! This counter is meaningless, it is not the number in the both set because there is no concept of an instance being in the both set, a word is either there or not in binary. 
					else:
						if word in output[diff_identifier]["both"]:
							#It was already there
							continue
						else:
							#Just B Word
							output[diff_identifier]["oneComp"][word] = data["G:"+b+"|P:"+a]["words_freq_alpha"][word]
							continue
			else:
				continue
				#Set B is empty 

			#data["G:"+b+"|P:"+a]

#print(json.dumps(output, indent=4, sort_keys=True))


#Generte an output summary
output_detail = {}
for key in output:

	output_detail[key] = {'both': 0, 'one': 0, 'oneComp': 0}
	for word in output[key]['both']:
		output_detail[key]["both"] = output_detail[key]["both"] + output[key]['both'][word]

	for word in output[key]['one']:
		output_detail[key]["one"] = output_detail[key]["one"] + output[key]['one'][word]

	for word in output[key]['oneComp']:
		output_detail[key]["oneComp"] = output_detail[key]["oneComp"] + output[key]['oneComp'][word]

#print(json.dumps(output_detail, indent=4, sort_keys=True))




#Generate CSV output
csv_blob = "Part of Speech Diff,Both,One,OneComplement\n"
for key, value in output_detail.iteritems():
	csv_blob += key+","+str(value['both'])+","+str(value['one'])+","+str(value['oneComp'])+"\n"

f = open("wordInPDC_summary.csv", "w")
f.write(csv_blob)

