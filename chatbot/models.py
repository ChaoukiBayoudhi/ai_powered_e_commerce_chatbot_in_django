from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator, MinLengthValidator, MaxLengthValidator, FileExtensionValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class UserProfile(AbstractUser):
    address = models.TextField(
        blank=True, 
        null=True,
        validators=[
            MinLengthValidator(10, message=_("Address must be at least 10 characters long.")),
            MaxLengthValidator(500, message=_("Address cannot exceed 500 characters."))
        ]
    )
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
    preferred_categories = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s,]+$',
                message=_("Categories can only contain letters, numbers, spaces, and commas.")
            )
        ]
    )
    birth_date = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='profiles/', 
        blank=True, 
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif'],
                message=_("Only JPG, JPEG, PNG and GIF files are allowed.")
            )
        ]
    )
    is_premium_user = models.BooleanField(default=False)

    # Add related_name to resolve reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='user_profiles',
        blank=True,
        help_text=_('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        verbose_name=_('groups'),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='user_profiles',
        blank=True,
        help_text=_('Specific permissions for this user.'),
        verbose_name=_('user permissions'),
    )

    class Meta:
        db_table = 'user_profiles'
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['is_premium_user']),
        ]

    def __str__(self):
        return self.username

class Product(models.Model):
    name = models.CharField(
        max_length=255,
        validators=[
            MinLengthValidator(3, message=_("Product name must be at least 3 characters long.")),
            MaxLengthValidator(255, message=_("Product name cannot exceed 255 characters.")),
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s\-_]+$',
                message=_("Product name can only contain letters, numbers, spaces, hyphens, and underscores.")
            )
        ]
    )
    description = models.TextField(
        validators=[
            MinLengthValidator(10, message=_("Description must be at least 10 characters long.")),
            MaxLengthValidator(2000, message=_("Description cannot exceed 2000 characters."))
        ]
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[
            MinValueValidator(0, message=_("Price cannot be negative.")),
            MaxValueValidator(999999.99, message=_("Price cannot exceed 999,999.99."))
        ]
    )
    stock_quantity = models.PositiveIntegerField(
        validators=[
            MinValueValidator(0, message=_("Stock quantity cannot be negative.")),
            MaxValueValidator(999999, message=_("Stock quantity cannot exceed 999,999."))
        ]
    )
    category = models.CharField(
        max_length=255,
        validators=[
            MinLengthValidator(2, message=_("Category must be at least 2 characters long.")),
            MaxLengthValidator(100, message=_("Category cannot exceed 100 characters.")),
            RegexValidator(
                regex=r'^[a-zA-Z\s]+$',
                message=_("Category can only contain letters and spaces.")
            )
        ]
    )
    image = models.ImageField(
        upload_to='products/', 
        blank=True, 
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif'],
                message=_("Only JPG, JPEG, PNG and GIF files are allowed.")
            )
        ]
    )
    manifacturing_date=models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['price']),
            models.Index(fields=['stock_quantity']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(stock_quantity__gte=0),
                name='positive_stock_quantity'
            ),
            models.CheckConstraint(
                check=models.Q(price__gte=0),
                name='positive_price'
            ),
        ]

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
    status = models.CharField(
        max_length=20, 
        choices=OrderStatus.choices, 
        default=OrderStatus.PENDING,
        validators=[
            RegexValidator(
                regex=r'^(PENDING|SHIPPED|COMPLETED)$',
                message=_("Invalid order status.")
            )
        ]
    )
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[
            MinValueValidator(0, message=_("Total price cannot be negative.")),
            MaxValueValidator(999999.99, message=_("Total price cannot exceed 999,999.99."))
        ]
    )
    
    class Meta:
        db_table = 'orders'
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-order_date']
        indexes = [
            models.Index(fields=['order_date']),
            models.Index(fields=['status']),
            models.Index(fields=['user']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(total_price__gte=0),
                name='positive_total_price'
            ),
        ]
    
    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

class ChatSession(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='chats')
    products = models.ManyToManyField(Product, blank=True, related_name='chat_sessions')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_sessions'
        verbose_name = _('Chat Session')
        verbose_name_plural = _('Chat Sessions')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Chat {self.id} - {self.user.username}"

class ChatMessage(models.Model):
    class MessageType(models.TextChoices):
        USER = 'USER', _('User')
        BOT = 'BOT', _('Bot')

    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(
        max_length=10, 
        choices=MessageType.choices,
        validators=[
            RegexValidator(
                regex=r'^(USER|BOT)$',
                message=_("Invalid message type.")
            )
        ]
    )
    content = models.TextField(
        validators=[
            MinLengthValidator(1, message=_("Message cannot be empty.")),
            MaxLengthValidator(5000, message=_("Message cannot exceed 5000 characters."))
        ]
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_messages'
        verbose_name = _('Chat Message')
        verbose_name_plural = _('Chat Messages')
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['chat_session']),
            models.Index(fields=['message_type']),
        ]
    
    def __str__(self):
        return f"{self.get_message_type_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
