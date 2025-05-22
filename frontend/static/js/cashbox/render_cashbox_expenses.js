export function renderExpenses(expenses) {
    const tbody = document.querySelector("#expense-table tbody");
    tbody.innerHTML = "";
  
    expenses.forEach(expense => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${expense.category.name}</td>
        <td>${expense.subcategory.name}</td>
        <td>${expense.amount}</td>
        <td>${expense.transacted_at}</td>
      `;
      tbody.appendChild(tr);
    });
  }
  