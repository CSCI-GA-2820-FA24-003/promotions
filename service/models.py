"""
Models for Promotion

All of the models are stored in this module
"""

import logging
import enum
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class PromotionType(enum.Enum):
    """ENUM class for promotion type"""

    AMOUNT_DISCOUNT = 0
    PERCENTAGE_DISCOUNT = 1
    BUY_ONE_GET_ONE = 2


class Promotion(db.Model):
    """
    Class that represents a Promotion
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40))
    description = db.Column(db.String(255))
    promo_code = db.Column(db.Integer)
    promo_type = db.Column(db.Enum(PromotionType), nullable=False)
    promo_value = db.Column(db.String(10))
    start_date = db.Column(db.Date)
    created_date = db.Column(db.Date)
    duration = db.Column(db.Interval)
    active = db.Column(db.Boolean)

    # Todo: Place the rest of your schema here...

    def __repr__(self):
        return f"<Promotion {self.title} id=[{self.id}]>"

    def create(self):
        """
        Creates a Promotion to the database
        """
        logger.info("Creating %s", self.title)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Promotion to the database
        """
        logger.info("Saving %s", self.title)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Promotion from the data store"""
        logger.info("Deleting %s", self.title)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Promotion into a dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "promo_code": self.promo_code,
            "promo_type": self.promo_type,
            "promo_value": self.promo_value,
            "start_date": self.start_date,
            "created_date": self.created_date,
            "duration": self.duration,
            "active": self.active,
        }

    def deserialize(self, data):
        """
        Deserializes a Promotion from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.title = data["title"]
            self.description = data["description"]
            self.promo_code = data["promo_code"]
            self.promo_type = data["promo_type"]
            self.promo_value = data["promo_value"]
            self.start_date = data["start_date"]
            self.created_date = data["created_date"]
            self.duration = data["duration"]
            self.active = data["active"]

        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Promotion: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Promotion: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Promotions in the database"""
        logger.info("Processing all Promotions")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Promotion by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_title(cls, title):
        """Returns all Promotions with the given title

        Args:
            title (string): the title of the Promotions you want to match
        """
        logger.info("Processing title query for %s ...", title)
        return cls.query.filter(cls.title == title)
