# PART 1
# # Data loading
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
try:
    df = pd.read_csv('metadata.csv.zip', compression='zip')
except FileNotFoundError:
    print("File not found. Please check the file path.")
    exit()

# Check the DataFrame dimensions (rows, columns)
print("DataFrame dimensions (rows, columns):")
print(df.shape)

# Identify data types of each column
print("Data types of each column:")
print(df.dtypes)

# Checking for missing values in important columns
print(df.info())
print(df.isnull().sum())

# Generate basic statistics for numerical columns
print("Basic statistics for numerical columns:")
print(df.describe())



# PART 2
# Identify columns with many missing values
missing_counts = df.isnull().sum()
many_missing = missing_counts[missing_counts > 0]
print("Columns with missing values:")
print(many_missing)

# Clean the dataset by filling missing values
# Use median for numeric columns, mode for object columns
for col in df.columns:
    if pd.api.types.is_numeric_dtype(df[col]):
        median_value = df[col].median()
        df[col] = df[col].fillna(median_value)
    else:
        # Only fill if there are missing values and mode is not empty
        if df[col].isnull().any():
            mode_series = df[col].mode()
            if not mode_series.empty:
                mode_value = mode_series[0]
            else:
                mode_value = ''
            df[col] = df[col].fillna(mode_value)

# Create a cleaned version of the dataset
cleaned_df = df.copy()
print("Cleaned DataFrame info:")
print(cleaned_df.info())

# Convert date columns to datetime format
date_columns = ['release_date', 'last_modified']
for col in date_columns:
    if col in cleaned_df.columns:
        cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
        # Fill any NaT values with the median date
        median_date = cleaned_df[col].median()
        cleaned_df[col] = cleaned_df[col].fillna(median_date)
        print(f"Converted {col} to datetime.")
        print(cleaned_df[col].head())
print("Cleaned DataFrame after date conversion:")
print(cleaned_df.info())

# Extract year from publication date for time-based analysis
if 'publication_date' in cleaned_df.columns:
    cleaned_df['publication_year'] = cleaned_df['publication_date'].dt.year.fillna(2020)
    print("Extracted publication year:")
    print(cleaned_df['publication_year'].head())



#   PART 3
# Count papers by publication year
if 'publication_year' in cleaned_df.columns:
    papers_per_year = cleaned_df['publication_year'].value_counts().sort_index()
    print("Number of papers published each year:")
    print(papers_per_year)

    # Plot the number of papers published each year
    plt.figure(figsize=(10, 6))
    sns.lineplot(x=papers_per_year.index, y=papers_per_year.values)
    plt.title('Number of Papers Published Each Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Papers')
    plt.grid(True)
    plt.show()

# Identify top journals publishing COVID-19 research
    if 'journal' in cleaned_df.columns:
        top_journals = cleaned_df['journal'].value_counts().head(10)
        print("Top 10 journals publishing COVID-19 research:")
        print(top_journals)

    # Plot the top journals
    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_journals.values, y=top_journals.index)
    plt.title('Top 10 Journals Publishing COVID-19 Research')
    plt.xlabel('Number of Papers')
    plt.ylabel('Journal')
    plt.show()

# Find most frequent words in titles
if 'title' in cleaned_df.columns:
    from collections import Counter
    import re

    # Combine all titles into a single string
    all_titles = ' '.join(cleaned_df['title'].dropna().astype(str)).lower()
    # Remove punctuation and split into words
    words = re.findall(r'\b\w+\b', all_titles)
    # Count word frequencies
    word_counts = Counter(words)
    most_common_words = word_counts.most_common(10)
    print("Most common words in titles:")
    print(most_common_words)

    # Plot the most common words
    words, counts = zip(*most_common_words)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=list(counts), y=list(words))
    plt.title('Most Common Words in Titles')
    plt.xlabel('Frequency')
    plt.ylabel('Word')
    plt.show()
    
# Plot distribution of paper counts by source
if 'source' in cleaned_df.columns:
    source_counts = cleaned_df['source'].value_counts()
    print("Paper counts by source:")
    print(source_counts)

    # Plot the distribution
    plt.figure(figsize=(10, 6))
    sns.barplot(x=source_counts.values, y=source_counts.index)
    plt.title('Distribution of Paper Counts by Source')
    plt.xlabel('Number of Papers')
    plt.ylabel('Source')
    plt.show()



# PART 4
# Create a basic layout of streamlit app with title and description
import streamlit as st

st.title("COVID-19 Data Archive")
st.write("Simple exploration of COVID-19 research papers")

# Add interactive widgets
year_range = st.slider("Select Publication Year Range", int(cleaned_df['publication_year'].min()), int(cleaned_df['publication_year'].max()), (2019, 2024))
st.write(f"Selected year range: {year_range[0]} - {year_range[1]}")

journal_options = cleaned_df['journal'].dropna().unique().tolist()
selected_journal = st.selectbox("Select Journal", ["All"] + sorted(journal_options))
st.write(f"Selected journal: {selected_journal}")

# Display visualizations in the app
filtered_df = cleaned_df[
    (cleaned_df['publication_year'] >= year_range[0]) & 
    (cleaned_df['publication_year'] <= year_range[1])
]
if selected_journal != "All":
    filtered_df = filtered_df[filtered_df['journal'] == selected_journal]

st.write(f"Number of papers in filtered data: {filtered_df.shape[0]}")

if 'publication_year' in filtered_df.columns and not filtered_df.empty:
    papers_per_year_filtered = filtered_df['publication_year'].value_counts().sort_index()
    st.line_chart(papers_per_year_filtered)
    st.bar_chart(filtered_df['source'].value_counts())
    st.bar_chart(filtered_df['journal'].value_counts().head(10))

    st.write("Most common words in titles:")
    if 'title' in filtered_df.columns and not filtered_df['title'].dropna().empty:
        all_titles_filtered = ' '.join(filtered_df['title'].dropna().astype(str)).lower()
        words_filtered = re.findall(r'\b\w+\b', all_titles_filtered)
        word_counts_filtered = Counter(words_filtered)
        most_common_words_filtered = word_counts_filtered.most_common(10)
        st.write(most_common_words_filtered)
    else:
        st.write("No titles found for the selected filter.")
else:
    st.write("No data found for the selected filter.")

# Show a sample of the data
st.write("Sample of the cleaned data:")
st.dataframe(filtered_df.head())