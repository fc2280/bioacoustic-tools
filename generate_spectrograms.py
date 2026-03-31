#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import soundfile as sf
from pathlib import Path
from tqdm import tqdm
import gc
from matplotlib.colors import LinearSegmentedColormap


# Raven colormap
raven = LinearSegmentedColormap.from_list(
    "raven",
    [
        "black",
        "#1a0f3d",
        "#3b0f70",
        "#8c2981",
        "#de4968",
        "#fe9f6d",
        "#fcfdbf"
    ]
)

print("\n==============================")
print("Spectrogram Generator")
print("==============================\n")


# YEAR
year = input("Enter year (e.g. 2014): ")

# INPUT
base_dir_input = input(
    "\nEnter recordings directory: "
).strip('"')

base_dir = Path(base_dir_input)
year_dir = base_dir / year


# OUTPUT
output_base_input = input(
    "\nEnter output directory: "
).strip('"')

output_base = Path(output_base_input)


# MODE
print("\nSelect analysis mode:")
print("1 = LOW frequency")
print("2 = MID frequency")
print("3 = HIGH frequency")

mode_choice = input("\nEnter choice (1/2/3): ")


if mode_choice == "1":
    mode = "low"
    chunk_duration = 60

elif mode_choice == "2":
    mode = "mid"
    chunk_duration = 30

elif mode_choice == "3":
    mode = "high"
    chunk_duration = 30

else:
    print("Invalid choice")
    exit()


output_year = output_base / year / mode.upper()

confirm = input("\nProceed? (y/n): ")

if confirm.lower() != "y":
    exit()


audio_files = sorted(list(year_dir.glob("*.wav")))
output_year.mkdir(parents=True, exist_ok=True)

sampling_rate = 192000


def create_output_folder(file):

    recording_name = file.stem
    output_folder = output_year / recording_name
    output_folder.mkdir(parents=True, exist_ok=True)

    return output_folder


def generate_spectrogram(y, sr, save_path, mode, start_time):

    if mode == "low":

        n_fft = 65536
        hop = 8192
        fmin = 0
        fmax = 2000
        vmin = -120
        vmax = -30

    elif mode == "mid":

        n_fft = 8192
        hop = 2048
        fmin = 1000
        fmax = 19000
        vmin = -110
        vmax = -30

    elif mode == "high":

        n_fft = 2048
        hop = 512
        fmin = 20000
        fmax = 76000
        vmin = -100
        vmax = -20


    # STFT
    S = librosa.stft(
        y,
        n_fft=n_fft,
        hop_length=hop
    )

    S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max)

    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)

    # Frequency band selection
    idx = np.where((freqs >= fmin) & (freqs <= fmax))[0]

    S_db = S_db[idx, :]
    freqs = freqs[idx]

    duration = len(y) / sr

    plt.figure(figsize=(14,4))

    librosa.display.specshow(
        S_db,
        sr=sr,
        hop_length=hop,
        x_axis='time',
        cmap=raven,
        vmin=vmin,
        vmax=vmax
    )

    # Y axis correct
    y_ticks = np.linspace(0, len(freqs), 5)
    y_labels = [f"{int(f)}" for f in np.linspace(fmin, fmax, 5)]

    plt.yticks(y_ticks, y_labels)

    # Continuous time axis
    ticks = np.linspace(0, duration, 6)
    labels = [f"{start_time + t:.0f}" for t in ticks]

    plt.xticks(ticks, labels)

    plt.ylabel("Frequency (Hz)")
    plt.xlabel("Time (s)")

    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    plt.close()

    del S
    del S_db


def process_recording(file):

    output_folder = create_output_folder(file)

    info = sf.info(file)
    duration = info.duration

    n_chunks = int(duration // chunk_duration)

    for chunk_index in range(n_chunks):

        start = chunk_index * chunk_duration

        save_path = output_folder / f"{file.stem}_chunk_{chunk_index}_{mode.upper()}.png"

        if save_path.exists():
            continue

        y, sr = librosa.load(
            file,
            sr=sampling_rate,
            offset=start,
            duration=chunk_duration
        )

        generate_spectrogram(
            y,
            sr,
            save_path,
            mode,
            start
        )

        del y
        gc.collect()


for file in tqdm(audio_files):

    process_recording(file)


print("\n==============================")
print("Processing completed")
print("==============================")