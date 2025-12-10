import time
from source.core.settings import settings
from source.resources.logging import get_logger

logger = get_logger()

def _time_run(func):
    def _time_total(*args, **kwarg):
        time_init = time.time()
        retorno = func(*args, **kwarg)
        time_fim = time.time() - time_init
        logger.info(f"{settings.UUID} - def name:{func.__name__} => Tempo Total em Segundos: {time_fim}")
        return retorno
    return _time_total
