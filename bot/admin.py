from django.contrib import admin

from .models import Profile, Message, UserSubscriptions, SentTask

from .forms import ProfileForm


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'external_id', 'name', 'is_registered')
    form = ProfileForm


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'profile',
        'text',
        'created_at',
    )


@admin.register(UserSubscriptions)
class UserSubscriptionsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'profile_id',
        'executor_id',
    )


@admin.register(SentTask)
class SentTaskAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'profile_id',
        'task_id',
        'is_sent',
    )
