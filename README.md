# EasyMarket

EasyMarket is a student-focused marketplace that enables students to buy and sell products within their school community.

The platform provides a dedicated marketplace where students can discover items, connect with sellers, manage listings, and conduct transactions within a familiar community.

## Features

* **User Accounts** — Students can register, authenticate, and manage their accounts.
* **Product Listings** — Sellers can create listings with product details, pricing, categories, and images.
* **Search & Filtering** — Buyers can search the marketplace and filter products by category.
* **Buyer & Seller Experience** — Users can browse available products and manage their own listings.
* **Real-Time Support** — Built with Django Channels and Daphne for asynchronous and real-time functionality.
* **API Support** — REST API functionality powered by Django REST Framework.
* **Authentication & Security** — Includes JWT and OTP-related authentication capabilities.
* **Payment Integration** — Includes support for M-Pesa integration through Daraja.

## Tech Stack

* **Backend:** Python, Django 5
* **API:** Django REST Framework
* **ASGI:** Django Channels, Daphne
* **Database:** PostgreSQL
* **Caching / Messaging:** Redis
* **Authentication:** JWT, Django OTP
* **Payments:** M-Pesa / Daraja
* **Frontend:** Django Templates
* **Media:** Pillow

## Getting Started

### Prerequisites

Make sure you have the following installed:

* Python 3
* pip
* Git
* PostgreSQL
* Redis

### Installation

1. Clone the repository:

```bash
git clone https://github.com/trent130/EasyMarket.git
cd EasyMarket
```

2. Create a virtual environment:

```bash
python -m venv .venv
```

3. Activate the virtual environment:

**Linux / macOS**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

4. Install the dependencies:

```bash
pip install -r requirements.txt
```

5. Configure the required environment variables for your local environment.

6. Apply database migrations:

```bash
python manage.py migrate
```

7. Start the development server:

```bash
python manage.py runserver
```

The application will be available at:

```text
http://localhost:8000
```

### Running with Daphne

Because EasyMarket supports ASGI, you can also run the application using Daphne:

```bash
daphne -p 8000 students.asgi:application
```

Then visit:

```text
http://localhost:8000
```

## Project Structure

EasyMarket is built around Django's application architecture, separating marketplace functionality, user management, persistence, authentication, and supporting services into maintainable components.

## Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch:

```bash
git checkout -b feature/my-feature
```

3. Commit your changes:

```bash
git commit -m "Add my feature"
```

4. Push your branch:

```bash
git push origin feature/my-feature
```

5. Open a pull request.

For larger changes, consider opening an issue first to discuss the proposed implementation.

## License

This project is distributed under the MIT License. See the `LICENSE` file for details.

## Author

**Lawrence Nyongesa**

* GitHub: `trent130`
* Website: `nyyongesa.me`
* Email: `nyyongesa@gmail.com`

## Repository

EasyMarket is available on GitHub under `trent130/EasyMarket`.
