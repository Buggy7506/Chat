from django.contrib import admin

# Register your models here.
from .models import Message, Profile, GroupChat, GroupMember, MessageReaction

admin.site.register(Message)
admin.site.register(Profile)
admin.site.register(GroupChat)
admin.site.register(GroupMember)
admin.site.register(MessageReaction)