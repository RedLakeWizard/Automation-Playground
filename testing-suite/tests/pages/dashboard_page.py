from playwright.sync_api import Page, expect

class DashboardPage:
    URL = "http://localhost:5000/account/dashboard"

    def __init__(self, page: Page):
        self.page = page
        self.topbar_title = page.locator("header.topbar h1")
        self.logout_link = page.locator("#logout-link")
        self.shop_button = page.locator('a.btn[href="/shop?page=1"]')
        self.cart_button = page.locator('a.btn[href="/cart"]')

    def assert_on_page(self, username: str | None = None):
        expect(self.topbar_title).to_be_visible()
        if username:
            expect(self.topbar_title).to_contain_text(username)

    def logout(self):
        self.logout_link.click()
