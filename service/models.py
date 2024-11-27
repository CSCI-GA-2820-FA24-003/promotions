# pylint: disable=too-many-instance-attributes

"""
Models for Promotion

All of the models are stored in this module
"""

import logging
import enum
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, Boolean, Float, Date, Interval

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DatabaseConnectionError(Exception):
    """Custom Exception when database connection fails"""


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

    ##################################################
    # INSTANCE METHODS
    ##################################################

    def __repr__(self):
        return f"<Promotion {self.title} id=[{self.id}]>"

    def create(self):
        """
        Creates a Promotion in the database after validating the data.
        """
        logger.info("Attempting to create promotion: %s", self.title)
        self.id = None  # Ensure the ID is None for a new record

        try:
            db.session.add(self)
            db.session.commit()
            logger.info("Promotion created with ID: %s", self.id)
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating Promotion: %s", e)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Promotion to the database
        """
        if not self.id:
            raise DataValidationError("Cannot update a Promotion without an ID.")

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
        promotion = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "promo_code": self.promo_code,
            "promo_type": self.promo_type.name,
            "promo_value": self.promo_value,
            "start_date": self.start_date,
            "created_date": self.created_date,
            "duration": str(self.duration),
            "active": self.active,
        }

        if self.id:
            promotion["id"] = self.id
        return promotion

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
    def remove_all(cls):
        """Removes all documents from the database (use for testing)"""
        logger.info("Deleting all Promotions")
        count = cls.query.delete(synchronize_session=False)
        db.session.commit()
        logger.info("Deleted %d record(s).", count)
        return count  # Return the number of deleted records

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

    @classmethod
    def find_by_promo_code(cls, promo_code):
        """Returns all Promotions with the specified promo_code

        Args:
            promo_code (int): the promo_code of the Promotions you want to match
        """
        logger.info("Processing promo_code query for %s ...", promo_code)
        return cls.query.filter(cls.promo_code == promo_code).all()

    @classmethod
    def find_by_promo_type(cls, promo_type):
        """Returns all Promotions with the specified promo_type

        Args:
            promo_type (PromotionType): the type of the Promotions you want to match
        """
        logger.info("Processing promo_type query for %s ...", promo_type)
        return cls.query.filter(cls.promo_type == promo_type).all()

    @classmethod
    def find_by_active(cls, active):
        """Returns all Promotions with the specified active status

        Args:
            active (bool): the active status of the Promotions you want to match
        """
        logger.info("Processing active status query for %s ...", active)
        return cls.query.filter(cls.active == active).all()

    @classmethod
    def find_by_fields(cls, query_params):
        """Returns all Promotions that match all field values provided in query_params.

        Args:
            query_params (dict): A dictionary where keys are field names and values are the values to match for.

        Raises:
            DataValidationError: If any field in query_params is not a valid attribute of the model.
        """
        query = cls.query
        for field_name, value in query_params.items():
            if not hasattr(cls, field_name):
                raise DataValidationError(
                    f"Field '{field_name}' is not a valid attribute of {cls.__name__}."
                )

            # Type casting based on the field's type
            field = getattr(cls, field_name)
            if isinstance(field.type, Integer):
                value = int(value)
            elif isinstance(field.type, Boolean):
                value = value.lower() == "true"
            elif isinstance(field.type, Float):
                value = float(value)
            elif isinstance(field.type, Date):
                # Convert to Python date object (expected format: YYYY-MM-DD)
                value = datetime.strptime(value, "%Y-%m-%d").date()
            elif isinstance(field.type, Interval):
                # Convert duration to timedelta
                if not isinstance(value, timedelta):
                    days, time_part = value.split(", ")
                    days = int(days.split()[0])  # Extract days
                    time_part = datetime.strptime(
                        time_part, "%H:%M:%S"
                    ).time()  # Extract time
                    value = timedelta(
                        days=days,
                        hours=time_part.hour,
                        minutes=time_part.minute,
                        seconds=time_part.second,
                    )

            query = query.filter(field == value)

        logger.info("Processing filter query with parameters: %s", query_params)
        return query.all()
