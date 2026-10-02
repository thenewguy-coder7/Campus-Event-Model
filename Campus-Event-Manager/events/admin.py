from django.contrib import admin

from .models import RSVP, Event, Venue


class RSVPInline(admin.TabularInline):
    model = RSVP
    extra = 0


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "seats")
    search_fields = ("name", "address")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "organizer", "venue", "starts_at", "state", "going_count")
    list_filter = ("state", "venue")
    search_fields = ("title", "details")
    date_hierarchy = "starts_at"
    inlines = [RSVPInline]


@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ("attendee", "event", "answer", "updated_at")
    list_filter = ("answer",)
