import streamlit as st
import pandas as pd

# --- APP TITLE ---
st.set_page_config(page_title="Carpet Inventory Search", layout="wide")
st.title("🧵 Carpet Inventory Search App")

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("Upload your Master Excel file", type=["xlsx", "xls"])

if uploaded_file:
    try:
        # Load only the "Inventory - Aryana" sheet
        df = pd.read_excel(uploaded_file, sheet_name="Inventory - Aryana")

        st.success(f"Loaded 'Inventory - Aryana' with {df.shape[0]} rows and {df.shape[1]} columns.")

        # --- SEARCH FILTERS ---
        with st.expander("🔍 Search & Filters"):
            serial_search = st.text_input("Search Serial No")
            origin_search = st.text_input("Search by Origin / Manufacturer")
            size_search = st.text_input("Search by Size")
            status_filter = st.multiselect("Filter by Status", options=df["Current Status"].unique())

        # --- APPLY FILTERS ---
        filtered_df = df.copy()

        if serial_search:
            filtered_df = filtered_df[filtered_df["Serial No"].astype(str).str.contains(serial_search, case=False, na=False)]

        if origin_search:
            filtered_df = filtered_df[filtered_df["Carpet Origin & Manufacturer"].str.contains(origin_search, case=False, na=False)]

        if size_search:
            filtered_df = filtered_df[filtered_df["Size"].astype(str).str.contains(size_search, case=False, na=False)]

        if status_filter:
            filtered_df = filtered_df[filtered_df["Current Status"].isin(status_filter)]

        # --- SHOW RESULTS ---
        st.subheader("📊 Search Results")
        st.dataframe(filtered_df, use_container_width=True)

        st.info(f"Showing {filtered_df.shape[0]} results")

        # --- DOWNLOAD FILTERED DATA ---
        @st.cache_data
        def convert_to_excel(dataframe):
            return dataframe.to_csv(index=False).encode("utf-8")

        csv = convert_to_excel(filtered_df)
        st.download_button(
            "⬇️ Download Filtered Data",
            data=csv,
            file_name="filtered_inventory.csv",
            mime="text/csv"
        )

    except ValueError:
        st.error("The uploaded Excel file does not contain a sheet named 'Inventory - Aryana'. Please check and upload again.")
