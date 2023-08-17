from functools import reduce

import logging

logger = logging.getLogger('rMoistPi')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)



def coalesce(*arg):
  return reduce(lambda x, y: x if x is not None else y, arg)
