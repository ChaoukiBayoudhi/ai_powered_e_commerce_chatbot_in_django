from django.core.management.base import BaseCommand
from django.utils import timezone
from chatbot.models import UserProfile, Product, Order, ChatSession, ChatMessage
from faker import Faker
import random
from datetime import timedelta
import os
from django.conf import settings
from django.core.files import File
from django.contrib.auth.hashers import make_password

fake = Faker()

class Command(BaseCommand):
    help = 'Generate fake data for the e-commerce chatbot application'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10, help='Number of users to create')
        parser.add_argument('--products', type=int, default=50, help='Number of products to create')
        parser.add_argument('--orders', type=int, default=30, help='Number of orders to create')
        parser.add_argument('--chats', type=int, default=20, help='Number of chat sessions to create')
        parser.add_argument('--messages', type=int, default=5, help='Number of messages per chat session')

    def handle(self, *args, **options):
        num_users = options['users']
        num_products = options['products']
        num_orders = options['orders']
        num_chats = options['chats']
        num_messages = options['messages']

        self.stdout.write(self.style.SUCCESS(f'Starting to generate fake data...'))
        
        # Create users
        users = self.create_users(num_users)
        self.stdout.write(self.style.SUCCESS(f'Created {len(users)} users'))
        
        # Create products
        products = self.create_products(num_products)
        self.stdout.write(self.style.SUCCESS(f'Created {len(products)} products'))
        
        # Create orders
        orders = self.create_orders(users, products, num_orders)
        self.stdout.write(self.style.SUCCESS(f'Created {len(orders)} orders'))
        
        # Create chat sessions and messages
        chat_sessions = self.create_chat_sessions(users, products, num_chats, num_messages)
        self.stdout.write(self.style.SUCCESS(f'Created {len(chat_sessions)} chat sessions with messages'))
        
        self.stdout.write(self.style.SUCCESS('Fake data generation completed!'))

    def create_users(self, count):
        users = []
        for _ in range(count):
            username = fake.user_name()
            while UserProfile.objects.filter(username=username).exists():
                username = fake.user_name()
                
            user = UserProfile(
                username=username,
                email=fake.email(),
                password=make_password('password123'),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                address=fake.address(),
                phone_number='+' + ''.join(random.choices('0123456789', k=random.randint(10, 14))),
                preferred_categories=', '.join(random.sample(['Electronics', 'Clothing', 'Books', 'Home', 'Sports'], k=random.randint(1, 3))),
                birth_date=fake.date_of_birth(minimum_age=18, maximum_age=80),
                is_premium_user=random.choice([True, False]),
                is_staff=random.choice([True, False]) if _ < 2 else False,  # Make some users staff
                is_active=True
            )
            user.save()
            users.append(user)
        return users

    def create_products(self, count):
        products = []
        categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports', 'Food', 'Toys']
        
        for _ in range(count):
            product = Product(
                name=fake.word().capitalize() + ' ' + fake.word().capitalize(),
                description=fake.paragraph(nb_sentences=random.randint(3, 8)),
                price=round(random.uniform(9.99, 999.99), 2),
                stock_quantity=random.randint(0, 100),  # Some products will be out of stock
                category=random.choice(categories),
                manifacturing_date=fake.date_between(start_date='-2y', end_date='today')
            )
            product.save()
            products.append(product)
        return products

    def create_orders(self, users, products, count):
        orders = []
        for _ in range(count):
            user = random.choice(users)
            order_products = random.sample(products, k=random.randint(1, 5))
            total_price = sum(product.price for product in order_products)
            
            order = Order(
                user=user,
                status=random.choice([Order.OrderStatus.PENDING, Order.OrderStatus.SHIPPED, Order.OrderStatus.COMPLETED]),
                total_price=total_price,
                order_date=fake.date_time_between(start_date='-1y', end_date='now')
            )
            order.save()
            order.products.set(order_products)
            orders.append(order)
        return orders

    def create_chat_sessions(self, users, products, count, messages_per_chat):
        chat_sessions = []
        for _ in range(count):
            user = random.choice(users)
            chat_products = random.sample(products, k=random.randint(0, 3))
            
            chat_session = ChatSession(
                user=user,
                timestamp=fake.date_time_between(start_date='-6m', end_date='now')
            )
            chat_session.save()
            
            if chat_products:
                chat_session.products.set(chat_products)
            
            # Create messages for this chat session
            self.create_chat_messages(chat_session, messages_per_chat)
            
            chat_sessions.append(chat_session)
        return chat_sessions

    def create_chat_messages(self, chat_session, count):
        messages = []
        # First message is always from user
        current_type = ChatMessage.MessageType.USER
        
        for i in range(count):
            message = ChatMessage(
                chat_session=chat_session,
                message_type=current_type,
                content=fake.paragraph(nb_sentences=random.randint(1, 3)),
                timestamp=chat_session.timestamp + timedelta(minutes=i*2)  # Messages are 2 minutes apart
            )
            message.save()
            messages.append(message)
            
            # Alternate between user and bot messages
            current_type = ChatMessage.MessageType.BOT if current_type == ChatMessage.MessageType.USER else ChatMessage.MessageType.USER
        
        return messages