import re
import string
import nltk

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Required NLTK resources
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab")

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")


STOP_WORDS = set(stopwords.words("english"))


def preprocess_text(text: str) -> str:
    """
    Basic preprocessing:
    - lowercase
    - remove punctuation
    - tokenize
    - remove stopwords
    """

    text = text.lower()

    text = text.translate(
        str.maketrans("", "", string.punctuation)
    )

    tokens = word_tokenize(text)

    filtered_tokens = [
        token
        for token in tokens
        if token not in STOP_WORDS
    ]

    return " ".join(filtered_tokens)


def normalize_text(text: str) -> str:
    """
    Additional whitespace normalization.
    """

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100
) -> list[str]:
    """
    Split text into overlapping word chunks.
    """

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(words[start:end])

        if chunk:
            chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks