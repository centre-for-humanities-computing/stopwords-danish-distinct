'''
From opensubtitles
'''

import glob
import re

import pandas as pd


da = pd.read_csv('data/da_50k.txt',
                 sep=" ",
                 header=None,
                 names=['word', 'count'])

word_paths = [word_file for word_file in glob.glob("data/*.txt")]

lang_tag_pattern = re.compile(r'(?<=data/).*(?=_50k)')

unwanted_lang = ['no', 'is', 'de', 'sv', 'en']


# extract top n words from a file and 
def get_top_n_words(filepath, n) -> dict:
    lang_tag = re.search(lang_tag_pattern, filepath).group(0)

    one_lang = pd.read_csv(filepath,
                           sep=" ",
                           header=None,
                           names=['word', 'count']).iloc[0:n, :]

    top_n_list = [word for word in one_lang.word]

    return {lang_tag: top_n_list}


# get top n words from all the files
out = {}
for path in word_paths:
    one_file = get_top_n_words(path, 200)
    out.update(one_file)


# exception for english: get all we can
en_file = get_top_n_words('data/en_50k.txt', 50000)
out['en'] = en_file


# find words in the danish list
for lang in out:
    if lang == "da":
        pass
    else:
        da[lang] = da.word.isin(out[lang])


# remove words that appear in other languages
da_distinct = da.copy()
for lang in unwanted_lang:
    da_distinct = da_distinct[~da_distinct[lang]]

da_distinct = (da_distinct
               .reset_index()
               .rename(columns={'index': 'rank'}))

# export
da_export = da_distinct.loc[0:1000, ['rank', 'word', 'count']]
da_export.write_csv