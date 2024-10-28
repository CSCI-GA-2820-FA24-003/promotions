"""
Test Factory to make fake objects for testing
"""

from datetime import timedelta, date
import random
import factory
from factory import Faker, LazyFunction
from service.models import Promotion, PromotionType


class PromotionFactory(factory.Factory):
    """Creates fake promotion"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Promotion

    id = factory.Sequence(lambda n: n)
    title = Faker("text", max_nb_chars=40)
    description = Faker("paragraph", nb_sentences=2)
    promo_code = Faker("ean8")
    promo_type = LazyFunction(lambda: random.choice(list(PromotionType)))
    promo_value = Faker("random_number", digits=2, fix_len=False)
    start_date = LazyFunction(date.today)
    created_date = LazyFunction(date.today)
    duration = LazyFunction(lambda: timedelta(days=random.randint(1, 30)))
    active = Faker("boolean")
