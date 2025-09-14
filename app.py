import streamlit as st
import pandas as pd

# ------------------------------
# STREAMLIT PAGE CONFIG
# ------------------------------
st.set_page_config(page_title="Aryana Carpets Dashboard", layout="wide")
st.title("🧵 Aryana Carpets Dashboard")

# ------------------------------
# FILE UPLOAD
# ------------------------------
uploaded_file = st.file_uploader("📂 Upload Master Excel File", type=["xlsx", "xls"])

if uploaded_file:
    try:
        # -------- INVENTORY MODULE --------
        inventory_df = pd.read_excel(uploaded_file, sheet_name="Inventory - Aryana", header=0)
        inventory_df.columns = inventory_df.columns.str.strip()

        # -------- SALES MODULE --------
        # Automatically detect first non-empty row for header
        raw_sales = pd.read_excel(uploaded_file, sheet_name="Sales - September 2025 (MD Joz and Aryana )", header=None)
        header_row_index = raw_sales.notna().any(axis=1).idxmax()  # first row with any non-NaN
        sales_df = pd.read_excel(
            uploaded_file,
            sheet_name="Sales - September 2025 (MD Joz and Aryana )",
            header=header_row_index
        )
        sales_df.columns = sales_df.columns.str.strip()

        # -------- TABS --------
        tab1, tab2 = st.tabs(["📦 Inventory", "💰 Sales & Accounts"])

        # -------- TAB 1: INVENTORY --------
        with tab1:
            st.subheader("📦 Inventory - Aryana")

            with st.expander("🔍 Search & Filters"):
                serial_search = st.text_input("Search Serial No")
                origin_search = st.text_input("Search by Origin / Manufacturer")
                size_search = st.text_input("Search by Size")
                status_filter = st.multiselect(
                    "Filter by Status", options=inventory_df["Current Status"].dropna().unique()
                )

            filtered_inventory = inventory_df.copy()

            if serial_search:
                filtered_inventory = filtered_inventory[
                    filtered_inventory["Serial No"].astype(str).str.contains(serial_search, case=False, na=False)
                ]
            if origin_search:
                filtered_inventory = filtered_inventory[
                    filtered_inventory["Carpet Origin & Manufacturer"].astype(str).str.contains(origin_search, case=False, na=False)
                ]
            if size_search:
                filtered_inventory = filtered_inventory[
                    filtered_inventory["Size"].astype(str).str.contains(size_search, case=False, na=False)
                ]
            if status_filter:
                filtered_inventory = filtered_inventory[
                    filtered_inventory["Current Status"].isin(status_filter)
                ]

            st.dataframe(filtered_inventory, use_container_width=True)
            st.info(f"Showing {filtered_inventory.shape[0]} of {inventory_df.shape[0]} carpets")

            @st.cache_data
            def convert_to_csv(df):
                return df.to_csv(index=False).encode("utf-8")

            st.download_button(
                "⬇️ Download Filtered Inventory",
                data=convert_to_csv(filtered_inventory),
                file_name="filtered_inventory.csv",
                mime="text/csv"
            )

        # -------- TAB 2: SALES --------
        with tab2:
            st.subheader("💰 Sales - Accounting")

            st.write("📑 Columns in Sales Sheet after cleaning:", list(sales_df.columns))

            # Ensure 'Date' column exists
            date_column_candidates = [col for col in sales_df.columns if "date" in col.lower()]
            if date_column_candidates:
                date_col = date_column_candidates[0]
                sales_df[date_col] = pd.to_datetime(sales_df[date_col], errors="coerce")

                # Date range filter
                min_date, max_date = sales_df[date_col].min(), sales_df[date_col].max()
                date_range = st.date_input("Select Date Range", [min_date, max_date])

                filtered_sales = sales_df[
                    (sales_df[date_col] >= pd.to_datetime(date_range[0])) &
                    (sales_df[date_col] <= pd.to_datetime(date_range[1]))
                ]

                # KPI
                if "Amount in BHD" in filtered_sales.columns:
                    total_sales = filtered_sales["Amount in BHD"].sum()
                    st.metric("Total Sales (BHD)", f"{total_sales:,.2f}")

                # Group by Items
                if "Items Details" in filtered_sales.columns:
                    sales_by_item = (
                        filtered_sales.groupby("Items Details")["Amount in BHD"]
                        .sum()
                        .sort_values(ascending=False)
                    )
                    st.subheader("📊 Sales by Item")
                    st.bar_chart(sales_by_item)

                st.subheader("🗂️ Sales Records")
                st.dataframe(filtered_sales, use_container_width=True)

                st.download_button(
                    "⬇️ Download Sales Report",
                    data=convert_to_csv(filtered_sales),
                    file_name="sales_report.csv",
                    mime="text/csv"
                )
            else:
                st.error("⚠️ No Date column found in the Sales sheet. Please check your Excel file.")

    except ValueError as e:
        st.error(f"⚠️ Error loading sheets: {e}")

else:
    st.info("Please upload your master Excel file to continue.")
