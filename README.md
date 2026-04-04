# CartFlow — Full Stack Django Shopping Platform 🛒

A full-stack e-commerce web application built with Django, simulating a real-world online shopping experience with secure authentication, a persistent cart, and product search.

---

## The Problem It Solves

Most beginner shopping apps lose cart data the moment a user refreshes the page. **CartFlow solves this** using Django Sessions — items stay in the cart across page reloads, just like a production e-commerce platform.

---

## Features

- **Secure User Authentication** — Full Sign-up, Login, and Logout system using Django's built-in auth
- **Persistent Shopping Cart** — Cart data survives page refresh using Django Sessions
- **Dynamic Product Search** — Filter products in real time without reloading the page
- **Product Listing** — Clean browsable product catalogue with individual detail pages
- **Add / Remove Cart Items** — Full cart management with quantity control
- **Responsive UI** — Mobile-friendly design built with Bootstrap 5

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django |
| Frontend | Bootstrap 5, Django Templates |
| Database | PostgreSQL |
| Auth | Django built-in authentication |
| Session Management | Django Sessions |

---

## Screenshots

> _Add screenshots here — home page, product listing, cart page, and login screen._
> _Tip: Create a `/screenshots` folder in the repo and use:_
> `![Home](screenshots/home.png)`

---

## Getting Started

```bash
# 1. Clone the repository
git clone https://github.com/etishagod/cartflow-django-ecommerce.git
cd cartflow-django-ecommerce

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up PostgreSQL database
# Create a database named 'cartflow_db' in PostgreSQL
# Update DB credentials in settings.py

# 5. Apply migrations
python manage.py migrate

# 6. Create superuser (for admin panel)
python manage.py createsuperuser

# 7. Run the server
python manage.py runserver
```

Open your browser at `http://127.0.0.1:8000`

---

## Project Structure

```
cartflow/
├── manage.py
├── requirements.txt
├── cartflow/                   # Project settings
│   ├── settings.py
│   └── urls.py
├── store/                      # Main app
│   ├── models.py               # Product model
│   ├── views.py                # Cart, Search, Auth logic
│   ├── urls.py
│   └── templates/
│       ├── home.html           # Product listing
│       ├── cart.html           # Cart page
│       ├── login.html
│       └── signup.html
└── static/                     # CSS, JS, Images
```

---

## How the Persistent Cart Works

```python
# Items are stored in Django's session — not in the database
# This means the cart survives page refresh automatically

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + 1
    request.session['cart'] = cart
    return redirect('cart')
```

> This is the core technical insight of the project — session-based state management without requiring a logged-in user.

---

## What I Learned

- Implementing end-to-end user authentication with Django
- Using Django Sessions to persist state across HTTP requests
- Connecting Django to PostgreSQL for production-grade data storage
- Building search/filter functionality using Django ORM queries
- Structuring a full-stack project with clean separation of concerns

---

## Future Improvements

- [ ] Add payment gateway integration (Razorpay / Stripe)
- [ ] Build REST API using Django REST Framework
- [ ] Add product categories and filters
- [ ] Implement order history and invoice generation
- [ ] Deploy live on Railway or Render
- [ ] Add product ratings and reviews

---

## Author

**Etisha Godle**
- GitHub: [@etishagod](https://github.com/etishagod)
- LinkedIn: [Etisha Godle](https://www.linkedin.com/in/etisha-godle-636744275)
- Email: etishagodle14@gmail.com

---

> Built with Django, Python & PostgreSQL | Open to feedback and collaboration
