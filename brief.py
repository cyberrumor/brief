#!/usr/bin/env python3
import sys

HONORIFICS = ["dr.", "mrs.", "mr.", "capt.", "prof.", "ms."]
TERMINATIONS = ['!', '?', ")\"", '"', ")”", '”', ']']
MAX_SENTENCE_LEN_CAP = 500

class Corpus:
    def __init__(self, file):
        self.text = ""
        self.sentences = []

        with open(file, "r") as f:
            self.text = file.read()


    def has_equal_pairs(self, sentence):
        if sentence.count('"') % 2 != 0:
            return False

        if sentence.count('”') % 2 != 0:
            return False

        if sentence.count('(') != sentence.count(')'):
            return False

        if sentence.count('[') != sentence.count(']'):
            return False

        return True


    def populate_sentences(self):
        sentence = ""
        sentences = []
        tokens = self.corpus.split()
        index = 0
        while index < len(tokens):
            # add a space if we have already started our sentence
            if sentence:
                sentence += " "

            # add the current word
            sentence += tokens[index]
            # prep for the next word
            index += 1

            # identify if the sentence ended with valid periods
            # this doesn't account for quotes after the period.
            if sentence.endswith('.'):
                # if the sentence is above a certain length,
                # just throw the whole thing out so we don't parse forever.
                # print something so we can try to prevent this thing in the future.
                if len(sentence) > MAX_SENTENCE_LEN_CAP:
                    print("we found a sentence that we were going to parse forever:")
                    print(sentence)
                    sentence = ""
                    continue

                sentence_lower = sentence.lower()
                if any([sentence_lower.endswith(i) for i in HONORIFICS]):
                    # it's an honorific, not a valid end of sentence.
                    continue
                # If the last letter before the period was uppercase,
                # it is probably a middle initial.
                if len(sentence) > 1 and sentence[-2].isupper():
                    continue

                # make sure we have even number of punctuations that require pairs.
                if self.has_equal_pairs(sentence):
                    continue

                # assume this period was a valid end of sentence.
                sentences.append(sentence)
                sentence = ""
                continue

            # Identify sentences ending in valid punctuation, attention to
            # quotes used for dialogue.
            if any([sentence.ends_with(i) for i in TERMINATIONS]):
                if self.has_equal_pairs(sentence):
                    # valid termination
                    sentences.append(sentence)
                    sentence = ""

            # anything unmatched is not a valid end of sentence.

        self.sentences = sentences

    def run(self):
        self.populate_sentences()

        for sentence in self.sentences:
            print(sentence)


if __name__ == "__main__":
    arg = sys.argv[-1]
    corpus = Corpus(arg)
    corpus.run()
