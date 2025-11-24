from playwright.sync_api import Page, expect


def login(page: Page, username: str = "test_user", password: str = "secret123"):
    page.goto("http://localhost:5000/auth/login")
    page.fill("#username", username)
    page.fill("#password", password)
    page.click("#login-btn")
    expect(page).to_have_url("http://localhost:5000/account/dashboard")


def test_shop_listing_and_add_to_cart(page: Page):
    login(page)
    page.goto("http://localhost:5000/shop")
    expect(page.locator(".product-card").first).to_be_visible()

    first_product = page.locator(".product-card").first
    first_product.locator("text=Add to cart").click()
    expect(page.get_by_text("added to cart")).to_be_visible()

    page.goto("http://localhost:5000/cart")
    expect(page.locator("table")).to_be_visible()


def test_cart_update_and_clear(page: Page):
    login(page)
    page.goto("http://localhost:5000/shop")
    page.locator(".product-card").first.locator("text=Add to cart").click()

    page.goto("http://localhost:5000/cart")
    qty_input = page.locator(".cart-qty-input").first
    qty_input.fill("2")
    page.locator("form.cart-update-form").first.locator("text=Update").click()
    expect(qty_input).to_have_value("2")

    page.locator("text=Clear cart").click()
    expect(page.get_by_text("Your cart is empty")).to_be_visible()
