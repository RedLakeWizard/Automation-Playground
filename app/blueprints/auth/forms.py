from dataclasses import dataclass
from typing import Optional

from flask import Request


@dataclass
class LoginForm:
    username: str = ""
    password: str = ""

    @classmethod
    def from_request(cls, request: Request) -> "LoginForm":
        return cls(
            username=(request.form.get("username") or "").strip(),
            password=request.form.get("password") or "",
        )

    def is_valid(self) -> bool:
        return bool(self.username and self.password)


@dataclass
class RegisterForm:
    username: str = ""
    email: str = ""
    password: str = ""
    confirm_password: str = ""

    @classmethod
    def from_request(cls, request: Request) -> "RegisterForm":
        return cls(
            username=(request.form.get("username") or "").strip(),
            email=(request.form.get("email") or "").strip(),
            password=request.form.get("password") or "",
            confirm_password=request.form.get("confirm_password") or "",
        )

    def passwords_match(self) -> bool:
        return self.password == self.confirm_password and bool(self.password)

    def is_valid(self) -> bool:
        return bool(self.username and self.email and self.passwords_match())
