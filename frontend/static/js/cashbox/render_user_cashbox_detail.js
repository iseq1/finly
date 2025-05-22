export function renderCashboxDetail(data) {
    const dl = document.querySelector("dl");
    dl.innerHTML = "";
  
    const fields = {
      "Наименование ": data.cashbox.name,
      "Тип": data.cashbox.type.name,
      "Провайдер": data.cashbox.provider.name,
      "Баланс": data.balance,
      "Валюта": data.cashbox.currency,
      "Кастомное наименование": data.custom_name,
      "Заметка": data.note,
    };
  
    for (const [label, value] of Object.entries(fields)) {
      const dt = document.createElement("dt");
      dt.textContent = label;
      dt.style = "margin: 0 0 0 0;";
  
      const dd = document.createElement("dd");
      const p = document.createElement("p");
      p.textContent = value;
  
      dd.appendChild(p);
      dl.appendChild(dt);
      dl.appendChild(dd);
    }
  }
  