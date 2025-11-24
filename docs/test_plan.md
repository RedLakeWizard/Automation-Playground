# Test Plan

## Features to Test
- Auth: login (user/admin), redirects, forced login on protected routes, logout.
- Catalogue: listing with pagination/sort/filter/search; product detail; add-to-cart; out-of-stock handling.
- Cart: view items, badge count, update/remove, clear cart, totals (subtotal/tax/shipping).
- Admin: dashboard access (admin only), product add/edit (price/compare/quantity/availability/image), orders listing, Flask-Admin console rendering.
- Checkout (current state): WIP page rendering and redirect back to cart on submit.
- Stock enforcement across add/update.

## Test Data
- Hardcoded users: `test_user/secret123` (customer), `admin/adminpass` (admin).
- Seed products/categories with known SKUs and stock; include at least one out-of-stock item.
- Optionally set `PER_PAGE=3` and seed 9 products to align with user stories if desired.

## Test Types
- E2E UI: Playwright+pytest.
- Basic data checks: via UI assertions (no API layer tests for now).

## Entry/Exit Criteria
- Entry: app running locally, seeded data, browsers available.
- Exit: all planned tests executed; failures triaged.

## Schedule / Order
1) Auth flows
2) Catalogue listing/detail/add-to-cart
3) Cart behaviors (update/remove/clear/totals)
4) Admin flows (access, product add/edit, orders, console render)
5) Checkout WIP behavior
6) Stock enforcement regression checks

## Owners
- Alejandro C.R. (Red Lake Wizard) - QA Tester

## Risks/Mitigations
- Checkout WIP: assert the WIP message; adjust when checkout is re-enabled.
- Login gating: every test must log in first; use fixtures to handle auth setup.
- Data drift: reseed DB as part of test setup to keep expectations stable.
