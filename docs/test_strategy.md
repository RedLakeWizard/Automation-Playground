# Test Strategy

## Scope
- Cover core user flows: authentication, catalogue browsing, cart management, admin management, and current checkout behavior (WIP notice).
- Environments: local Flask app with SQLite; UI tests via Playwright+pytest.
- Users: hardcoded `test_user` (customer) and `admin`.

## Objectives
- Validate that login gating works consistently and roles redirect correctly.
- Ensure catalogue listing, product detail, and cart behaviors align with current implementation.
- Verify admin product/order views work and respect stock/availability updates.
- Acknowledge checkout is currently WIP; assert the WIP path until real checkout is restored.

## Approach
- End-to-end UI tests using Playwright page objects and pytest.
- Deterministic test data seeding (products, categories, stock levels).
- Session-based auth; prefer UI login for full coverage.
- Assertions prioritize functional outcomes (redirects, flashes, badge counts, stock limits).

## In/Out of Scope
- In: auth flows, catalogue, cart, admin CRUD, current checkout WIP behavior.
- Out (for now): real payment processing, email delivery, API-level tests, performance, penetration tests.

## Risks
- Admin console view duplication risk on reload (mitigated by reset in app init).

## Tooling
- pytest, pytest-playwright, Playwright.
- SQLite for persistence; optional fixtures to reset DB.

## Reporting
- Pytest output
