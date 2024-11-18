from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer

from constants import EMPTY, SPACE


class Preprocessor:

    def case_fold(self, string: str) -> str:
        """Converts the string to lowercase"""
        return string.lower()

    def remove_stopwords(self, string: str) -> str:
        """Removes the stopwords from the string using NLTK's stopwords"""
        stop_words = set(stopwords.words('english'))
        return SPACE.join([word for word in string.split() if word not in stop_words])

    def remove_punctuation(self, string: str) -> str:
        """Removes the punctuation from the string"""
        return EMPTY.join([char for char in string if char.isalnum() or char.isspace()])

    def expand_contractions(self, string: str) -> str:
        """Expands the contractions in the string"""
        return string.replace("'", SPACE)

    def stem_string(self, tokens: list) -> list:
        """Stems the tokens using Porter Stemmer"""
        stemmer = PorterStemmer()
        return [stemmer.stem(word) for word in tokens]

    def lemmatize(self, tokens: list) -> list:
        """Lemmatizes the tokens using WordNet Lemmatizer"""
        lemmatizer = WordNetLemmatizer()
        return [lemmatizer.lemmatize(word) for word in tokens]

    def tokenize(self, string: str) -> list:
        """Tokenizes the string"""
        return word_tokenize(string)

    def preprocess(self, string: str) -> list:
        """Preprocesses the string using the following steps:
        1. Case Folding
        2. Expanding Contractions
        3. Removing Punctuation
        4. Removing Stopwords
        5. Tokenization
        6. Stemming
        7. Lemmatization
        """
        string = self.case_fold(string)
        string = self.expand_contractions(string)
        string = self.remove_punctuation(string)
        string = self.remove_stopwords(string)
        tokens = self.tokenize(string)
        tokens = self.stem_string(tokens)
        tokens = self.lemmatize(tokens)
        return tokens
