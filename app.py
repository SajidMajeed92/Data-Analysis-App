# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from io import BytesIO
import plotly.io as pio

st.set_page_config(page_title="Sleek Data Viz App", layout="wide")

# Theme toggle
mode = st.sidebar.radio("🌗 Select Theme Mode", ("Light", "Dark"))
if mode == "Dark":
    st.markdown("""
        <style>
            body {
                background-color: #1e1e1e;
                color: #f0f0f0;
            }
            .stApp {
                background-color: #1e1e1e;
                color: #f0f0f0;
            }
        </style>
    """, unsafe_allow_html=True)

st.title("📊 Sleek Data Visualization App")
st.markdown("""
Upload your dataset and explore it through powerful, interactive visualizations.
""")

col_left, col_right = st.columns([1, 2])

with col_left:
    uploaded_file = st.file_uploader("📂 Upload a CSV or Excel file", type=["csv", "xls", "xlsx"])

if uploaded_file:
    file_type = uploaded_file.name.split('.')[-1]
    df = pd.read_csv(uploaded_file) if file_type == 'csv' else pd.read_excel(uploaded_file)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    with col_right:
        st.subheader("📄 Data Preview")
        st.write(df.head())

        st.subheader("📊 Summary Statistics")
        st.dataframe(df.select_dtypes(include='number').describe().transpose())

        st.subheader("📌 Visualization Options")

        all_columns = df.columns.tolist()
        # Numeric and categorical columns filtered once for reuse
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

                                                
        chart_type = st.selectbox("Select Chart Type", ["None", "Bar Chart", "Histogram", "Pie Chart", "Box Plot", "Line Chart", "Scatter Plot", "3D Scatter Plot", "KDE Plot", "Violin Plot", "Heatmap"])

        selected_x = st.selectbox("X-axis Column", all_columns, index=None, help="Choose a column for X-axis")
        if chart_type in ["Scatter Plot", "3D Scatter Plot"]:
            selected_y = st.selectbox("Y-axis Column", all_columns, index=None, help="Choose a column for Y-axis")
        else:
            selected_y = None

        if chart_type == "None":
            st.info("Please select a chart type to begin visualization.")

        elif chart_type == "Bar Chart":
            if selected_x:
                value_counts = df[selected_x].value_counts()
                st.bar_chart(value_counts)
                with st.expander("ℹ️ About this chart"):
                    st.markdown("Bar charts help visualize the frequency of different categories to spot the most or least common groups.")

        elif chart_type == "Histogram":
            if selected_x and pd.api.types.is_numeric_dtype(df[selected_x]):
                fig, ax = plt.subplots()
                sns.histplot(df[selected_x], kde=False, ax=ax)
                st.pyplot(fig)
                st.caption("This plot shows how the values are distributed. It can help detect skewness, spread, and potential outliers.")
                with st.expander("💾 Save Plot"):
                    buf = BytesIO()
                    fig.savefig(buf, format='png')
                    st.download_button("Download as PNG", data=buf.getvalue(), file_name=f"histogram_{selected_x}.png", mime="image/png")

        elif chart_type == "Pie Chart":
            if selected_x and df[selected_x].nunique() <= 10:
                fig, ax = plt.subplots()
                df[selected_x].value_counts().plot.pie(autopct='%1.1f%%', ax=ax)
                ax.set_ylabel('')
                st.pyplot(fig)
                with st.expander("💾 Save Plot"):
                    buf = BytesIO()
                    fig.savefig(buf, format='png')
                    st.download_button("Download as PNG", data=buf.getvalue(), file_name=f"pie_chart_{selected_x}.png", mime="image/png")

        elif chart_type == "Box Plot":
            if selected_x and pd.api.types.is_numeric_dtype(df[selected_x]):
                fig, ax = plt.subplots()
                sns.boxplot(y=df[selected_x], ax=ax)
                st.pyplot(fig)
                with st.expander("💾 Save Plot"):
                    buf = BytesIO()
                    fig.savefig(buf, format='png')
                    st.download_button("Download as PNG", data=buf.getvalue(), file_name=f"box_plot_{selected_x}.png", mime="image/png")

        elif chart_type == "Line Chart":
            if selected_x and pd.api.types.is_numeric_dtype(df[selected_x]):
                fig, ax = plt.subplots()
                df[selected_x].plot(ax=ax)
                st.pyplot(fig)
                st.caption("Line charts help you understand time-series trends, such as seasonality or consistent growth/decline.")
                with st.expander("💾 Save Plot"):
                    buf = BytesIO()
                    fig.savefig(buf, format='png')
                    st.download_button("Download as PNG", data=buf.getvalue(), file_name=f"line_chart_{selected_x}.png", mime="image/png")
                st.caption("Line charts help you understand time-series trends, such as seasonality or consistent growth/decline.")

        elif chart_type == "Scatter Plot":
            if selected_x and selected_y:
                fig = px.scatter(df, x=selected_x, y=selected_y)
                st.plotly_chart(fig)
                st.caption("This chart reveals patterns, correlations, or clusters between selected variables.")
                with st.expander("💾 Save Plot"):
                    buf = BytesIO()
                    fig.write_image(buf, format='png')
                    st.download_button("Download as PNG", data=buf.getvalue(), file_name=f"scatter_{selected_x}_vs_{selected_y}.png", mime="image/png")

        elif chart_type == "3D Scatter Plot":
            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            if len(numeric_cols) >= 3:
                z_col = st.selectbox("Z-axis (3D)", numeric_cols, index=None, help="Must be a numeric column")
                if selected_x and selected_y:
                    fig = px.scatter_3d(df, x=selected_x, y=selected_y, z=z_col, color=None)
                    st.plotly_chart(fig)
                    with st.expander("💾 Save Plot"):
                        buf = BytesIO()
                        fig.write_image(buf, format='png')
                        st.download_button("Download as PNG", data=buf.getvalue(), file_name=f"3dscatter_{selected_x}_{selected_y}_{z_col}.png", mime="image/png")

        elif chart_type == "KDE Plot":
            if selected_x and pd.api.types.is_numeric_dtype(df[selected_x]):
                fig, ax = plt.subplots()
                sns.kdeplot(df[selected_x], ax=ax, shade=True)
                st.pyplot(fig)
                with st.expander("💾 Save Plot"):
                    buf = BytesIO()
                    fig.savefig(buf, format='png')
                    st.download_button("Download as PNG", data=buf.getvalue(), file_name=f"kde_{selected_x}.png", mime="image/png")

        elif chart_type == "Violin Plot":
            cat_cols = categorical_cols
            num_cols = numeric_cols
            if cat_cols and num_cols:
                cat_col = st.selectbox("Category Column", cat_cols)
                num_col = st.selectbox("Numeric Column", num_cols)
                fig, ax = plt.subplots()
                sns.violinplot(x=cat_col, y=num_col, data=df, ax=ax)
                st.pyplot(fig)
                with st.expander("💾 Save Plot"):
                    buf = BytesIO()
                    fig.savefig(buf, format='png')
                    st.download_button("Download as PNG", data=buf.getvalue(), file_name=f"violin_{cat_col}_vs_{num_col}.png", mime="image/png")

        elif chart_type == "Heatmap":
            corr = df.select_dtypes(include='number').corr()
            if corr.shape[0] >= 2:
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
                st.caption("A heatmap shows pairwise correlation between numeric variables, helping identify strong or weak relationships.")
                st.pyplot(fig)
                with st.expander("💾 Save Plot"):
                    buf = BytesIO()
                    fig.savefig(buf, format='png')
                    st.download_button("Download as PNG", data=buf.getvalue(), file_name="heatmap.png", mime="image/png")

else:
    with col_right:
        st.info("📁 Please upload a file to get started.")
