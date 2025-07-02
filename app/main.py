"""HP Ecommerce Store - Main UI Application"""

from nicegui import ui, app as nicegui_app
from typing import Optional, List, Dict, Any
import asyncio
from datetime import datetime

from app.core import app_logger, settings
from app.services.product_service import ProductService
from app.services.cart_service import CartService
from app.services.auth_service import AuthService
from app.services.order_service import OrderService
from app.models.user import User
from app.models.product import Product
from app.models.cart import Cart
from app.core.database import get_db_session

# Global state management
class AppState:
    def __init__(self):
        self.current_user: Optional[User] = None
        self.cart_items_count: int = 0
        self.current_cart: Optional[Cart] = None
        
    def set_user(self, user: Optional[User]):
        self.current_user = user
        if user:
            # Load user's cart
            with get_db_session() as db:
                cart_service = CartService(db)
                self.current_cart = cart_service.get_or_create_cart(user.id)
                self.cart_items_count = cart_service.get_cart_items_count(self.current_cart.id)
        else:
            self.current_cart = None
            self.cart_items_count = 0

app_state = AppState()

# Utility functions
def format_price(price: float) -> str:
    """Format price as currency"""
    return f"${price:,.2f}"

def create_header():
    """Create the main header with navigation"""
    with ui.header().classes('bg-blue-600 text-white shadow-lg'):
        with ui.row().classes('w-full items-center justify-between px-4 py-2'):
            # Logo and brand
            with ui.row().classes('items-center gap-4'):
                ui.image('/static/images/hp-logo.png').classes('h-8 w-auto').props('fit=contain')
                ui.label('HP Store').classes('text-2xl font-bold')
            
            # Navigation
            with ui.row().classes('items-center gap-6'):
                ui.link('Home', '/').classes('text-white hover:text-blue-200 font-medium')
                ui.link('Laptops', '/category/laptops').classes('text-white hover:text-blue-200 font-medium')
                ui.link('Desktops', '/category/desktops').classes('text-white hover:text-blue-200 font-medium')
                ui.link('Printers', '/category/printers').classes('text-white hover:text-blue-200 font-medium')
                ui.link('Accessories', '/category/accessories').classes('text-white hover:text-blue-200 font-medium')
            
            # User actions
            with ui.row().classes('items-center gap-4'):
                # Search
                search_input = ui.input(placeholder='Search products...').classes('w-64')
                ui.button(icon='search', on_click=lambda: search_products(search_input.value)).props('flat color=white')
                
                # Cart
                cart_button = ui.button(f'Cart ({app_state.cart_items_count})', icon='shopping_cart', 
                                      on_click=lambda: ui.navigate.to('/cart')).props('flat color=white')
                
                # User menu
                if app_state.current_user:
                    with ui.button(app_state.current_user.username, icon='account_circle').props('flat color=white'):
                        with ui.menu():
                            ui.menu_item('Profile', lambda: ui.navigate.to('/profile'))
                            ui.menu_item('Orders', lambda: ui.navigate.to('/orders'))
                            ui.menu_item('Logout', logout)
                else:
                    ui.button('Login', on_click=lambda: ui.navigate.to('/login')).props('flat color=white')

def create_product_card(product: Product) -> ui.card:
    """Create a product card component"""
    with ui.card().classes('w-72 h-96 cursor-pointer hover:shadow-xl transition-shadow') as card:
        # Product image
        ui.image(product.image_url or '/static/images/placeholder-product.png').classes('h-48 w-full object-cover')
        
        with ui.card_section().classes('p-4'):
            # Product name
            ui.label(product.name).classes('text-lg font-semibold text-gray-800 line-clamp-2')
            
            # Price
            ui.label(format_price(product.price)).classes('text-xl font-bold text-blue-600 mt-2')
            
            # Stock status
            if product.stock_quantity > 0:
                ui.label(f'In Stock ({product.stock_quantity} available)').classes('text-sm text-green-600')
            else:
                ui.label('Out of Stock').classes('text-sm text-red-600')
            
            # Action buttons
            with ui.row().classes('w-full justify-between mt-4'):
                ui.button('View Details', on_click=lambda p=product: ui.navigate.to(f'/product/{p.id}')).props('flat color=primary')
                
                if product.stock_quantity > 0:
                    ui.button('Add to Cart', icon='add_shopping_cart',
                             on_click=lambda p=product: add_to_cart(p.id)).props('color=primary')
                else:
                    ui.button('Out of Stock').props('disable color=grey')
    
    return card

def search_products(query: str):
    """Search for products"""
    if query.strip():
        ui.navigate.to(f'/search?q={query.strip()}')

def add_to_cart(product_id: int, quantity: int = 1):
    """Add product to cart"""
    if not app_state.current_user:
        ui.navigate.to('/login')
        return
    
    try:
        with get_db_session() as db:
            cart_service = CartService(db)
            cart_service.add_to_cart(app_state.current_cart.id, product_id, quantity)
            app_state.cart_items_count = cart_service.get_cart_items_count(app_state.current_cart.id)
            ui.notify('Product added to cart!', type='positive')
    except Exception as e:
        app_logger.error(f"Error adding to cart: {e}")
        ui.notify('Failed to add product to cart', type='negative')

def logout():
    """Logout current user"""
    app_state.set_user(None)
    ui.notify('Logged out successfully', type='positive')
    ui.navigate.to('/')

# Page routes
@ui.page('/')
def homepage():
    """Homepage with featured products"""
    create_header()
    
    with ui.column().classes('w-full max-w-7xl mx-auto px-4 py-8'):
        # Hero section
        with ui.card().classes('w-full bg-gradient-to-r from-blue-600 to-blue-800 text-white mb-8'):
            with ui.card_section().classes('p-8 text-center'):
                ui.label('Welcome to HP Store').classes('text-4xl font-bold mb-4')
                ui.label('Discover the latest HP laptops, desktops, printers, and accessories').classes('text-xl mb-6')
                ui.button('Shop Now', on_click=lambda: ui.navigate.to('/category/laptops')).props('size=lg color=white')
        
        # Featured categories
        ui.label('Shop by Category').classes('text-3xl font-bold mb-6')
        with ui.row().classes('w-full gap-6 mb-8'):
            categories = [
                {'name': 'Laptops', 'image': '/static/images/category-laptops.jpg', 'url': '/category/laptops'},
                {'name': 'Desktops', 'image': '/static/images/category-desktops.jpg', 'url': '/category/desktops'},
                {'name': 'Printers', 'image': '/static/images/category-printers.jpg', 'url': '/category/printers'},
                {'name': 'Accessories', 'image': '/static/images/category-accessories.jpg', 'url': '/category/accessories'},
            ]
            
            for category in categories:
                with ui.card().classes('w-64 cursor-pointer hover:shadow-lg transition-shadow'):
                    ui.image(category['image']).classes('h-40 w-full object-cover')
                    with ui.card_section().classes('p-4 text-center'):
                        ui.label(category['name']).classes('text-xl font-semibold')
                        ui.button('Browse', on_click=lambda url=category['url']: ui.navigate.to(url)).props('flat color=primary')
        
        # Featured products
        ui.label('Featured Products').classes('text-3xl font-bold mb-6')
        with ui.row().classes('w-full gap-6 flex-wrap'):
            try:
                with get_db_session() as db:
                    product_service = ProductService(db)
                    featured_products = product_service.get_featured_products(limit=8)
                    
                    for product in featured_products:
                        create_product_card(product)
            except Exception as e:
                app_logger.error(f"Error loading featured products: {e}")
                ui.label('Unable to load featured products').classes('text-gray-500')

@ui.page('/category/{category_name}')
def category_page(category_name: str):
    """Category page showing products in a specific category"""
    create_header()
    
    with ui.column().classes('w-full max-w-7xl mx-auto px-4 py-8'):
        ui.label(f'{category_name.title()} Products').classes('text-3xl font-bold mb-6')
        
        # Filters
        with ui.row().classes('w-full gap-4 mb-6'):
            price_filter = ui.select(['All Prices', 'Under $500', '$500-$1000', '$1000-$2000', 'Over $2000'], 
                                   value='All Prices').classes('w-48')
            sort_filter = ui.select(['Name A-Z', 'Name Z-A', 'Price Low-High', 'Price High-Low'], 
                                  value='Name A-Z').classes('w-48')
            ui.button('Apply Filters', on_click=lambda: apply_filters(category_name, price_filter.value, sort_filter.value))
        
        # Products grid
        products_container = ui.row().classes('w-full gap-6 flex-wrap')
        
        def load_products():
            products_container.clear()
            try:
                with get_db_session() as db:
                    product_service = ProductService(db)
                    products = product_service.get_products_by_category(category_name)
                    
                    if products:
                        with products_container:
                            for product in products:
                                create_product_card(product)
                    else:
                        with products_container:
                            ui.label(f'No products found in {category_name} category').classes('text-gray-500 text-xl')
            except Exception as e:
                app_logger.error(f"Error loading category products: {e}")
                with products_container:
                    ui.label('Unable to load products').classes('text-gray-500')
        
        load_products()

def apply_filters(category_name: str, price_filter: str, sort_filter: str):
    """Apply filters to product listing"""
    # This would implement actual filtering logic
    ui.notify(f'Filters applied: {price_filter}, {sort_filter}', type='info')

@ui.page('/product/{product_id}')
def product_detail_page(product_id: int):
    """Product detail page"""
    create_header()
    
    with ui.column().classes('w-full max-w-7xl mx-auto px-4 py-8'):
        try:
            with get_db_session() as db:
                product_service = ProductService(db)
                product = product_service.get_product(product_id)
                
                if not product:
                    ui.label('Product not found').classes('text-2xl text-gray-500')
                    return
                
                with ui.row().classes('w-full gap-8'):
                    # Product image
                    with ui.column().classes('w-1/2'):
                        ui.image(product.image_url or '/static/images/placeholder-product.png').classes('w-full h-96 object-cover rounded-lg')
                    
                    # Product details
                    with ui.column().classes('w-1/2'):
                        ui.label(product.name).classes('text-3xl font-bold mb-4')
                        ui.label(format_price(product.price)).classes('text-2xl font-bold text-blue-600 mb-4')
                        
                        # Stock status
                        if product.stock_quantity > 0:
                            ui.label(f'In Stock ({product.stock_quantity} available)').classes('text-lg text-green-600 mb-4')
                        else:
                            ui.label('Out of Stock').classes('text-lg text-red-600 mb-4')
                        
                        # Description
                        ui.label('Description').classes('text-xl font-semibold mb-2')
                        ui.label(product.description or 'No description available').classes('text-gray-700 mb-6')
                        
                        # Specifications
                        if product.specifications:
                            ui.label('Specifications').classes('text-xl font-semibold mb-2')
                            ui.label(product.specifications).classes('text-gray-700 mb-6')
                        
                        # Add to cart
                        if product.stock_quantity > 0:
                            with ui.row().classes('gap-4 items-center'):
                                quantity_input = ui.number('Quantity', value=1, min=1, max=product.stock_quantity).classes('w-24')
                                ui.button('Add to Cart', icon='add_shopping_cart',
                                         on_click=lambda: add_to_cart(product.id, int(quantity_input.value))).props('size=lg color=primary')
                        else:
                            ui.button('Out of Stock').props('size=lg disable color=grey')
                
        except Exception as e:
            app_logger.error(f"Error loading product details: {e}")
            ui.label('Unable to load product details').classes('text-2xl text-gray-500')

@ui.page('/cart')
def cart_page():
    """Shopping cart page"""
    create_header()
    
    with ui.column().classes('w-full max-w-4xl mx-auto px-4 py-8'):
        ui.label('Shopping Cart').classes('text-3xl font-bold mb-6')
        
        if not app_state.current_user:
            ui.label('Please login to view your cart').classes('text-xl text-gray-500')
            ui.button('Login', on_click=lambda: ui.navigate.to('/login')).props('color=primary')
            return
        
        cart_container = ui.column().classes('w-full')
        
        def load_cart():
            cart_container.clear()
            try:
                with get_db_session() as db:
                    cart_service = CartService(db)
                    cart_items = cart_service.get_cart_items(app_state.current_cart.id)
                    
                    if not cart_items:
                        with cart_container:
                            ui.label('Your cart is empty').classes('text-xl text-gray-500 text-center py-8')
                            ui.button('Continue Shopping', on_click=lambda: ui.navigate.to('/')).props('color=primary')
                        return
                    
                    total = 0
                    with cart_container:
                        for item in cart_items:
                            with ui.card().classes('w-full mb-4'):
                                with ui.row().classes('w-full items-center p-4'):
                                    # Product image
                                    ui.image(item.product.image_url or '/static/images/placeholder-product.png').classes('w-20 h-20 object-cover')
                                    
                                    # Product details
                                    with ui.column().classes('flex-1 ml-4'):
                                        ui.label(item.product.name).classes('text-lg font-semibold')
                                        ui.label(format_price(item.product.price)).classes('text-blue-600 font-bold')
                                    
                                    # Quantity controls
                                    with ui.row().classes('items-center gap-2'):
                                        ui.button('-', on_click=lambda item_id=item.id: update_cart_quantity(item_id, -1)).props('size=sm')
                                        ui.label(str(item.quantity)).classes('mx-2 font-semibold')
                                        ui.button('+', on_click=lambda item_id=item.id: update_cart_quantity(item_id, 1)).props('size=sm')
                                    
                                    # Remove button
                                    ui.button('Remove', icon='delete', 
                                             on_click=lambda item_id=item.id: remove_from_cart(item_id)).props('flat color=negative')
                                    
                                    # Item total
                                    item_total = item.product.price * item.quantity
                                    ui.label(format_price(item_total)).classes('text-lg font-bold ml-4')
                                    total += item_total
                        
                        # Cart summary
                        with ui.card().classes('w-full mt-6'):
                            with ui.card_section().classes('p-6'):
                                ui.label('Order Summary').classes('text-xl font-bold mb-4')
                                with ui.row().classes('w-full justify-between'):
                                    ui.label('Total:').classes('text-lg')
                                    ui.label(format_price(total)).classes('text-2xl font-bold text-blue-600')
                                
                                ui.button('Proceed to Checkout', on_click=lambda: ui.navigate.to('/checkout')).props('size=lg color=primary class=w-full mt-4')
            
            except Exception as e:
                app_logger.error(f"Error loading cart: {e}")
                with cart_container:
                    ui.label('Unable to load cart').classes('text-gray-500')
        
        load_cart()

def update_cart_quantity(item_id: int, change: int):
    """Update cart item quantity"""
    try:
        with get_db_session() as db:
            cart_service = CartService(db)
            cart_service.update_cart_item_quantity(item_id, change)
            app_state.cart_items_count = cart_service.get_cart_items_count(app_state.current_cart.id)
            ui.navigate.reload()
    except Exception as e:
        app_logger.error(f"Error updating cart quantity: {e}")
        ui.notify('Failed to update quantity', type='negative')

def remove_from_cart(item_id: int):
    """Remove item from cart"""
    try:
        with get_db_session() as db:
            cart_service = CartService(db)
            cart_service.remove_from_cart(item_id)
            app_state.cart_items_count = cart_service.get_cart_items_count(app_state.current_cart.id)
            ui.navigate.reload()
    except Exception as e:
        app_logger.error(f"Error removing from cart: {e}")
        ui.notify('Failed to remove item', type='negative')

@ui.page('/login')
def login_page():
    """User login page"""
    create_header()
    
    with ui.column().classes('w-full max-w-md mx-auto px-4 py-8'):
        with ui.card().classes('w-full'):
            with ui.card_section().classes('p-6'):
                ui.label('Login to HP Store').classes('text-2xl font-bold mb-6 text-center')
                
                email_input = ui.input('Email', placeholder='Enter your email').classes('w-full mb-4')
                password_input = ui.input('Password', placeholder='Enter your password', password=True).classes('w-full mb-6')
                
                def handle_login():
                    try:
                        with get_db_session() as db:
                            auth_service = AuthService(db)
                            user = auth_service.authenticate_user(email_input.value, password_input.value)
                            
                            if user:
                                app_state.set_user(user)
                                ui.notify('Login successful!', type='positive')
                                ui.navigate.to('/')
                            else:
                                ui.notify('Invalid email or password', type='negative')
                    except Exception as e:
                        app_logger.error(f"Login error: {e}")
                        ui.notify('Login failed', type='negative')
                
                ui.button('Login', on_click=handle_login).props('size=lg color=primary class=w-full mb-4')
                
                with ui.row().classes('w-full justify-center'):
                    ui.label("Don't have an account?").classes('text-gray-600')
                    ui.link('Sign up', '/register').classes('text-blue-600 ml-2')

@ui.page('/register')
def register_page():
    """User registration page"""
    create_header()
    
    with ui.column().classes('w-full max-w-md mx-auto px-4 py-8'):
        with ui.card().classes('w-full'):
            with ui.card_section().classes('p-6'):
                ui.label('Create Account').classes('text-2xl font-bold mb-6 text-center')
                
                username_input = ui.input('Username', placeholder='Choose a username').classes('w-full mb-4')
                email_input = ui.input('Email', placeholder='Enter your email').classes('w-full mb-4')
                full_name_input = ui.input('Full Name', placeholder='Enter your full name').classes('w-full mb-4')
                password_input = ui.input('Password', placeholder='Choose a password', password=True).classes('w-full mb-4')
                confirm_password_input = ui.input('Confirm Password', placeholder='Confirm your password', password=True).classes('w-full mb-6')
                
                def handle_register():
                    if password_input.value != confirm_password_input.value:
                        ui.notify('Passwords do not match', type='negative')
                        return
                    
                    try:
                        with get_db_session() as db:
                            auth_service = AuthService(db)
                            user = auth_service.create_user(
                                username=username_input.value,
                                email=email_input.value,
                                password=password_input.value,
                                full_name=full_name_input.value
                            )
                            
                            if user:
                                app_state.set_user(user)
                                ui.notify('Account created successfully!', type='positive')
                                ui.navigate.to('/')
                            else:
                                ui.notify('Failed to create account', type='negative')
                    except Exception as e:
                        app_logger.error(f"Registration error: {e}")
                        ui.notify('Registration failed', type='negative')
                
                ui.button('Create Account', on_click=handle_register).props('size=lg color=primary class=w-full mb-4')
                
                with ui.row().classes('w-full justify-center'):
                    ui.label("Already have an account?").classes('text-gray-600')
                    ui.link('Login', '/login').classes('text-blue-600 ml-2')

@ui.page('/checkout')
def checkout_page():
    """Checkout page"""
    create_header()
    
    if not app_state.current_user:
        ui.navigate.to('/login')
        return
    
    with ui.column().classes('w-full max-w-4xl mx-auto px-4 py-8'):
        ui.label('Checkout').classes('text-3xl font-bold mb-6')
        
        with ui.row().classes('w-full gap-8'):
            # Order summary
            with ui.column().classes('w-1/2'):
                ui.label('Order Summary').classes('text-xl font-bold mb-4')
                
                try:
                    with get_db_session() as db:
                        cart_service = CartService(db)
                        cart_items = cart_service.get_cart_items(app_state.current_cart.id)
                        
                        total = 0
                        for item in cart_items:
                            with ui.row().classes('w-full justify-between mb-2'):
                                ui.label(f"{item.product.name} x {item.quantity}")
                                item_total = item.product.price * item.quantity
                                ui.label(format_price(item_total))
                                total += item_total
                        
                        ui.separator()
                        with ui.row().classes('w-full justify-between mt-4'):
                            ui.label('Total:').classes('text-lg font-bold')
                            ui.label(format_price(total)).classes('text-xl font-bold text-blue-600')
                
                except Exception as e:
                    app_logger.error(f"Error loading checkout summary: {e}")
                    ui.label('Unable to load order summary').classes('text-gray-500')
            
            # Shipping and payment
            with ui.column().classes('w-1/2'):
                ui.label('Shipping Information').classes('text-xl font-bold mb-4')
                
                address_input = ui.textarea('Shipping Address', placeholder='Enter your shipping address').classes('w-full mb-4')
                phone_input = ui.input('Phone Number', placeholder='Enter your phone number').classes('w-full mb-6')
                
                ui.label('Payment Method').classes('text-xl font-bold mb-4')
                payment_method = ui.select(['Credit Card', 'PayPal', 'Bank Transfer'], value='Credit Card').classes('w-full mb-4')
                
                # Credit card fields (simplified)
                card_number_input = ui.input('Card Number', placeholder='1234 5678 9012 3456').classes('w-full mb-4')
                with ui.row().classes('w-full gap-4 mb-6'):
                    expiry_input = ui.input('MM/YY', placeholder='12/25').classes('w-1/2')
                    cvv_input = ui.input('CVV', placeholder='123').classes('w-1/2')
                
                def handle_place_order():
                    try:
                        with get_db_session() as db:
                            order_service = OrderService(db)
                            cart_service = CartService(db)
                            
                            # Create order from cart
                            order = order_service.create_order_from_cart(
                                user_id=app_state.current_user.id,
                                cart_id=app_state.current_cart.id,
                                shipping_address=address_input.value
                            )
                            
                            if order:
                                # Clear cart
                                cart_service.clear_cart(app_state.current_cart.id)
                                app_state.cart_items_count = 0
                                
                                ui.notify('Order placed successfully!', type='positive')
                                ui.navigate.to(f'/order-confirmation/{order.id}')
                            else:
                                ui.notify('Failed to place order', type='negative')
                    except Exception as e:
                        app_logger.error(f"Error placing order: {e}")
                        ui.notify('Failed to place order', type='negative')
                
                ui.button('Place Order', on_click=handle_place_order).props('size=lg color=primary class=w-full')

@ui.page('/order-confirmation/{order_id}')
def order_confirmation_page(order_id: int):
    """Order confirmation page"""
    create_header()
    
    with ui.column().classes('w-full max-w-2xl mx-auto px-4 py-8 text-center'):
        ui.icon('check_circle', size='4rem').classes('text-green-500 mb-4')
        ui.label('Order Confirmed!').classes('text-3xl font-bold mb-4')
        ui.label(f'Order #{order_id}').classes('text-xl text-gray-600 mb-6')
        
        ui.label('Thank you for your purchase. You will receive an email confirmation shortly.').classes('text-lg mb-8')
        
        with ui.row().classes('gap-4 justify-center'):
            ui.button('Continue Shopping', on_click=lambda: ui.navigate.to('/')).props('color=primary')
            ui.button('View Orders', on_click=lambda: ui.navigate.to('/orders')).props('flat color=primary')

@ui.page('/search')
def search_page():
    """Search results page"""
    create_header()
    
    # Get search query from URL parameters
    query = ui.context.client.query.get('q', '')
    
    with ui.column().classes('w-full max-w-7xl mx-auto px-4 py-8'):
        ui.label(f'Search Results for "{query}"').classes('text-3xl font-bold mb-6')
        
        products_container = ui.row().classes('w-full gap-6 flex-wrap')
        
        try:
            with get_db_session() as db:
                product_service = ProductService(db)
                products = product_service.search_products(query)
                
                if products:
                    with products_container:
                        for product in products:
                            create_product_card(product)
                else:
                    with products_container:
                        ui.label(f'No products found for "{query}"').classes('text-gray-500 text-xl')
        except Exception as e:
            app_logger.error(f"Error searching products: {e}")
            with products_container:
                ui.label('Unable to search products').classes('text-gray-500')

# Initialize sample data on startup
def init_sample_data():
    """Initialize sample HP products"""
    try:
        from app.core.sample_data import create_sample_data
        create_sample_data()
        app_logger.info("Sample data initialized")
    except Exception as e:
        app_logger.error(f"Error initializing sample data: {e}")

# Initialize when the module is imported
init_sample_data()