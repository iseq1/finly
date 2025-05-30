export function hidePopup() {
  const overlay = document.getElementById('popup-overlay');
  overlay.style.display = 'none';
}

export function showCategoryPopup(data) {
  const overlay = document.getElementById('popup-overlay');
  const popupTitle = document.getElementById('popup-title');
  const popupBody = document.getElementById('popup-body');

  if (!overlay || !popupTitle || !popupBody) {
    console.error('Не найдены элементы попапа');
    return;
  }

  popupTitle.textContent = `Категория: ${data.category_name}`;

  const tableHtml = `
    <table class="popup-subtable">
      <thead>
        <tr>
          <th>Подкатегория</th>
          <th>Транзакции</th>
          <th>Сумма</th>
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
                    <small>${new Date(tx.transacted_at).toLocaleDateString()} | ${tx.source} | ${tx.cashbox.cashbox_name} (${tx.cashbox.provider_name})</small>
                  </li>
                `).join('')}
              </ul>
            </td>
            <td>${stat.total}₽</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;

  popupBody.innerHTML = tableHtml;
  overlay.style.display = 'flex';
}

