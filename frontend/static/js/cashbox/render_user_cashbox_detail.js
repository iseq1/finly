export function renderCashboxDetail(data) {
  const ucbl = document.getElementById("ucbl");
  if (!ucbl) return;

  ucbl.innerHTML = "";

  const fields = {
    "Наименование": data.cashbox.name,
    "Тип": data.cashbox.type.name,
    "Провайдер": data.cashbox.provider.name,
    "Баланс": data.balance,
    "Валюта": data.cashbox.currency,
    "Кастомное наименование": data.custom_name,
    "Заметка": data.note,
  };

  for (const [label, value] of Object.entries(fields)) {
    const li = document.createElement("li");
    li.innerHTML = `<strong>${label}:</strong> <br>${value ?? "-"}</br>`;
    ucbl.appendChild(li);
  }
}
