from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Venue(models.Model):
    """A physical place on campus where events are held."""

    name = models.CharField(max_length=120, unique=True)
    address = models.CharField(max_length=250)
    seats = models.PositiveIntegerField(help_text="Maximum number of people the venue can hold.")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.seats} seats)"


class Event(models.Model):
    class State(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    # One user (organizer) -> many events
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hosted_events",
    )
    # One venue -> many events
    venue = models.ForeignKey(
        Venue,
        on_delete=models.PROTECT,
        related_name="scheduled_events",
    )
    title = models.CharField(max_length=180)
    details = models.TextField(blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    state = models.CharField(
        max_length=15,
        choices=State.choices,
        default=State.DRAFT,
    )
    # Many users <-> many events, through the RSVP model
    guests = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="RSVP",
        related_name="joined_events",
        blank=True,
    )
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["starts_at"]
        indexes = [models.Index(fields=["state", "starts_at"])]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(ends_at__gt=models.F("starts_at")),
                name="event_ends_after_it_starts",
            )
        ]

    def clean(self):
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            raise ValidationError({"ends_at": "An event must end after it starts."})

    @property
    def is_upcoming(self):
        return self.state == self.State.PUBLISHED and self.starts_at > timezone.now()

    @property
    def going_count(self):
        return self.rsvps.filter(answer=RSVP.Answer.GOING).count()

    @property
    def seats_left(self):
        return max(self.venue.seats - self.going_count, 0)

    def __str__(self):
        return f"{self.title} @ {self.venue.name}"


class RSVP(models.Model):
    class Answer(models.TextChoices):
        GOING = "going", "Going"
        MAYBE = "maybe", "Maybe"
        DECLINED = "declined", "Declined"

    attendee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rsvps",
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="rsvps",
    )
    answer = models.CharField(
        max_length=10,
        choices=Answer.choices,
        default=Answer.GOING,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "RSVP"
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["attendee", "event"],
                name="one_rsvp_per_user_per_event",
            )
        ]

    def __str__(self):
        return f"{self.attendee} -> {self.event} ({self.get_answer_display()})"
