# HP Ecommerce Store

A complete ecommerce platform for HP products built with NiceGUI, FastAPI, and SQLAlchemy.

## Features

### 🛍️ Core Ecommerce Features
- **Product Catalog**: Browse HP laptops, desktops, printers, and accessories
- **Category Navigation**: Organized product categories with filtering
- **Product Search**: Search products by name, description, or specifications
- **Shopping Cart**: Add/remove items, update quantities, persistent cart
- **User Authentication**: Secure user registration and login
- **Order Management**: Complete checkout process with order tracking
- **Inventory Management**: Real-time stock tracking and updates

### 🎨 User Interface
- **Modern Design**: Clean, responsive UI with HP branding
- **Product Cards**: Attractive product displays with images and details
- **Interactive Cart**: Real-time cart updates and item management
- **Mobile Responsive**: Optimized for desktop and mobile devices
- **Intuitive Navigation**: Easy-to-use category browsing and search

### 🔧 Technical Features
- **NiceGUI Frontend**: Modern Python-based UI framework
- **FastAPI Backend**: High-performance API with automatic documentation
- **SQLAlchemy V2**: Modern ORM with type hints and relationships
- **Pydantic V2**: Data validation and serialization
- **JWT Authentication**: Secure token-based authentication
- **SQLite Database**: Lightweight database for development

## Quick Start

### Prerequisites
- Python 3.9 or higher
- pip (Python package installer)

### Installation

1. **Clone or create the project directory**:
```bash
mkdir hp-ecommerce-store
cd hp-ecommerce-store
```

2. **Create a virtual environment**:
```bash
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env file with your configuration
```

5. **Run the application**:
```bash
python main.py
```

6. **Open your browser** and navigate to:
   - **Store**: http://127.0.0.1:8080
   - **API Documentation**: http://127.0.0.1:8080/docs

## Default Credentials

The application creates a default admin user:
- **Email**: admin@hpstore.com
- **Password**: admin123

## Project Structure

```
hp-ecommerce-store/
├── app/
│   ├── main.py                 # Main NiceGUI application
│   ├── core/                   # Core configuration and utilities
│   │   ├── config.py          # Application settings
│   │   ├── database.py        # Database configuration
│   │   ├── logging.py         # Logging setup
│   │   └── sample_data.py     # Sample product data
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py            # User model
│   │   ├── product.py         # Product and Category models
│   │   ├── cart.py            # Shopping cart models
│   │   └── order.py           # Order models
│   ├── services/               # Business logic layer
│   │   ├── auth_service.py    # Authentication service
│   │   ├── product_service.py # Product management
│   │   ├── cart_service.py    # Cart operations
│   │   └── order_service.py   # Order processing
│   ├── api/                    # FastAPI endpoints
│   │   ├── router.py          # API router configuration
│   │   └── __init__.py
│   └── static/                 # Static assets
│       ├── css/styles.css     # Custom styles
│       └── images/            # Product images
├── data/                       # Database files
├── logs/                       # Application logs
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## Sample Products

The application includes sample HP products:

### Laptops
- HP Pavilion 15.6" Laptop - $699.99
- HP Envy x360 13.3" 2-in-1 Laptop - $899.99
- HP Omen 16.1" Gaming Laptop - $1,299.99
- HP EliteBook 14" Business Laptop - $1,199.99

### Desktops
- HP Pavilion Desktop - $549.99
- HP Omen 45L Gaming Desktop - $1,599.99
- HP EliteDesk 800 G8 Mini - $899.99

### Printers
- HP OfficeJet Pro 9015e All-in-One - $199.99
- HP LaserJet Pro M404n - $179.99
- HP Envy 6055e Wireless All-in-One - $99.99

### Accessories
- HP 24" FHD Monitor - $149.99
- HP Wireless Mouse - $29.99
- HP USB-C Dock - $199.99
- HP Mechanical Gaming Keyboard - $89.99

## API Endpoints

The application provides a RESTful API:

- `GET /api/health` - Health check
- `GET /api/products` - List products
- `GET /api/products/{id}` - Get product details
- `GET /api/categories` - List categories
- `POST /api/cart/add` - Add item to cart
- `GET /api/cart` - Get cart contents
- `POST /api/orders` - Create order
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

## Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# Application
APP_NAME=HP Ecommerce Store
DEBUG=True
HOST=127.0.0.1
PORT=8080

# Database
DATABASE_URL=sqlite:///./data/hp_store.db

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
```

### Database

The application uses SQLite by default for easy setup. For production, you can configure PostgreSQL or MySQL by updating the `DATABASE_URL`.

## Development

### Adding New Products

Products are managed through the `ProductService` class. You can:

1. Add products programmatically in `sample_data.py`
2. Use the admin interface (future feature)
3. Import from CSV/JSON files (future feature)

### Customizing the UI

The UI is built with NiceGUI and can be customized by:

1. Modifying the page functions in `app/main.py`
2. Updating CSS styles in `app/static/css/styles.css`
3. Adding new components and layouts

### Extending the API

Add new API endpoints by:

1. Creating new routers in `app/api/`
2. Adding business logic in `app/services/`
3. Including routers in the main application

## Deployment

### Production Considerations

1. **Environment Variables**: Set production values in `.env`
2. **Database**: Use PostgreSQL or MySQL for production
3. **Security**: Change default secret keys and passwords
4. **HTTPS**: Configure SSL/TLS certificates
5. **Static Files**: Use a CDN for static assets
6. **Monitoring**: Set up logging and monitoring

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["python", "main.py"]
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **Database Errors**: Check database file permissions
3. **Port Conflicts**: Change PORT in `.env` if 8080 is in use
4. **Module Not Found**: Run `pip install -r requirements.txt`

### Logging

Application logs are available in:
- Console output (when running)
- `logs/app.log` file

Set `LOG_LEVEL=DEBUG` in `.env` for detailed logging.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Check the logs for error messages
- Review the API documentation at `/docs`
- Ensure all dependencies are installed correctly
- Verify environment configuration

---

**HP Ecommerce Store** - A modern, full-featured ecommerce platform built with Python.