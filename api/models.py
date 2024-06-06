from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache

# Create your models here.
class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=(('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')), default='pending')

    def __str__(self):
        return f'{self.from_user} to {self.to_user} ({self.status})'

    @staticmethod
    def can_send_request(from_user, to_user):
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        recent_requests = FriendRequest.objects.filter(from_user=from_user, timestamp__gte=one_minute_ago)
        if recent_requests.count() >= 3:
            return False
        
        cache_key = f'friend_request_{from_user.id}_{to_user.id}'
        if cache.get(cache_key):
            return False
        cache.set(cache_key, 'set', 60)  # Set the cache to expire in 60 seconds
        
        return True
