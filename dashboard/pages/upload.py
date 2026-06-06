# dashboard/pages/upload.py
"""CSV upload page with smart progressive disclosure UX."""
import streamlit as st
from ..utils.session_manager import AppState
from ..utils.csv_handler import process_upload


def render():
    """Render CSV upload page."""
    st.title("Upload Your City Data")

    st.markdown(
        """
    Upload a CSV file with Airbnb listing data from any city.

    **Required columns:** price, neighborhood, room type, accommodates
    **Optional columns:** bedrooms, bathrooms, beds, availability, rating

    The system will auto-detect column names (e.g., "Price per Night" → `price`)
    """
    )

    # Success message from previous upload (stored before rerun)
    if "_upload_success" in st.session_state:
        st.success(st.session_state["_upload_success"])
        del st.session_state["_upload_success"]

    uploaded_file = st.file_uploader(
        "Choose a CSV file", type=["csv"], help="Maximum file size: 100MB"
    )

    if uploaded_file is not None:
        with st.spinner("Processing your data..."):
            result = process_upload(uploaded_file, uploaded_file.name)

        if result["success"]:
            df = result["df"]
            warnings = result["warnings"]

            # Clean upload: minimal feedback
            if not warnings:
                st.session_state[AppState.UPLOADED_DF] = df
                st.session_state[AppState.DATA_SOURCE] = "uploaded"
                st.session_state[
                    "_upload_success"
                ] = f"✓ Uploaded {len(df):,} listings from {df['neighbourhood_cleansed'].nunique()} neighborhoods"
                st.rerun()

            # Warnings present: expand details automatically
            else:
                with st.expander("⚠ Data Quality Warnings", expanded=True):
                    for warning in warnings:
                        st.warning(warning)

                st.subheader("Preview")
                st.dataframe(df.head(10))

                st.subheader("Detected Columns")
                col_info = []
                for col in df.columns:
                    dtype = str(df[col].dtype)
                    missing = df[col].isna().sum()
                    col_info.append({"Column": col, "Type": dtype, "Missing": missing})
                st.table(col_info)

                if st.button("Use This Data Anyway"):
                    st.session_state[AppState.UPLOADED_DF] = df
                    st.session_state[AppState.DATA_SOURCE] = "uploaded"
                    st.session_state[
                        "_upload_success"
                    ] = f"✓ Uploaded {len(df):,} listings (with warnings)"
                    st.rerun()

        else:
            # Error: show details immediately
            error_type = result["error_type"]
            error_msg = result["error"]

            if error_type == "schema":
                st.error(f"Schema Error: {error_msg}")
                st.info(
                    "Make sure your CSV includes columns for: price, neighborhood, room type, and accommodates"
                )

            elif error_type == "quality":
                st.error(f"Data Quality Issue: {error_msg}")

            elif error_type == "size":
                st.error(error_msg)

            else:
                st.error(f"Upload Failed: {error_msg}")

    # Show current dataset info
    if st.session_state[AppState.DATA_SOURCE] == "uploaded":
        st.markdown("---")
        st.subheader("Currently Loaded Data")

        df = st.session_state[AppState.UPLOADED_DF]
        st.info(
            f"{len(df):,} listings from {df['neighbourhood_cleansed'].nunique()} neighborhoods"
        )

        if st.button("Clear Uploaded Data"):
            AppState.reset_to_default()
            st.rerun()
