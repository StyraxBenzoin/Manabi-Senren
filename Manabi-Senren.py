#!/usr/bin/env python
# coding: utf-8

# First download and import "https://github.com/BrenoAqua/Senren" note type into Anki
# Download "https://github.com/fafner8/Manabi" and import to Anki to get the media files in your collection
# Export the Manabi deck with "Notes in Plain Text (.txt)" selecting all checkboxes for inclusions 
# Run this script on the exported Manabi.txt file. Manabi-Senren.txt will be created.
# Import Manabi-Senren.txt into Anki
# Use "https://github.com/Manhhao/backfill-anki-yomitan" with Manabi_Backfill.json (edit glossary to your desired dictionaries) to fill the missing "glossary", "pitchAccents", "pitchPositions", "pitchCategories", and "frequencies"
# Done

import pandas as pd

# Load the file. EDIT TO MATCH YOUR FILENAME.
input_file = "Manabi.txt"

# Make a dataframe from the input file. Skip the first 3 rows as they are tags for Anki. We will add the tags later when writing the output.
manabi_df = pd.read_csv(input_file, sep="\t", skiprows=(0, 1, 2, 3, 4, 5), header=None)
manabi_df.columns = [
    "guid",
    "notetype",
    "deck",
    "word",
    "word_hirigana",
    "word_furigana",
    "word_romaji",
    "word_meaning",
    "word_audio",
    "sentence",
    "sentence_furigana",
    "sentence_meaning",
    "sentence_audio",
    "sentence2",
    "sentence2_furigana",
    "sentence2_meaning",
    "sentence2_audio",
    "notes",
    "frequency",
    "tags",
]

# Replace <b></b> tags with Senren's highlighting method <span class="highlight"></span>. Not stictly necessary as <b> is also supported in Senren
bold_fields = ["sentence", "sentence_furigana", "sentence2", "sentence2_furigana"]
for field in bold_fields:
    manabi_df[field] = manabi_df[field].str.replace(
        r"<b>(.*?)</b>", 
        r'<span class="highlight">\1</span>', 
        regex=True
    )

senren_fields = [
    "guid",
    "notetype",
    "deck",
    "word",
    "reading",
    "sentence",
    "sentenceFurigana",
    "sentenceTranslation",
    "sentenceCard",
    "audioCard",
    "notes",
    "hint",
    "picture",
    "wordAudio",
    "sentenceAudio",
    "selectionText",
    "definition",
    "glossary",
    "pitchAccents",
    "pitchPositions",
    "pitchCategories",
    "frequencies",
    "freqSort",
    "miscInfo",
    "dictionaryPreference",
    "tags",
]

# Create an empty DataFrame with these columns
senren_df = pd.DataFrame(columns=senren_fields)

# Function to wrap sentences in span "group" class tags and combine them. This handles multiple example sentences with Senren's scene switching feature
def wrap_and_combine(sentence_col1, sentence_col2):
    def wrapper(row):
        s1 = f'<span class="group">{row[sentence_col1]}</span>' if pd.notna(row[sentence_col1]) else ""
        s2 = f'<span class="group">{row[sentence_col2]}</span>' if pd.notna(row[sentence_col2]) else ""
        return s1 + s2
    return wrapper

# Map manabi_df columns to senren_df columns

senren_df["guid"] = manabi_df["guid"]
senren_df["notetype"] = "Senren"
senren_df["deck"] = "Manabi-Senren"
senren_df["word"] = manabi_df["word"]
senren_df["reading"] = manabi_df["word_hirigana"]
senren_df["sentence"] = manabi_df.apply(wrap_and_combine("sentence", "sentence2"), axis=1)
senren_df["sentenceFurigana"] = manabi_df.apply(wrap_and_combine("sentence_furigana", "sentence2_furigana"), axis=1)
senren_df["sentenceTranslation"] = manabi_df.apply(wrap_and_combine("sentence_meaning", "sentence2_meaning"), axis=1)
senren_df["sentenceCard"] = ""  # No equivalent
senren_df["audioCard"] = ""  # No equivalent
senren_df["notes"] = manabi_df["notes"]
senren_df["hint"] = ""  # No equivalent
senren_df["picture"] = ""  # No equivalent
senren_df["wordAudio"] = manabi_df["word_audio"]
senren_df["sentenceAudio"] = senren_df["sentenceAudio"] = (manabi_df["sentence_audio"].fillna("") + manabi_df["sentence2_audio"].fillna(""))
senren_df["selectionText"] = ""  # No equivalent
senren_df["definition"] = manabi_df["word_meaning"]
senren_df["glossary"] = ""  # No equivalent
senren_df["pitchAccents"] = ""  # No equivalent
senren_df["pitchCategories"] = ""  # No equivalent
senren_df["frequencies"] = ""  # No equivalent
senren_df["freqSort"] = manabi_df["frequency"].apply(lambda x: str(int(x)) if x % 1 == 0 else str(x)) # make zero decimals integer else keep float
senren_df["miscInfo"] = ""  # No equivalent
senren_df["dictionaryPreference"] = ""  # No equivalent
senren_df["tags"] = "" 

# Create the Anki header rows
headers = pd.DataFrame({
    'guid': ['#separator:tab', '#html:true', '#guid column:1', '#notetype column:2', '#deck column:3', '#tags column:26'],
    **{col: [''] * 6 for col in senren_df.columns[1:]}
})

# Concatenate Anki headers with senren_df
senren_df = pd.concat([headers, senren_df], ignore_index=True)

# Save the file, removing the dataframe headers and index.
senren_df.to_csv("Manabi-Senren.txt", sep="\t", index=False, header=False)

