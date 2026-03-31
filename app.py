import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image

# ======================
# Layout pagina
# ======================

st.set_page_config(layout="wide")

st.title("Bioacoustic Spectrogram Browser")

# ======================
# Upload Excel
# ======================

excel_file = st.file_uploader("Upload Excel file", type=["xlsx"])

# ======================
# Base directories
# ======================

spectrogram_base = st.text_input(
    "Spectrogram base directory",
    "/Volumes/FC2280/fc2280"
)

recording_base = st.text_input(
    "Recording base directory",
    "/Volumes/FC2280/fc2280"
)

# ======================
# Se Excel caricato
# ======================

if excel_file:

    df = pd.read_excel(excel_file)

    # ======================
    # Session dataframe
    # ======================

    if "working_df" not in st.session_state:
        st.session_state.working_df = df.copy()

    working_df = st.session_state.working_df

    # ======================
    # Sidebar Navigation
    # ======================

    st.sidebar.title("Navigation")

    recordings = working_df["recording"].unique()

    if "rec_index" not in st.session_state:
        st.session_state.rec_index = 0

    n_rec = len(recordings)

    st.sidebar.markdown("### Recording")

    if n_rec > 1:

        st.session_state.rec_index = st.sidebar.slider(
            "Recording",
            0,
            n_rec-1,
            st.session_state.rec_index
        )

    else:

        st.session_state.rec_index = 0
        st.sidebar.write("Recording: 0")

    rec_prev, rec_next = st.sidebar.columns(2)

    with rec_prev:
        if st.button("⬅ Rec"):
            st.session_state.rec_index = max(
                0,
                st.session_state.rec_index - 1
            )

    with rec_next:
        if st.button("Rec ➡"):
            st.session_state.rec_index = min(
                n_rec-1,
                st.session_state.rec_index + 1
            )

    selected_recording = recordings[st.session_state.rec_index]

    # ======================
    # Chunk navigation
    # ======================

    rec_df = working_df[
        working_df["recording"] == selected_recording
    ]

    if "chunk_index" not in st.session_state:
        st.session_state.chunk_index = 0

    st.sidebar.markdown("### Chunk")

    n_chunks = len(rec_df)

    if n_chunks > 1:

        st.session_state.chunk_index = st.sidebar.slider(
            "Chunk",
            0,
            n_chunks-1,
            min(
                st.session_state.chunk_index,
                n_chunks-1
            )
        )

    else:

        st.session_state.chunk_index = 0
        st.sidebar.write("Chunk: 0")

    chunk_prev, chunk_next = st.sidebar.columns(2)

    with chunk_prev:
        if st.button("⬅ Chunk"):
            st.session_state.chunk_index = max(
                0,
                st.session_state.chunk_index - 1
            )

    with chunk_next:
        if st.button("Chunk ➡"):
            st.session_state.chunk_index = min(
                n_chunks-1,
                st.session_state.chunk_index + 1
            )

    row = rec_df.iloc[
        st.session_state.chunk_index
    ]

    col1, col2 = st.columns([2,1])

    # ======================
    # Spectrogram viewer
    # ======================

    with col1:

        st.subheader("Spectrogram")

        base = Path(spectrogram_base)

        # nuovo path con year
        image_path = (
            base
            / str(row["year"])
            / str(row["level"])
            / row["recording"]
            / row["chunk_file"]
        )

        if not image_path.exists():
            image_path = (
                base
                / row["recording"]
                / row["chunk_file"]
            )

        if image_path.exists():

            image = Image.open(image_path)

            st.image(
                image,
                use_container_width=True
            )

        else:
            st.warning("Spectrogram not found")

        st.write(
            f"Recording: {row['recording']} | "
            f"Chunk {row['chunk_id']} | "
            f"Level {row['level']}"
        )

        # ======================
        # AUDIO PLAYER
        # ======================

        st.markdown("### Recording audio")

        rec_base = Path(recording_base)

        recording_path = (
            rec_base
            / str(row["year"])
            / "recordings"
            / row["file_name"]
        )

        if not recording_path.exists():

            recording_path = (
                rec_base
                / row["file_name"]
            )

        if recording_path.exists():

            st.audio(str(recording_path))

        else:

            st.warning(
                "Recording audio not found"
            )

        # ======================
        # Info
        # ======================

        st.markdown("### Recording info")

        info1, info2, info3 = st.columns(3)

        info1.write("Recording")
        info1.write(row["recording"])

        info2.write("Chunk")
        info2.write(row["chunk_id"])

        info3.write("Level")
        info3.write(row["level"])

        st.markdown("### Time info")

        info4, info5, info6 = st.columns(3)

        info4.write("Year")
        info4.write(row.get("year", ""))

        info5.write("Month")
        info5.write(row.get("month", ""))

        info6.write("Day")
        info6.write(row.get("day", ""))

        info7, info8 = st.columns(2)

        info7.write("Hour")
        info7.write(row.get("hour", ""))

        info8.write("Seconds")
        info8.write(row.get("sec", ""))

        st.markdown("### File info")

        st.write(row.get("file_name", ""))

    # ======================
    # Annotation
    # ======================

    with col2:

        st.subheader("Annotation")

        # Raven checkbox
        raven_checked = st.checkbox(
            "Raven checked",
            value=bool(
                row.get(
                    "raven_checked",
                    False
                )
            )
        )

        annotation_cols = [

            col for col in working_df.columns

            if col.startswith("chunk_")

        ]

        annotation_values = {}

        # salva raven
        annotation_values[
            "raven_checked"
        ] = raven_checked

        for col in annotation_cols:

            label = col.replace(
                "chunk_",""
            ).replace(
                "_"," "
            ).title()

            current_value = row.get(
                col,
                ""
            )

            if pd.isna(
                current_value
            ):
                current_value = ""

            if "presence" in col:

                annotation_values[col] = st.selectbox(
                    label,
                    [
                        "",
                        "unknown",
                        "present",
                        "absent"
                    ],
                    index=[
                        "",
                        "unknown",
                        "present",
                        "absent"
                    ].index(
                        current_value
                        if current_value in [
                            "unknown",
                            "present",
                            "absent"
                        ]
                        else ""
                    )
                )

            elif "confidence" in col:

                annotation_values[col] = st.selectbox(
                    label,
                    [
                        "",
                        "low",
                        "medium",
                        "high"
                    ],
                    index=[
                        "",
                        "low",
                        "medium",
                        "high"
                    ].index(
                        current_value
                        if current_value in [
                            "low",
                            "medium",
                            "high"
                        ]
                        else ""
                    )
                )

            elif "notes" in col:

                annotation_values[col] = st.text_area(
                    label,
                    value=current_value
                )

            else:

                annotation_values[col] = st.text_input(
                    label,
                    value=current_value
                )

        # ======================
        # Save annotation
        # ======================

        if st.button("Save annotation"):

            idx = rec_df.index[
                st.session_state.chunk_index
            ]

            for col, value in annotation_values.items():

                working_df.loc[
                    idx,
                    col
                ] = value

            st.success(
                "Annotation saved"
            )

    # ======================
    # Sidebar Save / Export
    # ======================

    st.sidebar.markdown("---")

    st.sidebar.markdown(
        "### Data Management"
    )

    if st.sidebar.button(
        "💾 Save progress"
    ):

        working_df.to_excel(
            "beluga_chunk_progress.xlsx",
            index=False
        )

        st.sidebar.success(
            "Progress saved"
        )

    if st.sidebar.button(
        "📤 Export Excel"
    ):

        output_file = "beluga_chunk_FINAL.xlsx"

        working_df.to_excel(
            output_file,
            index=False
        )

        st.sidebar.success(
            "Excel exported"
        )

        with open(
            output_file,
            "rb"
        ) as f:

            st.sidebar.download_button(
                "Download Excel",
                f,
                file_name=output_file
            )