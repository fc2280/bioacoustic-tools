#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import soundfile as sf
from pathlib import Path
from tqdm import tqdm
import gc
import multiprocessing as mp
from matplotlib.colors import LinearSegmentedColormap


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


def create_output_folder(file, output_year):

    recording_name = file.stem
    output_folder = output_year / recording_name
    output_folder.mkdir(parents=True, exist_ok=True)

    return output_folder


def get_params(mode):

    if mode == "low":
        return dict(n_fft=65536, hop=8192, fmin=0, fmax=2000, vmin=-120, vmax=-30)

    elif mode == "mid":
        return dict(n_fft=8192, hop=2048, fmin=1000, fmax=19000, vmin=-110, vmax=-30)

    elif mode == "high":
        return dict(n_fft=2048, hop=512, fmin=20000, fmax=76000, vmin=-100, vmax=-20)


def generate_spectrogram(y, sr, save_path, npy_path, mode, start_time):

    params = get_params(mode)

    S = librosa.stft(
        y,
        n_fft=params["n_fft"],
        hop_length=params["hop"]
    )

    S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max)

    freqs = librosa.fft_frequencies(sr=sr, n_fft=params["n_fft"])

    idx = np.where(
        (freqs >= params["fmin"]) &
        (freqs <= params["fmax"])
    )[0]

    S_db = S_db[idx, :]
    freqs = freqs[idx]

    np.save(npy_path, S_db)

    duration = len(y) / sr

    fig = plt.figure(figsize=(14,4))

    librosa.display.specshow(
        S_db,
        sr=sr,
        hop_length=params["hop"],
        x_axis='time',
        cmap=raven,
        vmin=params["vmin"],
        vmax=params["vmax"]
    )

    y_ticks = np.linspace(0, len(freqs), 5)
    y_labels = [f"{int(f)}" for f in np.linspace(params["fmin"], params["fmax"], 5)]

    plt.yticks(y_ticks, y_labels)

    ticks = np.linspace(0, duration, 6)
    labels = [f"{start_time + t:.0f}" for t in ticks]

    plt.xticks(ticks, labels)

    plt.ylabel("Frequency (Hz)")
    plt.xlabel("Time (s)")

    plt.tight_layout()
    plt.savefig(save_path, dpi=200)

    plt.close(fig)

    del S
    del S_db

    gc.collect()


def process_recording(args):

    file, mode, chunk_duration, sampling_rate, output_year = args

    output_folder = create_output_folder(file, output_year)

    info = sf.info(file)

    total_samples = info.frames
    chunk_samples = int(chunk_duration * sampling_rate)

    for start_sample in range(0, total_samples, chunk_samples):

        end_sample = start_sample + chunk_samples

        start_time = start_sample / sampling_rate

        save_png = output_folder / f"{file.stem}_chunk_{int(start_time)}_{mode.upper()}.png"
        save_npy = output_folder / f"{file.stem}_chunk_{int(start_time)}_{mode.upper()}.npy"

        if save_png.exists():
            continue

        y, sr = sf.read(
            file,
            start=start_sample,
            stop=end_sample
        )

        if len(y) < chunk_samples * 0.1:
            continue

        generate_spectrogram(
            y,
            sr,
            save_png,
            save_npy,
            mode,
            start_time
        )

        del y
        gc.collect()


if __name__ == "__main__":

    print("\n==============================")
    print("Spectrogram Generator PRO")
    print("==============================\n")

    year = input("Enter year (e.g. 2014): ")

    base_dir = Path(input("\nEnter recordings directory: ").strip('"'))
    year_dir = base_dir / year

    output_base = Path(input("\nEnter output directory: ").strip('"'))

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

    # LIMIT RAM USAGE
    n_cores = max(1, mp.cpu_count() // 2)

    print(f"\nUsing {n_cores} CPU cores\n")

    args = [
        (file, mode, chunk_duration, sampling_rate, output_year)
        for file in audio_files
    ]

    with mp.Pool(n_cores) as pool:

        list(
            tqdm(
                pool.imap(process_recording, args),
                total=len(audio_files)
            )
        )

    print("\n==============================")
    print("Processing completed")
    print("==============================")