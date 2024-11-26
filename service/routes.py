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

# spell: ignore Rofrano jsonify restx dbname
"""
Promotion Service with Swagger

Paths:
------
GET / - Displays a UI for Selenium testing
GET /promotions - Returns a list all of the promotions
GET /promotions/{id} - Returns the promotion with a given id number
POST /promotions - creates a new promotion record in the database
PUT /promotions/{id} - updates a promotion record in the database
DELETE /promotions/{id} - deletes a promotion record in the database
PUT /promotions/{id} - updates a promotion active status in the database
"""

import secrets
from functools import wraps
from flask import jsonify, request, abort
from flask import current_app as app  # Import Flask application
from flask_restx import Resource, fields, reqparse, inputs
from service.models import Promotion, PromotionType
from service.common import status  # HTTP Status Codes
from . import api


######################################################################
# Function to generate a random API key (good for testing)
######################################################################
def generate_apikey():
    """Helper function used when testing API keys"""
    return secrets.token_hex(16)


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return app.send_static_file("index.html")


# Define the model so that the docs reflect what can be sent
create_model = api.model(
    "Promotion",
    {
        "title": fields.String(required=True, description="The title of the Promotion"),
        "description": fields.String(
            required=False, description="A detailed description of the Promotion"
        ),
        "promo_code": fields.String(
            required=True, description="The unique promotional code for the Promotion"
        ),
        "promo_type": fields.String(
            required=True,
            description="The type of the Promotion (e.g., percentage, fixed amount, etc.)",
        ),
        "promo_value": fields.Float(
            required=True,
            description="The value of the Promotion (e.g., 20 for 20% or $20 off)",
        ),
        "start_date": fields.Date(
            required=True, description="The start date of the Promotion"
        ),
        "created_date": fields.Date(
            required=True, description="The creation date of the Promotion"
        ),
        "duration": fields.String(
            required=True,
            description="The duration of the Promotion in days",
        ),
        "active": fields.Boolean(
            required=True,
            description="Whether the Promotion is currently active",
        ),
    },
)

promotion_model = api.inherit(
    "PromotionModel",
    create_model,
    {
        "_id": fields.String(
            readOnly=True, description="The unique id assigned internally by service"
        ),
    },
)

toggle_active_model = api.model(
    "ToggleActive",
    {
        "active": fields.Boolean(
            required=True, description="The new active status for the promotion"
        ),
    },
)

# query string arguments
promotion_args = reqparse.RequestParser()
promotion_args.add_argument(
    "title",
    type=str,
    location="args",
    required=False,
    help="Filter Promotions by title",
)
promotion_args.add_argument(
    "description",
    type=str,
    location="args",
    required=False,
    help="Filter Promotions by description",
)
promotion_args.add_argument(
    "promo_code",
    type=str,
    location="args",
    required=False,
    help="Filter Promotions by promotional code",
)
promotion_args.add_argument(
    "promo_type",
    type=str,
    location="args",
    required=False,
    help="Filter Promotions by type (e.g., percentage, fixed amount, etc.)",
)
promotion_args.add_argument(
    "promo_value",
    type=float,
    location="args",
    required=False,
    help="Filter Promotions by value",
)
promotion_args.add_argument(
    "start_date",
    type=str,  # Typically handled as a string for date filtering in query parameters
    location="args",
    required=False,
    help="Filter Promotions by start date (format: YYYY-MM-DD)",
)
promotion_args.add_argument(
    "created_date",
    type=str,  # Typically handled as a string for date filtering
    location="args",
    required=False,
    help="Filter Promotions by creation date (format: YYYY-MM-DD)",
)
promotion_args.add_argument(
    "duration",
    type=str,
    location="args",
    required=False,
    help="Filter Promotions by duration (in days)",
)
promotion_args.add_argument(
    "active",
    type=inputs.boolean,
    location="args",
    required=False,
    help="Filter Promotions by active status (true/false)",
)


######################################################################
# Authorization Decorator
######################################################################
def token_required(func):
    """Decorator to require a token for this endpoint"""

    @wraps(func)
    def decorated(*args, **kwargs):
        token = None
        if "X-Api-Key" in request.headers:
            token = request.headers["X-Api-Key"]

        if app.config.get("API_KEY") and app.config["API_KEY"] == token:
            return func(*args, **kwargs)

        return {"message": "Invalid or missing token"}, 401

    return decorated


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
#  PATH: /promotions/{id}
######################################################################
@api.route("/promotions/<promotion_id>")
@api.param("promotion_id", "The Promotion identifier")
class PromotionResource(Resource):
    """
    PromotionResource class

    Allows the manipulation of a single Promotion
    GET /promotions/{id} - Returns a Promotion with the id
    PUT /promotions/{id} - Update a Promotion with the id
    DELETE /promotions/{id} -  Deletes a Promotion with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A PROMOTION
    # ------------------------------------------------------------------
    @api.doc("get_promotions")
    @api.response(404, "Promotion not found")
    @api.marshal_with(promotion_model)
    def get(self, promotion_id):
        """
        Retrieve a single Promotion

        This endpoint will return a Promotion based on it's id
        """
        app.logger.info("Request to Retrieve a promotion with id [%s]", promotion_id)

        # Attempt to find the Promotion and abort if not found
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Promotion with id '{promotion_id}' was not found.",
            )

        app.logger.info("Returning promotion: %s", promotion.title)
        return promotion.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING PROMOTION
    # ------------------------------------------------------------------
    @api.doc("update_promotions", security="apikey")
    @api.response(404, "Promotion not found")
    @api.response(400, "The posted Promotion data was not valid")
    @api.expect(promotion_model)
    @api.marshal_with(promotion_model)
    @token_required
    def put(self, promotion_id):
        """
        Update a Promotion

        This endpoint will update a Promotion based the body that is posted
        """
        app.logger.info("Request to Update a promotion with id [%s]", promotion_id)
        check_content_type("application/json")

        # Attempt to find the Promotion and abort if not found
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Promotion with id '{promotion_id}' was not found.",
            )

        # Update the Promotion with the new data
        data = request.get_json()
        app.logger.info("Processing: %s", data)
        promotion.deserialize(data)

        # Save the updates to the database
        promotion.update()

        app.logger.info("Promotion with ID: %d updated.", promotion.id)
        return promotion.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A PROMOTION
    # ------------------------------------------------------------------
    @api.doc("delete_promotions", security="apikey")
    @api.response(204, "Promotion deleted")
    @token_required
    def delete(self, promotion_id):
        """
        Delete a Promotion

        This endpoint will delete a Promotion based the id specified in the path
        """
        app.logger.info("Request to Delete a promotion with id [%s]", promotion_id)

        # Delete the Promotion if it exists
        promotion = Promotion.find(promotion_id)
        if promotion:
            app.logger.info("Promotion with ID: %d found.", promotion.id)
            promotion.delete()

        app.logger.info("Promotion with ID: %d delete complete.", promotion_id)
        return {}, status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /promotions
######################################################################
@api.route("/promotions", strict_slashes=False)
class PromotionCollection(Resource):
    """Handles all interactions with collections of Promotions"""

    # ------------------------------------------------------------------
    # LIST ALL PROMOTIONS
    # ------------------------------------------------------------------
    @api.doc("list_promotions")
    @api.expect(promotion_args, validate=True)
    @api.marshal_list_with(promotion_model)
    def get(self):
        """Returns all of the Promotions"""
        app.logger.info("Request for promotion list")

        promotions = []

        if len(request.args) > 1:
            app.logger.info("Query multiple params: %s", request.args)
            params = {}
            for key, value in request.args.items():
                params[key] = value
            promotions = Promotion.find_by_fields(params)
        else:
            # Parse any arguments from the query string
            title = request.args.get("title")
            promo_code = request.args.get("promo_code")
            promo_type = request.args.get("promo_type")
            active = request.args.get("active")

            if title:
                app.logger.info("Find by title: %s", title)
                promotions = Promotion.find_by_title(title)
            elif promo_code:
                app.logger.info("Find by promo_code: %s", promo_code)
                promotions = Promotion.find_by_promo_code(int(promo_code))
            elif promo_type:
                app.logger.info("Find by promo_type: %s", promo_type)
                promotions = Promotion.find_by_promo_type(
                    PromotionType[promo_type.upper()]
                )
            elif active:
                app.logger.info("Find by active status: %s", active)
                active_value = active.lower() == "true"
                promotions = Promotion.find_by_active(active_value)
            else:
                app.logger.info("Find all")
                promotions = Promotion.all()

        results = [promotion.serialize() for promotion in promotions]
        app.logger.info("Returning %d promotions", len(results))
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW PROMOTION
    # ------------------------------------------------------------------
    @api.doc("create_promotions", security="apikey")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_model)
    @api.marshal_with(promotion_model, code=201)
    @token_required
    def post(self):
        """
        Creates a Promotion
        This endpoint will create a Promotion based the data in the body that is posted
        """
        app.logger.info("Request to create a new promotion")
        check_content_type("application/json")

        promotion = Promotion()
        # Get the data from the request and deserialize it
        data = request.get_json()
        app.logger.info("Processing: %s", data)
        promotion.deserialize(data)

        # Save the new promotion to the database
        promotion.create()
        app.logger.info("promotion with new id [%s] saved!", promotion.id)
        location_url = api.url_for(
            PromotionResource, promotion_id=promotion.id, _external=True
        )
        return (
            promotion.serialize(),
            status.HTTP_201_CREATED,
            {"Location": location_url},
        )

    # ------------------------------------------------------------------
    # DELETE ALL PROMOTIONS (for testing only)
    # ------------------------------------------------------------------
    @api.doc("delete_all_promotions", security="apikey")
    @api.response(204, "All Promotions deleted")
    @token_required
    def delete(self):
        """
        Delete all Promotion

        This endpoint will delete all Promotion only if the system is under test
        """
        app.logger.info("Request to Delete all promotions...")
        if "TESTING" in app.config and app.config["TESTING"]:
            Promotion.remove_all()
            app.logger.info("Removed all Promotions from the database")
        else:
            app.logger.warning("Request to clear database while system not under test")

        return "", status.HTTP_204_NO_CONTENT


######################################################################
# LIST ALL PROMOTIONS
######################################################################
@app.route("/promotions", methods=["GET"])
def list_promotions():
    """Returns all of the Promotions"""
    app.logger.info("Request for promotion list")

    promotions = []

    if len(request.args) > 1:
        app.logger.info("Query multiple params: %s", request.args)
        params = {}
        for key, value in request.args.items():
            params[key] = value
        promotions = Promotion.find_by_fields(params)
    else:
        # Parse any arguments from the query string
        title = request.args.get("title")
        promo_code = request.args.get("promo_code")
        promo_type = request.args.get("promo_type")
        active = request.args.get("active")

        if title:
            app.logger.info("Find by title: %s", title)
            promotions = Promotion.find_by_title(title)
        elif promo_code:
            app.logger.info("Find by promo_code: %s", promo_code)
            promotions = Promotion.find_by_promo_code(int(promo_code))
        elif promo_type:
            app.logger.info("Find by promo_type: %s", promo_type)
            promotions = Promotion.find_by_promo_type(PromotionType[promo_type.upper()])
        elif active:
            app.logger.info("Find by active status: %s", active)
            active_value = active.lower() == "true"
            promotions = Promotion.find_by_active(active_value)
        else:
            app.logger.info("Find all")
            promotions = Promotion.all()

    results = [promotion.serialize() for promotion in promotions]
    app.logger.info("Returning %d promotions", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
#  PATH: /promotions/{id}/activate
######################################################################
@api.route("/promotions/<promotion_id>/activate")
@api.param("promotion_id", "The promotion identifier")
class ToggleActivateResource(Resource):
    """Toggle active on a promotion"""

    @api.doc("toggle_active", security="apikey")
    @api.expect(toggle_active_model)
    @api.marshal_with(promotion_model)
    @api.response(404, "promotion not found")
    @api.response(409, "The promotion is not available for toggling")
    @token_required
    def put(self, promotion_id):
        """
        Toggle active for a promotion

        This endpoint will update a Promotion active status based on the request
        """
        app.logger.info(
            "Request to Update promotion active status with id [%s]", promotion_id
        )
        check_content_type("application/json")

        # Attempt to find the Promotion and abort if not found
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Promotion with id '{promotion_id}' was not found.",
            )

        # Update the Promotion with the new data
        data = request.get_json()
        promotion.active = data["active"]

        # Save the updates to the database
        promotion.update()

        app.logger.info("Promotion with ID: %d updated.", promotion.id)
        return promotion.serialize(), status.HTTP_200_OK


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
