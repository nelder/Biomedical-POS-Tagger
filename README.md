# Biomedical Part of Speech Tagger
This repository is related to the paper: Building a Biomedical Full-Text Part-of-Speech Corpus Semi-Automatically by Nicholas Elder and Dr. Robert Mercer from the Department of Computer Science at the University of Western Ontario. The full paper can be accessed [here](https://elder.ca/research/2019_bio_med_part_of_speech_tagger_for_conference.pdf).

## Research Outcomes
This directory contains two files:
* `pos_diff_interventions.json`	- this file contains the decesion procedure we defined to handle each of the POSDiffs (Part of Speech Tagging Difference).
* `posdiffs_full.csv`	- this file contains data describing the frequency of each POSDiff from our training corpus. 

## Codebase
This directory contains several programs:
* `POSDiffBuilder/compare.py` - this code analyzes two tagged corpuses and generates a JSON file describing the POSDiffs, this POSDiffs file is used as the input to the web viewer along side a copy of the tagged corpuses. 
* `POSDiffCAnalysis/wordInPDC.py` - this code creates summary data on the POSDiff data generated by the previous program which describes the complementary POSDiff.
* `Viewer Website/*` - the 5 code files here constitute the Web Viewer program which takes as input the POSDiff JSON data and the two tagged corpuses. Note: each file will require an update if you change the journal director or POS Diff directory.  
* `contextAnalyze/POSDiffContext.py` - this code was not used in the paper, it was built to analyze the typical context arund each POSDiff and answer the question: Is this POSDiff always proceeded by another? 
* `corpusBuilder/corpusBuilder.py` - this code takes as input the POSDiff decision procedure like `pos_diff_interventions.json`, and the two tagged corpora, and generates a new single tagged corpus like ours published [here](https://elder.ca/research/biomed_pos_corpus.txt)

## Corpus
* The corpus can be downloaded [here](https://elder.ca/research/biomed_pos_corpus.txt) as it is too large for Github. 