import glob
import re

import pandas as pd


class DistinctStopwords:
    '''
    Get the most frequent words that are distinctly in a target language 
    '''
    
    word_paths = [word_file for word_file in glob.glob("data/*.txt")]
    lang_tag_pattern = re.compile(r'(?<=data/).*(?=_50k)')
    
    
    def __init__(self,
                 target_lang,
                 n_stopwords=100,
                 keep_lang=None,
                 unwanted_lang='all',
                 unwanted_threshold=200,
                 feared_lang=None,
                 output_path="../ds.txt"):
        '''
        target_lang (str): ISO 639-1 code of language to get distinct stopwords for
        n_stopwords (int): how many distinct stopwords to get in target language 
        keep_lang (str|list): languages not to remove 
        unwanted_lang (str|list): ISO 639-1 codes of languages to partly remove. 
            - 'all' uses all available languages, except for keep_lang & feared_lang 
        unwanted_threshold (int): use this many top words from an unwanted language to remove
        feared_lang (str|list): ISO 639-1 codes of languages to completely remove
        output_path (str): where to save the list
        '''
        self.target_lang = target_lang
        self.n_stopwords = n_stopwords
        
        if isinstance(keep_lang, str):
            self.keep_lang = [keep_lang]
        elif isinstance(keep_lang, list):
            self.keep_lang = keep_lang
        
        if isinstance(unwanted_lang, str) and unwanted_lang != 'all':
            self.unwanted_lang = [unwanted_lang]
        elif unwanted_lang == 'all':
            self.unwanted_lang = unwanted_lang
        elif isinstance(unwanted_lang, list):
            self.unwanted_lang = unwanted_lang
            
        self.unwanted_threshold = unwanted_threshold
        
        if isinstance(feared_lang, str):
            self.feared_lang = [feared_lang]    
        elif isinstance(feared_lang, list):
            self.feared_lang = feared_lang 
            
        self.output_path = output_path
        
        target_df = pd.read_csv('data/' + target_lang + '_50k.txt',
                                sep=" ",
                                header=None,
                                names=['word', 'count'])
        
        self.target_df = target_df
    
    
    def get_top_n_words(self, filepath, n) -> dict:
        '''
        filepath (str): file to extract from
        n (int): n top words to extract
        '''
        lang_tag = re.search(self.lang_tag_pattern, filepath).group(0)

        one_lang = pd.read_csv(filepath,
                               sep=" ",
                               header=None,
                               names=['word', 'count']).iloc[0:n, :]

        top_n_list = [word for word in one_lang.word]

        return {lang_tag: top_n_list}
    
    
    def get_matching_paths(self, language_tags, everything_except=False) -> list:
        '''
        filter the list of files to get only those desired
        
        language_tags (str|list): tags of language to get filepaths for
        everything_except (bool): 
            - False = only paths specified by language_tags are extracted
            - True =  all paths everything except those in language_tags are extracted
        '''
        file_style = ['/' + tag + '_' for tag in language_tags]
        single_string = "|".join(file_style)
        rpat = re.compile(single_string)
        
        # 
        if everything_except is False:
            pathlist = [path for path in self.word_paths if re.search(rpat, path)]
            
        elif everything_except is True:
            pathlist = [path for path in self.word_paths if not re.search(rpat, path)]
        
        return pathlist
    
    
    def get_distinct_stopwords(self):
        '''
        run everything
        '''
        
        stopwords = {}
        
        # build removal dictionary from PARTLY removed languages
        ## option 1: partly filtering out all possible languages
        if self.unwanted_lang is "all":
            ### get all paths except for wanted languages
            except_wanted = self.get_matching_paths(self.keep_lang,
                                                    everything_except=True)
            ### get all paths exept for feared languages
            except_feared = self.get_matching_paths(self.feared_lang,
                                                    everything_except=True)
            ### join them into a single list
            unwanted_paths = except_wanted.copy()
            unwanted_paths.extend(except_feared)
            ### make sure only unique elements are present
            unwanted_paths = list(set(unwanted_paths))

            
        ## option 2: partly filtering out only specified languages 
        else:       
            unwanted_paths = self.get_matching_paths(self.unwanted_lang)
        
        # build removal dictionary from COMPLETELY removed languages
        feared_path = self.get_matching_paths(self.feared_lang)

        ## include all available words from feared language to remove
        for path in feared_path:
            one_file = self.get_top_n_words(path, 50000)
            stopwords.update(one_file)

        ## run through unwanted paths, building a word dictionary for later removal
        ## feared is in front of unwanted, so that it becomes the first new column
        for path in unwanted_paths:
            one_file = self.get_top_n_words(path, self.unwanted_threshold)
            stopwords.update(one_file)
            

            
        # update target language df with matches in other langs
        for lang in stopwords:
            if lang == self.target_lang:
                pass
            else:
                self.target_df[lang] = (self.target_df
                                        .word
                                        .isin(stopwords[lang]))

        # remove words that appear in other languages
        distinct_df = self.target_df.copy()
        for lang in stopwords:
            if lang == self.target_lang:
                pass
            else:
                distinct_df = distinct_df[~distinct_df[lang]]
            
        
        # update index
        distinct_df = (distinct_df
                       .reset_index()
                       .rename(columns={'index': 'rank'}))
        
        self.distinct_df = distinct_df


    def save(self):
        da_export = self.distinct_df.loc[0:self.n_stopwords, 'word']
        da_export.to_csv(self.output_path, header=None, index=None, sep=' ', mode='a')


def distinct_da():
    da = DistinctStopwords(target_lang='da',
                           n_stopwords=100,
                           keep_lang=['no', 'sv'],
                           unwanted_lang="all",
                           unwanted_threshold=200,
                           feared_lang='en')
    
    da.get_distinct_stopwords()
    da.save()
    return da
    