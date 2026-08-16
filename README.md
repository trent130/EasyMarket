# EasyMarket

EasyMarket is a student marketplace where students can buy and sell items within their school community.

## Features

- CustomUser Registration: Students can create an account to start buying or selling.
- Item Listing: Sellers can list their items with details and images.
- Search and Filter: Buyers can search for items and filter results based on categories.
- Secure Transactions: The platform ensures secure transactions between buyers and sellers.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites
- git config --global http.postBuffer 524288000

- Python 3.14
- [uv](https://docs.astral.sh/uv/)
- sql

### Installation

1. Clone the repo
   ```
   git clone https://github.com/trent130/Easymarket.git
   ```
2. Create a Python 3.14 environment and install packages
   ```
   uv venv --python 3.14 easymarket
   source easymarket/bin/activate
   uv pip install -r requirements.txt -r test-requirements.txt
   ```

## Usage

After setting up, you can run `python manage.py runserver or daphne -p 8000 students.asgi: application` to start the application. Open your browser and visit `http://localhost:8000/

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

trent130 - lawrencewafula408@gmail.com - email

Project Link: [https://github.com/trent130/Easymarket.git](https://github.com/trent130/Easymarket.git)

## Acknowledgements

- [greyworm](http://127.0.0.1:8000)
