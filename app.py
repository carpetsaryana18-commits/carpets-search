# Show columns for debugging
st.write("📑 Columns in Sales Sheet:", list(sales_df.columns))

# Normalize column names (remove spaces, lowercase)
sales_df.columns = sales_df.columns.str.strip()

if "Date" in sales_df.columns:
    sales_df["Date"] = pd.to_datetime(sales_df["Date"], errors="coerce")

    # Date range filter
    min_date, max_date = sales_df["Date"].min(), sales_df["Date"].max()
    date_range = st.date_input("Select Date Range", [min_date, max_date])

    filtered_sales = sales_df[
        (sales_df["Date"] >= pd.to_datetime(date_range[0])) &
        (sales_df["Date"] <= pd.to_datetime(date_range[1]))
    ]

    # Show KPIs and charts
    total_sales = filtered_sales["Amount in BHD"].sum()
    st.metric("Total Sales (BHD)", f"{total_sales:,.2f}")

    sales_by_item = (
        filtered_sales.groupby("Items Details")["Amount in BHD"]
        .sum()
        .sort_values(ascending=False)
    )
    st.subheader("📊 Sales by Item")
    st.bar_chart(sales_by_item)

    st.subheader("🗂️ Sales Records")
    st.dataframe(filtered_sales, use_container_width=True)

else:
    st.error("⚠️ Could not find a column named 'Date'. Please check your Excel header row.")
