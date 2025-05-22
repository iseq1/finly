export function renderCashboxForm(data = null, isCreate = false) {
    const nameField = document.querySelector('#cashbox-name');
    const typeField = document.querySelector('#cashbox-type');
    const customNameField = document.querySelector('#custom-name');
    const noteField = document.querySelector('#note');
    const balanceField = document.querySelector('#balance');
    const currencyField = document.querySelector('#currency');
    const autoUpdateCheckbox = document.querySelector('#demo-copy');
  
    // Заполняем поля, если есть данные
    if (data) {
      // Общие поля
      nameField.value = data.cashbox?.name || data.name || '';
      typeField.value = data.cashbox?.type?.name || data.type?.name || '';
      currencyField.value = data.cashbox?.currency || data.currency || '';
  
      if (isCreate) {
        // Создание — поля пустые
        customNameField.value = '';
        noteField.value = '';
        balanceField.value = '';
        autoUpdateCheckbox.checked = false;
      } else {
        // Редактирование
        customNameField.value = data.custom_name || '';
        noteField.value = data.note || '';
        balanceField.value = data.balance || '';
        autoUpdateCheckbox.checked = !!data.is_auto_update;
      }
    }
  
    // Заголовок и текст кнопки
    const title = document.querySelector('section header h1');
    const submitBtn = document.querySelector('input[type="submit"]');
    title.textContent = isCreate ? 'Создать кэшбокс' : 'Редактировать кэшбокс';
    submitBtn.value = isCreate ? 'Создать' : 'Обновить';
  }
  