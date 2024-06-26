import logging

from dateutil.relativedelta import relativedelta
from django.utils.timezone import now

from gi.models import Paciente

logger = logging.getLogger(__name__)


def div_by_zero_catch(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ZeroDivisionError:
            logger.error(f'Division by zero on function "{f.__name__}".')
            return indicador_zero(*args, **kwargs)

    return wrapper


def indicador_zero(*args, **kwargs):
    return 0, Paciente.objects.none()


def get_tamizaje_qs(base_qs, extra_filters: dict = None):
    # limit = now() - relativedelta(years=1)
    qs = base_qs  # .filter(examenpaciente__fecha=limit)
    if extra_filters:
        qs = qs.filter(**extra_filters)
    return qs
