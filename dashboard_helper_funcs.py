import pandas as pd
import plotly.graph_objects as go
import streamlit as st

@st.cache_data
def load_soc_dfs():
    """
    Loads pre-cleaned, deduplicated SOC4 and SOC6 parquet files.
    Returns:
        df_soc4, df_soc6
    """
    df_soc4 = pd.read_parquet("us_soc4_distances_clean.parquet")
    df_soc6 = pd.read_parquet("us_soc6_distances_clean.parquet")
    return df_soc4, df_soc6

################################################################################################################
################################################################################################################
################################################################################################################

def plot_distance_over_years(df_soc4, df_soc6, soc_mode, distance_type, soc1, soc2, start_year, end_year):
    """
    Returns a Plotly lineplot of distance over years for a SOC pair, with min/max horizontal lines.
    """
    # Select dataframe
    df = df_soc4 if soc_mode == "SOC4" else df_soc6
    soc1_colname = "SOC4_1_Code" if soc_mode == "SOC4" else "SOC6_1_Code"
    soc2_colname = "SOC4_2_Code" if soc_mode == "SOC4" else "SOC6_2_Code"

    # Canonical ordering of codes
    soc_min = min(soc1, soc2)
    soc_max = max(soc1, soc2)

    # Filter for the pair
    filtered = df[
        (df[soc1_colname] == soc_min) & (df[soc2_colname] == soc_max)
    ]

    # Filter by year range
    filtered = filtered[
        (filtered["year"] >= start_year) & (filtered["year"] <= end_year)
    ].sort_values("year")

    # Extract min/max values
    min_value = filtered[f"{distance_type}_Distance"].min()
    max_value = filtered[f"{distance_type}_Distance"].max()

    # Create figure
    fig = go.Figure()

    # Line trace with large markers
    fig.add_trace(
        go.Scatter(
            x=filtered["year"],
            y=filtered[f"{distance_type}_Distance"],
            mode="lines+markers",
            name="Distance",
            line=dict(width=3),
            marker=dict(size=8)
        )
    )

    # Add horizontal max line
    fig.add_hline(
        y=max_value,
        line_dash="dash",
        line_color="green",
        annotation_text=f"Max: {max_value:.3f}",
        annotation_position="top left"
    )

    # Add horizontal min line
    fig.add_hline(
        y=min_value,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Min: {min_value:.3f}",
        annotation_position="bottom left"
    )

    # Update layout
    fig.update_layout(
        title=f"{distance_type} Distance between {soc1} and {soc2} ({start_year}-{end_year})",
        xaxis=dict(
            title="Year",
            tickmode="linear",
            dtick=1
        ),
        yaxis=dict(title="Distance"),
        height=500
    )

    return fig

################################################################################################################
################################################################################################################
################################################################################################################

def get_top_bottom_k_table(df_soc4, df_soc6, soc_mode, distance_type, start_year, end_year, k, min_or_max, pivot_soc=None):
    """
    Returns a DataFrame with the top/bottom K pairs for a given year or year range.
    """
    # Select dataframe
    df = df_soc4 if soc_mode == "SOC4" else df_soc6
    soc1_colname = "SOC4_1_Code" if soc_mode == "SOC4" else "SOC6_1_Code"
    soc2_colname = "SOC4_2_Code" if soc_mode == "SOC4" else "SOC6_2_Code"
    soc1_title_col = "SOC4_1_Title" if soc_mode == "SOC4" else "SOC6_1_Title"
    soc2_title_col = "SOC4_2_Title" if soc_mode == "SOC4" else "SOC6_2_Title"

    # Filter by year(s)
    if start_year == end_year:
        filtered = df[df["year"] == start_year]
    else:
        filtered = df[
            (df["year"] >= start_year) & (df["year"] <= end_year)
        ]

    # Filter by pivot SOC if provided
    if pivot_soc:
        filtered = filtered[
            (filtered[soc1_colname] == pivot_soc) | (filtered[soc2_colname] == pivot_soc)
        ]

    # Sort ascending for Min, descending for Max
    ascending = min_or_max == "Min"
    sorted_df = filtered.sort_values(f"{distance_type}_Distance", ascending=ascending)

    # Take top K
    topk = sorted_df.head(k)

    # Columns to return
    cols = [
        "year",
        soc1_colname,
        soc1_title_col,
        soc2_colname,
        soc2_title_col,
        f"{distance_type}_Distance"
    ]

    # Reset index for clean output
    return topk[cols].reset_index(drop=True)

##################################################################################################################
##################################################################################################################
##################################################################################################################

def plot_average_distance_per_year(df_soc4, df_soc6, soc_mode, distance_type, start_year, end_year):
    """
    Returns a Plotly line plot of average distance per year, with min/max reference lines.
    """
    # Select dataframe
    df = df_soc4 if soc_mode == "SOC4" else df_soc6

    # Filter by year range
    filtered = df[
        (df["year"] >= start_year) & (df["year"] <= end_year)
    ]

    # Group and compute average
    avg_df = (
        filtered.groupby("year")[f"{distance_type}_Distance"]
        .mean()
        .reset_index()
        .sort_values("year")
    )

    # Get min and max values
    y_min = avg_df[f"{distance_type}_Distance"].min()
    y_max = avg_df[f"{distance_type}_Distance"].max()

    # Create figure manually for full control
    fig = go.Figure()

    # Add line trace with large markers
    fig.add_trace(go.Scatter(
        x=avg_df["year"],
        y=avg_df[f"{distance_type}_Distance"],
        mode="lines+markers",
        line=dict(color="blue"),
        marker=dict(size=10, color="blue"),
        name="Average Distance"
    ))

    # Add horizontal dashed lines
    fig.add_hline(
        y=y_max,
        line_dash="dash",
        line_color="green",
        annotation_text=f"Max: {y_max:.4f}",
        annotation_position="top left"
    )
    fig.add_hline(
        y=y_min,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Min: {y_min:.4f}",
        annotation_position="bottom left"
    )

    # Update layout to ensure all years are shown
    fig.update_layout(
        title=f"Average {distance_type} Distance per Year ({start_year}-{end_year})",
        xaxis_title="Year",
        yaxis_title="Average Distance",
        xaxis=dict(
            dtick=1  # Show every year tick
        ),
        height=500,  # Make plot larger
        width=900
    )

    return fig

################################################################################################################
################################################################################################################
################################################################################################################

import plotly.graph_objects as go

def plot_distance_heatmap(df_soc4, distance_type, year):
    """
    Returns a Heatmap of distances between SOC4 pairs as flat pairwise cells,
    with small tick labels.
    """
    soc1_col = "SOC4_1_Code"
    soc2_col = "SOC4_2_Code"

    # Filter by year
    filtered = df_soc4[df_soc4["year"] == year].copy()
    filtered[soc1_col] = filtered[soc1_col].astype(str)
    filtered[soc2_col] = filtered[soc2_col].astype(str)

    fig = go.Figure(
        data=go.Heatmap(
            x=filtered[soc2_col],
            y=filtered[soc1_col],
            z=filtered[f"{distance_type}_Distance"],
            colorscale="Viridis",
            colorbar=dict(title=f"{distance_type} Distance"),
            zmin=0
        )
    )

    fig.update_layout(
        title=f"{distance_type} Distance Heatmap between SOC4 Occupations ({year})",
        xaxis=dict(
            title="SOC4 Code",
            type="category",
            tickfont=dict(size=8)  # Make x labels smaller
        ),
        yaxis=dict(
            title="SOC4 Code",
            type="category",
            tickfont=dict(size=8)  # Make y labels smaller
        ),
        height=800
    )

    return fig

################################################################################################################
################################################################################################################
################################################################################################################

def lookup_title_from_code(df, code_col, title_col, code):
    """
    Returns the title corresponding to a code.
    """
    result = df[df[code_col] == code][title_col].unique()
    return result[0] if len(result) > 0 else "Not found"

def lookup_code_from_title(df, code_col, title_col, title):
    """
    Returns the code corresponding to a title.
    """
    result = df[df[title_col] == title][code_col].unique()
    return result[0] if len(result) > 0 else "Not found"

################################################################################################################
################################################################################################################
################################################################################################################