from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from customers.models import CustomerProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create customer profile when a customer user is created"""
    if created and instance.user_type == 'customer':
        CustomerProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save customer profile when user is saved"""
    if instance.user_type == 'customer' and hasattr(instance, 'customer_profile'):
        instance.customer_profile.save()
