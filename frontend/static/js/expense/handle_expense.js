import { setupExpenseFormSubmission } from '/static/js/expense/setup_payload.js';
import { createExpense } from '/static/js/expense/post_new_expense.js';
import { getAccessToken, logout } from '/static/js/security/token.js';


export async function handleExpenseForm() {
  const form = document.getElementById('expense-form');
  if (!form) {
    return;
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    try {
       const payload = setupExpenseFormSubmission();
       await createExpense(payload);
       alert('Новая запись о расходах записана!');
       window.location.href = '/templates/expense/history.html';
    } catch (err) {
      console.error(err);
      alert('Ошибка при сохранении записи о расходах');
    }
  });
}
