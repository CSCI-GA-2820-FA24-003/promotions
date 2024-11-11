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
TestPromotion API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from urllib.parse import quote_plus
from wsgi import app
from service.common import status
from service.models import db, Promotion, PromotionType
from .factories import PromotionFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/promotions"

######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods


class TestYourResourceService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ############################################################
    # Utility function to bulk create promotions
    ############################################################
    def _create_promotions(self, count: int = 1) -> list:
        """Factory method to create promotions in bulk with specified attributes"""
        promotions = []
        for _ in range(count):
            test_promotion = PromotionFactory(
                title="Discount Deal",
                promo_code=12345,
                promo_type=PromotionType.AMOUNT_DISCOUNT,
                active=True,
            )
            response = self.client.post(BASE_URL, json=test_promotion.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test promotion",
            )
            new_promotion = response.get_json()
            test_promotion.id = new_promotion["id"]
            promotions.append(test_promotion)
        return promotions

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------
    def test_create_promotion(self):
        """It should Create a new promotion"""
        test_promotion = PromotionFactory()
        logging.debug("Test promotion: %s", test_promotion.serialize())
        response = self.client.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_promotion = response.get_json()
        self.assertEqual(new_promotion["title"], test_promotion.title)
        self.assertEqual(new_promotion["description"], test_promotion.description)
        self.assertEqual(new_promotion["promo_code"], int(test_promotion.promo_code))
        self.assertEqual(new_promotion["promo_type"], test_promotion.promo_type.name)
        self.assertEqual(int(new_promotion["promo_value"]), test_promotion.promo_value)
        self.assertEqual(new_promotion["active"], test_promotion.active)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_promotion = response.get_json()
        self.assertEqual(new_promotion["title"], test_promotion.title)
        self.assertEqual(new_promotion["description"], test_promotion.description)
        self.assertEqual(new_promotion["promo_code"], int(test_promotion.promo_code))
        self.assertEqual(new_promotion["promo_type"], test_promotion.promo_type.name)
        self.assertEqual(int(new_promotion["promo_value"]), test_promotion.promo_value)
        self.assertEqual(new_promotion["active"], test_promotion.active)

    # ----------------------------------------------------------
    # TEST METHOD NOT ALLOWED
    # ----------------------------------------------------------
    def test_method_not_allowed(self):
        """It should return method not allowed"""
        response = self.client.patch(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # ----------------------------------------------------------
    # TEST CREATE WITH EMPTY DATA
    # ----------------------------------------------------------
    def test_create_promotion_empty_data(self):
        """It should not create a promotion because of empty data"""
        logging.debug("Test promotion with empty data")
        response = self.client.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------
    # TEST UNSUPPORTED MEDIA TYPE
    # ----------------------------------------------------------
    def test_unsupported_media_type(self):
        """It should not create a promotion when sending wrong media type"""
        test_promotion = PromotionFactory()
        response = self.client.post(
            BASE_URL, json=test_promotion.serialize(), content_type="test/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # ----------------------------------------------------------
    # TEST UPDATE
    # ----------------------------------------------------------
    def test_update_promotion(self):
        """It should Update an existing Promotion"""
        # create a promotion to update
        test_promotion = PromotionFactory()
        response = self.client.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the promotion
        new_promotion = response.get_json()
        logging.debug(new_promotion)
        new_promotion["title"] = "Updated Title"
        response = self.client.put(
            f"{BASE_URL}/{new_promotion['id']}", json=new_promotion
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_promotion = response.get_json()
        self.assertEqual(updated_promotion["title"], "Updated Title")

    # ----------------------------------------------------------
    # TEST UPDATE WITH NOT FOUND PROMOTION
    # ----------------------------------------------------------
    def test_update_promotion_with_invalid_id(self):
        """It should not update promotion because it is not found"""
        test_promotion = PromotionFactory()
        response = self.client.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the promotion
        new_promotion = response.get_json()
        logging.debug(new_promotion)
        new_promotion["title"] = "Updated Title"
        response = self.client.put(
            f"{BASE_URL}/{new_promotion['id'] + 1}", json=new_promotion
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------
    # TEST DELETE
    # ----------------------------------------------------------
    def test_delete_promotion(self):
        """It should Delete a Promotion"""
        test_promotion = self._create_promotions(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_existing_promotion(self):
        """It should Delete a Promotion even if it doesn't exist"""
        response = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------
    def test_get_promotion(self):
        """It should Get a single Promotion"""
        # get the id of a promotion
        test_promotion = self._create_promotions(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["title"], test_promotion.title)

    def test_get_promotion_not_found(self):
        """It should not Get a Promotion thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    # ----------------------------------------------------------
    # TEST QUERY
    # ----------------------------------------------------------

    def test_query_by_title(self):
        """It should Query Promotions by title"""
        promotions = self._create_promotions(5)
        test_title = promotions[0].title
        title_count = len(
            [promotion for promotion in promotions if promotion.title == test_title]
        )
        response = self.client.get(f"{BASE_URL}?title={quote_plus(test_title)}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), title_count)
        # check the data just to be sure
        for promotion in data:
            self.assertEqual(promotion["title"], test_title)

    def test_query_by_promo_code(self):
        """It should Query Promotions by promo_code"""
        self._create_promotions(5)
        response = self.client.get(f"{BASE_URL}?promo_code=12345")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)
        for promotion in data:
            self.assertEqual(promotion["promo_code"], 12345)

    def test_query_by_promo_type(self):
        """It should Query Promotions by promo_type"""
        self._create_promotions(5)
        response = self.client.get(f"{BASE_URL}?promo_type=AMOUNT_DISCOUNT")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)
        for promotion in data:
            self.assertEqual(promotion["promo_type"], "AMOUNT_DISCOUNT")

    def test_query_by_active_status(self):
        """It should Query Promotions by active status"""
        self._create_promotions(5)
        response = self.client.get(f"{BASE_URL}?active=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)
        for promotion in data:
            self.assertEqual(promotion["active"], True)

    def test_query_by_multiple_fields(self):
        """It should Get all promotions that match"""
        # get the id of a promotion
        test_promotion = self._create_promotions(1)[0]
        response = self.client.get(
            f"{BASE_URL}?title={test_promotion.title}"
            f"&description={test_promotion.description}"
            f"&promo_code={test_promotion.promo_code}"
            f"&promo_type={test_promotion.promo_type.name}"
            f"&promo_value={test_promotion.promo_value}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)

    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------
    def test_get_promotion_list(self):
        """It should Get a list of Promotions"""
        self._create_promotions(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    # ----------------------------------------------------------
    # TEST LIST WITH TITLE
    # ----------------------------------------------------------
    def test_get_promotion_list_with_title(self):
        """It should Get a list of Promotions"""
        test_promotion = self._create_promotions(1)[0]
        response = self.client.get(f"{BASE_URL}?title={test_promotion.title}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)

    # ----------------------------------------------------------
    # TEST TOGGLE ACTIVE
    # ----------------------------------------------------------
    def test_toggle_active(self):
        """It should toggle active for target promotion"""
        test_promotion = self._create_promotions(1)[0]
        self.toggle_helper(test_promotion, True)
        self.toggle_helper(test_promotion, False)

        response = self.client.put(f"{BASE_URL}/-1/activate", json={"active": True})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------
    # HELPER FUNCTION FOR test_toggle_active
    # ----------------------------------------------------------
    def toggle_helper(self, promotion, is_active):
        """Send activate request, then check active status"""
        active_json = {"active": is_active}
        response = self.client.put(
            f"{BASE_URL}/{promotion.id}/activate", json=active_json
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        get_response = self.client.get(f"{BASE_URL}/{promotion.id}")
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["active"], is_active)
