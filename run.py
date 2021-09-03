from parser.funcs import main
from loguru import logger


if __name__ == '__main__':
    with logger.catch(reraise=True):
        main()
