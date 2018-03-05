#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 12:50:46 2018

@author: alexmerryman
"""

import pandas as pd
import numpy as np
import spacy
import math
import glob
import os
import re



current_wd = os.getcwd()





nlp = spacy.load('en')


percent_list = []
ceo_list = []
company_list = []

file_counter = 1
for f in glob.glob("*.txt"):

    print '-----------------------------'
    print 'File #{} of 730 ({}%)'.format(file_counter, 100*float(file_counter)/730.)
    print 'Analyzing file f{}'.format(f)

    indoc = unicode(open(f).read(), errors='ignore')
    #print indoc

    # Tokenization
    print 'Tokenization...'
    nlp_doc = nlp(indoc)

    #print 'Sample text (first 10 tokens)...'
    ## first 10 tokens
    #print nlp_doc[0:9]



    ## Lemmatization, POS tagging
    #print 'POS tagging...'
    #token_dict_list = []
    #
    #token_num = 0
    #for token in nlp_doc:
    #    token_dict = {
    #    't_num': token_num,
    #    'text': token.text,
    #    'lemma': token.lemma_,
    #    'pos': token.pos_,
    #    'tag': token.tag_,
    #    'dep': token.dep_,
    #    'shape': token.shape_,
    ##    'alpha': token.is_alpha,
    #    'stop': token.is_stop
    #    }
    #    token_dict_list.append(token_dict)
    #    token_num += 1
    #
    #
    #token_df = pd.DataFrame(token_dict_list)
    #
    ## Remove all stop words
    #token_df = token_df[token_df['stop'] == False]
    ##token_df = token_df.reset_index()
    ##token_df.drop(['index'], axis=1, inplace=True)
    #
    #
    #CEO_tokens = token_df[token_df['lemma'] == 'ceo']
    #prop_noun_tokens = token_df[token_df['pos'] == 'PROPN']
    #number_tokens = token_df[token_df['pos'] == 'NUM']
    #percent_symbol_tokens = token_df[token_df['shape'].str.contains('%') == True]



    '''
    All percent-related numbers are succeeded by '%', 'percent', 'percentile', 'percentile point(s)',
    'percentage', or 'percentage point(s)'

    Thus, a naive NER classifier can be created using Regex to identify those instances.
    '''


    # first, find all instances of % sign
    # captures integer, decimal, and ranged (hypenated) percentage numbers
    print 'Finding % matches...'
    pct_pattern = re.compile("(\d*\-*\d*\.*\d*%)")
    pct_matches = pct_pattern.findall(indoc)

    for item in pct_matches:
        percent_list.append(item)

    # Find integer and decimal matches with 'percent,', 'percentage,' and 'percentile'
    num_long_pattern = re.compile("((negative)*\s*\d*\s*(to)*\s*\d*\-*\d*\.*\d+\s*\-*(percent)+((age)|(ile))*\s*(point(s*))*)")
    num_long_matches = num_long_pattern.findall(indoc)

    for i in num_long_matches:
        percent_list.append(i[0])


    cd_percent_list = []

    for t in range(len(nlp_doc)-1):
        curr_token = nlp_doc[t]
        next_token = curr_token.nbor(1)

        # percentages
        pct_token_list = []
        pct_backtrack_list = []

        pct_stop_pattern = ['percent', 'percentage', 'percentile']


        # CEOs
        ceo_token_list = []
        ceo_backtrack_list = []

        ceo_keywords = ['ceo', 'chief', 'executive']


        # Companies
        company_token_list = []
        company_backtrack_list = []
        company_keywords = ['company', 'group', 'business', 'corporation', 'corp', 'inc', 'co', 'technologies']


        # Percentages
        if curr_token.lemma_ in pct_stop_pattern:
            pct_token_list.append(curr_token.text)

            # backtrack to collect all the numbers
            prev_token = curr_token.nbor(-1)
            while prev_token.pos_ == 'NUM' or prev_token.tag_ == 'HYPH' or prev_token.lemma_ == 'to':
                pct_backtrack_list.insert(0, prev_token.text)
                prev_token = prev_token.nbor(-1)

        pct_token_list = pct_backtrack_list + pct_token_list

        if len(pct_token_list) > 0:
            cd_percent_list.append(pct_token_list)


        # CEOs
        if curr_token.lemma_ in ceo_keywords or (curr_token.pos_ == 'PROPN' and curr_token.nbor().pos_ == 'PROPN'):
            ceo_token_list.append(curr_token.text)

            begin_search = t-5
            end_search = t+5

            for poss_ceo in nlp_doc[begin_search:end_search]:
                if poss_ceo.pos_ == 'PROPN' and poss_ceo.nbor().pos_ == 'PROPN':
                    ceo_backtrack_list.append(poss_ceo.text)
                    ceo_backtrack_list.append(poss_ceo.nbor().text)

        ceo_token_list = ceo_backtrack_list + ceo_token_list

        if len(ceo_token_list) > 0:
            ceo_list.append(ceo_token_list)


        # Companies
        if (curr_token.lemma_ in company_keywords) or (curr_token.pos_ == 'PROPN' and curr_token.nbor().pos_ == 'PROPN'):
            company_token_list.append(curr_token.text)
            company_token_list.append(curr_token.nbor().text)

            begin_search = t-7
            end_search = t+7

            for poss_comp in nlp_doc[begin_search:end_search]:
                if poss_comp.pos_ == 'PROPN' and poss_comp.nbor().pos_ == 'PROPN':
                    company_backtrack_list.append(poss_comp.text)
                    company_backtrack_list.append(poss_comp.nbor().text)

            if len(company_backtrack_list) == 1 and str(company_backtrack_list[0]) in company_keywords:
                pass
            else:
                company_token_list = company_backtrack_list

        if len(company_token_list) > 0:
            company_list.append(company_token_list)






    cd_percent_list_final = []
    for i in cd_percent_list:
        i = ' '.join(i)
        cd_percent_list_final.append(i)

    file_counter += 1

#    for sublist in company_list:
#        if sublist not in company_list_clean:
#            company_list.append(sublist)





#percent_list_final = []
#for item in pct_matches:
#    percent_list_final.append(item)


pct_file = open('percentages_identified.txt', 'w')
#for item in percent_list:
#    pct_file.write("\n".join(item))
pct_file.write("\n".join(percent_list))

pct_file.close()

ceo_file = open('CEOs_identified.txt', 'w')
for item in ceo_list:
    ceo_file.write("\n".join(item))

ceo_file.close()

company_file = open('companies_identified.txt', 'w')
for item in company_list:
    company_file.write("\n".join(item))

company_file.close()



'''
CEO rules:
- Must be PROPN (proper noun).
- Contains at least one CEO keyword nearby.
- Search through and find all cases of 2-3 PROPN in a row (first and last name, maybe middle name or initial)
- Create list of CEOs' last names.
- Search corpus again for the last names.
'''
# also include 'president', 'managing direector', 'chairman'?








