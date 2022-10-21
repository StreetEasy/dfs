import logging
from dfschema.core.legacy.v1 import V1_DfSchema


LegacySchemaRegistry = {1.0: V1_DfSchema}


def infer_protocol_version(d: dict) -> float:
    if "metadata" not in d or "protocol_version" not in d["metadata"]:
        logging.info("Missing `protocol_version` in metadata. Assuming PV=1.0")

    return d.get("metadata", {}).get("protocol_version", 1.0)
