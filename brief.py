#!/usr/bin/env python3
import sys

# These do not count as valid sentence terminations
# despite ending in a period.
HONORIFICS = ["Dr.", "Mrs.", "Mr.", "Capt.", "Prof.", "Ms."]

# Various ways sentences can end.
TERMINATIONS = ['!', '?', ")\"", '"', ")”", '”', ']', '’', '’']

# If it has parsed this many words without terminating a sentence,
# discard it on the next '.' or termination and start anew.
MAX_SENTENCE_LEN_CAP = 200

# How many sentences we should include in the summary.
SUMMARY_SENTENCE_COUNT = 3

# Don't score sentences shorter than this many words.
MIN_SENTENCE_LEN = 4

# How few words should be considered n in an ngram.
MIN_N = 2

# Max words that should be considered n in an ngram.
# set to 0 to disable. Increasing this is computationally
# expensive.
MAX_N = 10




# Verify settings are valid.
if MAX_N != 0:
    assert MIN_N <= MAX_N, "MIN_N must be less than or equal to MAX_N"




class Corpus:
    def __init__(self, file):
        self.sentences = {}
        self.ngram_model = {}
        self.summary = ""

        print(f"parsing: {file}")
        with open(file, "r") as f:
            self.text = f.read()

        self.tokens = self.text.split()


    def has_equal_pairs(self, sentence):
        if sentence.count('"') % 2 != 0:
            return False

        # unreliable
        # if sentence.count('”') % 2 != 0:
        #    return False

        if sentence.count('(') != sentence.count(')'):
            return False

        if sentence.count('[') != sentence.count(']'):
            return False

        # unreliable
        # if sentence.count('‘') != sentence.count('’'):
        #    return False

        return True


    def populate_sentences(self):
        sentence = ""
        index = 0
        while index < len(self.tokens):
            # add a space if we have already started our sentence
            if sentence:
                sentence += " "

            # add the current word
            sentence += self.tokens[index]

            # prep for the next word
            index += 1

            # identify if the sentence ended with valid periods
            # this doesn't account for quotes after the period.
            if sentence.endswith('.'):
                # if the sentence is above a certain length,
                # just throw the whole thing out so we don't parse forever.
                # print something so we can try to prevent this thing in the future.
                if len(sentence) > MAX_SENTENCE_LEN_CAP:
                    # print("we found a sentence that we were going to parse forever:")
                    # print(sentence)
                    sentence = ""
                    continue

                if any([sentence.endswith(i) for i in HONORIFICS]):
                    # it's an honorific, not a valid end of sentence.
                    continue

                # If the last letter before the period was uppercase,
                # it is probably a middle initial.
                if len(sentence) > 1 and sentence[-2].isupper():
                    continue

                # make sure we have even number of punctuations that require pairs.
                if not self.has_equal_pairs(sentence):
                    continue

                # assume this period was a valid end of sentence.
                self.sentences[sentence] = {}
                sentence = ""
                continue

            # Identify sentences ending in valid punctuation, attention to
            # quotes used for dialogue.
            if any([sentence.endswith(i) for i in TERMINATIONS]):
                if len(sentence) > MAX_SENTENCE_LEN_CAP:
                    sentence = ""
                    continue

                if self.has_equal_pairs(sentence):
                    # valid termination
                    self.sentences[sentence] = {}
                    sentence = ""


    def populate_ngram_model(self):
        for i, sentence in enumerate(self.sentences):
            print(f"loading ngram markov model: {int((i / len(self.sentences)) * 100)}%",
                  end = "\r", flush=True)
            sanitized_sentence = ''.join([i for i in sentence if i.isalpha() or i == ' ']).split()
            self.sentences[sentence]['sanitized'] = sanitized_sentence
            # if we sanitized it into blankness, don't try to process it.
            if not sanitized_sentence:
                continue

            self.sentences[sentence]['ngrams'] = set()
            for index in range(len(sanitized_sentence)):
                n = index + MIN_N
                while n < min(len(sanitized_sentence), MAX_N):
                    ngram_slice = sanitized_sentence[index:n]
                    ngram = ' '.join(ngram_slice)
                    if ngram in self.ngram_model:
                        self.ngram_model[ngram] += 1
                        n += 1
                        continue
                    self.ngram_model[ngram] = 1
                    self.sentences[sentence]['ngrams'].add(ngram)
                    n += 1

        # Score our sentences
        for sentence in self.sentences:
            self.sentences[sentence]['score'] = 0

            if len(self.sentences[sentence]['sanitized']) <= MIN_SENTENCE_LEN:
                # print(f"skipping {sentence} ")
                continue

            for ngram in self.sentences[sentence]['ngrams']:
                score = self.ngram_model.get(ngram, 0)
                self.sentences[sentence]['score'] += score

            # penalize run-on sentences
            score = self.sentences[sentence]['score']
            score //= max(1, sum([sentence.count(i) for i in [',', ':', ';']]))
            self.sentences[sentence]['score'] = score


    def load_summary(self):
        self.populate_sentences()
        self.populate_ngram_model()

        # sort our sentences by value
        sorted_sentences = {
            k: v for k, v in sorted(
                self.sentences.items(),
                key=lambda item: item[1]['score'],
                reverse = True
            )
        }
        # display our x best sentences
        index = 0
        sentences = list(sorted_sentences.keys())
        summary = []
        while index < min(len(sentences), SUMMARY_SENTENCE_COUNT):
            summary.append(sentences[index])
            index += 1

        # put the summary sentences in their original chronological order.
        for sentence in self.sentences:
            if sentence in summary:
                self.summary += sentence + " "
        self.summary.strip()


if __name__ == "__main__":
    arg = sys.argv[-1]
    corpus = Corpus(arg)
    corpus.load_summary()
    print(corpus.summary)
