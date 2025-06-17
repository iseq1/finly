export function hidePopup() {
  const overlay = document.getElementById('popup-overlay');
  overlay.style.display = 'none';
}

export function showProviderPopup(data) {
  const overlay = document.getElementById('popup-overlay');
  const popupTitle = document.getElementById('popup-title');
  const popupBody = document.getElementById('popup-body');

  popupTitle.textContent = `Провайдер: ${data.provider_name}`;

  const tableHtml = `
    <table class="popup-subtable">
      <thead>
        <tr>
          <th>Касса</th>
          <th>Тип</th>
          <th>Сумма</th>
        </tr>
      </thead>
      <tbody>
        ${data.statistics.map(stat => `
          <tr>
            <td>${stat.cashbox_name}</td>
            <td>${stat.cashbox_type}</td>
            <td>${stat.total}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;

  popupBody.innerHTML = tableHtml;
  overlay.style.display = 'flex';
}