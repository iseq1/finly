import { handleForm } from '/static/js/cashbox/handle_user_cashbox_form.js';
import { authGuard } from '/static/js/security/guard.js';

authGuard();

document.addEventListener('DOMContentLoaded', async () => {
  await handleForm();
});
