export function renderBalanceTable(balanceSnapshots) {
    const tableHead = document.querySelector('thead tr');
    const tableBody = document.querySelector('tbody');
  
    // Подготовим форматтеры
    const monthFormatter = new Intl.DateTimeFormat('ru-RU', { month: 'long' });
    const dateFormatter = new Intl.DateTimeFormat('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  
    const columnDefs = []; // [{ key: '2025-05-static', title: 'Май 2025 (стат.)', snapshot }]
    const cashboxMap = new Map(); // id => { name, currency }
  
    for (const snap of balanceSnapshots) {
      const keyBase = `${snap.year}-${String(snap.month).padStart(2, '0')}`;
      const suffix = snap.is_static ? 'static' : 'dynamic';
      const key = `${keyBase}-${suffix}`;
  
      let title;
      if (snap.is_static) {
        const monthName = monthFormatter.format(new Date(`${snap.year}-${snap.month}-01`));
        title = `${capitalize(monthName)} ${snap.year}`;
      } else {
        const updatedAt = new Date(snap.updated_at || snap.created_at);
        title = `${dateFormatter.format(updatedAt)}`;
      }
  
      columnDefs.push({ key, title, snapshot: snap.snapshot });
  
      // Собираем кэшбоксы
      for (const [id, data] of Object.entries(snap.snapshot)) {
        if (!cashboxMap.has(id)) {
          cashboxMap.set(id, { name: data.name, currency: data.currency });
        }
      }
    }
  
    // ==== 1. Заголовок таблицы ====
    tableHead.innerHTML =
      '<th>Кэшбокс</th>' +
      columnDefs
        .map((col) => `<th>${col.title}</th>`)
        .join('');
  
    // ==== 2. Тело таблицы ====
    tableBody.innerHTML = '';
  
    for (const [cashboxId, info] of cashboxMap.entries()) {
      const row = document.createElement('tr');
      const cells = [];
  
      cells.push(`<td>${info.name} (${info.currency})</td>`);
  
      for (const col of columnDefs) {
        const entry = col.snapshot[cashboxId];
        const cellValue = entry ? entry.balance.toLocaleString('ru-RU') : '—';
        cells.push(`<td>${cellValue}</td>`);
      }
  
      row.innerHTML = cells.join('');
      tableBody.appendChild(row);
    }
  }

  function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }
  