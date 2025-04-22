# Import Django's BaseCommand class which is the foundation for creating custom management commands
from django.core.management.base import BaseCommand
# Import timezone utilities for handling date and time operations
from django.utils import timezone
# Import all the models from the chatbot app that we'll be populating with fake data
from chatbot.models import UserProfile, Product, Order, ChatSession, ChatMessage
# Import the Faker library which generates realistic fake data like names, addresses, etc.
from faker import Faker
# Import random module for generating random values and making random selections
import random
# Import timedelta for adding time intervals to datetime objects
from datetime import timedelta
# Import os module for operating system dependent functionality like file path operations
import os
# Import Django settings which contains project configuration
from django.conf import settings
# Import File class for handling file operations in Django
from django.core.files import File
# Import make_password to securely hash passwords before storing them
from django.contrib.auth.hashers import make_password

# Create an instance of the Faker class to generate fake data
fake = Faker()

# Define a custom management command by extending BaseCommand
class Command(BaseCommand):
    # Provide a help text that describes what this command does
    help = 'Generate fake data for the e-commerce chatbot application'

    # Define command-line arguments that this command accepts
    def add_arguments(self, parser):
        # Add argument for number of users to create, with a default value of 10
        parser.add_argument('--users', type=int, default=10, help='Number of users to create')
        # Add argument for number of products to create, with a default value of 50
        parser.add_argument('--products', type=int, default=50, help='Number of products to create')
        # Add argument for number of orders to create, with a default value of 30
        parser.add_argument('--orders', type=int, default=30, help='Number of orders to create')
        # Add argument for number of chat sessions to create, with a default value of 20
        parser.add_argument('--chats', type=int, default=20, help='Number of chat sessions to create')
        # Add argument for number of messages per chat session, with a default value of 5
        parser.add_argument('--messages', type=int, default=5, help='Number of messages per chat session')

    # The main method that gets called when the command is executed
    def handle(self, *args, **options):
        # Extract the command-line arguments from the options dictionary
        num_users = options['users']
        num_products = options['products']
        num_orders = options['orders']
        num_chats = options['chats']
        num_messages = options['messages']

        # Print a message indicating that the data generation process is starting
        # self.style.SUCCESS applies a green color to the text in the terminal
        self.stdout.write(self.style.SUCCESS(f'Starting to generate fake data...'))
        
        # Call the create_users method to generate fake users and store the result
        users = self.create_users(num_users)
        # Print a success message showing how many users were created
        self.stdout.write(self.style.SUCCESS(f'Created {len(users)} users'))
        
        # Call the create_products method to generate fake products and store the result
        products = self.create_products(num_products)
        # Print a success message showing how many products were created
        self.stdout.write(self.style.SUCCESS(f'Created {len(products)} products'))
        
        # Call the create_orders method to generate fake orders and store the result
        orders = self.create_orders(users, products, num_orders)
        # Print a success message showing how many orders were created
        self.stdout.write(self.style.SUCCESS(f'Created {len(orders)} orders'))
        
        # Call the create_chat_sessions method to generate fake chat sessions with messages
        chat_sessions = self.create_chat_sessions(users, products, num_chats, num_messages)
        # Print a success message showing how many chat sessions were created
        self.stdout.write(self.style.SUCCESS(f'Created {len(chat_sessions)} chat sessions with messages'))
        
        # Print a final success message indicating that the data generation process is complete
        self.stdout.write(self.style.SUCCESS('Fake data generation completed!'))

    # Method to create fake user profiles
    def create_users(self, count):
        # Initialize an empty list to store the created users
        users = []
        # Loop 'count' number of times to create 'count' users
        for _ in range(count):
            # Generate a random username using Faker
            username = fake.user_name()
            # Check if the username already exists in the database
            # If it does, generate a new username until we get a unique one
            while UserProfile.objects.filter(username=username).exists():
                username = fake.user_name()
            
            # Create a new UserProfile instance with fake data
            user = UserProfile(
                # Set the username to the unique username we generated
                username=username,
                # Generate a fake email address
                email=fake.email(),
                # Hash the password 'password123' for security
                password=make_password('password123'),
                # Generate a fake first name
                first_name=fake.first_name(),
                # Generate a fake last name
                last_name=fake.last_name(),
                # Generate a fake address
                address=fake.address(),
                # Generate a fake phone number starting with '+' followed by 10-14 random digits
                phone_number='+' + ''.join(random.choices('0123456789', k=random.randint(10, 14))),
                # Generate 1-3 random preferred categories from the given list
                preferred_categories=', '.join(random.sample(['Electronics', 'Clothing', 'Books', 'Home', 'Sports'], k=random.randint(1, 3))),
                # Generate a fake birth date for someone between 18 and 80 years old
                birth_date=fake.date_of_birth(minimum_age=18, maximum_age=80),
                # Randomly set whether the user is a premium user or not
                is_premium_user=random.choice([True, False]),
                # Make some users staff members (only the first 2 in this case)
                is_staff=random.choice([True, False]) if _ < 2 else False,
                # Set all users as active
                is_active=True
            )
            # Save the user to the database
            user.save()
            # Add the user to our list of created users
            users.append(user)
        # Return the list of created users
        return users

    # Method to create fake products
    def create_products(self, count):
        # Initialize an empty list to store the created products
        products = []
        # Define a list of possible product categories
        categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports', 'Food', 'Toys']
        
        # Loop 'count' number of times to create 'count' products
        for _ in range(count):
            # Create a new Product instance with fake data
            product = Product(
                # Generate a product name by capitalizing two random words
                name=fake.word().capitalize() + ' ' + fake.word().capitalize(),
                # Generate a product description as a paragraph with 3-8 sentences
                description=fake.paragraph(nb_sentences=random.randint(3, 8)),
                # Generate a random price between 9.99 and 999.99, rounded to 2 decimal places
                price=round(random.uniform(9.99, 999.99), 2),
                # Generate a random stock quantity between 0 and 100
                # Some products will have 0 stock (out of stock)
                stock_quantity=random.randint(0, 100),
                # Randomly select a category from the categories list
                category=random.choice(categories),
                # Generate a random manufacturing date within the last 2 years
                manifacturing_date=fake.date_between(start_date='-2y', end_date='today')
            )
            # Save the product to the database
            product.save()
            # Add the product to our list of created products
            products.append(product)
        # Return the list of created products
        return products

    # Method to create fake orders
    def create_orders(self, users, products, count):
        # Initialize an empty list to store the created orders
        orders = []
        # Loop 'count' number of times to create 'count' orders
        for _ in range(count):
            # Randomly select a user from the list of users
            user = random.choice(users)
            # Randomly select 1-5 products from the list of products
            order_products = random.sample(products, k=random.randint(1, 5))
            # Calculate the total price by summing the prices of all selected products
            total_price = sum(product.price for product in order_products)
            
            # Create a new Order instance with the selected user and calculated total price
            order = Order(
                # Set the user who placed the order
                user=user,
                # Randomly select an order status from the OrderStatus enum
                status=random.choice([Order.OrderStatus.PENDING, Order.OrderStatus.SHIPPED, Order.OrderStatus.COMPLETED]),
                # Set the total price of the order
                total_price=total_price,
                # Generate a random order date within the last year
                order_date=fake.date_time_between(start_date='-1y', end_date='now')
            )
            # Save the order to the database
            order.save()
            # Associate the selected products with this order using the many-to-many relationship
            order.products.set(order_products)
            # Add the order to our list of created orders
            orders.append(order)
        # Return the list of created orders
        return orders

    # Method to create fake chat sessions
    def create_chat_sessions(self, users, products, count, messages_per_chat):
        # Initialize an empty list to store the created chat sessions
        chat_sessions = []
        # Loop 'count' number of times to create 'count' chat sessions
        for _ in range(count):
            # Randomly select a user from the list of users
            user = random.choice(users)
            # Randomly select 0-3 products from the list of products
            # These are products that were discussed in the chat
            chat_products = random.sample(products, k=random.randint(0, 3))
            
            # Create a new ChatSession instance with the selected user
            chat_session = ChatSession(
                # Set the user who participated in the chat
                user=user,
                # Generate a random timestamp within the last 6 months
                timestamp=fake.date_time_between(start_date='-6m', end_date='now')
            )
            # Save the chat session to the database
            chat_session.save()
            
            # If there are products associated with this chat, set them
            if chat_products:
                # Associate the selected products with this chat session using the many-to-many relationship
                chat_session.products.set(chat_products)
            
            # Create messages for this chat session by calling the create_chat_messages method
            self.create_chat_messages(chat_session, messages_per_chat)
            
            # Add the chat session to our list of created chat sessions
            chat_sessions.append(chat_session)
        # Return the list of created chat sessions
        return chat_sessions

    # Method to create fake chat messages for a given chat session
    def create_chat_messages(self, chat_session, count):
        # Initialize an empty list to store the created messages
        messages = []
        # Set the first message type to USER (conversation always starts with the user)
        current_type = ChatMessage.MessageType.USER
        
        # Loop 'count' number of times to create 'count' messages
        for i in range(count):
            # Create a new ChatMessage instance
            message = ChatMessage(
                # Associate this message with the given chat session
                chat_session=chat_session,
                # Set the message type (alternating between USER and BOT)
                message_type=current_type,
                # Generate fake content as a paragraph with 1-3 sentences
                content=fake.paragraph(nb_sentences=random.randint(1, 3)),
                # Set the timestamp as the chat session timestamp plus i*2 minutes
                # This ensures messages are in chronological order, 2 minutes apart
                timestamp=chat_session.timestamp + timedelta(minutes=i*2)
            )
            # Save the message to the database
            message.save()
            # Add the message to our list of created messages
            messages.append(message)
            
            # Alternate the message type between USER and BOT for the next message
            current_type = ChatMessage.MessageType.BOT if current_type == ChatMessage.MessageType.USER else ChatMessage.MessageType.USER
        
        # Return the list of created messages
        return messages