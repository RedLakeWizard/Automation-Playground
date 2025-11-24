from playwright.sync_api import Page, expect

class LoginPage:
    URL = "http://localhost:5000/auth/login"

    def __init__(self, page: Page):
        self.page = page
        self.username_input = page.locator("#username")
        self.password_input = page.locator("#password")
        self.login_button = page.locator("#login-btn")
        self.error_message = page.locator("#login-error")
        self.instructions_box = page.locator("#login-instructions")

    def open(self):
        self.page.goto(self.URL)

    def login(self, username: str, password: str):
        self.username_input.fill(username)
        #timeouts for visual demonstration purposes
        # self.page.wait_for_timeout(3000)
        self.password_input.fill(password)
        # self.page.wait_for_timeout(3000)
        self.login_button.click()

    def assert_on_page(self):
        expect(self.username_input).to_be_visible()
        expect(self.password_input).to_be_visible()
        expect(self.login_button).to_be_visible()
