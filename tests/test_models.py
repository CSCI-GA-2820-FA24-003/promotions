######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Test cases for promotion Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import Promotion, db, PromotionType
from .factories import PromotionFactory
from service.models import Promotion, db, PromotionType, DataValidationError

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  Promotion   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestPromotion(TestCase):
    """Test Cases for Promotion Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()
        self.client = app.test_client()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_promotion(self):
        """It should create a Promotion"""
        promotion = PromotionFactory()
        promotion.create()
        self.assertIsNotNone(promotion.id)
        found = Promotion.all()
        self.assertEqual(len(found), 1)
        data = Promotion.find(promotion.id)
        self.assertEqual(data.title, promotion.title)
        self.assertEqual(data.description, promotion.description)
        self.assertEqual(data.promo_code, promotion.promo_code)
        self.assertEqual(data.promo_type, promotion.promo_type)
        self.assertEqual(data.promo_value, promotion.promo_value)
        self.assertEqual(data.start_date, promotion.start_date)
        self.assertEqual(data.created_date, promotion.created_date)
        self.assertEqual(data.duration, promotion.duration)
        self.assertEqual(data.active, promotion.active)

    def test_create_a_promotion(self):
        """It should Create a promotion and assert that it exists"""
        promotion = Promotion(
            title="New Customer",
            promo_type=PromotionType.PERCENTAGE_DISCOUNT,
            active=True,
        )
        self.assertEqual(str(promotion), "<Promotion New Customer id=[None]>")
        self.assertTrue(promotion is not None)
        self.assertEqual(promotion.id, None)
        self.assertEqual(promotion.title, "New Customer")
        self.assertEqual(promotion.promo_type, PromotionType.PERCENTAGE_DISCOUNT)
        self.assertEqual(promotion.active, True)
        promotion = Promotion(
            title="New Customer", promo_type=PromotionType.AMOUNT_DISCOUNT, active=False
        )
        self.assertEqual(promotion.active, False)
        self.assertEqual(promotion.promo_type, PromotionType.AMOUNT_DISCOUNT)

    def test_add_a_promotion(self):
        """It should Create a promotion and add it to the database"""
        promotions = Promotion.all()
        self.assertEqual(promotions, [])
        promotion = Promotion(
            title="New Customer",
            promo_type=PromotionType.PERCENTAGE_DISCOUNT,
            active=True,
        )
        self.assertTrue(promotion is not None)
        self.assertEqual(promotion.id, None)
        promotion.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(promotion.id)
        promotions = promotion.all()
        self.assertEqual(len(promotions), 1)

    # update & delete
    def test_update_promotion(self):
        """It should Update a Promotion"""
        promotion = PromotionFactory()
        logging.debug(promotion)
        promotion.create()
        self.assertIsNotNone(promotion.id)

        # Change it an save it
        promotion.title = "Updated Title"
        original_id = promotion.id
        promotion.update()
        self.assertEqual(promotion.id, original_id)
        self.assertEqual(promotion.title, "Updated Title")

        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 1)
        self.assertEqual(promotions[0].id, original_id)
        self.assertEqual(promotions[0].title, "Updated Title")

    def test_update_no_id(self):
        """It should not Update a Promotion with no id"""
        promotion = PromotionFactory()
        logging.debug(promotion)
        promotion.id = None
        self.assertRaises(DataValidationError, promotion.update)

    def test_delete_promotion(self):
        """It should Delete a Promotion"""
        promotion = PromotionFactory()
        promotion.create()
        self.assertEqual(len(Promotion.all()), 1)

        # delete the promotion and make sure it isn't in the database
        promotion.delete()
        self.assertEqual(len(Promotion.all()), 0)
