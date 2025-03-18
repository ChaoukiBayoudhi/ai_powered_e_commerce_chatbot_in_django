
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _

class UserProfile(AbstractUser):
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?[0-9]{10,15}$',
                message=_("Phone number must be between 10 to 15 digits, optionally starting with '+'.")
            )
        ],
        blank=True, 
        null=True
    )
    preferred_categories = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_premium_user = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock_quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    category = models.CharField(max_length=255)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_available(self):
        return self.stock_quantity > 0

    def __str__(self):
        return self.name

class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        SHIPPED = 'SHIPPED', _('Shipped')
        COMPLETED = 'COMPLETED', _('Completed')

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

class ChatSession(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='chats')
    products = models.ManyToManyField(Product, blank=True, related_name='chat_sessions')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.id} - {self.user.username}"

class ChatMessage(models.Model):
    class MessageType(models.TextChoices):
        USER = 'USER', _('User')
        BOT = 'BOT', _('Bot')

    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MessageType.choices)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_message_type_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
