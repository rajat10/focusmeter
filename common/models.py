from datetime import datetime

from django.core.validators import RegexValidator
from django.db import models, transaction
from django.db.models import manager, signals
from django.utils.translation import ugettext_lazy as _


class GenderModel(models.Model):
    """
    Abstract model for gender info
    """

    MALE = u'M'
    FEMALE = u'F'

    GENDERS = (
        (MALE, u'Male'),
        (FEMALE, u'Female'),
    )

    gender = models.CharField(max_length=1, choices=GENDERS)

    class Meta:
        abstract = True


class DatesModel(models.Model):
    """
    Abstract model for dates
    """
    created_at = models.DateTimeField(_('Created at'), default=datetime.now)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        abstract = True


class AddressModel(models.Model):
    """
    Abstract model for Address fields
    """
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zipcode = models.CharField(
        max_length=6,
        validators=[
            RegexValidator(regex=u'.{6,}', message=u'Ensure this field has no less than 6 characters.', code=u'nomatch'),
            RegexValidator(regex=u'^\d+$', message=u'Ensure this field has digits only', code=u'nomatch')
        ]
    )

    class Meta:
        abstract = True

    def _get_address(self):
        """
        get address in one line
        """
        return u"{} {}{}, {} {}".format(
            self.address_line_1, u'{} '.format(self.address_line_2) if self.address_line_2 else u'', self.city, self.state, self.zipcode
        )
    address = property(_get_address)


class PhoneModel(models.Model):
    """
    Abstract model for Phone Field
    """
    phone = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(regex=u'.{10,}', message=u'Ensure this field has no less than 10 characters.', code=u'nomatch'),
            RegexValidator(regex=u'^\d+$', message=u'Ensure this field has digits only', code=u'nomatch')
        ]
    )

    class Meta:
        abstract = True


class LocationModel(models.Model):
    """
    Abstract model for Location fields
    """
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        abstract = True


class PhoneAddressModel(AddressModel, PhoneModel):
    """
    Abstract model for Phone and Address fields
    """

    class Meta:
        abstract = True


class AddressLocationModel(AddressModel, LocationModel):
    """
    Abstract model for Address and Location fields
    """

    class Meta:
        abstract = True


class PhoneAddressLocationModel(PhoneModel, AddressModel, LocationModel):
    """
    Abstract model for Phone, Address and Location fields
    """

    class Meta:
        abstract = True
