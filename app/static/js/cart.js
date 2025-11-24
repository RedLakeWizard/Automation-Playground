document.addEventListener("DOMContentLoaded", () => {
  const updateForms = document.querySelectorAll(".cart-update-form");
  const removeForms = document.querySelectorAll(".cart-remove-form");

  async function handleSubmit(event, url) {
    event.preventDefault();
    const form = event.target;
    const quantityInput = form.querySelector(".cart-qty-input");
    const quantity = quantityInput ? Number(quantityInput.value) : 0;

    try {
      const resp = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({ quantity }),
      });
      const data = await resp.json();
      if (!data.success) {
        alert(data.message || "Unable to update cart.");
      }
      window.location.reload();
    } catch (err) {
      console.error(err);
      window.location.reload();
    }
  }

  updateForms.forEach((form) => {
    form.addEventListener("submit", (e) => {
      const productId = form.dataset.productId;
      handleSubmit(e, `/cart/update/${productId}`);
    });
  });

  removeForms.forEach((form) => {
    form.addEventListener("submit", (e) => {
      const productId = form.dataset.productId;
      handleSubmit(e, `/cart/remove/${productId}`);
    });
  });
});
