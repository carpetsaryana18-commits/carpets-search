import streamlit as st
import pandas as pd

# ------------------------------
# STREAMLIT PAGE CONFIG
# ------------------------------
st.set_page_config(page_title="Aryana Carpets - Dashboard", layout="wide")
st.title("🧵 Aryana Carpets Dashboard")

# ------------------------------
# FILE UPLOAD
# ------------------------------
uploaded_file = st.file_uploader("📂 Upload Master Excel File", type=["xlsx", "xls"])

if uploaded_file:
    try:
        # Load sheets
        inventory_df = pd.read_excel(uploaded_file, sheet_name="Inventory - Aryana", header=0)
        sales_df = pd.read_excel(uploaded_file, sheet_name="Asia Carpets Sales", header=0)

        # Clean column names (remove spaces)
        inventory_df.columns = inventory_df.columns.str.strip()
        sales_df.columns = sales_df.columns.str.strip()

        # Tabs for modules
        tab1, tab2 = st.tabs(["📦 Inventory", "💰 Sales & Accounts"])

        # ------------------------------
        # TAB 1: INVENTORY MODULE
        # ------------------------------
        with tab1:
            st.subheader("📦 Inventory - Aryana")

            # Search Filters
            with st.expander("🔍 Search & Filters"):
                serial_search = st.text_input("Search Serial No")
                origin_search = st.text_input("Search by Origin / Manufacturer")
                size_search = st.text_input("Search by Size")
                status_filter = st.multiselect(
                    "Filter by Status", options=inventory_df["Current Status"].dropna().unique()
                )

            # Apply Filters
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

            # Show Results
            st.dataframe(filtered_inventory, use_container_width=True)
            st.info(f"Showing {filtered_inventory.shape[0]} of {inventory_df.shape[0]} carpets")

            # Download
            @st.cache_data
            def convert_to_csv(df):
                return df.to_csv(index=False).encode("utf-8")

            csv_inventory = convert_to_csv(filtered_inventory)
            st.download_button(
                "⬇️ Download Filtered Inventory",
                data=csv_inventory,
                file_name="filtered_inventory.csv",
                mime="text/csv"
            )

        # ------------------------------
        # TAB 2: SALES MODULE
        # ------------------------------
        with tab2:
            st.subheader("💰 Asia Carpets Sales - Accounting")

            # Debug: Show actual column names
            st.write("📑 Columns in Sales Sheet:", list(sales_df.columns))

            if "Date" in sales_df.columns:
                # Ensure Date is datetime
                sales_df["Date"] = pd.to_datetime(sales_df["Date"], errors="coerce")

                # Date Range Filter
                min_date, max_date = sales_df["Date"].min(), sales_df["Date"].max()
                date_range = st.date_input("Select Date Range", [min_date, max_date])

                filtered_sales = sales_df[
                    (sales_df["Date"] >= pd.to_datetime(date_range[0])) &
                    (sales_df["Date"] <= pd.to_datetime(date_range[1]))
                ]

                # KPIs
                total_sales = filtered_sales["Amount in BHD"].sum()
                st.metric("Total Sales (BHD)", f"{total_sales:,.2f}")

                # Group by Item
                if "Items Details" in filtered_sales.columns:
                    sales_by_item = (
                        filtered_sales.groupby("Items Details")["Amount in BHD"]
                        .sum()
                        .sort_values(ascending=False)
                    )
                    st.subheader("📊 Sales by Item")
                    st.bar_chart(sales_by_item)

                # Show Table
                st.subheader("🗂️ Sales Records")
                st.dataframe(filtered_sales, use_container_width=True)

                # Download
                csv_sales = convert_to_csv(filtered_sales)
                st.download_button(
                    "⬇️ Download Sales Report",
                    data=csv_sales,
                    file_name="sales_report.csv",
                    mime="text/csv"
                )
            else:
                st.error("⚠️ Could not find a column named 'Date'. Please check your Excel header row.")

    except ValueError:
        st.error("⚠️ The uploaded file must contain both 'Inventory - Aryana' and 'Asia Carpets Sales' sheets.")

else:
    st.info("Please upload your master Excel file to continue.")
