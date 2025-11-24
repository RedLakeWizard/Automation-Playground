# Automation-Playground
*A fantasy-themed Flask web application built as a personal QA/automation testing playground.*

---

## 📽️ Demo GIF of Playwright in action


![Image](https://github.com/user-attachments/assets/1b12617a-a077-4d09-bb59-5346e8533fee)

---

## 🧙 Overview

**Automation-Playground** is a Flask web application created as a controlled environment for practicing manual testing, automation, UI testing, and QA workflows.

This project is born due to a personal need for a safe space to practice back end verification in a safe environment.

All routes are gated behind login by design.

---

## 📦 Current Capabilities (Accurate to Current Build)

### 🔐 **Authentication**
- Session-based login system  
- Two pre-seeded test accounts:
  - **Customer:** `test_user / secret123`
  - **Admin:** `admin / adminpass`
- Login required for:
  - Shop browsing  
  - Cart actions  
  - Checkout  
  - Admin dashboard  

### 🛒 **Potions / Products Catalogue**
Accessible at `/shop`:
- Filtering  
- Sorting  
- Search  
- Product detail pages via slug or ID  
- Prices stored internally as **cents** (integer math — no floats)  
- Add-to-cart checks **stock availability**

### 🧺 **Cart System**
- Session + database-backed  
- Update quantities  
- Remove items  
- Clear cart  
- Total calculation
- Cart item count displayed in navbar

### 💳 **Checkout (WIP)**
- `/checkout` currently shows a **“work in progress”** page  
- Submitting the form redirects back to cart with a success flash message

### 🛠️ **Admin Dashboard**
- Custom admin pages: products, orders, users  
- Flask-Admin console available at:  
  ```
  /admin/console/
  ```
- Product management includes:
  - Add/edit/delete products  
  - Set price, compare price, quantity, availability  
  - Image upload support  

### 👤 **Account System**
- User dashboard  
- Profile overview  
- Basic user information display  

---

## ⚙️ Tech Stack

### Backend
- Python 3  
- Flask  
- SQLAlchemy ORM  
- Flask-Admin  
- Flask-WTF  
- Flask-Mail (configured but currently unavailable) 
- SQLite

### Frontend
- Jinja2 templates  
- Bootstrap 5  
- CSS3

### Testing
- **pytest**  
- **Playwright**  
- Documentation available under `docs/`

---

## 📁 Project Structure

```
app/
  blueprints/            # auth, shop, cart, checkout (WIP), account, admin
  models/                # User, Product, Category, Order, OrderItem, CartItem, Review
  services/              # cart and order helper logic
  templates/             # base, shop, cart, admin, account, checkout (WIP)
  static/                # css/js/images
docs/                    # test plan, test strategy, known issues, retrospective
testing-suite/tests/     # pytest + Playwright tests
run.py
requirements.txt
```

---

## 🚀 Running the Application

### 1. Create virtual environment
```bash
python -m venv .venv
```

### 2. Activate environment
**Linux/macOS**
```bash
source .venv/bin/activate
```
**Windows**
```bash
.venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python run.py
```

Visit the app at:
```
http://localhost:5000
```

### 5. Log in using test accounts
- **Customer:** `test_user / secret123`  
- **Admin:** `admin / adminpass`

---

## 🧪 Running Playwright Tests (pytest)

### 1. Install Playwright browsers
```bash
playwright install
```

### 2. Run all tests
```bash
pytest testing-suite/tests
```

### 3. Run in headed mode (with browser window)
```bash
pytest --headed --browser=firefox
```

---

## 🐛 Known Constraints

- Checkout is **disabled** and intentionally incomplete  
- Auth uses seeded credentials; passwords are created programmatically  
- Some admin and order flows are overly simplified due to the current scope
- Several inconsistencies in product edition
---

## 🛣️ Roadmap

Planned features include:
- Cat + Dog API integration through "familiars" product
- Fully functional checkout flow  
- Email order confirmations for OTP validation 
- Review system 
- Additional admin reporting tools  
- API endpoints (for Postman / API test automation)
- Docker deployment setup
- Cool medieval fantasy UI!!

---

## 📜 License
This project is released under the **MIT License**.
