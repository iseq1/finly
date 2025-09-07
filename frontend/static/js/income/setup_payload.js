export function setupIncomeFormSubmission() {
  const user_cashbox_id = parseInt(document.getElementById("user_cashbox").value) || 0;
  const category_id = parseInt(document.getElementById("category").value) || 0;
  const subcategory_id = parseInt(document.getElementById("subcategory").value) || 0;
  const amount = parseFloat(document.getElementById("amount").value) || 0;
  const comment = document.getElementById("comment").value || "";
  const source = document.getElementById("source").value || "";
  const dateInput = document.getElementById("transacted_at").value || "";

  let transacted_at = null;
  const [day, month, year] = dateInput.split(".");
  if (day && month && year) {
    transacted_at = new Date(`${year}-${month}-${day}T00:00:00`).toISOString();
  }

  return {
    user_cashbox_id,
    category_id,
    subcategory_id,
    amount,
    comment,
    source,
    transacted_at,
  };
}
