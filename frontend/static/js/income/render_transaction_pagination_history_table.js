export function renderPaginationControls(pagination, onPageChange) {
  const container = document.querySelector('.pagination');
  if (!container) return;

  container.innerHTML = '';

  const { page, pages, has_prev, has_next } = pagination;

  const createPageButton = (label, disabled, callback, isActive = false) => {
    const li = document.createElement('li');
    const btn = document.createElement('a');
    btn.href = '#';
    btn.className = isActive ? 'page active' : 'page';
    btn.textContent = label;

    if (disabled) {
      btn.classList.add('disabled');
    } else {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        callback();
      });
    }

    li.appendChild(btn);
    return li;
  };

  // Prev
  container.appendChild(
    createPageButton('Prev', !has_prev, () => onPageChange(page - 1))
  );

  // Pages
  const maxPagesToShow = 7;
  const startPage = Math.max(1, page - 3);
  const endPage = Math.min(pages, startPage + maxPagesToShow - 1);

  if (startPage > 1) {
    container.appendChild(createPageButton('1', false, () => onPageChange(1)));
    if (startPage > 2) {
      const dots = document.createElement('li');
      dots.innerHTML = '<span>&hellip;</span>';
      container.appendChild(dots);
    }
  }

  for (let i = startPage; i <= endPage; i++) {
    container.appendChild(
      createPageButton(i.toString(), false, () => onPageChange(i), i === page)
    );
  }

  if (endPage < pages) {
    if (endPage < pages - 1) {
      const dots = document.createElement('li');
      dots.innerHTML = '<span>&hellip;</span>';
      container.appendChild(dots);
    }
    container.appendChild(
      createPageButton(pages.toString(), false, () => onPageChange(pages))
    );
  }

  // Next
  container.appendChild(
    createPageButton('Next', !has_next, () => onPageChange(page + 1))
  );
}
