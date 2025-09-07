import { setupIncomeFormSubmission } from '/static/js/income/setup_payload.js';
import { createIncome } from '/static/js/income/post_new_income.js';
import { getAccessToken, logout } from '/static/js/security/token.js';


export async function handleIncomeForm() {
  const form = document.getElementById('income-form');
  if (!form) {
    return;
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    try {
       const payload = setupIncomeFormSubmission();
       await createIncome(payload);
       alert('Новая запись о доходе записана!');
       window.location.href = '/templates/income/history.html';
    } catch (err) {
      console.error(err);
      alert('Ошибка при сохранении записи о доходе');
    }
  });
}
