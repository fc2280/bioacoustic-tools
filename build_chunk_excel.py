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

                # FORMAT 1: NYA-B_20200130_093000
                match1 = re.match(
                    r"([A-Za-z0-9\-]+)_(\d{8})_(\d{6})",
                    recording_name
                )

                # FORMAT 2: 5498.250607092504
                match2 = re.match(
                    r"([A-Za-z0-9\-]+)\.(\d{12})",
                    recording_name
                )

                if match1:

                    site = match1.group(1)
                    date = match1.group(2)
                    time = match1.group(3)

                    year_val = date[0:4]
                    month = date[4:6]
                    day = date[6:8]

                    hour = time[0:2]
                    minute = time[2:4]
                    sec = time[4:6]

                elif match2:

                    site = match2.group(1)
                    datetime_part = match2.group(2)

                    year_val = "20" + datetime_part[0:2]
                    month = datetime_part[2:4]
                    day = datetime_part[4:6]

                    hour = datetime_part[6:8]
                    minute = datetime_part[8:10]
                    sec = datetime_part[10:12]

                datetime_str = f"{year_val}-{month}-{day} {hour}:{minute}:{sec}"

            except Exception as e:
                print(f"Error parsing {recording_name}: {e}")

            if datetime_str is None:
                print(f"⚠ Could not parse: {recording_name}")

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

df = pd.DataFrame(rows, columns=columns_order)

df = df.sort_values(
    ["recording", "level", "chunk_id"]
)

output = f"beluga_chunks_{year}.xlsx"

df.to_excel(output, index=False)

print(f"\nSaved: {output}")
