# Claire Ewen
# CS602
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import pydeck as pdk

# This program uses Streamlit, Pandas, Matplotlid, and PyDeck to analyze museum data.
# Users can filter and explore museums by state, revenue, location, and museum type.
# View charts, maps, and summary statistics that highlight trends in museum performance.

# read in data
def read_data():
    return pd.read_csv("museums.csv").set_index("Museum ID")


# [ST4] Custom streamlit page configuration
st.set_page_config(page_title="Museum Analytics Dashboard")


# [PY2] Returns three values (museum name, city, and museum type)
def largest_museum(filtered_df):
    top_museum = filtered_df.loc[filtered_df["Revenue"].idxmax()] # [DA3] Find museum with highest revenue
    museum_name = top_museum["Museum Name"]
    city = top_museum["City (Administrative Location)"]
    museum_type = top_museum["Museum Type"]
    return museum_name, city, museum_type

# [VIZ1] {ie chart with labels and totle showing museum type distribution
def museum_type_chart(filtered_df):
    type_counts = filtered_df["Museum Type"].value_counts()
    st.subheader("Museum Types in Selected State")
    fig, ax = plt.subplots()
    ax.pie(type_counts, labels=type_counts.index, autopct="%1.1f%%")
    plt.tight_layout()
    st.pyplot(fig)

# [VIZ2] bar chart showing top 10 museums by revenue
def revenue_chart(filtered_df):
    top_10 = filtered_df.nlargest(10, "Revenue")
    fig, ax = plt.subplots(figsize=(10,5))
    ax.barh(top_10["Museum Name"], top_10["Revenue"], color='purple')
    ax.set_title("Top 10 Museums by Revenue")
    ax.set_xlabel("Revenue ($)")
    ax.set_ylabel("Museum Name")
    plt.tight_layout()
    st.pyplot(fig)

# Horizontal bar chart showing average revenue by museum type
def revenue_by_type(filtered_df):
    revenue_type = (filtered_df.groupby("Museum Type")["Revenue"].mean().sort_values(ascending=False))
    fig, ax = plt.subplots(figsize=(10,5))
    ax.barh(revenue_type.index, revenue_type.values, color='green')
    ax.set_title("Average Revenue by Museum Type")
    ax.set_xlabel("Average Revenue ($)")
    ax.set_ylabel("Museum Type")
    plt.tight_layout()
    st.pyplot(fig)

# Horizontal bar chart that puts revenue into bins to get a better understanding of revenue distribution across a state
def revenue_ranges(filtered_df):
    bins = [0, 100000, 500000, 1000000, 5000000, float('inf')] # I used Copilot to help me figure out how to use the bins see section 2 of accompanying document.
    labels = ['Under $100K', '$100K-$500K', '$500K-$1M', '$1M-$5M', '$5M+'] # I used Copilot to help with the labels on bar chart
    filtered_df["Revenue Range"] = pd.cut(filtered_df["Revenue"], bins=bins, labels=labels)  # [DA6] Create revenue range column
    counts = (filtered_df["Revenue Range"].value_counts().sort_index())
    fig, ax = plt.subplots(figsize=(8,5))
    counts.plot(kind="barh",color="purple", ax=ax)
    ax.set_title("Museums by Revenue Range")
    ax.set_xlabel("Number of Museums")
    ax.set_ylabel("Revenue Range")
    plt.tight_layout()
    st.pyplot(fig)

# [MAP] Interactive PyDeck map with markers and hover tooltip information
def museum_map(filtered_df):
    st.subheader("Museum Locations")
    st.caption("Hover over any marker to view museum details including name, type, city, and revenue.")
    map_df = filtered_df.dropna(subset=["Latitude", "Longitude"])
    layer = pdk.Layer( "ScatterplotLayer", data=map_df, get_position="[Longitude, Latitude]", get_fill_color=[255, 0, 0], get_radius=5000, pickable=True)
    view_state = pdk.ViewState(latitude=map_df["Latitude"].mean(), longitude=map_df["Longitude"].mean(), zoom=5)
    tooltip = {"html":"""<b>{Museum Name}</b><br/>Type: {Museum Type}<br/>City: {City (Administrative Location)}<br/>Revenue: ${Revenue}"""}
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip))

# Filtering data for future plots
def filter_data():
    df = read_data()
    st.sidebar.header("Museum Filters")
    states = sorted(df["State (Administrative Location)"].dropna().unique())
    selected_state = st.sidebar.selectbox("Choose a State", states)   #[ST2] Streamlit slider widget
    filtered_df = df[df["State (Administrative Location)"] == selected_state]  # [DA4] Filter by selected state
    filtered_df["Revenue"] = pd.to_numeric(filtered_df["Revenue"], errors="coerce")  # [DA1] Convert REvenue column to numeric values
    min_revenue = st.sidebar.slider("Minimum Revenue", 0, int(filtered_df["Revenue"].max()),0)
    filtered_df = filtered_df[filtered_df["Revenue"] >= min_revenue]  #[DA5] Filter by revenue and museum type conditions
    museum_types = sorted( filtered_df["Museum Type"].dropna().unique())
    selected_types = st.sidebar.multiselect("Museum Types", museum_types, default=museum_types)  # [ST3] Streamlit multiselect widget
    filtered_df = filtered_df[filtered_df["Museum Type"].isin(selected_types)]  #[DA5] Filter by revenue and museum type conditions
    search = st.sidebar.text_input("Search Museum Name")  # [ST3] Additional widget: text input
    if search:
        filtered_df = filtered_df[filtered_df["Museum Name"].str.contains(search, case=False, na=False)]
    if filtered_df.empty:
        st.sidebar.error("No museums found matching your search. Please search again and press enter.")
        st.stop()
    return filtered_df

# [DA6] Create pivot table of average revenue by museum type and state
def museum_type_pivot(filtered_df):
    pivot = pd.pivot_table(filtered_df, values="Revenue", index="Museum Type", columns="State (Administrative Location)", aggfunc="mean")
    st.subheader("Average Revenue by Museum Type and State")
    st.dataframe(pivot.style.format("${:,.2f}"))

# Etric that shows the museum type with the most amount of revenue in the state
def top_museum_type(filtered_df):
    revenue_type = (filtered_df.groupby("Museum Type")["Revenue"].sum().sort_values(ascending=False))  # [DA9] Calculate total revenue
    highest = revenue_type.idxmax()
    st.metric("Highest Revenue Museum Type", highest)

# Function that gives the total revenue by museum type within the state
def total_revenue_type_chart(filtered_df):
    revenue_type = (filtered_df.groupby("Museum Type") ["Revenue"].sum().sort_values(ascending=True))
    fig, ax = plt.subplots(figsize=(10,5))
    ax.barh(revenue_type.index, revenue_type.values, color="purple")
    ax.set_title("Total Revenue by Museum Type")
    ax.set_xlabel("Total Revenue ($)")
    ax.set_ylabel("Museum Type")
    plt.tight_layout()
    st.pyplot(fig)

# [VIZ3] Scatter plot showing relationship between revenue and income
def revenue_income_scatter(filtered_df):
    filtered_df["Income"] = pd.to_numeric(filtered_df["Income"], errors="coerce")
    fig, ax = plt.subplots()
    ax.scatter(filtered_df["Income"], filtered_df["Revenue"], alpha=0.7, color="purple")
    ax.set_title("Revenue vs Income")
    ax.set_xlabel("Income")
    ax.set_ylabel("Revenue")
    ax.set_xscale("log")
    ax.set_yscale("log") # I used AI to help me with the log scaling of this chart see section 3 of accompanying document
    plt.tight_layout()
    st.pyplot(fig)

# I used AI to generate code to create this table see section 4 of accompanying documnet
def museum_type_summary(filtered_df):
    summary = (filtered_df.groupby("Museum Type").agg(Avg_Revenue=("Revenue", "mean"), total_revenue=("Revenue", "sum")).sort_values("total_revenue", ascending=False))
    st.subheader("Museum Type Summary")
    st.caption("This table gives an overview of the average versus total revenue for each museum type in the state.")
    st.dataframe(summary.style.format({"Avg_Revenue": "${:,.2f}", "total_revenue": "${:,.2f}"}))

# Horizontal bar chart that displays the top 10 cities with the highest revenue
def top_cities(filtered_df):
    city_revenue = (filtered_df.groupby("City (Administrative Location)")["Revenue"].sum().sort_values(ascending=True).tail(10))
    fig, ax = plt.subplots(figsize=(10,6))
    ax.barh(city_revenue.index, city_revenue.values, color="steelblue")
    ax.set_title("Top Cities by Revenue")
    ax.set_xlabel("Revenue ($)")
    ax.set_ylabel("City")
    st.subheader("Top Cities By Revenue")
    plt.tight_layout()
    st.pyplot(fig)

# I used AI to help with the creation of this table see section 4 on accompanying document
def leaders_by_type(filtered_df):
    leaders = (filtered_df.sort_values("Revenue", ascending=False).groupby("Museum Type").first())
    st.subheader("Leaders by Museum Type")
    st.caption("The table below identifies the highest revenue museum within each museum category.")
    st.dataframe(leaders[["Museum Name", "Revenue"]].style.format({"Revenue": "${:,.2f}"}))

# Bar chart that gives the top 10 number of museums in each city
def museums_by_city(filtered_df):
    city_counts = (filtered_df["City (Administrative Location)"]).value_counts().head(10)
    fig, ax = plt.subplots(figsize=(10,5))
    ax.bar(city_counts.index, city_counts.values, color="steelblue")
    ax.set_title("Top 10 cities by Number of Museums")
    ax.set_xlabel("City")
    ax.set_ylabel("Museum Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

# I used AI to help with the creation of this table see section 4 on accompanying document
def high_revenue_museums(filtered_df):
    high_revenue = filtered_df[filtered_df["Revenue"] > 1000000][["Museum Name", "Revenue"]]
    st.dataframe(high_revenue.style.format({"Revenue": "${:,.2f}"}))
    museum_names = [name for name, revenue in zip(filtered_df["Museum Name"], filtered_df["Revenue"])if revenue > 1000000]
# ^ List comprehension used to create a list of museum types and counts

# Dictionary that shows how many of each museum type there is in each city
def museum_type_dictionary(filtered_df):
    museum_counts = (filtered_df["Museum Type"].value_counts().to_dict()) # [PY5] Dictionary created from museum types and counts
    st.subheader("Museum Types Dictionary")
    for museum_type, count in museum_counts.items(): # [PY5} Accessing dictionary items
        st.write(f"{museum_type}: {count}")

# [PY1] Function with two parameters, one has default value ("Revenue")
# [PY3] Function returns a value (average revenue)
def revenue_stat(df, column="Revenue"):
    return df[column].mean()  # [DA9] Calculate average revenue using revenue column

# Metrics to give the number of museums, number of different museum types, and number of cities on the dashboard page
def data_explorer_metrics(filtered_df):
    col1, col2, col3 = st.columns(3) # I used aI to figure out how to put metrics onto my page see section 5 on accompanying document
    with col1:
        st.metric("Museums", len(filtered_df))
    with col2:
        st.metric("Museum Types", filtered_df["Museum Type"].nunique())
    with col3:
        st.metric("Cities", filtered_df["City (Administrative Location)"].nunique())

# Table with revenue statistics in data exploreer page
def revenue_statistics(filtered_df):
    st.subheader("Revenue Statistics")
    stats = (filtered_df["Revenue"].describe().to_frame())
    st.dataframe(stats.style.format("${:,.2f}"))

# Gives the drop down and the search bar and sorting ability in the total data table
def sortable_data(filtered_df):
    search = st.text_input("Search Table")
    if search:
        mask = filtered_df.astype(str).apply(lambda row: row.str.contains(search, case=False, na=False).any(), axis=1)
        filtered_df = filtered_df[mask] #I used AI to generate the code to get the searchbox field see section 1 of accompanying document
    sort_column = st.selectbox("Sort By", filtered_df.columns)
    if filtered_df.empty:
        st.warning("No matching records found.") # Copilot helped me with the warning error
        return
    st.write(f"Showing {len(filtered_df)} records")
    ascending = st.checkbox("Ascending", value=False)
    st.dataframe(filtered_df.sort_values(sort_column, ascending=ascending)) # [DA2] Sort dataframe by selected column ascending or descending


filtered_df = filter_data()
# [ST4] Sidebar navigation for customized application layout
page = st.sidebar.radio("Navigation", ["Home", "Dashboard", "Revenue Analysis", "Museum Types", "Geographic Analysis", "Data Explorer"])
# Tells what charts should be on which button on the radio bar on the side.
if page == "Home":
    st.title("Museum Analytics Dashboard")
    st.write("Created by: Claire Ewen")
    st.write("""This interactive dashboard explores museum revenue, museum types, and geographic trends across the United States.
    Users can filter museums by state, revenue level, museum type, and museum name to discover patterns in museum performance and distribution.""")
    st.info("Select a state from the sidebar to begin exploring museum data.")
    st.image(r"C:\Users\Claire Ewen\OneDrive - Bentley University\CS602\Museum.jfif", caption="Smithsonian Institution American Art Museum", use_container_width=True)

elif page == "Dashboard":
    st.title("Dashboard")
    st.write("""The dashboard provides a summary of museum activity within the selected state. 
    key metrics highlight the number of museums, the highest revenue museum, and the museum category
    generating the most revenue""")
    st.markdown("### Key Insights")
    museum_name, city, museum_type = largest_museum(filtered_df)
    st.metric("Museums", len(filtered_df))
    st.info(f"Highest Revenue Museum: {museum_name}\n\n"
            f"City: {city}\n\n"
            f"Type: {museum_type}")
    top_museum_type(filtered_df)
    st.subheader("Museums with Revenue Over $1 Million")
    high_revenue_museums(filtered_df)

elif page == "Revenue Analysis":
    st.title("Revenue Analysis")
    st.write("""This section focuses on financial performance across museums. 
    Explore revenue distributions, compare revenues across museum types, and examine the 
    relationship between income and revenue.""")
    st.subheader("Revenue Distribution")
    avg_revenue = revenue_stat(filtered_df)   # [PY1] Function called using default parameter [PY3] First Call
    avg_revenue2 = revenue_stat(filtered_df, "Revenue")   # [PY1] Function called by explicitly passing parameter [PY3] Second Call
    max_revenue = filtered_df["Revenue"].max()
    total_revenue = filtered_df["Revenue"].sum()
    st.metric("Total Revenue:", f"${total_revenue:,.2f}")
    col1, col2 = st.columns(2) # I used aI to figure out how to put metrics onto my page see section 5 on accompanying document
    with col1:
        st.metric("Average Revenue:", f"${avg_revenue:,.2f}")
    with col2:
        st.metric("Maximum Revenue:", f"{max_revenue:,.2f}")
    top_museum = filtered_df.loc[filtered_df["Revenue"].idxmax()]
    st.info(f"{top_museum['Museum Name']} generates the highest revenue in the selected state.")
    st.subheader("Revenue Ranges")
    st.caption(
        """The chart below groups museums into revenue categories to better visualize the distribution of museum earnings.""")
    revenue_ranges(filtered_df)
    st.subheader("Top Museums")
    st.caption("The chart below shows the top 10 museums by revenue based on the selected state.")
    revenue_chart(filtered_df)
    st.subheader("Revenue vs. Income")
    st.caption("""The scatterplot below helps identify whether museums with higher incomes generally
               generate higher revenues""")
    revenue_income_scatter(filtered_df)
    st.subheader("Museum Type Revenue")
    st.caption("The chart below displays the revenue distribution between museum type categories.")
    total_revenue_type_chart(filtered_df)

elif page == "Museum Types":
    st.title("Museum Types")
    st.write("""Museums are categorized into different types such as art, history, science, and specialized
    museums. This section compares museum categories based on counts and revenue performance.""")
    museum_type_dictionary(filtered_df)
    museum_type_chart(filtered_df)
    museum_type_summary(filtered_df)
    st.subheader("Museum Type Revenue")
    revenue_by_type(filtered_df)
    leaders_by_type(filtered_df)

elif page == "Geographic Analysis":
    st.title("Geographic Analysis")
    st.write("""Geography plays an important role in museum distribution and revenue generation. 
    Use the interactive map to explore where museums are located and examine which cities contribute the most revenue.""")
    col1, col2, col3 = st.columns(3) # I used aI to figure out how to put metrics onto my page see section 5 on accompanying document
    with col1:
        st.metric("Cities", filtered_df["City (Administrative Location)"].nunique())
    with col2:
        st.metric("Museums Mapped", len(filtered_df))
    with col3:
        city_revenue = (filtered_df.groupby("City (Administrative Location)")["Revenue"].sum())
        highest_city = city_revenue.idxmax()
        st.metric("Highest Revenue City", highest_city)
    museum_map(filtered_df)
    st.caption("The charts below compare museum concentration and revenue generation across cities.")
    st.subheader("Number of Museums in Each City")
    museums_by_city(filtered_df)
    top_cities(filtered_df)

elif page == "Data Explorer":
    st.title("Data Explorer")
    st.write("""The Data Explorer allows users to search, sort, and inspect the museum dataset in detail. 
    Interactive filtering makes it easy to locate specific museums and compare information across records.""")
    data_explorer_metrics(filtered_df)
    revenue_statistics(filtered_df)
    st.subheader("Search All Statistics")
    st.caption("Use the search box and sorting options below to customize the data view.")
    sortable_data(filtered_df)
    museum_type_pivot(filtered_df)










