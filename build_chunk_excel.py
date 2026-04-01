#!/usr/bin/env python

import pandas as pd
from pathlib import Path
import re
import soundfile as sf

print("\n==============================")
print("Build Chunk Excel")
print("==============================\n")

# INPUT
spectrogram_dir = input("Spectrogram directory: ").strip('"')
recording_dir = input("Recording directory (.wav): ").strip('"')
year = input("Year (e.g. 2014): ")

spectrogram_path = Path(spectrogram_dir) / year
recording_path = Path(recording_dir) / year

levels = ["LOW", "MID", "HIGH"]

rows = []

print("\nScanning folders...\n")

for level in levels:

    level_path = spectrogram_path / level

    if not level_path.exists():
        print(f"Skipping {level}")
        continue

    recordings = sorted([d for d in level_path.iterdir() if d.is_dir()])

    for rec in recordings:

        recording_name = rec.name
        wav_file = recording_path / f"{recording_name}.wav"

        # durata recording
        duration_sec = None

        if wav_file.exists():
            try:
                info = sf.info(wav_file)
                duration_sec = round(info.duration, 2)
            except:
                print(f"Could not read {wav_file}")

        chunks = sorted(rec.glob("*.png"))

        for chunk in chunks:

            # chunk id
            match = re.search(r"chunk_(\d+)", chunk.name)

            if match:
                chunk_id = int(match.group(1))
            else:
                chunk_id = None

            # parse recording name
            datetime_str = None
            year_val = None
            month = None
            day = None
            hour = None
            minute = None
            sec = None
            site = None

            try:

                parts = recording_name.split("_")

                site = parts[0]

                year_val = parts[1][:4]
                month = parts[1][4:6]
                day = parts[1][6:8]

                hour = parts[2][:2]
                minute = parts[2][2:4]
                sec = parts[2][4:6]

                datetime_str = f"{year_val}-{month}-{day} {hour}:{minute}:{sec}"

            except:
                pass

            row = {

                "datetime_str": datetime_str,
                "file_name": recording_name + ".wav",
                "recording": recording_name,
                "site": site,
                "chunk_id": chunk_id,
                "chunk_file": chunk.name,
                "level": level,
                "year": year_val,
                "month": month,
                "day": day,
                "hour": hour,
                "min": minute,
                "sec": sec,
                "duration_sec": duration_sec,
                "chunk_presence": "",
                "chunk_sound_type": "",
                "chunk_confidence": "",
                "raven_checked": "",
                "chunk_notes": ""

            }

            rows.append(row)

print(f"\nTotal chunks found: {len(rows)}")

df = pd.DataFrame(rows)

columns_order = [

    "datetime_str",
    "file_name",
    "recording",
    "site",
    "chunk_id",
    "chunk_file",
    "level",
    "year",
    "month",
    "day",
    "hour",
    "min",
    "sec",
    "duration_sec",
    "chunk_presence",
    "chunk_sound_type",
    "chunk_confidence",
    "raven_checked",
    "chunk_notes"

]

df = df[columns_order]

df = df.sort_values(
    ["recording", "level", "chunk_id"]
)

output = f"beluga_chunks_{year}.xlsx"

df.to_excel(output, index=False)

print(f"\nSaved: {output}")
