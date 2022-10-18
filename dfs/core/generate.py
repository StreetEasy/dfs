import pandas as pd


def generate_schema_dict_from_df(df: pd.DataFrame) -> dict:
    """
    generate Schema object from given dataframe.
    by default will generate strict schema that given dataframe should match.
    """

    columns = []

    for col in df.columns:
        cd = {"name": col}

        cd["dtype"] = (
            "string" if pd.api.types.is_string_dtype(df[col]) else str(df[col].dtype)
        )
        cd["na_limit"] = max(0.9999, (df[col].isnull().mean() + 0.1))  # +10%

        if pd.api.types.is_numeric_dtype(df[col]):
            add_range = 0.05 * df[col].std()

            mthd = int if pd.api.types.is_integer_dtype(df[col]) else float

            cd["value_limits"] = dict(
                min=mthd(df[col].min() - add_range),
                max=mthd(df[col].max() + add_range),
            )

        elif cd["dtype"] in {"string", "object", "character", "category"}:
            vc = df[col].value_counts()
            # vcm = vc / vc.sum()  # percentage

            categorical = {
                "unique": (vc.iloc[0] == 1),
            }
            if len(vc) <= 15:  # treshold for categorical
                categorical["value_set"] = set(vc.index)
                categorical["mode"] = "exact_set"
            elif len(vc) <= 25:
                categorical["value_set"] = set(vc.index)
                categorical["mode"] = "oneof"
            else:
                categorical["value_set"] = set(vc.index[:25])
                categorical["mode"] = "include"
            cd["categorical"] = categorical

        columns.append(cd)  # type: ignore

    schema = {
        "columns": columns,
        "additionalColumns": False,
    }

    return schema
