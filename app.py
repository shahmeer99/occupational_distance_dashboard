import streamlit as st
import pandas as pd

# Import your functions
from dashboard_helper_funcs import (
    load_soc_dfs,
    plot_distance_over_years,
    get_top_bottom_k_table,
    plot_average_distance_per_year,
    plot_distance_heatmap,
    lookup_title_from_code,
    lookup_code_from_title
)

# Title and description
st.markdown("""
# SOC Distance Dashboard

This dashboard presents an interactive exploration of occupational distances derived from millions of US job advertisements. Each job ad has been classified into its corresponding O*NET Standard Occupational Classification (SOC) code. We calculate pairwise distances between SOCs based on the **skills required in job postings**, providing a novel data-driven measure of occupational similarity and divergence. These distance measures can inform research in labor economics, workforce development, and occupational mobility.

You can find additional methodological details in the following paper:  
[Measuring Distances Between Occupations Using Job Advertisements](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5096487)

---

## What This Dashboard Offers

- **SOC Lookup**
  
  Above the tabs, you can look up the official title of any SOC code, or retrieve the SOC code for a given title. This is available for both SOC4 and SOC6 classification levels.

- **Tabs**
  
  The dashboard has **five main tabs**:
  
  1. **Download Data**
     
     Download our processed distance data for SOC4 or SOC6 levels in either CSV or Parquet format. This allows you to work with the raw distance matrices directly in your own analyses.
  
  2. **Distance Over Years**
     
     Visualize how the distance between any two SOC codes has evolved over time. Select a pair of occupations and see a line plot showing their yearly distances, with clear markers for the minimum and maximum values.
  
  3. **Top/Bottom K Occupations**
     
     Identify the pairs of occupations that are most similar or most dissimilar in a given year or year range. This table shows the top or bottom *K* pairs sorted by their distance values, with options to filter by a specific SOC pivot code if desired.
  
  4. **Average Distance Per Year**
     
     Explore trends in occupational similarity across the entire labor market over time. This plot shows the average distance between all occupation pairs for each year, providing a high-level view of how occupations have converged or diverged.
  
  5. **Heatmap**
     
     Inspect a heatmap of pairwise distances between all SOC4 occupations in a selected year. This visualization helps you spot clusters of similar occupations and outliers with high dissimilarity.

---

Feel free to explore and download the data. If you have questions or feedback please reach out to us at aa658@georgetown.edu or mohammadshahmeerah@hbku.edu or ec1269@georgetown.edu !!!

""")

# Load the data
with st.spinner("Loading data..."):
    df_soc4, df_soc6 = load_soc_dfs()
st.success("Data loaded successfully.")

df_soc4, df_soc6 = load_soc_dfs()

### lookup Options
st.subheader("Lookup SOC Codes and Titles")

col1, col2 = st.columns(2)

# SOC4 lookup
with col1:
    st.markdown("**SOC4 Lookup**")

    soc4_code = st.selectbox("Select SOC4 Code", sorted(df_soc4["SOC4_1_Code"].unique()))
    title_from_code = lookup_title_from_code(
        df_soc4,
        "SOC4_1_Code",
        "SOC4_1_Title",
        soc4_code
    )
    st.write(f"**Title:** {title_from_code}")

    soc4_title = st.selectbox("Select SOC4 Title", sorted(df_soc4["SOC4_1_Title"].unique()))
    code_from_title = lookup_code_from_title(
        df_soc4,
        "SOC4_1_Code",
        "SOC4_1_Title",
        soc4_title
    )
    st.write(f"**Code:** {code_from_title}")

# SOC6 lookup
with col2:
    st.markdown("**SOC6 Lookup**")

    soc6_code = st.selectbox("Select SOC6 Code", sorted(df_soc6["SOC6_1_Code"].unique()))
    title_from_code6 = lookup_title_from_code(
        df_soc6,
        "SOC6_1_Code",
        "SOC6_1_Title",
        soc6_code
    )
    st.write(f"**Title:** {title_from_code6}")

    soc6_title = st.selectbox("Select SOC6 Title", sorted(df_soc6["SOC6_1_Title"].unique()))
    code_from_title6 = lookup_code_from_title(
        df_soc6,
        "SOC6_1_Code",
        "SOC6_1_Title",
        soc6_title
    )
    st.write(f"**Code:** {code_from_title6}")

# Create tabs for the 5 visualizations
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Download Data",
    "Distance Over Years",
    "Top/Bottom K Occupations",
    "Average Distance Per Year",
    "Heatmap"
])
# Tab 1: Download Data
with tab1:
    st.subheader("Download Data")
    download_soc = st.radio("Select dataset to download", ["SOC4", "SOC6"], horizontal=True)
    download_format = st.radio("Select format", ["CSV", "Parquet"], horizontal=True)

    if download_soc == "SOC4":
        data_to_download = df_soc4
    else:
        data_to_download = df_soc6

    if download_format == "CSV":
        data_bytes = data_to_download.to_csv(index=False).encode()
        mime = "text/csv"
        file_ext = "csv"
    else:
        import io
        buffer = io.BytesIO()
        data_to_download.to_parquet(buffer, index=False)
        data_bytes = buffer.getvalue()
        mime = "application/octet-stream"
        file_ext = "parquet"

    st.download_button(
        label=f"Download {download_soc} Data ({file_ext.upper()})",
        data=data_bytes,
        file_name=f"{download_soc.lower()}_data.{file_ext}",
        mime=mime
    )

# Tab 2: Distance Over Years
with tab2:
    st.header("Distance Over Years")
    # Widgets for inputs
    soc_mode = st.radio("SOC Mode", ["SOC4", "SOC6"])
    distance_type = st.radio("Distance Type", ["Euclidean", "Cosine"])
    soc1 = st.selectbox("SOC 1 Code", sorted(df_soc4["SOC4_1_Code"].unique()) if soc_mode=="SOC4" else sorted(df_soc6["SOC6_1_Code"].unique()))
    soc2 = st.selectbox("SOC 2 Code", sorted(df_soc4["SOC4_2_Code"].unique()) if soc_mode=="SOC4" else sorted(df_soc6["SOC6_2_Code"].unique()))
    start_year, end_year = st.slider("Year Range", min_value=int(df_soc4["year"].min()), max_value=int(df_soc4["year"].max()), value=(2010,2022))
    if st.button("Generate Plot", key="tab2"):
        fig = plot_distance_over_years(df_soc4, df_soc6, soc_mode, distance_type, soc1, soc2, start_year, end_year)
        st.plotly_chart(fig, use_container_width=True)

# Tab 3: Top/Bottom K Occupations
with tab3:
    st.header("Top/Bottom K Occupations")
    soc_mode = st.radio("SOC Mode", ["SOC4", "SOC6"], key="tab2_mode")
    distance_type = st.radio("Distance Type", ["Euclidean", "Cosine"], key="tab2_dist")
    start_year, end_year = st.slider("Year Range", min_value=int(df_soc4["year"].min()), max_value=int(df_soc4["year"].max()), value=(2010,2022), key="tab2_slider")
    min_or_max = st.radio("Show", ["Min", "Max"])
    k = st.slider("K", 1, 25, 5)
    pivot_soc = st.text_input("Pivot SOC (Optional)", "")
    if st.button("Generate Table", key="tab3"):
        pivot_soc_input = pivot_soc.strip() if pivot_soc else None
        table = get_top_bottom_k_table(df_soc4, df_soc6, soc_mode, distance_type, start_year, end_year, k, min_or_max, pivot_soc_input)
        st.dataframe(table)
        csv = table.to_csv(index=False).encode()
        st.download_button("Download CSV", csv, "top_bottom_k.csv")

# Tab 4: Average Distance Per Year
with tab4:
    st.header("Average Distance Per Year")
    soc_mode = st.radio("SOC Mode", ["SOC4", "SOC6"], key="tab3_mode")
    distance_type = st.radio("Distance Type", ["Euclidean", "Cosine"], key="tab3_dist")
    start_year, end_year = st.slider("Year Range", min_value=int(df_soc4["year"].min()), max_value=int(df_soc4["year"].max()), value=(2010,2022), key="tab3_slider")
    if st.button("Generate Plot", key="tab4"):
        fig = plot_average_distance_per_year(df_soc4, df_soc6, soc_mode, distance_type, start_year, end_year)
        st.plotly_chart(fig, use_container_width=True)

# Tab 5: Heatmap
with tab5:
    st.header("Heatmap")
    distance_type = st.radio("Distance Type", ["Euclidean", "Cosine"], key="tab4_dist")
    year = st.selectbox("Year", sorted(df_soc4["year"].unique()))
    if st.button("Generate Heatmap"):
        fig = plot_distance_heatmap(df_soc4, distance_type, year)
        st.plotly_chart(fig, use_container_width=True)
