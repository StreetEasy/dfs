if __name__ == "__main__":
    from dataframe_schema.core.core import DfSchema

    with open("./jsonschemas/schema.json", "w") as f:
        f.write(DfSchema.schema_json(indent=2))
        print("Wrote schema to ./jsonschemas/schema.json")
