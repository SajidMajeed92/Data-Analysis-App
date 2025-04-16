# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from io import BytesIO
import plotly.io as pio

st.set_page_config(page_title="Classic Data Viz App", layout="wide")

# Title and intro
st.title("📊 Classic Data Visualization App")
st.markdown("""
Welcome to your one-stop platform for interactive data analysis.
- Upload a CSV or Excel file
- Explore insights through dynamic plots and summary statistics
""")

# File uploader
uploaded_file = st.file_uploader("📂 Upload a CSV or Excel file", type=["csv", "xls", "xlsx"])

if uploaded_file:
    file_type = uploaded_file.name.split('.')[-1]
    df = pd.read_csv(uploaded_file) if file_type == 'csv' else pd.read_excel(uploaded_file)

    # Remove unnamed index-like columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    st.subheader("📄 Data Preview")
    st.write(df.head())

    st.subheader("📊 Summary Statistics")
    st.dataframe(df.select_dtypes(include='number').describe().transpose())

    st.subheader("📌 Visualization Options")

    # Optional filters for analysis
    with st.expander("🔎 Add Filters (optional)"):
        filter_summary = []
        for col in df.select_dtypes(include=['object', 'category']).columns:
            unique_vals = df[col].unique().tolist()
            selected_vals = st.multiselect(f"Filter by {col}", options=unique_vals, default=unique_vals)
            if set(selected_vals) != set(unique_vals):
                filter_summary.append(f"{col}: {selected_vals}")
            df = df[df[col].isin(selected_vals)]

        if st.button("🔄 Reset Filters"):
            st.experimental_rerun()

        
    columns = df.columns.tolist()
    col1 = st.selectbox("Select Column for Analysis", columns)
    chart_type = st.selectbox("Select Chart Type", ["3D Scatter Plot", 
        "Bar Chart", "Histogram", "Pie Chart", "Box Plot", "Line Chart", 
        "Scatter Plot", "Heatmap", "Violin Plot", "KDE Plot"])

    if chart_type == "Bar Chart":
        value_counts = df[col1].value_counts()
        if not value_counts.empty:
            st.bar_chart(value_counts)
        else:
            st.warning("Selected column does not contain valid data for a bar chart.")

    elif chart_type == "Histogram":
        if pd.api.types.is_numeric_dtype(df[col1]):
            fig, ax = plt.subplots()
            sns.histplot(df[col1], kde=False, ax=ax)
            st.pyplot(fig)
            with st.expander("💾 Save Plot"):
                buf = BytesIO()
                fig.savefig(buf, format='png')
                st.download_button("Download as PNG", data=buf.getvalue(), file_name="plot.png", mime="image/png")

    elif chart_type == "Pie Chart":
        if df[col1].nunique() <= 10:
            fig, ax = plt.subplots()
            df[col1].value_counts().plot.pie(autopct='%1.1f%%', ax=ax)
            ax.set_ylabel('')
            st.pyplot(fig)
        else:
            st.warning("Too many unique values for pie chart.")

    elif chart_type == "Box Plot":
        if pd.api.types.is_numeric_dtype(df[col1]):
            fig, ax = plt.subplots()
            sns.boxplot(y=df[col1], ax=ax)
            st.pyplot(fig)

    elif chart_type == "Line Chart":
        if pd.api.types.is_numeric_dtype(df[col1]):
            st.line_chart(df[col1])

    elif chart_type == "3D Scatter Plot":
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        if len(numeric_cols) >= 3:
            x_col = st.selectbox("X-axis (3D)", numeric_cols, index=0)
            y_col = st.selectbox("Y-axis (3D)", numeric_cols, index=1)
            z_col = st.selectbox("Z-axis (3D)", numeric_cols, index=2)

            fig = px.scatter_3d(df, x=x_col, y=y_col, z=z_col, color=col1 if col1 in df.columns and df[col1].nunique() > 1 else None)
            st.plotly_chart(fig)
            with st.expander("💾 Save Plot"):
                fig.write_image("3d_plotly_fig.png")
                with open("3d_plotly_fig.png", "rb") as f:
                    st.download_button("Download as PNG", data=f, file_name="3d_plot.png", mime="image/png")
        else:
            st.warning("Need at least 3 numeric columns for 3D scatter plot.")

    elif chart_type == "Scatter Plot":
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        if len(numeric_cols) >= 2:
            x_col = st.selectbox("X-axis", numeric_cols, index=0)
            y_col = st.selectbox("Y-axis", numeric_cols, index=1)

            if col1 in df.columns and df[col1].nunique() > 1:
                fig = px.scatter(df, x=x_col, y=y_col, color=col1)
            else:
                fig = px.scatter(df, x=x_col, y=y_col)

            st.plotly_chart(fig)
            with st.expander("💾 Save Plot"):
                fig.write_image("plotly_fig.png")
                with open("plotly_fig.png", "rb") as f:
                    st.download_button("Download as PNG", data=f, file_name="plot.png", mime="image/png")
        else:
            st.warning("Need at least 2 numeric columns for scatter plot.")

    elif chart_type == "Heatmap":
        corr = df.select_dtypes(include='number').corr()
        if corr.shape[0] >= 2:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig)
        else:
            st.warning("Not enough numeric data for heatmap.")

    elif chart_type == "Violin Plot":
        num_cols = df.select_dtypes(include='number').columns
        cat_cols = df.select_dtypes(include='object').columns
        if len(cat_cols) > 0 and len(num_cols) > 0:
            cat_col = st.selectbox("Category Column", cat_cols)
            num_col = st.selectbox("Numeric Column", num_cols)
            fig, ax = plt.subplots()
            sns.violinplot(x=cat_col, y=num_col, data=df, ax=ax)
            st.pyplot(fig)
        else:
            st.warning("No suitable categorical and numeric columns for violin plot.")

    elif chart_type == "KDE Plot":
        if pd.api.types.is_numeric_dtype(df[col1]):
            fig, ax = plt.subplots()
            sns.kdeplot(df[col1], ax=ax, shade=True)
            st.pyplot(fig)

    st.success("✅ Visualization generated successfully!")

else:
    st.info("📁 Please upload a file to get started.")
