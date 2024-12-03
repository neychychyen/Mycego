// Функция для обработки клика по элементу
function toggleActiveClass(event) {
  // Получаем элемент, по которому кликнули
  const clickedElement = event.target;

  // Проверяем, является ли элемент с классом 'file-item'
  if (clickedElement.classList.contains('file-item')) {
    // Если класс 'active' уже есть, удаляем его, иначе добавляем
    clickedElement.classList.toggle('active');
  }
}

// Привязываем обработчик события ко всем элементам с классом 'file-item'

function getActiveDataNames() {
    // Находим все элементы с классом "active"
    const activeElements = document.querySelectorAll('.active');

    // Собираем значения атрибута data-name в массив
    const dataNames = Array.from(activeElements).map(element => element.getAttribute('data-name'));

    return dataNames;
}

// Пример использования
