"""Cart service for managing shopping cart operations"""

from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from typing import List, Optional
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.core.logging import app_logger

class CartService:
    """Service for cart-related operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_cart(self, user_id: int) -> Cart:
        """Get existing cart or create new one for user"""
        try:
            # Try to get existing cart
            stmt = select(Cart).where(Cart.user_id == user_id)
            result = self.db.execute(stmt)
            cart = result.scalar_one_or_none()
            
            if not cart:
                # Create new cart
                cart = Cart(user_id=user_id)
                self.db.add(cart)
                self.db.commit()
                self.db.refresh(cart)
                app_logger.info(f"Created new cart for user {user_id}")
            
            return cart
        except Exception as e:
            app_logger.error(f"Error getting/creating cart for user {user_id}: {e}")
            raise
    
    def add_to_cart(self, cart_id: int, product_id: int, quantity: int = 1) -> bool:
        """Add product to cart or update quantity if already exists"""
        try:
            # Check if product exists and has stock
            product = self.db.get(Product, product_id)
            if not product or not product.is_active:
                app_logger.warning(f"Attempted to add inactive/non-existent product {product_id} to cart")
                return False
            
            if product.stock_quantity < quantity:
                app_logger.warning(f"Insufficient stock for product {product_id}: requested {quantity}, available {product.stock_quantity}")
                return False
            
            # Check if item already in cart
            stmt = select(CartItem).where(
                and_(
                    CartItem.cart_id == cart_id,
                    CartItem.product_id == product_id
                )
            )
            result = self.db.execute(stmt)
            cart_item = result.scalar_one_or_none()
            
            if cart_item:
                # Update existing item
                new_quantity = cart_item.quantity + quantity
                if product.stock_quantity < new_quantity:
                    app_logger.warning(f"Insufficient stock for product {product_id}: requested {new_quantity}, available {product.stock_quantity}")
                    return False
                
                cart_item.quantity = new_quantity
                app_logger.info(f"Updated cart item quantity: product {product_id}, new quantity {new_quantity}")
            else:
                # Add new item
                cart_item = CartItem(
                    cart_id=cart_id,
                    product_id=product_id,
                    quantity=quantity
                )
                self.db.add(cart_item)
                app_logger.info(f"Added new item to cart: product {product_id}, quantity {quantity}")
            
            self.db.commit()
            return True
        except Exception as e:
            app_logger.error(f"Error adding product {product_id} to cart {cart_id}: {e}")
            self.db.rollback()
            return False
    
    def get_cart_items(self, cart_id: int) -> List[CartItem]:
        """Get all items in cart with product details"""
        try:
            stmt = (
                select(CartItem)
                .where(CartItem.cart_id == cart_id)
                .join(Product)
                .where(Product.is_active == True)
            )
            result = self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            app_logger.error(f"Error getting cart items for cart {cart_id}: {e}")
            return []
    
    def get_cart_items_count(self, cart_id: int) -> int:
        """Get total number of items in cart"""
        try:
            items = self.get_cart_items(cart_id)
            return sum(item.quantity for item in items)
        except Exception as e:
            app_logger.error(f"Error getting cart items count for cart {cart_id}: {e}")
            return 0
    
    def update_cart_item_quantity(self, cart_item_id: int, quantity_change: int) -> bool:
        """Update cart item quantity"""
        try:
            cart_item = self.db.get(CartItem, cart_item_id)
            if not cart_item:
                return False
            
            new_quantity = cart_item.quantity + quantity_change
            
            if new_quantity <= 0:
                # Remove item if quantity becomes 0 or negative
                self.db.delete(cart_item)
                app_logger.info(f"Removed cart item {cart_item_id}")
            else:
                # Check stock availability
                product = cart_item.product
                if product.stock_quantity < new_quantity:
                    app_logger.warning(f"Insufficient stock for product {product.id}: requested {new_quantity}, available {product.stock_quantity}")
                    return False
                
                cart_item.quantity = new_quantity
                app_logger.info(f"Updated cart item {cart_item_id} quantity to {new_quantity}")
            
            self.db.commit()
            return True
        except Exception as e:
            app_logger.error(f"Error updating cart item {cart_item_id} quantity: {e}")
            self.db.rollback()
            return False
    
    def remove_from_cart(self, cart_item_id: int) -> bool:
        """Remove item from cart"""
        try:
            cart_item = self.db.get(CartItem, cart_item_id)
            if not cart_item:
                return False
            
            self.db.delete(cart_item)
            self.db.commit()
            app_logger.info(f"Removed cart item {cart_item_id}")
            return True
        except Exception as e:
            app_logger.error(f"Error removing cart item {cart_item_id}: {e}")
            self.db.rollback()
            return False
    
    def clear_cart(self, cart_id: int) -> bool:
        """Clear all items from cart"""
        try:
            stmt = select(CartItem).where(CartItem.cart_id == cart_id)
            result = self.db.execute(stmt)
            cart_items = result.scalars().all()
            
            for item in cart_items:
                self.db.delete(item)
            
            self.db.commit()
            app_logger.info(f"Cleared cart {cart_id}")
            return True
        except Exception as e:
            app_logger.error(f"Error clearing cart {cart_id}: {e}")
            self.db.rollback()
            return False
    
    def get_cart_total(self, cart_id: int) -> float:
        """Calculate total price of items in cart"""
        try:
            items = self.get_cart_items(cart_id)
            total = sum(item.product.price * item.quantity for item in items)
            return total
        except Exception as e:
            app_logger.error(f"Error calculating cart total for cart {cart_id}: {e}")
            return 0.0