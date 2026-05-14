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

    features = st.multiselect(
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
        default=[]
    )

    new_df = df.copy()

    for feature in features:
        new_df = all_features(feature, new_df)