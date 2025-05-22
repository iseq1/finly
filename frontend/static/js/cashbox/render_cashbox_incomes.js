export function renderIncomes(incomes) {
    const tbody = document.querySelector("#income-table tbody");
    tbody.innerHTML = "";
  
    incomes.forEach(income => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${income.category.name}</td>
        <td>${income.subcategory.name}</td>
        <td>${income.amount}</td>
        <td>${income.transacted_at}</td>
      `;
      tbody.appendChild(tr);
    });
  }
  