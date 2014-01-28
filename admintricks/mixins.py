# coding: utf-8
"""Useful ModelAdmin mixins."""


class NoDeleteAdminMixin(object):

    """Mixin that doesn't allow deletion."""

    def get_actions(self, request):
        """Exclude delete_selected action from the list.

        :returns: list of actions

        """
        actions = super(NoDeleteAdminMixin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    @staticmethod
    def has_delete_permission(request, obj=None):
        """Revoke delete permission.

        :returns: False

        """
        return False


class ReadOnlyViewAdminMixin(NoDeleteAdminMixin):

    """Disallow add, delete and restrict change. Allow view."""

    extra = 0

    @staticmethod
    def has_add_permission(request):
        """Revoke add permission.

        :returns: False

        """
        return False

    def get_readonly_fields(self, request, obj=None):
        """Get fields to show on object page.

        :returns: list of field names

        """
        if self.readonly_fields:
            return self.readonly_fields
        elif self.fields:
            return self.fields
        else:
            meta = self.model._meta  # pylint: disable=W0212
            return [f.name for f in meta.fields]


class RestrictedChangeAdminMixin(object):

    """Mixin setting readonly fields on object change."""

    readonly_on_change_fields = ()

    def get_readonly_fields(self, request, obj=None):
        """Separate lists of fields readonly on add and readonly on change.

        :returns: field name sequence

        """
        if obj:
            return self.readonly_on_change_fields
        else:
            return self.readonly_fields


class ReadOnlyAdminMixin(ReadOnlyViewAdminMixin):

    """Disallow add, delete, change and view."""

    def __init__(self, *args, **kwargs):
        self.list_display_links = (None,)
        super(ReadOnlyAdminMixin, self).__init__(*args, **kwargs)

    def has_change_permission(self, request, obj=None):
        """Revoke change permission. Editable changelist is allowed.

        :returns: has_change_permission flag

        """
        if obj:
            return False
        else:
            return super(ReadOnlyAdminMixin,
                         self).has_change_permission(request, obj)
