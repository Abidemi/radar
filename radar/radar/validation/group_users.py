from radar.roles import ROLES
from radar.validation.core import Validation, Field, pass_old_obj, ValidationError, pass_context
from radar.validation.meta import MetaValidationMixin
from radar.validation.validators import required, in_
from radar.permissions import has_permission_for_group_role


class GroupUserValidation(MetaValidationMixin, Validation):
    id = Field()
    group = Field([required()])
    user = Field([required()])
    role = Field([required(), in_(ROLES)])

    @classmethod
    def check_permissions(cls, user, obj):
        # Can't change your own role
        if user == obj.user and not user.is_admin:
            raise ValidationError({'group': 'Permission denied!'})

        # Check the user has permission for the group and role
        if not has_permission_for_group_role(user, obj.group, obj.role):
            raise ValidationError({'role': 'Permission denied!'})

    @classmethod
    def is_duplicate(cls, obj):
        group = obj.group
        duplicate = any(x != obj and x.group == group for x in obj.user.group_users)
        return duplicate

    @pass_context
    @pass_old_obj
    def validate(self, ctx, old_obj, new_obj):
        current_user = ctx['user']

        # Updating existing record
        if old_obj.id is not None:
            self.check_permissions(current_user, old_obj)

        self.check_permissions(current_user, new_obj)

        # Check that the user doesn't already belong to this group
        # Note: it's important this check happens after the above permission check to prevent membership enumeration
        if self.is_duplicate(new_obj):
            raise ValidationError({'group': 'User already belongs to this group.'})

        return new_obj
