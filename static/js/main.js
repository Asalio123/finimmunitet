// ФинИммунитет: мобильное меню + фильтр карточек. Без зависимостей.

// Мобильное меню (бургер на CSS :checked, тут только каретка фильтра)
// Фильтр каталога разборов: кнопки [data-filter] скрывают превью [data-tag]
const filterBtns = document.querySelectorAll(".filter-btn");
const cards = document.querySelectorAll("[data-tag]");

if (filterBtns.length && cards.length) {
  filterBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      filterBtns.forEach((b) => b.classList.remove("is-active"));
      btn.classList.add("is-active");
      const tag = btn.dataset.filter;
      cards.forEach((c) => {
        c.hidden = tag !== "all" && c.dataset.tag !== tag;
      });
    });
  });
}
