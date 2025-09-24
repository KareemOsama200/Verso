# Verso Store - E-Commerce Clothing Website

A full-featured e-commerce clothing website built with Django, featuring a modern, minimalist design inspired by contemporary fashion retail sites.

## 🌟 Features

### Customer Features
- **User Authentication**: Registration, login, password reset
- **Product Browsing**: Category-based navigation, search, filters
- **Product Details**: Multiple images, videos, size/color variants, reviews
- **Shopping Cart**: Add/remove items, quantity management
- **Checkout**: Multiple payment options (COD, Wallet, Stripe-ready)
- **Order Tracking**: View order history and status
- **Wishlist**: Save favorite products
- **Geolocation**: Map-based address selection using OpenStreetMap

### Admin/Staff Features
- **Role-Based Access**: Admin, Manager, Employee, Customer roles
- **Dashboard**: Sales analytics, recent orders, inventory status
- **Product Management**: Add/edit products, manage inventory
- **Order Management**: Process orders, update status
- **Customer Management**: View and manage customers
- **Staff Management**: Create and manage staff accounts with permissions
- **Data Export**: Export orders, products, customers to CSV

### Technical Features
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **SEO Optimized**: Meta tags, clean URLs, sitemap-ready
- **Security**: CSRF protection, secure password hashing, SQL injection prevention
- **Performance**: Optimized queries, caching-ready, static file compression
- **Scalable**: PostgreSQL-ready, media storage abstraction

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- pip (Python package manager)
- Virtual environment (recommended)

### Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd verso-store
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create admin user**
```bash
python manage.py create_admin
# Default credentials: admin/admin123
```

7. **Load sample data**
```bash
python manage.py seed_data
```

8. **Collect static files**
```bash
python manage.py collectstatic --noinput
```

9. **Run development server**
```bash
python manage.py runserver
```

Visit http://localhost:8000

## 📦 Initial Accounts

### Admin Account
- **Username**: admin
- **Password**: admin123
- **Role**: Administrator (full access)

### Staff Accounts (created by seed_data)
- **Manager**: manager/manager123
- **Employee**: employee/employee123

### Sample Customers (created by seed_data)
- john_doe/customer123
- jane_smith/customer123
- bob_wilson/customer123

## 🌐 PythonAnywhere Deployment

### Step 1: Create PythonAnywhere Account
1. Sign up at [PythonAnywhere](https://www.pythonanywhere.com)
2. Choose a free or paid plan

### Step 2: Upload Code
1. Open a Bash console on PythonAnywhere
2. Clone your repository:
```bash
git clone https://github.com/yourusername/verso-store.git
cd verso-store
```

### Step 3: Set Up Virtual Environment
```bash
mkvirtualenv --python=/usr/bin/python3.11 verso-env
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
1. Create `.env` file:
```bash
cp .env.example .env
nano .env
```

2. Update settings:
```
DEBUG=False
SECRET_KEY=your-production-secret-key-here
ALLOWED_HOSTS=yourusername.pythonanywhere.com
```

### Step 5: Database Setup
```bash
python manage.py migrate
python manage.py create_admin
python manage.py seed_data  # Optional
```

### Step 6: Static Files Configuration
```bash
python manage.py collectstatic --noinput
```

### Step 7: Web App Configuration

1. Go to Web tab in PythonAnywhere dashboard
2. Create new web app
3. Choose "Manual configuration" with Python 3.11
4. Set source code directory: `/home/yourusername/verso-store`

### Step 8: WSGI Configuration
Edit the WSGI configuration file:
```python
import os
import sys

# Add your project directory to the sys.path
project_home = '/home/yourusername/verso-store'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variable to tell django where your settings.py is
os.environ['DJANGO_SETTINGS_MODULE'] = 'verso.settings'

# Activate virtual environment
activate_this = '/home/yourusername/.virtualenvs/verso-env/bin/activate_this.py'
with open(activate_this) as f:
    exec(f.read(), {'__file__': activate_this})

# Import django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Step 9: Static Files Mapping
In Web tab, set up static files:
- URL: `/static/`
- Directory: `/home/yourusername/verso-store/staticfiles`
- URL: `/media/`
- Directory: `/home/yourusername/verso-store/media`

### Step 10: Reload Web App
Click "Reload" button in Web tab

### Step 11: Scheduled Tasks (Optional)
Set up scheduled tasks for:
- Database backups
- Data exports
- Email reports

## 📁 Project Structure

```
verso-store/
├── accounts/           # User authentication and profiles
├── products/           # Product catalog management
├── orders/            # Cart and order processing
├── dashboard/         # Admin dashboard
├── templates/         # HTML templates
├── static/            # CSS, JS, images
├── media/             # User uploads
├── data/              # Data exports and backups
├── verso/             # Project settings
├── manage.py          # Django management script
├── requirements.txt   # Python dependencies
└── README.md         # Documentation
```

## 💾 Data Storage Layout

```
media/
├── products/
│   └── <product_id>/
│       ├── images/
│       └── videos/
├── profiles/          # User profile images
└── brands/           # Brand logos

data/
├── customers/        # Customer data exports
├── orders/          # Order data exports
└── exports/         # General exports
```

## 🔧 Management Commands

```bash
# Create admin user
python manage.py create_admin --username admin --password admin123

# Seed database with sample data
python manage.py seed_data

# Export data
python manage.py export_orders
python manage.py export_products
python manage.py export_customers
```

## 🧪 Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test products
python manage.py test orders

# With coverage
coverage run --source='.' manage.py test
coverage report
```

## 🔒 Security Considerations

1. **Change default passwords** immediately after deployment
2. **Set strong SECRET_KEY** in production
3. **Enable HTTPS** on PythonAnywhere (included in paid plans)
4. **Regular backups** of database and media files
5. **Monitor logs** for suspicious activity

## 🎨 Design System

### Color Palette
- **Primary**: #1a1a1a (Near black)
- **Secondary**: #f5f5f5 (Light gray)
- **Accent**: #d4af37 (Gold)
- **Danger**: #ef4444 (Red)
- **Success**: #10b981 (Green)
- **Info**: #3b82f6 (Blue)

### Typography
- **Font**: Inter (Google Fonts)
- **Headings**: Bold, varied sizes
- **Body**: Regular, 16px base

### Components
- Modern card-based layout
- Hover animations
- Smooth transitions
- Mobile-responsive navigation

## 📝 Environment Variables

Required environment variables (see `.env.example`):

```
SECRET_KEY=your-secret-key
DEBUG=True/False
ALLOWED_HOSTS=localhost,yourdomain.com
DATABASE_URL=postgresql://user:pass@localhost/dbname
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
STRIPE_PUBLIC_KEY=pk_test_xxx
STRIPE_SECRET_KEY=sk_test_xxx
```

## 🚀 Production Checklist

- [ ] Change all default passwords
- [ ] Set DEBUG=False
- [ ] Configure proper ALLOWED_HOSTS
- [ ] Set up PostgreSQL database
- [ ] Configure email backend
- [ ] Set up media file storage (S3 or similar)
- [ ] Enable HTTPS
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline

## 🤝 API Integration

### Payment Gateways
- **Stripe**: Set STRIPE_PUBLIC_KEY and STRIPE_SECRET_KEY
- **PayPal**: Configure in payment settings
- **Test Mode**: Use "test" payment method for development

### Maps
- **OpenStreetMap**: No API key required
- **Mapbox**: Optional, set MAPBOX_TOKEN for enhanced features

## 📊 Analytics Integration

To add analytics:
1. Google Analytics: Add tracking code to base template
2. Facebook Pixel: Add pixel code to base template
3. Custom events: Use Django signals for tracking

## 🐛 Troubleshooting

### Common Issues

1. **Static files not loading**
   - Run `python manage.py collectstatic`
   - Check STATIC_ROOT and STATIC_URL settings

2. **Database errors**
   - Run `python manage.py migrate`
   - Check database connection settings

3. **Media files not uploading**
   - Check MEDIA_ROOT directory permissions
   - Ensure directory exists

4. **Email not sending**
   - Verify EMAIL_* settings
   - Check firewall/security settings

## 📚 Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [PythonAnywhere Help](https://help.pythonanywhere.com/)
- [Tailwind CSS](https://tailwindcss.com/docs)

## 📄 License

This project is provided as-is for educational and commercial use.

## 👥 Support

For issues or questions:
- Create an issue in the repository
- Contact: support@verso-store.com

## 🎯 Future Enhancements

- [ ] Product recommendations
- [ ] Advanced search with filters
- [ ] Social media login
- [ ] Multi-language support
- [ ] PWA features
- [ ] Real-time chat support
- [ ] Inventory tracking system
- [ ] Advanced analytics dashboard
- [ ] Email marketing integration
- [ ] Mobile app API

---

**Version**: 1.0.0  
**Last Updated**: September 2025  
**Built with**: Django 4.2+, Python 3.11, Tailwind CSS