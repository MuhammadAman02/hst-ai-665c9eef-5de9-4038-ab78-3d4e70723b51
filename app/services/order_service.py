"""Order service for managing purchase orders"""

from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from typing import List, Optional
from app.models.order import Order, OrderItem, OrderStatus
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.services.cart_service import CartService
from app.services.product_service import ProductService
from app.core.logging import app_logger

class OrderService:
    """Service for order-related operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_order_from_cart(self, user_id: int, cart_id: int, shipping_address: str, phone: str = None) -> Optional[Order]:
        """Create order from cart items"""
        try:
            # Get cart items
            cart_service = CartService(self.db)
            cart_items = cart_service.get_cart_items(cart_id)
            
            if not cart_items:
                app_logger.warning(f"Attempted to create order from empty cart {cart_id}")
                return None
            
            # Calculate total and validate stock
            total_amount = 0
            order_items_data = []
            
            for cart_item in cart_items:
                product = cart_item.product
                
                # Check stock availability
                if product.stock_quantity < cart_item.quantity:
                    app_logger.warning(f"Insufficient stock for product {product.id}: requested {cart_item.quantity}, available {product.stock_quantity}")
                    return None
                
                item_total = product.price * cart_item.quantity
                total_amount += item_total
                
                order_items_data.append({
                    'product_id': product.id,
                    'quantity': cart_item.quantity,
                    'price': product.price
                })
            
            # Create order
            order = Order(
                user_id=user_id,
                total_amount=total_amount,
                status=OrderStatus.PENDING,
                shipping_address=shipping_address,
                phone=phone,
                payment_method="Credit Card",  # Default for now
                payment_status="pending"
            )
            
            self.db.add(order)
            self.db.flush()  # Get order ID
            
            # Create order items and update stock
            product_service = ProductService(self.db)
            for item_data in order_items_data:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
                self.db.add(order_item)
                
                # Update product stock
                product_service.update_stock(item_data['product_id'], -item_data['quantity'])
            
            self.db.commit()
            self.db.refresh(order)
            
            app_logger.info(f"Created order {order.id} for user {user_id}, total: ${total_amount:.2f}")
            return order
            
        except Exception as e:
            app_logger.error(f"Error creating order from cart {cart_id}: {e}")
            self.db.rollback()
            return None
    
    def get_order(self, order_id: int) -> Optional[Order]:
        """Get order by ID"""
        try:
            return self.db.get(Order, order_id)
        except Exception as e:
            app_logger.error(f"Error getting order {order_id}: {e}")
            return None
    
    def get_user_orders(self, user_id: int, limit: int = 50) -> List[Order]:
        """Get all orders for a user"""
        try:
            stmt = (
                select(Order)
                .where(Order.user_id == user_id)
                .order_by(Order.created_at.desc())
                .limit(limit)
            )
            result = self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            app_logger.error(f"Error getting orders for user {user_id}: {e}")
            return []
    
    def get_order_items(self, order_id: int) -> List[OrderItem]:
        """Get all items in an order"""
        try:
            stmt = select(OrderItem).where(OrderItem.order_id == order_id)
            result = self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            app_logger.error(f"Error getting order items for order {order_id}: {e}")
            return []
    
    def update_order_status(self, order_id: int, status: OrderStatus) -> bool:
        """Update order status"""
        try:
            order = self.get_order(order_id)
            if not order:
                return False
            
            old_status = order.status
            order.status = status
            self.db.commit()
            
            app_logger.info(f"Updated order {order_id} status from {old_status.value} to {status.value}")
            return True
        except Exception as e:
            app_logger.error(f"Error updating order {order_id} status: {e}")
            self.db.rollback()
            return False
    
    def update_payment_status(self, order_id: int, payment_status: str) -> bool:
        """Update order payment status"""
        try:
            order = self.get_order(order_id)
            if not order:
                return False
            
            order.payment_status = payment_status
            self.db.commit()
            
            app_logger.info(f"Updated order {order_id} payment status to {payment_status}")
            return True
        except Exception as e:
            app_logger.error(f"Error updating order {order_id} payment status: {e}")
            self.db.rollback()
            return False
    
    def add_tracking_number(self, order_id: int, tracking_number: str) -> bool:
        """Add tracking number to order"""
        try:
            order = self.get_order(order_id)
            if not order:
                return False
            
            order.tracking_number = tracking_number
            order.status = OrderStatus.SHIPPED
            self.db.commit()
            
            app_logger.info(f"Added tracking number {tracking_number} to order {order_id}")
            return True
        except Exception as e:
            app_logger.error(f"Error adding tracking number to order {order_id}: {e}")
            self.db.rollback()
            return False
    
    def cancel_order(self, order_id: int) -> bool:
        """Cancel an order and restore stock"""
        try:
            order = self.get_order(order_id)
            if not order:
                return False
            
            if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
                app_logger.warning(f"Cannot cancel order {order_id} with status {order.status.value}")
                return False
            
            # Restore stock for all items
            product_service = ProductService(self.db)
            order_items = self.get_order_items(order_id)
            
            for item in order_items:
                product_service.update_stock(item.product_id, item.quantity)
            
            # Update order status
            order.status = OrderStatus.CANCELLED
            self.db.commit()
            
            app_logger.info(f"Cancelled order {order_id} and restored stock")
            return True
        except Exception as e:
            app_logger.error(f"Error cancelling order {order_id}: {e}")
            self.db.rollback()
            return False
    
    def get_all_orders(self, limit: int = 100) -> List[Order]:
        """Get all orders (admin function)"""
        try:
            stmt = (
                select(Order)
                .order_by(Order.created_at.desc())
                .limit(limit)
            )
            result = self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            app_logger.error(f"Error getting all orders: {e}")
            return []
    
    def get_orders_by_status(self, status: OrderStatus, limit: int = 100) -> List[Order]:
        """Get orders by status"""
        try:
            stmt = (
                select(Order)
                .where(Order.status == status)
                .order_by(Order.created_at.desc())
                .limit(limit)
            )
            result = self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            app_logger.error(f"Error getting orders by status {status.value}: {e}")
            return []