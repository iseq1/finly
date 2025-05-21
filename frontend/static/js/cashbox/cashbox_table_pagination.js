import { loadTable, getCurrentPage } from '/static/js/cashbox/cashbox_table_render.js';

export function renderPagination(totalPages, hasPrev, hasNext, onPageChange, currentPage, sortBy, sortDir, userCashboxIds) {
  const pagination = document.querySelector(".pagination");
  pagination.innerHTML = "";

  // Prev
  const prev = document.createElement("li");
  prev.innerHTML = `<a href="#" class="button${hasPrev ? '' : ' disabled'}">Prev</a>`;
  if (hasPrev) {
    prev.addEventListener("click", (e) => {
      e.preventDefault();
      onPageChange(currentPage - 1, sortBy, sortDir, userCashboxIds);
    });
  }
  pagination.appendChild(prev);

  // Pages
  for (let i = 1; i <= totalPages; i++) {
    const li = document.createElement("li");
    li.innerHTML = `<a href="#" class="page${i === currentPage ? ' active' : ''}">${i}</a>`;
    li.addEventListener("click", (e) => {
      e.preventDefault();
      onPageChange(i, sortBy, sortDir, userCashboxIds);
    });
    pagination.appendChild(li);
  }

  // Next
  const next = document.createElement("li");
  next.innerHTML = `<a href="#" class="button${hasNext ? '' : ' disabled'}">Next</a>`;
  if (hasNext) {
    next.addEventListener("click", (e) => {
      e.preventDefault();
      onPageChange(currentPage + 1, sortBy, sortDir, userCashboxIds);
    });
  }
  pagination.appendChild(next);
}
