#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import functools
import operator
import numpy as np

NUM_NOTES = 12
NUM_MODES = 2

NOTE_NAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
MODE_NAMES = ['Maj', 'min']

MUSIC_KEY_PROFILE_MAJOR = [ 5.0, 2.0, 3.5, 2.0, 4.5, 4.0, 2.0, 4.5, 2.0, 3.5, 1.5, 4.0 ] # Major scale
MUSIC_KEY_PROFILE_MINOR = [ 5.0, 2.0, 3.5, 4.5, 2.0, 4.0, 2.0, 4.5, 3.5, 2.0, 1.5, 4.0 ] # Harmonic minor scale

MUSIC_KEY_PROFILE_OFFSET = 4.

MUSIC_KEY_FREQUENCIES_MAJOR = [math.exp(v - MUSIC_KEY_PROFILE_OFFSET)/(1. + math.exp(v - MUSIC_KEY_PROFILE_OFFSET)) for v in MUSIC_KEY_PROFILE_MAJOR]
MUSIC_KEY_FREQUENCIES_MINOR = [math.exp(v - MUSIC_KEY_PROFILE_OFFSET)/(1. + math.exp(v - MUSIC_KEY_PROFILE_OFFSET)) for v in MUSIC_KEY_PROFILE_MINOR]

MUSIC_KEY_K_MAJOR = sum([math.log(1-f) for f in MUSIC_KEY_FREQUENCIES_MAJOR])
MUSIC_KEY_K_MINOR = sum([math.log(1-f) for f in MUSIC_KEY_FREQUENCIES_MINOR])

MUSIC_SCALE_MAJOR = (1<<0) + (1<<2) + (1<<4) + (1<<5) + (1<<7) + (1<<9) + (1<<11)
MUSIC_SCALE_MINOR = (1<<0) + (1<<2) + (1<<4) + (1<<5) + (1<<7) + (1<<9) + (1<<10)

TEST_PITCH_HISTOGRAMS = [
        [2, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [1, 0, 0, 0, 2, 0, 0, 0, 0, 5, 0, 2],
        [2, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [2, 0, 0, 0, 2, 0, 0, 0, 0, 5, 0, 2],
        [3, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [2, 0, 0, 0, 2, 0, 0, 0, 0, 5, 0, 2],
        [3, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [2, 0, 0, 0, 2, 0, 0, 0, 0, 5, 0, 2],
        [2, 0, 0, 0, 0, 2, 0, 0, 0, 6, 0, 0],
        [0, 0, 2, 0, 0, 0, 0, 3, 0, 0, 0, 6],
        [3, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [0, 0, 1, 0, 0, 0, 0, 4, 0, 0, 0, 6],
        [3, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [0, 0, 2, 0, 0, 0, 0, 6, 0, 0, 0, 3],
        [2, 0, 0, 0, 2, 0, 0, 0, 0, 5, 0, 2],
        [2, 0, 0, 0, 0, 2, 0, 0, 0, 6, 0, 0],
        [0, 0, 2, 0, 0, 0, 0, 3, 0, 0, 0, 6],
        [0, 0, 0, 0, 4, 0, 0, 1, 0, 0, 0, 6],
        [3, 0, 0, 0, 2, 0, 0, 0, 0, 6, 0, 0],
        [1, 0, 0, 0, 2, 0, 0, 0, 0, 3, 0, 0],
        [2, 0, 0, 0, 0, 3, 0, 0, 0, 7, 0, 0],
        [3, 0, 0, 0, 0, 3, 0, 0, 0, 6, 0, 0],
        [2, 0, 0, 0, 3, 0, 0, 0, 0, 6, 0, 2],
        [3, 0, 0, 0, 2, 0, 0, 0, 0, 6, 0, 2],
        [2, 0, 0, 0, 0, 3, 0, 0, 0, 7, 0, 0],
        [3, 0, 0, 0, 0, 3, 0, 0, 0, 6, 0, 0],
        [5, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [0, 0, 3, 0, 0, 0, 0, 4, 0, 0, 0, 6],
        [5, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [0, 0, 2, 0, 1, 0, 0, 3, 0, 0, 0, 6],
        [2, 0, 0, 0, 2, 0, 0, 0, 0, 6, 0, 2],
        [3, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [2, 0, 0, 0, 2, 0, 0, 0, 0, 5, 0, 2],
        [3, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [2, 0, 0, 0, 2, 0, 0, 0, 0, 5, 0, 2],
        [2, 0, 0, 0, 0, 2, 0, 0, 0, 6, 0, 0],
        [0, 0, 2, 0, 0, 0, 0, 3, 0, 0, 0, 6],
        [3, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [0, 0, 1, 0, 0, 0, 0, 4, 0, 0, 0, 6],
        [3, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [0, 0, 2, 0, 0, 0, 0, 6, 0, 0, 0, 3],
        [2, 0, 0, 0, 2, 0, 0, 0, 0, 5, 0, 2],
        [2, 0, 0, 0, 0, 2, 0, 0, 0, 6, 0, 0],
        [0, 0, 2, 0, 0, 0, 0, 3, 0, 0, 0, 6],
        [0, 0, 0, 0, 4, 0, 0, 1, 0, 0, 0, 6],
        [3, 0, 0, 0, 2, 0, 0, 0, 0, 6, 0, 0],
        [1, 0, 0, 0, 2, 0, 0, 0, 0, 3, 0, 0],
        [2, 0, 0, 0, 0, 3, 0, 0, 0, 7, 0, 0],
        [3, 0, 0, 0, 0, 3, 0, 0, 0, 6, 0, 0],
        [2, 0, 0, 0, 3, 0, 0, 0, 0, 6, 0, 2],
        [3, 0, 0, 0, 2, 0, 0, 0, 0, 6, 0, 2],
        [2, 0, 0, 0, 0, 3, 0, 0, 0, 7, 0, 0],
        [3, 0, 0, 0, 0, 3, 0, 0, 0, 6, 0, 0],
        [5, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [0, 0, 3, 0, 0, 0, 0, 4, 0, 0, 0, 6],
        [5, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [0, 0, 2, 0, 1, 0, 0, 3, 0, 0, 0, 6],
        [2, 0, 0, 0, 2, 0, 0, 0, 0, 6, 0, 2],
        [3, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [2, 0, 0, 0, 2, 0, 0, 0, 0, 5, 0, 2],
        [3, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [2, 0, 0, 0, 2, 0, 0, 0, 0, 5, 0, 2],
        [2, 0, 0, 0, 0, 2, 0, 0, 0, 6, 0, 0],
        [0, 0, 2, 0, 0, 0, 0, 3, 0, 0, 0, 6],
        [3, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [0, 0, 1, 0, 0, 0, 0, 4, 0, 0, 0, 6],
        [3, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [0, 0, 2, 0, 0, 0, 0, 6, 0, 0, 0, 3],
        [2, 0, 0, 0, 2, 0, 0, 0, 0, 5, 0, 2],
        [2, 0, 0, 0, 0, 2, 0, 0, 0, 6, 0, 0],
        [0, 0, 2, 0, 0, 0, 0, 3, 0, 0, 0, 6],
        [0, 0, 0, 0, 4, 0, 0, 1, 0, 0, 0, 6],
        [3, 0, 0, 0, 2, 0, 0, 0, 0, 6, 0, 0],
        [1, 0, 0, 0, 2, 0, 0, 0, 0, 3, 0, 0],
        [2, 0, 0, 0, 0, 3, 0, 0, 0, 7, 0, 0],
        [3, 0, 0, 0, 0, 3, 0, 0, 0, 6, 0, 0],
        [2, 0, 0, 0, 3, 0, 0, 0, 0, 6, 0, 2],
        [3, 0, 0, 0, 2, 0, 0, 0, 0, 6, 0, 2],
        [2, 0, 0, 0, 0, 3, 0, 0, 0, 7, 0, 0],
        [3, 0, 0, 0, 0, 3, 0, 0, 0, 6, 0, 0],
        [5, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [0, 0, 3, 0, 0, 0, 0, 4, 0, 0, 0, 6],
        [5, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [0, 0, 2, 0, 1, 0, 0, 3, 0, 0, 0, 6],
        [2, 0, 0, 0, 2, 0, 0, 0, 0, 6, 0, 2],
        [3, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [2, 0, 0, 0, 2, 0, 0, 0, 0, 5, 0, 2],
        [3, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [2, 0, 0, 0, 2, 0, 0, 0, 0, 5, 0, 2],
        [2, 0, 0, 0, 0, 2, 0, 0, 0, 6, 0, 0],
        [0, 0, 2, 0, 0, 0, 0, 3, 0, 0, 0, 6],
        [3, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [0, 0, 1, 0, 0, 0, 0, 4, 0, 0, 0, 6],
        [3, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [0, 0, 2, 0, 0, 0, 0, 6, 0, 0, 0, 3],
        [2, 0, 0, 0, 2, 0, 0, 0, 0, 5, 0, 2],
        [2, 0, 0, 0, 0, 2, 0, 0, 0, 6, 0, 0],
        [0, 0, 2, 0, 0, 0, 0, 3, 0, 0, 0, 6],
        [0, 0, 0, 0, 4, 0, 0, 1, 0, 0, 0, 6],
        [3, 0, 0, 0, 2, 0, 0, 0, 0, 6, 0, 0],
        [1, 0, 0, 0, 2, 0, 0, 0, 0, 3, 0, 0],
        [2, 0, 0, 0, 0, 3, 0, 0, 0, 7, 0, 0],
        [3, 0, 0, 0, 0, 3, 0, 0, 0, 6, 0, 0],
        [2, 0, 0, 0, 3, 0, 0, 0, 0, 6, 0, 2],
        [3, 0, 0, 0, 2, 0, 0, 0, 0, 6, 0, 2],
        [2, 0, 0, 0, 0, 3, 0, 0, 0, 7, 0, 0],
        [3, 0, 0, 0, 0, 3, 0, 0, 0, 6, 0, 0],
        [5, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [0, 0, 3, 0, 0, 0, 0, 4, 0, 0, 0, 6],
        [5, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [0, 0, 2, 0, 1, 0, 0, 3, 0, 0, 0, 6],
        [2, 0, 0, 0, 2, 0, 0, 0, 0, 6, 0, 2],
        [3, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [2, 0, 0, 0, 2, 0, 0, 0, 0, 5, 0, 2],
        [3, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [2, 0, 0, 0, 2, 0, 0, 0, 0, 5, 0, 2],
        [2, 0, 0, 0, 0, 2, 0, 0, 0, 6, 0, 0],
        [0, 0, 2, 0, 0, 0, 0, 3, 0, 0, 0, 6],
        [3, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [0, 0, 1, 0, 0, 0, 0, 4, 0, 0, 0, 6],
        [3, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [0, 0, 2, 0, 0, 0, 0, 6, 0, 0, 0, 3],
        [2, 0, 0, 0, 2, 0, 0, 0, 0, 5, 0, 2],
        [2, 0, 0, 0, 0, 2, 0, 0, 0, 6, 0, 0],
        [0, 0, 2, 0, 0, 0, 0, 3, 0, 0, 0, 6],
        [0, 0, 0, 0, 4, 0, 0, 1, 0, 0, 0, 6],
        [3, 0, 0, 0, 2, 0, 0, 0, 0, 6, 0, 0],
        [1, 0, 0, 0, 2, 0, 0, 0, 0, 3, 0, 0],
        [2, 0, 0, 0, 0, 3, 0, 0, 0, 7, 0, 0],
        [3, 0, 0, 0, 0, 3, 0, 0, 0, 6, 0, 0],
        [2, 0, 0, 0, 3, 0, 0, 0, 0, 6, 0, 2],
        [3, 0, 0, 0, 2, 0, 0, 0, 0, 6, 0, 2],
        [2, 0, 0, 0, 0, 3, 0, 0, 0, 7, 0, 0],
        [3, 0, 0, 0, 0, 3, 0, 0, 0, 6, 0, 0],
        [5, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 2],
        [0, 0, 3, 0, 0, 0, 0, 4, 0, 0, 0, 6],
        [5, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 1],
        [5, 0, 0, 0, 3, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

class StateChangeProbabilities():
    def __init__(self, prob_same_state):
        self.prob_same_state = prob_same_state
        self.prob_other_state = (1. - self.prob_same_state) / (NUM_MODES * NUM_NOTES - 1)
        self.shape = (NUM_MODES * NUM_NOTES, NUM_MODES * NUM_NOTES)

    def __getitem__(self, args):
        initial_state, final_state = args

        if isinstance(initial_state, int) and isinstance(final_state, int):
            if (initial_state == final_state):
                probability = self.prob_same_state
            else:
                probability = self.prob_other_state
            #print(f">>> InitialState={initial_state} ; FinalState={final_state} -> Probability={probability}")
            return probability

        elif isinstance(initial_state, slice):
            probabilities = np.array([self.prob_other_state] * NUM_MODES * NUM_NOTES)
            probabilities[final_state] = self.prob_same_state
            #print(f">>> InitialState={initial_state} ; FinalState={final_state} -> Probabilities={probabilities}")
            return probabilities

        else:
            raise TypeError("index must be int or slice")

class EmissionProbabilities():
    def __init__(self):
        self.data = [
            MUSIC_KEY_FREQUENCIES_MAJOR + MUSIC_KEY_FREQUENCIES_MAJOR,
            MUSIC_KEY_FREQUENCIES_MINOR + MUSIC_KEY_FREQUENCIES_MINOR,
        ]

    def get_probabilities(self, root_note, mode):
        return np.array(self.data[mode][12 - root_note:24 - root_note])

    def get_probabilities_for_histogram(self, root_note, mode, pitch_classes):
        return [p if (pitch_classes & 1<<(r%12) != 0) else (1. - p) for r, p in enumerate(self.data[mode][12 - root_note:24 - root_note])]

    def __getitem__(self, args):
        h, o = args

        # This checks that:
        # - key is an integer (or can be converted to an integer)
        # - key is replaced by an appropriate positive value when < 0
        # - key is made = self._length when key >= self._length (not exactly as before)
        max_o = 2**12
        o = slice(o).indices(max_o)[1]

        pitch_classes = [(o & 1<<(r%12) != 0) for r in range(0, 12)]
        #print(f">>> HiddenStates={h} ; ObservableStates={o:03x} -> {pitch_classes}")

        if isinstance(h, int):
            note = h % 12
            mode = h // 12
            raw_probabilities = self.get_probabilities(note, mode)
            probabilities = self.get_probabilities_for_histogram(note, mode, o)
            probability = functools.reduce(operator.mul, probabilities)
            p1 = [round(p, 2) if c else math.nan for c, p in zip(pitch_classes, probabilities)]
            p2 = [round(p, 2) if not c else math.nan for c, p in zip(pitch_classes, probabilities)]
            #print(f">>> Note={note} ; Mode={mode} ; ObservableState={o:03x} ~ {o:012b} ; Data={p1}; {p2} -> {probability}")
            return probability
        elif isinstance(h, slice):
            max_h = NUM_MODES * NUM_NOTES
            v = np.array([0.5] * NUM_MODES * NUM_NOTES)
            for i in range(*h.indices(max_h)):
                note = i % 12
                mode = i // 12
                probabilities = self.get_probabilities(note, mode)
                p1 = [round(p, 2) if c else math.nan for c, p in zip(pitch_classes, probabilities)]
                p2 = [round(p, 2) if not c else math.nan for c, p in zip(pitch_classes, probabilities)]
                #print(f">>> Note={note} ; Mode={mode} ; ObservableState={o:03x} ; Data={p1}; {p2}")
            #print(f">>> Value={v}")
            return v
        else:
            raise TypeError("index must be int or slice")

def viterbi(V, a, b, initial_distribution):
    T = V.shape[0]
    M = a.shape[0]

    omega = np.zeros((T, M))
    omega[0, :] = np.log(initial_distribution * b[:, V[0]])

    prev = np.zeros((T - 1, M))

    # ωi(t+1) = max(i, ωi(t)·aij·bjkv(t+1))

    # One implementation trick is to use the log scale so that we dont get the underflow error.

    for t in range(1, T):
        for j in range(M):
            # Same as Forward Probability
            probability = omega[t - 1] + np.log(a[:, j]) + np.log(b[j, V[t]])

            # This is our most probable state given previous state at time t (1)
            prev[t - 1, j] = np.argmax(probability)

            # This is the probability of the most probable state (2)
            omega[t, j] = np.max(probability)

    # Path Array
    S = np.zeros(T)

    # Find the most probable last hidden state
    last_state = np.argmax(omega[T - 1, :])

    S[0] = last_state

    backtrack_index = 1
    for i in range(T - 2, -1, -1):
        S[backtrack_index] = prev[i, int(last_state)]
        last_state = prev[i, int(last_state)]
        backtrack_index += 1

    # Flip the path array since we were backtracking
    S = np.flip(S, axis=0)

    return S


def find_music_key(pitch_histograms):
    V = np.array(pitch_histograms)
    a = StateChangeProbabilities(0.8)
    b = EmissionProbabilities()
    initial_distribution = np.array([1] * NUM_MODES * NUM_NOTES)
    initial_distribution = initial_distribution / np.sum(initial_distribution)
    return [int(s) for s in viterbi(V, a, b, initial_distribution)]

def get_music_key_name(s):
    return '{}:{}'.format(NOTE_NAMES[int(s)%12], MODE_NAMES[int(s)//12])

def get_root_note_from_music_key(s):
    return int(s) % 12

def get_scale_from_music_key(s):
    return [MUSIC_SCALE_MAJOR, MUSIC_SCALE_MINOR][int(s) // 12]

def test_viterbi():
    pitch_histograms = []
    for pitch_histogram in TEST_PITCH_HISTOGRAMS:
        h = sum([1 << (n % 12) if pitch_histogram[n] > 0 else 0 for n in range(12)])
        pitch_histogram_k = bin(h).count('1') * MUSIC_KEY_PROFILE_OFFSET
        #print(f"{pitch_histogram} ~ {h:#06x} -> {bin(h).count('1')} pitch classes ~  Kh = {pitch_histogram_k}")
        pitch_histograms.append(h)

    V = np.array(pitch_histograms)

    # Transition Probabilities
    #a = np.array([[80. if i == j else (20. / (NUM_MODES * NUM_NOTES - 1)) for i in range(NUM_MODES * NUM_NOTES)] for j in range(NUM_MODES * NUM_NOTES)])
    #a = a / np.sum(a, axis=1)

    a = StateChangeProbabilities(0.8)

    # Emission Probabilities
    b = EmissionProbabilities()

    # Equal Probabilities for the initial distribution
    initial_distribution = np.array([1] * NUM_MODES * NUM_NOTES)
    initial_distribution = initial_distribution / np.sum(initial_distribution)

    #print(f"P:\n{initial_distribution}")
    print(['{:03x}={}:{}'.format(v, NOTE_NAMES[int(s)%12], MODE_NAMES[int(s)//12]) for v, s in zip(V, viterbi(V, a, b, initial_distribution))])


def test_probability_conversion():
    print(f"Major: {MUSIC_KEY_PROFILE_MAJOR} -> {MUSIC_KEY_FREQUENCIES_MAJOR} (K = {MUSIC_KEY_K_MAJOR})")
    print(f"Minor: {MUSIC_KEY_PROFILE_MINOR} -> {MUSIC_KEY_FREQUENCIES_MINOR} (K = {MUSIC_KEY_K_MINOR})")
    for pitch_histogram in TEST_PITCH_HISTOGRAMS:
        h = sum([1 << (n % 12) if pitch_histogram[n] > 0 else 0 for n in range(12)])
        pitch_histogram_k = bin(h).count('1') * MUSIC_KEY_PROFILE_OFFSET
        #print(f"{pitch_histogram} ~ {h:#06x} -> {bin(h).count('1')} pitch classes ~  Kh = {pitch_histogram_k}")

        ks_major_values = [
            sum([
                (MUSIC_KEY_PROFILE_MAJOR[i]) if pitch_histogram[(key + i)%12] > 0 \
                else 0. \
                for i in range(12) \
            ]) for key in range(12)
        ]

        ks_minor_values = [ 
            sum([
                (MUSIC_KEY_PROFILE_MINOR[i]) if pitch_histogram[(key + i)%12] > 0 \
                else 0. \
                for i in range(12) \
            ]) for key in range(12)
        ]

        #print(f"{pitch_histogram} -> KSmaj = {ks_major_values}  KSmin = {ks_minor_values}")

        major_values = [
            functools.reduce(operator.mul, [
                MUSIC_KEY_FREQUENCIES_MAJOR[i] if pitch_histogram[(key + i)%12] > 0 \
                else (1. - MUSIC_KEY_FREQUENCIES_MAJOR[i]) \
                for i in range(12) \
            ]) for key in range(12)
        ]

        minor_values = [
            functools.reduce(operator.mul, [
                MUSIC_KEY_FREQUENCIES_MINOR[i] if pitch_histogram[(key + i)%12] > 0 \
                else (1. - MUSIC_KEY_FREQUENCIES_MINOR[i]) \
                for i in range(12) \
            ]) for key in range(12)
        ]

        #print(f"{pitch_histogram} -> Pmaj = {major_values}  Pmin = {minor_values}")

        major_error = max([abs(math.exp(MUSIC_KEY_K_MAJOR + ks_v - pitch_histogram_k) - v) for ks_v, v in zip(ks_major_values, major_values)])
        major_error = major_error if major_error > 1e-16 else 0

        minor_error = max([abs(math.exp(MUSIC_KEY_K_MINOR + ks_v - pitch_histogram_k) - v) for ks_v, v in zip(ks_minor_values, minor_values)])
        minor_error = minor_error if minor_error > 1e-16 else 0

        if minor_error or major_error:
            print(f"{pitch_histogram} -> {major_values} (Err: {major_error})  {minor_values} (Err: {minor_error})")

if __name__ == '__main__':
    test_probability_conversion()
    test_viterbi()
