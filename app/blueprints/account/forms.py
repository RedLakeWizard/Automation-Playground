from dataclasses import dataclass

from flask import Request


@dataclass
class ProfileForm:
    display_name: str = ""
    email: str = ""
    role: str = ""

    @classmethod
    def from_request(cls, request: Request) -> "ProfileForm":
        return cls(
            display_name=(request.form.get("display_name") or "").strip(),
            email=(request.form.get("email") or "").strip(),
            role=(request.form.get("role") or "").strip(),
        )

    def is_valid(self) -> bool:
        return bool(self.display_name and self.email)
