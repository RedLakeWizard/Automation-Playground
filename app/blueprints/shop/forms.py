from dataclasses import dataclass

from flask import Request


@dataclass
class ProductSearchForm:
    query: str = ""

    @classmethod
    def from_request(cls, request: Request) -> "ProductSearchForm":
        return cls(query=(request.args.get("q") or "").strip())
