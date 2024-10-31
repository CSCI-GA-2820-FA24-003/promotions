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
Promotion Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Promotion
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Promotion, PromotionType
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Promotion REST API Service",
            version="1.0",
            description="This is a RESTful service for managing e-commerce promotions. You can list, view, create, update, "
            + "and delete promotions.",
            paths={
                "list_promotions": {
                    "method": "GET",
                    "url": url_for("list_promotions", _external=True),
                },
                "get_promotion": {
                    "method": "GET",
                    "url": url_for("get_promotion", promotion_id=1, _external=True),
                },
                "create_promotion": {
                    "method": "POST",
                    "url": url_for("create_promotion", _external=True),
                },
                "update_promotion": {
                    "method": "PUT",
                    "url": url_for("update_promotion", promotion_id=1, _external=True),
                },
                "delete_promotion": {
                    "method": "DELETE",
                    "url": url_for("delete_promotion", promotion_id=1, _external=True),
                },
            },
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# LIST ALL PROMOTIONS
######################################################################
@app.route("/promotions", methods=["GET"])
def list_promotions():
    """Returns all of the Promotions"""
    app.logger.info("Request for promotion list")

    promotions = []

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
# READ A PROMOTION
######################################################################
@app.route("/promotions/<int:promotion_id>", methods=["GET"])
def get_promotion(promotion_id):
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
    return jsonify(promotion.serialize()), status.HTTP_200_OK


######################################################################
# CREATE A NEW PROMOTION
######################################################################
@app.route("/promotions", methods=["POST"])
def create_promotion():
    """
    Creates a new Promotion
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

    # Return the location of the new promotion
    location_url = url_for("get_promotion", promotion_id=promotion.id, _external=True)
    return (
        jsonify(promotion.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# UPDATE AN EXISTING PROMOTION
######################################################################
@app.route("/promotions/<int:promotion_id>", methods=["PUT"])
def update_promotion(promotion_id):
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
    return jsonify(promotion.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A PROMOTION
######################################################################
@app.route("/promotions/<int:promotion_id>", methods=["DELETE"])
def delete_promotion(promotion_id):
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
# Toggle active for A PROMOTION
######################################################################
@app.route("/promotions/<int:promotion_id>/activate", methods=["PUT"])
def toggle_promotion_active(promotion_id):
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
    return jsonify(promotion.serialize()), status.HTTP_200_OK


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
