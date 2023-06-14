from hypothesis.extra.pandas import column, data_frames

# import hypothesis.strategies as st


def generate_hypothesis_from_schema(schema: dict):
    columns = schema["columns"]

    if isinstance(columns, list):
        columns = [column(c, dtype=int) for c in columns]

    return data_frames(columns)
