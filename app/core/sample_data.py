"""Sample data creation for HP ecommerce store"""

from app.core.database import get_db_session
from app.models.product import Category, Product
from app.models.user import User
from app.services.auth_service import AuthService
from app.core.logging import app_logger

def create_sample_data():
    """Create sample categories, products, and admin user"""
    try:
        with get_db_session() as db:
            # Check if data already exists
            existing_categories = db.query(Category).count()
            if existing_categories > 0:
                app_logger.info("Sample data already exists, skipping creation")
                return
            
            # Create categories
            categories_data = [
                {
                    'name': 'Laptops',
                    'description': 'HP Laptops for work, gaming, and everyday use',
                    'image_url': '/static/images/category-laptops.jpg'
                },
                {
                    'name': 'Desktops',
                    'description': 'HP Desktop computers and workstations',
                    'image_url': '/static/images/category-desktops.jpg'
                },
                {
                    'name': 'Printers',
                    'description': 'HP Printers, scanners, and all-in-one devices',
                    'image_url': '/static/images/category-printers.jpg'
                },
                {
                    'name': 'Accessories',
                    'description': 'HP Accessories, monitors, keyboards, and more',
                    'image_url': '/static/images/category-accessories.jpg'
                }
            ]
            
            categories = {}
            for cat_data in categories_data:
                category = Category(**cat_data)
                db.add(category)
                db.flush()
                categories[cat_data['name']] = category
            
            # Create sample products
            products_data = [
                # Laptops
                {
                    'name': 'HP Pavilion 15.6" Laptop',
                    'description': 'Powerful laptop with Intel Core i5 processor, 8GB RAM, and 256GB SSD. Perfect for work and entertainment.',
                    'price': 699.99,
                    'sku': 'HP-PAV-15-001',
                    'stock_quantity': 25,
                    'category_id': categories['Laptops'].id,
                    'image_url': '/static/images/hp-pavilion-laptop.jpg',
                    'specifications': 'Intel Core i5-1135G7, 8GB DDR4 RAM, 256GB SSD, 15.6" FHD Display, Windows 11',
                    'is_featured': True
                },
                {
                    'name': 'HP Envy x360 13.3" 2-in-1 Laptop',
                    'description': 'Versatile 2-in-1 laptop with touchscreen and 360-degree hinge. AMD Ryzen 5 processor for excellent performance.',
                    'price': 899.99,
                    'sku': 'HP-ENVY-X360-001',
                    'stock_quantity': 15,
                    'category_id': categories['Laptops'].id,
                    'image_url': '/static/images/hp-envy-x360.jpg',
                    'specifications': 'AMD Ryzen 5 5500U, 8GB DDR4 RAM, 512GB SSD, 13.3" FHD Touchscreen, Windows 11',
                    'is_featured': True
                },
                {
                    'name': 'HP Omen 16.1" Gaming Laptop',
                    'description': 'High-performance gaming laptop with NVIDIA GeForce RTX graphics and Intel Core i7 processor.',
                    'price': 1299.99,
                    'sku': 'HP-OMEN-16-001',
                    'stock_quantity': 10,
                    'category_id': categories['Laptops'].id,
                    'image_url': '/static/images/hp-omen-gaming.jpg',
                    'specifications': 'Intel Core i7-11800H, 16GB DDR4 RAM, 512GB SSD, NVIDIA GeForce RTX 3060, 16.1" FHD 144Hz',
                    'is_featured': True
                },
                {
                    'name': 'HP EliteBook 14" Business Laptop',
                    'description': 'Professional business laptop with enhanced security features and long battery life.',
                    'price': 1199.99,
                    'sku': 'HP-ELITE-14-001',
                    'stock_quantity': 20,
                    'category_id': categories['Laptops'].id,
                    'image_url': '/static/images/hp-elitebook.jpg',
                    'specifications': 'Intel Core i5-1145G7, 16GB DDR4 RAM, 512GB SSD, 14" FHD Display, Windows 11 Pro'
                },
                
                # Desktops
                {
                    'name': 'HP Pavilion Desktop',
                    'description': 'Reliable desktop computer for everyday computing tasks and light gaming.',
                    'price': 549.99,
                    'sku': 'HP-PAV-DT-001',
                    'stock_quantity': 30,
                    'category_id': categories['Desktops'].id,
                    'image_url': '/static/images/hp-pavilion-desktop.jpg',
                    'specifications': 'Intel Core i3-10100, 8GB DDR4 RAM, 256GB SSD + 1TB HDD, Intel UHD Graphics, Windows 11',
                    'is_featured': True
                },
                {
                    'name': 'HP Omen 45L Gaming Desktop',
                    'description': 'Powerful gaming desktop with RGB lighting and high-performance components.',
                    'price': 1599.99,
                    'sku': 'HP-OMEN-45L-001',
                    'stock_quantity': 8,
                    'category_id': categories['Desktops'].id,
                    'image_url': '/static/images/hp-omen-desktop.jpg',
                    'specifications': 'Intel Core i7-11700F, 16GB DDR4 RAM, 512GB SSD + 1TB HDD, NVIDIA GeForce RTX 3070, Windows 11',
                    'is_featured': True
                },
                {
                    'name': 'HP EliteDesk 800 G8 Mini',
                    'description': 'Compact business desktop with enterprise-grade security and performance.',
                    'price': 899.99,
                    'sku': 'HP-ELITE-MINI-001',
                    'stock_quantity': 15,
                    'category_id': categories['Desktops'].id,
                    'image_url': '/static/images/hp-elitedesk-mini.jpg',
                    'specifications': 'Intel Core i5-11500T, 8GB DDR4 RAM, 256GB SSD, Intel UHD Graphics, Windows 11 Pro'
                },
                
                # Printers
                {
                    'name': 'HP OfficeJet Pro 9015e All-in-One Printer',
                    'description': 'Wireless all-in-one printer with print, scan, copy, and fax capabilities.',
                    'price': 199.99,
                    'sku': 'HP-OJ-9015E-001',
                    'stock_quantity': 40,
                    'category_id': categories['Printers'].id,
                    'image_url': '/static/images/hp-officejet-9015e.jpg',
                    'specifications': 'Print Speed: 22 ppm black, 18 ppm color, Wireless, Auto Duplex, 35-page ADF',
                    'is_featured': True
                },
                {
                    'name': 'HP LaserJet Pro M404n Printer',
                    'description': 'Fast and reliable monochrome laser printer for office use.',
                    'price': 179.99,
                    'sku': 'HP-LJ-M404N-001',
                    'stock_quantity': 25,
                    'category_id': categories['Printers'].id,
                    'image_url': '/static/images/hp-laserjet-m404n.jpg',
                    'specifications': 'Print Speed: 38 ppm, Ethernet, Auto Duplex, 250-sheet input tray'
                },
                {
                    'name': 'HP Envy 6055e Wireless All-in-One Printer',
                    'description': 'Compact wireless printer perfect for home use with mobile printing.',
                    'price': 99.99,
                    'sku': 'HP-ENVY-6055E-001',
                    'stock_quantity': 35,
                    'category_id': categories['Printers'].id,
                    'image_url': '/static/images/hp-envy-6055e.jpg',
                    'specifications': 'Print Speed: 10 ppm black, 7 ppm color, Wireless, Mobile Printing, Compact Design'
                },
                
                # Accessories
                {
                    'name': 'HP 24" FHD Monitor',
                    'description': '24-inch Full HD monitor with IPS panel for crisp and clear visuals.',
                    'price': 149.99,
                    'sku': 'HP-MON-24-001',
                    'stock_quantity': 50,
                    'category_id': categories['Accessories'].id,
                    'image_url': '/static/images/hp-24-monitor.jpg',
                    'specifications': '24" IPS Panel, 1920x1080 Resolution, 75Hz Refresh Rate, HDMI/VGA Inputs',
                    'is_featured': True
                },
                {
                    'name': 'HP Wireless Mouse',
                    'description': 'Ergonomic wireless mouse with long battery life and precise tracking.',
                    'price': 29.99,
                    'sku': 'HP-MOUSE-WL-001',
                    'stock_quantity': 100,
                    'category_id': categories['Accessories'].id,
                    'image_url': '/static/images/hp-wireless-mouse.jpg',
                    'specifications': '2.4GHz Wireless, 1600 DPI, 18-month battery life, Ergonomic design'
                },
                {
                    'name': 'HP USB-C Dock',
                    'description': 'Universal USB-C docking station for connecting multiple devices.',
                    'price': 199.99,
                    'sku': 'HP-DOCK-USBC-001',
                    'stock_quantity': 20,
                    'category_id': categories['Accessories'].id,
                    'image_url': '/static/images/hp-usbc-dock.jpg',
                    'specifications': 'USB-C 3.1, HDMI 2.0, DisplayPort 1.4, 4x USB-A 3.0, Ethernet, 90W Power Delivery'
                },
                {
                    'name': 'HP Mechanical Gaming Keyboard',
                    'description': 'RGB backlit mechanical keyboard designed for gaming and productivity.',
                    'price': 89.99,
                    'sku': 'HP-KB-MECH-001',
                    'stock_quantity': 30,
                    'category_id': categories['Accessories'].id,
                    'image_url': '/static/images/hp-gaming-keyboard.jpg',
                    'specifications': 'Mechanical Blue Switches, RGB Backlighting, Anti-ghosting, USB-A Connection'
                }
            ]
            
            for product_data in products_data:
                product = Product(**product_data)
                db.add(product)
            
            # Create admin user
            auth_service = AuthService(db)
            admin_user = auth_service.create_user(
                username="admin",
                email="admin@hpstore.com",
                password="admin123",
                full_name="Store Administrator"
            )
            
            if admin_user:
                admin_user.is_admin = True
                db.commit()
            
            db.commit()
            app_logger.info("Sample data created successfully")
            
    except Exception as e:
        app_logger.error(f"Error creating sample data: {e}")
        raise

if __name__ == "__main__":
    create_sample_data()