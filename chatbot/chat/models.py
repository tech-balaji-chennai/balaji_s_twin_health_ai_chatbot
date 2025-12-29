# chat/models.py

from django.db import models


class Conversation(models.Model):
    """Represents a single conversation session tracked by the frontend's SESSION_ID."""
    session_id = models.CharField(max_length=100, unique=True, db_index=True)
    start_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation: {self.session_id}"


class Message(models.Model):
    """Represents an individual message (user or AI) within a conversation."""
    # Links a message back to its conversation session
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')

    sender = models.CharField(max_length=10, choices=[('user', 'User'), ('ai', 'AI')])
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # Fields to log the result of the LLM classification for auditing/context
    topic_category = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f'{self.sender}: {self.text[:50]}'

    class Meta:
        ordering = ['timestamp']
