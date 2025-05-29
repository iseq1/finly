
export function getDefaultOrUrlParams() {
  const { start_date, end_date, include_empty_categories } = getDateRangeFromInputs();

  const safeStartDate = start_date ?? new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0];
  const safeEndDate = end_date ?? new Date().toISOString().split('T')[0];
  const safeIncludeEmpty = include_empty_categories ?? 'true';

  console.log({ safeStartDate, safeEndDate, safeIncludeEmpty });

  return new URLSearchParams({
    start_date: safeStartDate,
    end_date: safeEndDate,
    type: 'expense',
    include_empty_categories: safeIncludeEmpty,
  });
}

export function getDateRangeFromInputs() {
  const monthStart = document.getElementById('month-start')?.value;
  const yearStart = document.getElementById('year-start')?.value;
  const monthFinish = document.getElementById('month-finish')?.value;
  const yearFinish = document.getElementById('year-finish')?.value;
  const includeEmptyCheckbox = document.getElementById('demo-human');

  let start_date, end_date;

  if (monthStart && yearStart) {
    start_date = new Date(Number(yearStart), Number(monthStart) - 1, 1);
  }
  else {
    const now = new Date();
    start_date = new Date(now.getFullYear(), now.getMonth(), 1);
  }

  if (monthFinish && yearFinish) {
    // Последний день месяца
    end_date = new Date(Number(yearFinish), Number(monthFinish), 0);
  }
  else{
    end_date = new Date();
  }

  const include_empty_categories = includeEmptyCheckbox && !includeEmptyCheckbox.checked ? 'false' : 'true';

  return {
    start_date: start_date.toLocaleDateString('en-CA').split('T')[0],
    end_date: end_date.toLocaleDateString('en-CA').split('T')[0],
    include_empty_categories: include_empty_categories,
  };
}