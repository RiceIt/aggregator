import logging

logger = logging.getLogger("parser")
logger.setLevel(logging.INFO)

handler = logging.FileHandler(filename='logs.log')
formatter = logging.Formatter(fmt='%(asctime)s %(name)s %(levelname)s:%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
