from playwright.sync_api import Page, expect


def login(page: Page, username: str = "test_user", password: str = "secret123"):
    page.goto("http://localhost:5000/auth/login")
    page.fill("#username", username)
    page.fill("#password", password)
    page.click("#login-btn")
    expect(page).to_have_url("http://localhost:5000/account/dashboard")


def test_checkout_wip_message(page: Page):
    login(page)
    page.goto("http://localhost:5000/checkout")
    expect(page.get_by_text("work in progress")).to_be_visible()
    page.click("text=Proceed")
    expect(page.get_by_text("work in progress")).to_be_visible()
