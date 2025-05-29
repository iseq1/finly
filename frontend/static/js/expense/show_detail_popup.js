export function hidePopup() {
  const overlay = document.getElementById('popup-overlay');
  overlay.style.display = 'none';
}

export function showDetailPopup(data) {
  const overlay = document.getElementById('popup-overlay');
  const popupTitle = document.getElementById('popup-title');
  const popupBody = document.getElementById('popup-body');

  if (!overlay || !popupTitle || !popupBody) {
    console.error('Не найдены элементы попапа');
    return;
  }

  popupTitle.textContent = `Категория: ${data.category_name} — Провайдер: ${data.provider_name}`;

  const tableHtml = `
    <table class="popup-subtable">
      <thead>
        <tr>
          <th>Подкатегория</th>
          <th>Транзакции</th>
          <th>Сумма</th>
          <th>%</th>
        </tr>
      </thead>
      <tbody>
        ${data.statistics.map(stat => `
          <tr>
            <td>${stat.subcategory_name}</td>
            <td>
              <ul>
                ${stat.transactions.map(tx => `
                  <li>
                    <strong>${tx.amount}₽</strong> — ${tx.comment || 'Без комментария'}<br>
                    <small>${new Date(tx.date).toLocaleDateString()} | ${tx.cashbox_name}</small>
                  </li>
                `).join('')}
              </ul>
            </td>
            <td>${stat.total}₽</td>
            <td>${stat.percentage}%</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;

  popupBody.innerHTML = tableHtml;
  overlay.style.display = 'flex';
}
