import { getUserIdFromToken } from '/static/js/security/identity_by_token.js';
import { logout } from '/static/js/security/token.js';
import { renderCashboxForm } from '/static/js/cashbox/render_user_cashbox_form.js';
import { updateUserCashbox, createUserCashbox } from '/static/js/cashbox/fetch_user_cashbox.js';

export async function handleForm() {
  const form = document.querySelector('form');
  const params = new URLSearchParams(window.location.search);
  const id = params.get('id');
  const userId = getUserIdFromToken();

  if (!userId) {
    alert("Не удалось получить ID пользователя из токена");
    logout();
    return;
  }

  const storedEdit = sessionStorage.getItem('editingCashbox');
  const storedCreate = sessionStorage.getItem('creatingCashbox');

  let formData = null;
  let isCreate = false;

  if (storedEdit) {
    formData = JSON.parse(storedEdit);
  } else if (storedCreate) {
    formData = JSON.parse(storedCreate);
    isCreate = true;
  }

  renderCashboxForm(formData, isCreate);

  // Проставим data-cashbox-id в форму (нужно для payload)
  const cashboxId = isCreate ? formData.id : formData.cashbox_id;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const payload = {
      user_id: Number(userId),
      cashbox_id: parseInt(cashboxId),
      balance: parseFloat(document.querySelector('#balance').value) || 0,
      is_auto_update: document.querySelector('#demo-copy').checked,
      custom_name: document.querySelector('#custom-name').value.trim() || "",
      note: document.querySelector('#note').value.trim() || "",
      last_synced_at: new Date().toISOString(),
    };
    console.log(payload);
    try {
      if (isCreate) {
        await createUserCashbox(payload);
        alert('Кэшбокс создан');
      } else {
        const userCashboxId = formData.id; // 
        await updateUserCashbox(userCashboxId, payload);
        alert('Кэшбокс обновлён');
      }

      // Удалим временные данные из sessionStorage
      sessionStorage.removeItem('editingCashbox');
      sessionStorage.removeItem('creatingCashbox');

      window.location.href = '/templates/cashbox/main.html';
    } catch (err) {
      console.error(err);
      alert('Ошибка при сохранении кэшбокса');
    }
  });
}
