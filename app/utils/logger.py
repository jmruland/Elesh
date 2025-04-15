import logging
import sys

def setup_logger(name="elesh_archivist", level="INFO"):
    logger = logging.getLogger(name)
    level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(level)
    
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.handlers = []  # Avoid duplicate logs
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger

logger = setup_logger()