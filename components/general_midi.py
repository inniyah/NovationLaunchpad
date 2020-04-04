#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# General MIDI Instrument List

# These are the instruments in the General MIDI Level 1 sound set.
# https://soundprogramming.net/file-formats/general-midi-instrument-list/

MIDI_GM1_INSTRUMENT_NAMES = {
	# Piano:
	1: "Acoustic Grand Piano",
	2: "Bright Acoustic Piano",
	3: "Electric Grand Piano",
	4: "Honky-tonk Piano",
	5: "Electric Piano 1",
	6: "Electric Piano 2",
	7: "Harpsichord",
	8: "Clavinet",

	# Chromatic Percussion:
	9: "Celesta",
	10: "Glockenspiel",
	11: "Music Box",
	12: "Vibraphone",
	13: "Marimba",
	14: "Xylophone",
	15: "Tubular Bells",
	16: "Dulcimer",

	# Organ:
	17: "Drawbar Organ",
	18: "Percussive Organ",
	19: "Rock Organ",
	20: "Church Organ",
	21: "Reed Organ",
	22: "Accordion",
	23: "Harmonica",
	24: "Tango Accordion",

	# Guitar:
	25: "Acoustic Guitar (nylon)",
	26: "Acoustic Guitar (steel)",
	27: "Electric Guitar (jazz)",
	28: "Electric Guitar (clean)",
	29: "Electric Guitar (muted)",
	30: "Overdriven Guitar",
	31: "Distortion Guitar",
	32: "Guitar harmonics",

	# Bass:
	33: "Acoustic Bass",
	34: "Electric Bass (finger)",
	35: "Electric Bass (pick)",
	36: "Fretless Bass",
	37: "Slap Bass 1",
	38: "Slap Bass 2",
	39: "Synth Bass 1",
	40: "Synth Bass 2",

	# Strings:
	41: "Violin",
	42: "Viola",
	43: "Cello",
	44: "Contrabass",
	45: "Tremolo Strings",
	46: "Pizzicato Strings",
	47: "Orchestral Harp",
	48: "Timpani",

	# Strings (continued):
	49: "String Ensemble 1",
	50: "String Ensemble 2",
	51: "Synth Strings 1",
	52: "Synth Strings 2",
	53: "Choir Aahs",
	54: "Voice Oohs",
	55: "Synth Voice",
	56: "Orchestra Hit",

	# Brass:
	57: "Trumpet",
	58: "Trombone",
	59: "Tuba",
	60: "Muted Trumpet",
	61: "French Horn",
	62: "Brass Section",
	63: "Synth Brass 1",
	64: "Synth Brass 2",

	# Reed:
	65: "Soprano Sax",
	66: "Alto Sax",
	67: "Tenor Sax",
	68: "Baritone Sax",
	69: "Oboe",
	70: "English Horn",
	71: "Bassoon",
	72: "Clarinet",

	# Pipe:
	73: "Piccolo",
	74: "Flute",
	75: "Recorder",
	76: "Pan Flute",
	77: "Blown Bottle",
	78: "Shakuhachi",
	79: "Whistle",
	80: "Ocarina",

	# Synth Lead:
	81: "Lead 1 (square)",
	82: "Lead 2 (sawtooth)",
	83: "Lead 3 (calliope)",
	84: "Lead 4 (chiff)",
	85: "Lead 5 (charang)",
	86: "Lead 6 (voice)",
	87: "Lead 7 (fifths)",
	88: "Lead 8 (bass + lead)",

	# Synth Pad:
	89: "Pad 1 (new age)",
	90: "Pad 2 (warm)",
	91: "Pad 3 (polysynth)",
	92: "Pad 4 (choir)",
	93: "Pad 5 (bowed)",
	94: "Pad 6 (metallic)",
	95: "Pad 7 (halo)",
	96: "Pad 8 (sweep)",

	# Synth Effects:
	97: "FX 1 (rain)",
	98: "FX 2 (soundtrack)",
	99: "FX 3 (crystal)",
	100: "FX 4 (atmosphere)",
	101: "FX 5 (brightness)",
	102: "FX 6 (goblins)",
	103: "FX 7 (echoes)",
	104: "FX 8 (sci-fi)",

	# Ethnic:
	105: "Sitar",
	106: "Banjo",
	107: "Shamisen",
	108: "Koto",
	109: "Kalimba",
	110: "Bag pipe",
	111: "Fiddle",
	112: "Shanai",

	# Percussive:
	113: "Tinkle Bell",
	114: "Agogo",
	115: "Steel Drums",
	116: "Woodblock",
	117: "Taiko Drum",
	118: "Melodic Tom",
	119: "Synth Drum",
	120: "Reverse Cymbal",

	# Sound effects:
	121: "Guitar Fret Noise",
	122: "Breath Noise",
	123: "Seashore",
	124: "Bird Tweet",
	125: "Telephone Ring",
	126: "Helicopter",
	127: "Applause",
	128: "Gunshot",
}

# General MIDI Level 2 Instrument List

# These are the instruments in the General MIDI Level 2 sound set.
# The first number listed is the patch number, and the second number is the bank number.
# https://soundprogramming.net/file-formats/general-midi-level-2-instrument-list/

MIDI_GM2_INSTRUMENT_NAMES = {
	0: {
		# Piano:
		1: "Acoustic Grand Piano",
		2: "Bright Acoustic Piano",
		3: "Electric Grand Piano",
		4: "Honky-tonk Piano",
		5: "Rhodes Piano",
		6: "Chorused Electric Piano",
		7: "Harpsichord",
		8: "Clavinet",

		# Chromatic Percussion:
		9: "Celesta",
		10: "Glockenspiel",
		11: "Music Box",
		12: "Vibraphone",
		13: "Marimba",
		14: "Xylophone",
		15: "Tubular Bells",
		16: "Dulcimer/Santur",

		# Organ:
		17: "Hammond Organ",
		18: "Percussive Organ",
		19: "Rock Organ",
		20: "Church Organ 1",
		21: "Reed Organ",
		22: "French Accordion",
		23: "Harmonica",
		24: "Bandoneon",

		# Guitar:
		25: "Nylon-String Guitar",
		26: "Steel-String Guitar",
		27: "Jazz Guitar",
		28: "Clean Electric Guitar",
		29: "Muted Electric Guitar",
		30: "Overdriven Guitar",
		31: "Distortion Guitar",
		32: "Guitar Harmonics",

		# Bass:
		33: "Acoustic Bass",
		34: "Fingered Bass",
		35: "Picked Bass",
		36: "Fretless Bass",
		37: "Slap Bass 1",
		38: "Slap Bass 2",
		39: "Synth Bass 1",
		40: "Synth Bass 2",

		# Strings:
		41: "Violin",
		42: "Viola",
		43: "Cello",
		44: "Contrabass",
		45: "Tremolo Strings",
		46: "Pizzicato Strings",
		47: "Harp",
		48: "Timpani",

		# Orchestral Ensemble:
		49: "String Ensemble",
		50: "Slow String Ensemble",
		51: "Synth Strings 1",
		52: "Synth Strings 2",
		53: "Choir Aahs",
		54: "Voice Oohs",
		55: "Synth Voice",
		56: "Orchestra Hit",

		# Brass:
		57: "Trumpet",
		58: "Trombone",
		59: "Tuba",
		60: "Muted Trumpet",
		61: "French Horn",
		62: "Brass Section",
		63: "Synth Brass 1",
		64: "Synth Brass 2",

		# Reed:
		65: "Soprano Sax",
		66: "Alto Sax",
		67: "Tenor Sax",
		68: "Baritone Sax",
		69: "Oboe",
		70: "English Horn",
		71: "Bassoon",
		72: "Clarinet",

		# Wind:
		73: "Piccolo",
		74: "Flute",
		75: "Recorder",
		76: "Pan Flute",
		77: "Blown Bottle",
		78: "Shakuhachi",
		79: "Whistle",
		80: "Ocarina",

		# Synth Lead:",
		81: "Square Lead",
		82: "Saw Lead",
		83: "Synth Calliope",
		84: "Chiffer Lead",
		85: "Charang",
		86: "Solo Synth Vox",
		87: "5th Saw Wave",
		88: "Bass & Lead",

		# Synth Pad:
		89: "Fantasia Pad",
		90: "Warm Pad",
		91: "Polysynth Pad",
		92: "Space Voice Pad",
		93: "Bowed Glass Pad",
		94: "Metal Pad",
		95: "Halo Pad",
		96: "Sweep Pad",

		# Synth Effects:
		97: "Ice Rain",
		98: "Soundtrack",
		99: "Crystal",
		100: "Atmosphere",
		101: "Brightness",
		102: "Goblin",
		103: "Echo Drops",
		104: "Star Theme",

		# Ethnic:
		105: "Sitar",
		106: "Banjo",
		107: "Shamisen",
		108: "Koto",
		109: "Kalimba",
		110: "Bagpipe",
		111: "Fiddle",
		112: "Shanai",

		# Percussive:
		113: "Tinkle Bell",
		114: "Agogo",
		115: "Steel Drums",
		116: "Woodblock",
		117: "Taiko Drum",
		118: "Melodic Tom 1",
		119: "Synth Drum",
		120: "Reverse Cymbal",

		# Sound effects:
		121: "Guitar Fret Noise",
		122: "Breath Noise",
		123: "Seashore",
		124: "Bird Tweet",
		125: "Telephone 1",
		126: "Helicopter",
		127: "Applause",
		128: "Gun Shot",
	},
	1: {
		# Piano:
		1: "Wide Acoustic Grand",
		2: "Wide Bright Acoustic",
		3: "Wide Electric Grand",
		4: "Wide Honky-tonk",
		5: "Detuned Electric Piano 1",
		6: "Detuned Electric Piano 2",
		7: "Coupled Harpsichord",
		8: "Pulse Clavinet",

		# Chromatic Percussion:
		12: "Wet Vibraphone",
		13: "Wide Marimba",
		15: "Church Bells",

		# Organ:
		17: "Detuned Organ 1",
		18: "Detuned Organ 2",
		20: "Church Organ 2",
		21: "Puff Organ",
		22: "Italian Accordion",

		# Guitar:
		25: "Ukelele",
		26: "12-String Guitar",
		27: "Hawaiian Guitar",
		28: "Chorus Guitar",
		29: "Funk Guitar",
		30: "Guitar Pinch",
		31: "Feedback Guitar",
		32: "Guitar Feedback",

		# Bass:
		34: "Finger Slap",
		39: "Synth Bass 101",
		40: "Synth Bass 4",

		# Strings:
		41: "Slow Violin",
		47: "Yang Qin",

		# Orchestral Ensemble:
		49: "Orchestra Strings",
		51: "Synth Strings 3",
		53: "Choir Aahs 2",
		54: "Humming",
		55: "Analog Voice",
		56: "Bass Hit",

		# Brass:
		57: "Dark Trumpet",
		58: "Trombone 2",
		60: "Muted Trumpet 2",
		61: "French Horn 2",
		62: "Brass Section",
		63: "Synth Brass 3",
		64: "Synth Brass 4",

		# Synth Lead:
		81: "Square Wave",
		82: "Saw Wave",
		85: "Wire Lead",
		88: "Delayed Lead",

		# Synth Pad:
		90: "Sine Pad",
		92: "Itopia",

		# Synth Effects:
		99: "Synth Mallet",
		103: "Echo Bell",

		# Ethnic:
		105: "Sitar 2",
		108: "Taisho Koto",

		# Percussive:
		116: "Castanets",
		117: "Concert Bass Drum",
		118: "Melodic Tom 2",
		119: "808 Tom",

		# Sound effects:
		121: "Guitar Cut Noise",
		122: "Flute Key Click",
		123: "Rain",
		124: "Dog",
		125: "Telephone 2",
		126: "Car Engine",
		127: "Laughing",
		128: "Machine Gun",
	},
	2: {
		# Piano:
		1: "Dark Acoustic Grand",
		5: "Electric Piano 1 Variation",
		6: "Electric Piano 2 Variation",
		7: "Wide Harpsichord",

		# Chromatic Percussion:
		15: "Carillon",

		# Organ:
		17: "60's Organ 1",
		18: "Organ 5",
		20: "Church Organ 3",

		# Guitar:
		25: "Open Nylon Guitar",
		26: "Mandolin",
		28: "Mid Tone Guitar",
		29: "Funk Guitar 2",
		31: "Distortion Rtm Guitar",

		# Bass:
		39: "Synth Bass 3",
		40: "Rubber Bass",

		# Orchestral Ensemble:
		49: "60's Strings",
		56: "6th Hit",

		# Brass:
		58: "Bright Trombone",
		63: "Analog Brass 1",
		64: "Analog Brass 2",

		# Synth Lead:
		81: "Sine Wave",
		82: "Doctor Solo",

		# Synth Effects:
		103: "Echo Pan",

		# Percussive:
		119: "Electric Percussion",

		# Sound effects:
		121: "String Slap",
		123: "Thunder",
		124: "Horse Gallop",
		125: "Door Creaking",
		126: "Car Stop",
		127: "Screaming",
		128: "Lasergun",
	},
	3: {
		# Piano:
		5: "60's Electric Piano",
		6: "Electric Piano Legend",
		7: "Open Harpsichord",

		# Organ:
		17: "Organ 4",

		# Guitar:
		25: "Nylon Guitar 2",
		26: "Steel + Body",
		29: "Jazz Man",

		# Bass:
		39: "Clavi Bass",
		40: "Attack Pulse",

		# Brass:
		63: "Jump Brass",

		# Synth Lead:
		82: "Natural Lead",

		# Sound effects:
		123: "Wind",
		124: "Bird 2",
		125: "Door Closing",
		126: "Car Pass",
		127: "Punch",
		128: "Explosion",
	},
	4: {
		# Piano:
		6: "Electric Piano Phase",

		# Bass:
		39: "Hammer",

		# Synth Lead:
		82: "Sequenced Saw",

		# Sound effects:
		123: "Stream",
		125: "Scratch",
		126: "Car Crash",
		127: "Heart Beat",
	},
	5: {
		# Sound effects:
		123: "Bubble",
		125: "Wind Chimes",
		126: "Siren",
		127: "Footsteps",
	},
	6: {
		# Sound effects:
		126: "Train",
	},
	7: {
		# Sound effects:
		126: "Jetplane",
	},
	8: {
		# Sound effects:
		126: "Starship",
	},
	9: {
		# Sound effects:
		126: "Burst Noise",
	}
}

# General MIDI Drum Note Numbers

# General MIDI Drums (Channel 10): The numbers listed correspond to the MIDI note number for that drum sound.
# Drum sounds added in General MIDI Level 2 are tagged with (GM2). 
# https://soundprogramming.net/file-formats/general-midi-drum-note-numbers/

MIDI_PERCUSSION_NAMES = {
	27: "High Q (GM2)",
	28: "Slap (GM2)",
	29: "Scratch Push (GM2)",
	30: "Scratch Pull (GM2)",
	31: "Sticks (GM2)",
	32: "Square Click (GM2)",
	33: "Metronome Click (GM2)",
	34: "Metronome Bell (GM2)",
	35: "Bass Drum 2",
	36: "Bass Drum 1",
	37: "Side Stick",
	38: "Snare Drum 1",
	39: "Hand Clap",
	40: "Snare Drum 2",
	41: "Low Tom 2",
	42: "Closed Hi-hat",
	43: "Low Tom 1",
	44: "Pedal Hi-hat",
	45: "Mid Tom 2",
	46: "Open Hi-hat",
	47: "Mid Tom 1",
	48: "High Tom 2",
	49: "Crash Cymbal 1",
	50: "High Tom 1",
	51: "Ride Cymbal 1",
	52: "Chinese Cymbal",
	53: "Ride Bell",
	54: "Tambourine",
	55: "Splash Cymbal",
	56: "Cowbell",
	57: "Crash Cymbal 2",
	58: "Vibra Slap",
	59: "Ride Cymbal 2",
	60: "High Bongo",
	61: "Low Bongo",
	62: "Mute High Conga",
	63: "Open High Conga",
	64: "Low Conga",
	65: "High Timbale",
	66: "Low Timbale",
	67: "High Agogo",
	68: "Low Agogo",
	69: "Cabasa",
	70: "Maracas",
	71: "Short Whistle",
	72: "Long Whistle",
	73: "Short Guiro",
	74: "Long Guiro",
	75: "Claves",
	76: "High Wood Block",
	77: "Low Wood Block",
	78: "Mute Cuica",
	79: "Open Cuica",
	80: "Mute Triangle",
	81: "Open Triangle",
	82: "Shaker (GM2)",
	83: "Jingle Bell (GM2)",
	84: "Belltree (GM2)",
	85: "Castanets (GM2)",
	86: "Mute Surdo (GM2)",
	87: "Open Surdo (GM2)",
}
