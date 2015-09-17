from radar.lib.permissions import has_demographics_permission
from radar.lib.serializers import Empty


class PatientAddressProxy(object):
    def __init__(self, address, user):
        self.address = address
        self.user = user
        self.demographics_permission = has_demographics_permission(address.patient, user)

    @property
    def address_line_1(self):
        if self.demographics_permission:
            return self.address.address_line_1
        else:
            return Empty

    @property
    def address_line_2(self):
        if self.demographics_permission:
            return self.address.address_line_2
        else:
            return Empty

    @property
    def address_line_3(self):
        if self.demographics_permission:
            return self.address.address_line_3
        else:
            return Empty

    @property
    def postcode(self):
        postcode = self.address.postcode

        if self.demographics_permission:
            return postcode
        else:
            # Return the first part of the postcode
            # Postcodes from the database should have a space but limit to 4 characters just in case
            return postcode.split(' ')[0][:4]

    def __getattr__(self, item):
        return getattr(self.address, item)
