"""Product service for managing product operations"""

from sqlalchemy.orm import Session
from sqlalchemy import select, or_, and_
from typing import List, Optional
from app.models.product import Product, Category
from app.core.logging import app_logger

class ProductService:
    """Service for product-related operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_product(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        try:
            return self.db.get(Product, product_id)
        except Exception as e:
            app_logger.error(f"Error getting product {product_id}: {e}")
            return None
    
    def get_products_by_category(self, category_name: str, limit: int = 50) -> List[Product]:
        """Get products by category name"""
        try:
            stmt = (
                select(Product)
                .join(Category)
                .where(
                    and_(
                        Category.name.ilike(f"%{category_name}%"),
                        Product.is_active == True
                    )
                )
                .limit(limit)
            )
            result = self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            app_logger.error(f"Error getting products by category {category_name}: {e}")
            return []
    
    def get_featured_products(self, limit: int = 8) -> List[Product]:
        """Get featured products"""
        try:
            stmt = (
                select(Product)
                .where(
                    and_(
                        Product.is_featured == True,
                        Product.is_active == True
                    )
                )
                .limit(limit)
            )
            result = self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            app_logger.error(f"Error getting featured products: {e}")
            return []
    
    def search_products(self, query: str, limit: int = 50) -> List[Product]:
        """Search products by name or description"""
        try:
            search_term = f"%{query}%"
            stmt = (
                select(Product)
                .where(
                    and_(
                        or_(
                            Product.name.ilike(search_term),
                            Product.description.ilike(search_term),
                            Product.specifications.ilike(search_term)
                        ),
                        Product.is_active == True
                    )
                )
                .limit(limit)
            )
            result = self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            app_logger.error(f"Error searching products with query '{query}': {e}")
            return []
    
    def get_products_by_price_range(self, min_price: float, max_price: float, limit: int = 50) -> List[Product]:
        """Get products within price range"""
        try:
            stmt = (
                select(Product)
                .where(
                    and_(
                        Product.price >= min_price,
                        Product.price <= max_price,
                        Product.is_active == True
                    )
                )
                .limit(limit)
            )
            result = self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            app_logger.error(f"Error getting products by price range {min_price}-{max_price}: {e}")
            return []
    
    def get_all_categories(self) -> List[Category]:
        """Get all product categories"""
        try:
            stmt = select(Category)
            result = self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            app_logger.error(f"Error getting categories: {e}")
            return []
    
    def create_product(self, product_data: dict) -> Optional[Product]:
        """Create a new product"""
        try:
            product = Product(**product_data)
            self.db.add(product)
            self.db.commit()
            self.db.refresh(product)
            app_logger.info(f"Created product: {product.name}")
            return product
        except Exception as e:
            app_logger.error(f"Error creating product: {e}")
            self.db.rollback()
            return None
    
    def update_product(self, product_id: int, product_data: dict) -> Optional[Product]:
        """Update an existing product"""
        try:
            product = self.get_product(product_id)
            if not product:
                return None
            
            for key, value in product_data.items():
                if hasattr(product, key):
                    setattr(product, key, value)
            
            self.db.commit()
            self.db.refresh(product)
            app_logger.info(f"Updated product: {product.name}")
            return product
        except Exception as e:
            app_logger.error(f"Error updating product {product_id}: {e}")
            self.db.rollback()
            return None
    
    def delete_product(self, product_id: int) -> bool:
        """Delete a product (soft delete by setting is_active=False)"""
        try:
            product = self.get_product(product_id)
            if not product:
                return False
            
            product.is_active = False
            self.db.commit()
            app_logger.info(f"Deleted product: {product.name}")
            return True
        except Exception as e:
            app_logger.error(f"Error deleting product {product_id}: {e}")
            self.db.rollback()
            return False
    
    def update_stock(self, product_id: int, quantity_change: int) -> bool:
        """Update product stock quantity"""
        try:
            product = self.get_product(product_id)
            if not product:
                return False
            
            new_quantity = product.stock_quantity + quantity_change
            if new_quantity < 0:
                app_logger.warning(f"Attempted to set negative stock for product {product_id}")
                return False
            
            product.stock_quantity = new_quantity
            self.db.commit()
            app_logger.info(f"Updated stock for product {product.name}: {product.stock_quantity}")
            return True
        except Exception as e:
            app_logger.error(f"Error updating stock for product {product_id}: {e}")
            self.db.rollback()
            return False