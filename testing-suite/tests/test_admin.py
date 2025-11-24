from playwright.sync_api import Page, expect


def admin_login(page: Page):
    page.goto("http://localhost:5000/auth/login")
    page.fill("#username", "admin")
    page.fill("#password", "adminpass")
    page.click("#login-btn")
    expect(page).to_have_url("http://localhost:5000/admin/dashboard")


def test_admin_products_page(page: Page):
    admin_login(page)
    page.goto("http://localhost:5000/admin/products")
    expect(page.get_by_text("Products")).to_be_visible()
    expect(page.locator("table")).to_be_visible()


def test_admin_console_renders(page: Page):
    admin_login(page)
    page.goto("http://localhost:5000/admin/console/")
    expect(page.get_by_text("Admin Console")).to_be_visible()
