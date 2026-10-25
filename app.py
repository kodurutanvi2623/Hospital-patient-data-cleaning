
import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(
    page_title="Hospital Patient Data Cleaning",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Hospital Patient Data Cleaning")
st.write("Upload, clean and download your patient dataset.")

uploaded_file = st.file_uploader(
    "Upload Patient CSV Dataset",
    type=["csv"]
)

if uploaded_file is not None:
    if "original_df" not in st.session_state:
        st.session_state["original_df"] = pd.read_csv(uploaded_file)

    df = st.session_state["original_df"].copy()

    st.subheader("Original Patient Dataset")
    st.dataframe(df, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", len(df))
    with col2:
        st.metric("Total Columns", len(df.columns))
    with col3:
        st.metric("Missing Values", int(df.isnull().sum().sum()))

    st.subheader("Cleaning Options")
   
    if "cleaned_df" not in st.session_state:
        st.session_state["cleaned_df"] = df.copy()

    cleaned_df = st.session_state["cleaned_df"].copy()

    if st.button("Remove Duplicate Records"):
        cleaned_df = cleaned_df.drop_duplicates()
        st.session_state["cleaned_df"] = cleaned_df
        st.success("Duplicate records removed!")
    
if st.button("Handle Missing Values"):
    for column in cleaned_df.columns:
        if cleaned_df[column].isnull().any():
            if pd.api.types.is_numeric_dtype(cleaned_df[column]):
                cleaned_df[column] = cleaned_df[column].fillna(
                    cleaned_df[column].median()
                )
            else:
                mode = cleaned_df[column].mode()
                if not mode.empty:
                    cleaned_df[column] = cleaned_df[column].fillna(
                        mode.iloc[0]
                    )

    st.session_state["cleaned_df"] = cleaned_df
    st.success("Missing values handled!")


    cleaned_df = st.session_state.get("cleaned_df", df.copy())

if st.button("Encode Categorical Columns"):
    categorical_columns = cleaned_df.select_dtypes(
        include=["object", "category"]
    ).columns

    if len(categorical_columns) > 0:
        categorical_columns = [
            col for col in categorical_columns
            if not col.lower().startswith("patient id")
        ]

        if categorical_columns:
            cleaned_df = pd.get_dummies(
                cleaned_df,
                columns=categorical_columns,
                dtype=int
            )
            st.session_state["cleaned_df"] = cleaned_df
            st.success("Categorical data encoded successfully!")
        else:
            st.info("No categorical columns available for encoding.")
    else:
        st.info("No categorical columns available for encoding.")

    st.subheader("Cleaned Patient Dataset")
    st.dataframe(cleaned_df, use_container_width=True)

    csv_data = cleaned_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Cleaned CSV",
        data=csv_data,
        file_name="cleaned_hospital_patient_data.csv",
        mime="text/csv"
    )
else:
    st.info("Please upload a patient CSV file to begin.")
