# streamlit_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from io import BytesIO

# Step 1: Upload the File
st.title("📊 Data Visualization App")
st.write("Upload a CSV or Excel file to begin analysis")

# Sidebar filter and interaction options
st.sidebar.header("🔧 Filter Options")
filter_col = st.sidebar.multiselect("Select column(s) to filter:", [])

uploaded_file = st.file_uploader("Upload your file", type=["csv", "xls", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        applied_filters = []  # Track applied filters for summary

        # Refresh sidebar filters
        st.sidebar.subheader("Apply Filters")
        filter_col = st.sidebar.multiselect("Select column(s) to filter:", df.columns.tolist())
        if filter_col:
            for col in filter_col:
                if df[col].dtype == 'object':
                    selected_values = st.sidebar.multiselect(f"Filter {col} by:", df[col].unique().tolist())
                    if selected_values:
                        df = df[df[col].isin(selected_values)]
                        applied_filters.append(f"{col} in {selected_values}")
                else:
                    min_val = float(df[col].min())
                    max_val = float(df[col].max())
                    range_val = st.sidebar.slider(f"Filter {col} range:", min_val, max_val, (min_val, max_val))
                    df = df[df[col].between(*range_val)]
                    applied_filters.append(f"{col} between {range_val[0]} and {range_val[1]}")

        # Step 2: Show first 5 records
        st.subheader("🔍 Initial Data Preview")
        st.write(df.head())



        # Step 4: Column selection dropdown
        st.subheader("📌 Select Column for Visualization")
        selected_col = st.selectbox("Choose a column", df.columns)

        # Step 5: Chart selection
        st.subheader("📊 Choose Visualization Type")
        chart_type = st.selectbox("Select chart type", [
            "Bar Chart", "Pie Chart", "Scatter Plot", "Box Plot", "Histogram",
            "KDE with Bar Plot", "Correlation Matrix", "Bivariate Analysis", "Multivariate Analysis",
            "Violin Plot", "Categorical Heatmap", "3D Scatter Plot", "Time Series Line Plot"])

        # Step 6: Generate plots with validation
        st.subheader("📈 Visualization Output")

        # Display applied filters
        if applied_filters:
            st.markdown("### 🧾 Applied Filters")
            for f in applied_filters:
                st.markdown(f"- {f}")

        fig, ax = plt.subplots()
        try:
            if chart_type == "Time Series Line Plot":
                time_cols = df.select_dtypes(include=['datetime64', 'object']).columns.tolist()
                num_cols = df.select_dtypes(include='number').columns.tolist()
                time_col = st.selectbox("Select time/date column", time_cols)
                y_col = st.selectbox("Select value column for Y-axis", num_cols)
                try:
                    df[time_col] = pd.to_datetime(df[time_col])
                    fig_ts, ax_ts = plt.subplots()
                    df.sort_values(by=time_col).plot(x=time_col, y=y_col, ax=ax_ts)
                    ax_ts.set_title(f"Time Series Plot: {y_col} over {time_col}")
                    st.pyplot(fig_ts)
                    img_buffer = BytesIO()
                    fig_ts.savefig(img_buffer, format='png')
                    st.download_button("📸 Download Chart as PNG", data=img_buffer.getvalue(), file_name="time_series_plot.png", mime="image/png")
                except Exception as e:
                    st.error(f"Error parsing time column: {str(e)}")

            # Add chart export functionality placeholder
            elif chart_type != "3D Scatter Plot":
                # Plot example chart (replace this with actual plot logic as needed)
                st.write(f"Selected chart: {chart_type}")
                ax.plot([1, 2, 3], [4, 5, 6])
                st.pyplot(fig)
                img_buffer = BytesIO()
                fig.savefig(img_buffer, format='png')
                st.download_button("📸 Download Chart as PNG", data=img_buffer.getvalue(), file_name="chart.png", mime="image/png")

        except Exception as e:
            st.error(f"An error occurred during plotting: {str(e)}")

    except Exception as e:
        st.error(f"Failed to read the file. Error: {str(e)}")
else:
    st.info("Please upload a file to proceed.")
