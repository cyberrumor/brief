#!/usr/bin/env python3
import sys

# These do not count as valid sentence terminations
# despite ending in a period.
HONORIFICS = ["Dr.", "Mrs.", "Mr.", "Capt.", "Prof.", "Ms."]

# Various ways sentences can end.
TERMINATIONS = ['!', '?', ")\"", '"', ")”", '”', ']', '.’']

# If it has parsed this many words without terminating a sentence,
# discard it on the next '.' and start anew.
MAX_SENTENCE_LEN_CAP = 500

# How many sentences we should include in the summary.
SUMMARY_SENTENCE_COUNT = 5

# Don't score sentences shorter than this many words.
MIN_SENTENCE_LEN = 6

# Potentially endless list of exceptions can go here.
# It should contain connectives, pronouns, prepositions, determiners, modal verbs.
# Everything we're checking against this will be stripped of non alphas.
IGNORE = ["the", "he", "her", "it", "there", "then", "my", "mine", "i", "you", "your", "yours",
          "theyre", "its", "their", "when", "who", "but", "be", "because", "or", "his",
          "hers", "theirs", "theres", "are", "arent", "been", "will", "wont", "by"]

class Corpus:
    def __init__(self, file):
        self.sentences = {}
        self.word_heatmap = {}
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
                    # exit()
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
                self.sentences[sentence] = 0
                sentence = ""
                continue

            # Identify sentences ending in valid punctuation, attention to
            # quotes used for dialogue.
            if any([sentence.endswith(i) for i in TERMINATIONS]):
                if self.has_equal_pairs(sentence):
                    # valid termination
                    self.sentences[sentence] = 0
                    sentence = ""


    def populate_word_heatmap(self):
        for word in self.tokens:
            sanitized_word = ''.join([i for i in word if i.isalpha()])

            if sanitized_word in self.word_heatmap:
                self.word_heatmap[sanitized_word] += 1
                continue

            # word is new to the heatmap
            self.word_heatmap[sanitized_word] = 1


    def score_sentences(self):
        # get our sentences
        for sentence in self.sentences:
            # get the words in the sentence
            split_sentence = sentence.split()
            # only care about sentences longer than x.
            if len(split_sentence) <= MIN_SENTENCE_LEN:
                assert self.sentences[sentence] == 0
                continue

            for word in split_sentence:
                sanitized_word = ''.join([i for i in word if i.isalpha()])
                # get a score for our word
                if sanitized_word in self.word_heatmap:
                    # add points to our sentence
                    self.sentences[sentence] += self.word_heatmap[sanitized_word]

            # Divide the sentence score by the length of the sentence.
            # A sentence shouldn't be automatically better because it's longer.
            self.sentences[sentence] = self.sentences[sentence] / max(1, len(sentence))

    def load_summary(self):
        self.populate_sentences()
        self.populate_word_heatmap()
        self.score_sentences()

        # sort our sentences by value
        sorted_sentences = {
            k: v for k, v in sorted(
                self.sentences.items(),
                key=lambda item: item[1]
            )
        }
        # display our x best sentences
        index = 0
        sentences = list(sorted_sentences.keys())
        while index < min(len(sentences), SUMMARY_SENTENCE_COUNT):
            self.summary += sentences[index] + " "
            index += 1
        self.summary.strip()


if __name__ == "__main__":
    arg = sys.argv[-1]
    corpus = Corpus(arg)
    corpus.load_summary()
    print(corpus.summary)
