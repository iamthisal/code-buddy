import json
import logging

logger = logging.getLogger("siteforge.events")


def record_event(event: str, **fields: object) -> None:
    logger.info(json.dumps({"event": event, **fields}, sort_keys=True, separators=(",", ":")))
