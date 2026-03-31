# Bioacoustic Processing Pipeline

A modular pipeline for bioacoustic data processing and annotation.

## Workflow

1. Generate spectrograms

generate_spectrograms.py

2. Build chunk excel

build_chunk_excel.py

3. Annotate spectrograms

Streamlit app

app.py

4. Merge annotated datasets

merge_chunk_excels.py

## Pipeline

Recordings  
↓  
Spectrogram generation  
↓  
Chunk Excel generation  
↓  
Manual annotation  
↓  
Merge final dataset  

## Structure

spectrogram_generator/  
chunk_builder/  
annotation_app/  
merge_tools/  

## Requirements

Python 3.9+

Install dependencies:

pip install -r requirements.txt

## Streamlit app

Run:

streamlit run app.py
