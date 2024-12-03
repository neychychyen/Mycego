function press_button(){
    console.log('activeDataNames');
    const activeDataNames = getActiveDataNames();
    console.log(activeDataNames);
    console.log(public_url)


    const paths = activeDataNames.map(path => encodeURIComponent(public_url + '/' + path));
    const zipHref = baseUrl + '/?' + paths.map(p => `paths=${p}`).join('&');
    window.open(zipHref);

}

function ajax_items() {
  return fetch(get_items_url, {
      method: 'GET',
  }).then(response => response.json()) // Преобразуем полученный ответ в JSON
    .catch(error => console.error('Ошибка:', error)); // Если возникли ошибки, выводим их в консоль
}

function draw_messages(messages) { // То что мы будем делать с нашими данными

  const fileContainer = document.querySelector('.file-container');

  if (messages.status === false) {
    // Если статус false, заменяем содержимое элемента
    fileContainer.innerHTML = messages.Warnings;
    return false;
  } else {
    draw_items(messages); // Передаем данные в draw_items
    return true;
  }
}

function ajax_get() {
  return fetch(get_data_url, {
      method: 'GET',
  }).then(response => response.json()) // Преобразуем полученный ответ в JSON
    .then(data => draw_messages(data)) // Обрабатываем данные, полученные в ответе с помощью функции draw_messages
    .catch(error => console.error('Ошибка:', error)); // Если возникли ошибки, выводим их в консоль
}

function draw_items(items) {
    const container = document.querySelector('.file-container');

    // Очищаем контейнер перед добавлением новых элементов
    container.innerHTML = '';

    // Убедимся, что элементы существуют и являются массивом
    if (items && Array.isArray(items.elements)) {
        items.elements.forEach(item => {
            const fileDiv = document.createElement('div');
            fileDiv.setAttribute('data-name', item);
            fileDiv.classList.add('file-item');
            fileDiv.textContent = item; // Вставляем название файла или путь
            container.appendChild(fileDiv);
        });

        const fileItems = document.querySelectorAll('.file-item');
        fileItems.forEach(item => {
          item.addEventListener('click', toggleActiveClass);
        });

        const pressDiv = document.querySelector('#press');
        const button = document.createElement('button');

        // Устанавливаем текст кнопки
        button.textContent = 'Скачать';
        button.onclick = press_button;

        pressDiv.appendChild(button);

    } else {
        console.error('Нет элементов для отображения');
    }
}

function repeat_ajax_get() {
  ajax_get().then(success => {
    if (!success) {
      // Если результат false, повторяем запрос через 1 секунду
      setTimeout(repeat_ajax_get, 1000); // 1 секунда
    } else {
      console.log('Запрос успешен, все готово!');
      // Получаем данные из ajax_items и передаем их в draw_items
      ajax_items().then(data => {
        if (data) {
          draw_items(data); // Вызываем draw_items с полученными данными
        }
      });
    }
  });
}


repeat_ajax_get();
