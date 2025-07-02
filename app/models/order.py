"""Order models for purchase tracking"""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Text, Enum, func
from datetime import datetime
from typing import List, Optional
import enum

from app.core.database import Base

class OrderStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Order(Base):
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    
    total_amount: Mapped[float] = mapped_column(Float)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING)
    
    shipping_address: Mapped[str] = mapped_column(Text)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Payment info (simplified)
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    payment_status: Mapped[str] = mapped_column(String(50), default="pending")
    
    # Tracking
    tracking_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Order(id={self.id}, user_id={self.user_id}, total={self.total_amount}, status={self.status.value})>"

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)  # Price at time of purchase
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    order: Mapped[Order] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")
    
    def __repr__(self) -> str:
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id}, quantity={self.quantity})>"