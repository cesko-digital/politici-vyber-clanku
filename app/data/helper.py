import re
from nltk.util import ngrams
import unicodedata
import collections
from ufal.morphodita import Forms, TaggedLemmas, TokenRanges, Tagger

class Helper:
    tokenizer = None
    tagger = None

    def load(self):
        self.tagger = Tagger.load("./MorfFlexCZ/morfflex-cz.2016-03-10.utf8.lemmaID_suff-tag-form.tab.csv.xz")
        self.tokenizer = self.tagger.newTokenizer()

    def create_ngrams(self, text):
        forms = Forms()
        lemmas = TaggedLemmas()
        tokens = TokenRanges()
        self.tokenizer.setText(text)
        while self.tokenizer.nextSentence(forms, tokens):
            self.tagger.tag(forms, lemmas)
            for i in range(len(lemmas)):
                lemma = lemmas[i]
                token = tokens[i]
        s = text.lower()
        s = re.sub(r'[^a-zA-Z0-9\s]', ' ', s)
        tokens = [token for token in s.split(" ") if token != ""]
        biGrams = ngrams(tokens, 2)
        triGrams = ngrams(tokens, 3)
        quadGrams = ngrams(tokens, 4)
        freq = collections.Counter([*biGrams, *triGrams, *quadGrams])
        return freq.most_common(20)


def is_about_politician(name, party, text):
    found = False
    for sentence in text.split("."):
        found = name in sentence and party in sentence
        if found:
            return sentence, True
    return False



def remove_diacritic(input):
    '''
    Accept a unicode string, and return a normal string (bytes in Python 3)
    without any diacritical marks.
    '''
    return unicodedata.normalize('NFKD', input).encode('ASCII', 'ignore')