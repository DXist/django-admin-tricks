# -*- coding: utf-8 -*-
"""Tools for admin actions."""
from django.contrib import admin
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _


class FormActionFactory(object):

    """Action factory for actions with intermidiate form."""

    form_class = None
    name = "form_action"
    short_description = _("Change me")
    processed_message = _("Processed")
    template_name = "admin/action_form.html"

    def get_context_data(self, request, queryset, form):
        return {}

    def get_form(self, data=None):
        if self.form_class:
            return self.form_class(data)

        raise NotImplementedError

    @staticmethod
    def get_queryset(queryset):
        return queryset

    def get_template_names(self):
        return [self.template_name]

    def process_queryset(self, queryset, form):
        """Implement processing logic in subclass.

        :returns: number of processed objects

        """
        raise NotImplementedError

    def construct_processed_message(self, processed):
        """Construct message to inform user about processed objects."""
        return "%s: %s" % (self.processed_message, processed)

    def make_action(self, name=None, short_description=None,
                    get_queryset=None):
        """Action factory."""

        get_queryset = get_queryset if get_queryset else self.get_queryset

        def action_body(modeladmin, request, queryset):
            self.request = request
            if request.POST.get('post'):
                form = self.get_form(request.POST)
                if form.is_valid():
                    processed = self.process_queryset(get_queryset(queryset),
                                                      form)

                    message = self.construct_processed_message(processed)
                    modeladmin.message_user(request, message)
                    # Return None to display the change list page again.
                    return None
            else:
                if self.validate_queryset(queryset):
                    form = self.get_form()
                else:
                    # Return None to display the change list page again.
                    return None

            opts = modeladmin.model._meta  # pylint: disable=W0212
            app_label = opts.app_label
            media = modeladmin.media + form.media
            context = {
                "title": action_body.short_description,
                "action_title": action_body.short_description,
                "action_name": action_body.__name__,
                'queryset': queryset,
                "form": form,
                "media": media,
                "opts": opts,
                "app_label": app_label,
                'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
            }

            context.update(self.get_context_data(request, queryset, form))

            # Display the confirmation page
            return render_to_response(request, self.get_template_names(),
                                      context,
                                      context_instance=RequestContext(request))

        action_body.short_description = (short_description if
                                         short_description else
                                         self.short_description)
        name = name if name else self.name
        action_body.__name__ = name
        return action_body

    def validate_queryset(self, queryset):
        """Hook for extra queryset validation."""
        return True
