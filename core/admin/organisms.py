from __future__ import unicode_literals, absolute_import, print_function, division

import json

from django.contrib import admin

from core.models.organisms import Individual, Growth


class IndividualInline(admin.StackedInline):
    model = Individual
    fields = ("properties",)
    extra = 0


class OrganismAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'pretty_content', 'created_at', 'modified_at']

    def pretty_content(self, organism):
        return json.dumps(organism.content)
    pretty_content.short_description = "Content"


class CollectiveAdmin(OrganismAdmin):
    inlines = [IndividualInline]


class GrowthInline(admin.StackedInline):
    model = Growth
    fields = ("type, state, config",)
    extra = 0


class GrowthAdmin(admin.ModelAdmin):
    list_display = ["type", "state", "config"]


class CommunityAdmin(admin.ModelAdmin):
    list_display = ["spirit", "state", "views", "config"]
    inlines = [GrowthInline]