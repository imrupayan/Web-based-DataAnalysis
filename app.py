import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import sqlite3
from pandasai import Agent
from pandasai.llm.local_llm import LocalLLM
from pandasai.responses import ResponseParser
import re

# Page Configuration
st.set_page_config(
    layout="wide",
    page_title="DataPulse | Analytics Dashboard",
    page_icon="📊",
)

# ── Login Authentication (uses CSS from login.html) ──────────────────────────
# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False

# if not st.session_state.logged_in:
#     # Apply the gradient background from login.html without breaking Streamlit widgets
#     st.markdown("""
#     <style>
#         .stApp {
#             background: linear-gradient(135deg, #0f2027, #203a43, #2c5364) !important;
#         }
#         header[data-testid="stHeader"] { background: transparent !important; }
#         [data-testid="stSidebar"] { display: none !important; }
#         .login-title {
#             text-align: center; color: #fff;
#             font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#             margin-bottom: 1rem;
#         }
#     </style>
#     """, unsafe_allow_html=True)

#     st.markdown("<h2 class='login-title'>Welcome</h2>", unsafe_allow_html=True)

#     col1, col2, col3 = st.columns([1.2, 1, 1.2])
#     with col2:
#         with st.form("login_form"):
#             email = st.text_input("Email ID", placeholder="Enter your email")
#             password = st.text_input("Password", type="password", placeholder="Enter your password")
#             submitted = st.form_submit_button("Login", use_container_width=True)

#         if submitted:
#             if email == "admin@datapulse.com" and password == "admin123":
#                 st.session_state.logged_in = True
#                 st.rerun()
#             else:
#                 st.error("Invalid email or password")

#         if st.button("Sign Up", use_container_width=True):
#             st.info("Sign up is not available yet. Use demo credentials: admin@datapulse.com / admin123")

#     st.stop()

class PermissiveParser(ResponseParser):
    def parse(self, result):
        if isinstance(result, dict):
            return result.get("value", "Analysis complete.")
        return result

# Dark Dashboard CSS 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #0d1117; color: #e2e8f0; }
header[data-testid="stHeader"] { background: #0d1117; border-bottom: 1px solid #1e2535; }
[data-testid="stSidebar"] { background-color: #161b27 !important; border-right: 1px solid #1e2535; }
[data-testid="stMetricValue"] { color: #e2e8f0 !important; font-size: 1.6rem !important; }
.dash-card {
    background: #1a2035; border: 1px solid #2a3450;
    border-radius: 14px; padding: 1.2rem; margin-bottom: 1rem;
}
.section-title { font-size: 1rem; font-weight: 600; color: #e2e8f0; margin: 0; }
</style>
""", unsafe_allow_html=True)

PLOTLY_TEMPLATE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#161b27",
    font=dict(color="#cbd5e1", family="Inter"),
    xaxis=dict(gridcolor="#1e2a3a", linecolor="#2a3450"),
    yaxis=dict(gridcolor="#1e2a3a", linecolor="#2a3450"),
    colorway=["#3b82f6","#06b6d4","#8b5cf6","#10b981","#f59e0b"],
)

#  Sidebar: Navigation & File Upload 
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📂 Data Sources")
    
    uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
    
    st.markdown("---")
    if uploaded_file is not None:
        st.success("File Loaded!")
        
        if 'df_previous' in st.session_state and st.session_state.df_previous is not None:
            if st.button("⏪ Undo Last Action", use_container_width=True):
                st.session_state.df = st.session_state.df_previous.copy()
                st.session_state.df_previous = None
                st.rerun()
    else:
        st.info("Waiting for data...")

#App Title
st.title("📊 DataPulse")

# 1. Define the tabs
tab1, tab2, tab3, tab4 = st.tabs(["Home", "Analytics", "Visualization", "AI feature"])
if uploaded_file is not None:
    try:
        if 'uploaded_file_name' not in st.session_state or st.session_state.uploaded_file_name != uploaded_file.name:
            st.session_state.uploaded_file_name = uploaded_file.name
            if uploaded_file.name.endswith('.csv'):
                st.session_state.df = pd.read_csv(uploaded_file)
            else:
                st.session_state.df = pd.read_excel(uploaded_file)
            st.session_state.df_previous = None
                
        df = st.session_state.df
            
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        cat_cols = df.select_dtypes(exclude=np.number).columns.tolist()

        # PAGE: HOME 
        with tab1:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Rows", f"{len(df):,}")
            m2.metric("Total Columns", len(df.columns))
            m3.metric("Numeric Cols", len(num_cols))
            m4.metric("Missing Values", df.isnull().sum().sum())

            st.markdown("### 📊 Interactive Analytics")
            row1_1, row1_2 = st.columns([1.5, 1])

            with row1_1:
                st.markdown("<div class='dash-card'>", unsafe_allow_html=True)

                numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
                categorical_cols = df.select_dtypes(exclude=np.number).columns.tolist()
                all_cols = df.columns.tolist()
                st.write(df)



                    


            with row1_2:
                    st.markdown("<div class='dash-card'>", unsafe_allow_html=True)
                    st.write("Summary Statistics")
                    st.write(df.describe())
                    st.markdown("</div>", unsafe_allow_html=True)

            if num_cols:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("<div class='dash-card'>", unsafe_allow_html=True)
                    st.markdown("<p class='section-title'>Data Composition</p>", unsafe_allow_html=True)
                    if cat_cols:
                        target = st.selectbox("Group By", cat_cols)
                        fig_pie = px.pie(df, names=target, hole=0.4)
                        fig_pie.update_layout(**PLOTLY_TEMPLATE, height=300, showlegend=False)
                        st.plotly_chart(fig_pie, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            
                with col2:
                    st.markdown("<div class='dash-card'>", unsafe_allow_html=True)
                    st.write("Correlation Map")
                    if len(num_cols) > 1:
                        fig_corr = px.imshow(df[num_cols].corr(), text_auto=True, template="plotly_dark")
                        st.plotly_chart(fig_corr, use_container_width=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.info("💡 A correlation map requires at least two numerical columns. Your dataset only has one.")

                    
            
            else:
                st.warning("No numerical columns found for deep analysis.")



        # PAGE: REPORTS 
        with tab2:
            st.markdown("### 📋 Data Analysis")
            st.markdown("<div class='dash-card'>", unsafe_allow_html=True)
            st.write("Complete Dataset View")
            #st.dataframe(df, use_container_width=True)
            
            def all_features(feature: str, data_frame: pd.DataFrame) -> pd.DataFrame:
                temp_data = data_frame.copy()

                if feature == "Handling Missing Data":
                    method = st.selectbox(
                        "How do you want to handle?",
                        ["Drop that Row", "With Mean", "With Median",
                        "With Standard Deviation", "With Mode",
                        "Data From Previous Row", "Data From Next Row"],
                        key="missing_method"
                    )
                    
                    if method == "Drop that Row":
                        temp_data.dropna(inplace=True)
                    elif method == "With Mean":
                        temp_data.fillna(temp_data.mean(numeric_only=True), inplace=True)
                    elif method == "With Median":
                        temp_data.fillna(temp_data.median(numeric_only=True), inplace=True)
                    elif method == "With Standard Deviation":
                        temp_data.fillna(temp_data.std(numeric_only=True), inplace=True)
                    elif method == "With Mode":
                        mode_vals = temp_data.mode(numeric_only=True)
                        if not mode_vals.empty:
                            temp_data.fillna(mode_vals.iloc[0], inplace=True)
                    elif method == "Data From Previous Row":
                        temp_data.ffill(inplace=True)
                    elif method == "Data From Next Row":
                        temp_data.bfill(inplace=True)

                    if st.button("Apply Change", key="btn_missing"):
                        st.session_state.df_previous = st.session_state.df.copy()
                        st.session_state.df = temp_data
                        st.rerun()

                elif feature == "Groupwise Filter":
                    group_filter = st.selectbox("Select a Column", temp_data.columns, key="group_col")
                    unique_group = temp_data[group_filter].dropna().unique()
                    
                    select_a_group = st.multiselect("Select a group", unique_group, key="group_val")   
                    if select_a_group: 
                        temp_data = temp_data[temp_data[group_filter].isin(select_a_group)]
                        if st.button("Apply Change", key="btn_group"):
                            st.session_state.df_previous = st.session_state.df.copy()
                            st.session_state.df = temp_data
                            st.rerun()
                elif feature=="Use Range":
                    numeric_cols = temp_data.select_dtypes(include=['int64','float64']).columns

                    column_to_filter = st.selectbox("Select Numeric Column", numeric_cols)

                    if not temp_data[column_to_filter].dropna().empty:
                        min_val = float(temp_data[column_to_filter].min())
                        max_val = float(temp_data[column_to_filter].max())
                    else:
                        min_val, max_val = 0.0, 0.0

                    min_input = st.number_input("Minimum Value", value=min_val)
                    max_input = st.number_input("Maximum Value", value=max_val)

                    temp_data = temp_data[
                        (temp_data[column_to_filter] >= min_input) &
                        (temp_data[column_to_filter] <= max_input)
                    ]
                    if st.button("Apply Change", key="btn_range"):
                        st.session_state.df_previous = st.session_state.df.copy()
                        st.session_state.df = temp_data
                        st.rerun()

                elif feature == "Statistical Summary":
                    temp_data = temp_data.describe()

                elif feature == "Rename Column":
                    col_to_rename = st.selectbox("Select column to rename", temp_data.columns, key="rename_col")
                    new_name = st.text_input("Enter new column name", value=col_to_rename, key="rename_val")
                    if new_name and new_name != col_to_rename:
                        temp_data.rename(columns={col_to_rename: new_name}, inplace=True)
                        if st.button("Apply Change", key="btn_rename"):
                            st.session_state.df_previous = st.session_state.df.copy()
                            st.session_state.df = temp_data
                            st.success(f'Renamed "{col_to_rename}" → "{new_name}"')
                            st.rerun()

                elif feature == "Remove Outlier":

                    numeric_cols = temp_data.select_dtypes(include=np.number).columns

                    if len(numeric_cols) > 0:

                        select_col = st.selectbox(
                            "Select Numeric Column",
                            numeric_cols,
                            key="outlier_col"
                        )

                        q1 = temp_data[select_col].quantile(0.25)
                        q3 = temp_data[select_col].quantile(0.75)

                        iqr = q3 - q1

                        lower_limit = q1 - 1.5 * iqr
                        upper_limit = q3 + 1.5 * iqr

                        temp_data = temp_data[
                            (temp_data[select_col] >= lower_limit) &
                            (temp_data[select_col] <= upper_limit)
                        ]
                    else:
                        st.warning("No numeric columns found.")

                elif feature == "Remove Duplicate Rows":
                    before_rows = temp_data.shape[0]

                    temp_data.drop_duplicates(inplace=True)

                    after_rows = temp_data.shape[0]

                    st.success(
                        f"{before_rows - after_rows} duplicate rows removed."
                    )
                elif feature == "Column Search":

                    search_col = st.selectbox(
                        "Select Column",
                        temp_data.columns,
                        key="search_col"
                    )

                    search_value = st.text_input(
                        "Search Value",
                        key="search_val"
                    )

                    if search_value:

                        temp_data = temp_data[
                            temp_data[search_col]
                            .astype(str)
                            .str.contains(search_value, case=False, na=False)
                        ]

                elif feature == "Negative Value Detection":

                    numeric_cols = temp_data.select_dtypes(
                        include=np.number
                    ).columns

                    if len(numeric_cols) > 0:

                        negative_count = (
                            temp_data[numeric_cols] < 0
                        ).sum().sum()

                        st.info(
                            f"Total Negative Values Found : {negative_count}"
                        )

                    else:
                        st.warning("No numeric columns found.")

                elif feature == "Column Datatype Viewer":

                    dtype_df = pd.DataFrame({
                        "Column Name": temp_data.columns,
                        "Datatype": temp_data.dtypes.astype(str)
                    })

                    st.dataframe(dtype_df)

                elif feature == "Top Values Viewer":

                    select_col = st.selectbox(
                        "Select Column",
                        temp_data.columns,
                        key="top_val_col"
                    )

                    top_values = (
                        temp_data[select_col]
                        .value_counts()
                        .head(10)
                    )

                    st.dataframe(top_values)
                return temp_data
            col_left, col_right = st.columns([1, 5])

            with col_left:

                features = st.selectbox(
                    "Let's do something",
                    ["Handling Missing Data",
                    "Remove Outlier",
                    "Groupwise Filter",
                    "Statistical Summary",
                    "Rename Column",
                    "Remove Duplicate Rows",
                    "Column Search",
                    "Negative Value Detection",
                    "Column Datatype Viewer",
                    "Top Values Viewer"],
                    key="feature_select"
                )

                new_df = df.copy()


                new_df = all_features(features, new_df)
            # col_left, col_right = st.columns([1, 5])

            # with col_left:
            #     features = st.selectbox(
            #         "Let's do something",
            #         ["Handling Missing Data", "Groupwise Filter", "Use Range","Statistical Summary", "Rename Column","Remove Outlier","Column Search","Negative Value Detection","Column Datatype Viewer","Top Values Viewer"],
            #         key="feature_select",
            #     )
            #     new_df = all_features(features, df)

            with col_right:
                st.dataframe(new_df, use_container_width=True)

            
            #csv = df.to_csv(index=False).encode('utf-8')
            #st.download_button("Download Full CSV", data=csv, file_name="report.csv", mime="text/csv")
            st.markdown("</div>", unsafe_allow_html=True)
        # PAGE: ANALYTICS 
        with tab3:
            st.markdown("### 📈 Data Visulization")
            if len(all_cols) < 1:
                st.warning("Not enough columns to visualise.")
            else:
                chart_type = st.selectbox(
                    "Select Chart Type",
                    ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart"],
                    key="chart_type",
                )

                v1, v2 = st.columns(2)
            

            if chart_type == "Bar Chart":
                with v1:
                    x_col = st.selectbox("X-axis (Category)", all_cols, key="bar_x")
                with v2:
                    y_col = st.selectbox("Y-axis (Value)", numeric_cols or all_cols, key="bar_y")
                color_col = st.selectbox("Color by (optional)", ["None"] + categorical_cols, key="bar_color")
                fig = px.bar(df, x=x_col, y=y_col,
                            color=None if color_col == "None" else color_col,
                            title=f"{y_col} by {x_col}", template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "Line Chart":
                with v1:
                    x_col = st.selectbox("X-axis", all_cols, key="line_x")
                with v2:
                    y_col = st.selectbox("Y-axis (Value)", numeric_cols or all_cols, key="line_y")
                color_col = st.selectbox("Color by (optional)", ["None"] + categorical_cols, key="line_color")
                fig = px.line(df, x=x_col, y=y_col,
                            color=None if color_col == "None" else color_col,
                            title=f"{y_col} over {x_col}", template="plotly_white", markers=True)
                st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "Scatter Plot":
                with v1:
                    x_col = st.selectbox("X-axis", numeric_cols or all_cols, key="scatter_x")
                with v2:
                    y_col = st.selectbox("Y-axis", numeric_cols or all_cols, key="scatter_y")
                color_col = st.selectbox("Color by (optional)", ["None"] + categorical_cols, key="scatter_color")
                
                fig = px.scatter(df, x=x_col, y=y_col,
                                color=None if color_col == "None" else color_col,
                                title=f"{y_col} vs {x_col}", template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "Pie Chart":
                if not categorical_cols:
                    st.warning("Pie chart needs at least one categorical column.")
                else:
                    with v1:
                        names_col = st.selectbox("Labels (Category)", categorical_cols, key="pie_names")
                    with v2:
                        values_col = st.selectbox("Values", numeric_cols or all_cols, key="pie_values")
                    fig = px.pie(df, names=names_col, values=values_col,
                                title=f"{values_col} by {names_col}", template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)



        # ── PAGE: SETTINGS ────────────────────────────────────────────────────
        with tab4:
            st.markdown("### AI Analysis")
            st.markdown("<div class='dash-card'>", unsafe_allow_html=True)


            model = LocalLLM(
                api_base="http://localhost:11434/v1",
                model="glm-4.7:cloud"
            )


            ALLOWED_LIBS_NOTE = (
                "CRITICAL: You may ONLY use these Python libraries: "
                "pandas, numpy, matplotlib, seaborn, plotly, streamlit, "
                "scipy, sklearn, datetime, math, io, os, Pillow. "
                "Do NOT import any other library. "
                "Do NOT generate any CSS, HTML, st.markdown with style tags, "
                "or font-family declarations. Use ONLY pure Python code with "
                "st.write, st.dataframe, st.plotly_chart, st.metric for display. "
                "Do NOT use the 'key' argument on any Streamlit element. "
                "IMPORTANT: At the end of your code, always assign a simple string "
                "to the variable 'result', like: result = 'Analysis complete'. "
                "Never assign a figure, plot, or chart object to result."
            )

            PROMPTS = {
                "Run Analysis": f"Analyze the dataset: identify data types, count missing values, and summarize the top 3 most significant statistical insights or correlations. Show results using pandas and streamlit. {ALLOWED_LIBS_NOTE}",
                "Fix Dataset": f"Clean the dataset: 1. Fill or drop missing values appropriately. 2. Remove duplicate rows. 3. Standardize column names to snake_case. 4. Detect and flag extreme outliers in numerical columns. {ALLOWED_LIBS_NOTE}",
                "Pivot Table": f"Create a pivot table aggregating the main numerical columns by the most relevant categorical columns. Show sum and average for each category. {ALLOWED_LIBS_NOTE}",
                "Dashboard Generation": f"Generate a full static business analysis dashboard with multiple charts (bar, line, pie, scatter) using plotly and streamlit. Include KPI metrics at the top and at least 4 visualizations. {ALLOWED_LIBS_NOTE}",
                "Trend Analysis": f"Identify the primary time-series column and a numerical value. Plot a line chart showing the trend over time. Highlight any significant spikes, dips, or seasonality. {ALLOWED_LIBS_NOTE}",
                "Forecast": f"Perform a simple linear regression or time-series forecast. Predict values for the next 5 time periods and visualize 'Actual vs Predicted' in a chart. {ALLOWED_LIBS_NOTE}"
            }


            if 'response' not in st.session_state:
                st.session_state.response = None

            config = {
                "llm": model,
                "save_charts": False,
                "save_charts_path": "exports/charts",
                "response_parser": PermissiveParser, 
                "security": "none", 
                "custom_whitelisted_dependencies": [
                    "streamlit", "pandas", "numpy", "matplotlib", "seaborn",
                    "Pillow", "plotly", "scipy", "sklearn", "datetime",
                    "math", "io", "os", "json", "re", "collections"
                ]
            }

            st.title("AI Analysis")
            if df is not None:
                agent = Agent(
                    df,
                    description="""You are a data analysis agent. Your main goal is to help non-technical users to analyze data, visualize, storytelling about the data, generating insights, dashboard generation and also other help they need.CRITICAL INSTRUCTIONS: You must write a Python script using pandas to answer this. Always wrap your code in standard markdown ```python 
``` blocks. Do not provide conversational text. """,
                    config=config
                )
                st.success("Data loaded! What would you like to do?")

                selected_task = st.selectbox(
                    "Select an Analysis Task:",
                    list(PROMPTS.keys()) 
                )

                if st.button(f"Generate {selected_task}"):
                    with st.spinner(f"Running {selected_task}..."):
                        dtype_info = ", ".join([f"{c}({d})" for c, d in zip(df.columns, df.dtypes)])
                        current_prompt = f"Dataset columns and types: [{dtype_info}]. " + PROMPTS[selected_task]
                        st.session_state.response = agent.chat(current_prompt)
                

                general_query = st.text_area("Ask your Query").strip()
                
                if general_query: 
                    if st.button("Ask"):
                        with st.spinner("Generating response..."):
                            st.session_state.response = agent.chat(general_query)
            

                if st.session_state.response is not None:
                    if isinstance(st.session_state.response, pd.DataFrame):
                        st.write("### AI Response")
                        st.dataframe(st.session_state.response)
                    elif isinstance(st.session_state.response, str) and st.session_state.response.strip():
                        st.write("### AI Response")
                        st.write(st.session_state.response)
                    elif isinstance(st.session_state.response, (int, float)):
                        st.write("### AI Response")
                        st.write(st.session_state.response)
                st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error loading file: {e}")

else:
    # Default landing state when no file is uploaded
    st.info("👈 Please upload a CSV or Excel file in the sidebar to begin.")
    st.image("https://via.placeholder.com/800x400.png?text=Upload+Data+to+Preview+Dashboard", use_container_width=True)
