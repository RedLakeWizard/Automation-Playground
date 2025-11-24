# Retrospective & Future Thoughts

## Current State Reflections
- Everything is login-gated, which fits the QA focus on authentication but requires every flow to handle auth first.
- Checkout is parked as “work in progress”, so purchase completion isn’t testable yet; the WIP placeholder protects users from a broken flow.
- Catalogue, cart, and admin pieces are functional and support stock-aware carts and admin product management.
- Hardcoded users simplify testing but mean DB rows are seeded without real passwords; fine for the current state of the app but I want to add a security update later on.

## What Went Well
- Clear separation of roles: admin redirect works; admin console and custom admin panel both render.
- Stock enforcement is respected in add/update cart logic.
- Admin product forms now capture quantity/availability and allow edits.
- UI uses consistent formatting and flashes for feedback.

## What Needs Improvement
- Checkout must be restored for end-to-end purchase testing.
- Pagination/counts don’t match the original US7 story, UI is currently not how I conceptualized it. Since I'm currently going with form over function, this will have to serve for now until I'm more capable in front-end.
- Data seeding is manual; tests depend on hand-crafted fixtures.
- Global login gate may block public browsing if we ever want to simulate guest flows.

## Future Plans
- Re-enable checkout from the archived WIP, add payment stub, and cover it with tests.
- Align catalogue pagination and seeding with user stories.
- Add DB seeding fixtures and optional API helpers for test setup.
- Consider loosening login gating for catalogue-only browsing if required by future stories.
- Expand Playwright coverage (shop/cart/admin/order flows) and add CI integration.
- Include hand-made and documented defects to showcase high integrity bug reporting
- Include GHERKIN tests for non-technical users.
- Refine the product model to include wizard familiars by using the cat & dog APIs.

## How I’ll Proceed
- Start with coding automated data seeding and migration scripts and fixing pagination to match user-stories.
- Reintroduce checkout once stable, then grow the test suite to cover it.
- Keep refining fixtures and page objects to make tests faster to write and maintain.


