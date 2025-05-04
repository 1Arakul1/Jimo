// Инициализация всплывающих подсказок Bootstrap
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });
  
    // Инициализация всплывающих окон Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
      return new bootstrap.Popover(popoverTriggerEl);
    });
  
    // Анимация для элементов при прокрутке
    const animateOnScroll = function() {
      const elements = document.querySelectorAll('.animate-on-scroll');
      
      elements.forEach(element => {
        const elementPosition = element.getBoundingClientRect().top;
        const windowHeight = window.innerHeight;
        
        if (elementPosition < windowHeight - 50) {
          element.classList.add('fade-in');
        }
      });
    };
  
    // Запуск анимации при загрузке и прокрутке
    animateOnScroll();
    window.addEventListener('scroll', animateOnScroll);
  
    // Обработка форм с подтверждением
    const confirmForms = document.querySelectorAll('.confirm-form');
    confirmForms.forEach(form => {
      form.addEventListener('submit', function(e) {
        if (!confirm('Вы уверены, что хотите выполнить это действие?')) {
          e.preventDefault();
        }
      });
    });
  
    // Предварительный просмотр изображений при загрузке
    const imageInputs = document.querySelectorAll('.image-preview-input');
    imageInputs.forEach(input => {
      input.addEventListener('change', function() {
        const preview = document.querySelector(this.dataset.previewTarget);
        if (preview && this.files && this.files[0]) {
          const reader = new FileReader();
          reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
          };
          reader.readAsDataURL(this.files[0]);
        }
      });
    });
  
    // Динамическая валидация форм
    const validateForms = document.querySelectorAll('.needs-validation');
    validateForms.forEach(form => {
      form.addEventListener('submit', function(event) {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add('was-validated');
      }, false);
    });
  });
  
  // Функция для фильтрации карточек собак
  function filterDogs(query) {
    const dogCards = document.querySelectorAll('.dog-card');
    query = query.toLowerCase().trim();
    
    dogCards.forEach(card => {
      const dogName = card.querySelector('.card-title').textContent.toLowerCase();
      const dogBreed = card.querySelector('.dog-breed').textContent.toLowerCase();
      const dogDesc = card.querySelector('.dog-description').textContent.toLowerCase();
      
      if (dogName.includes(query) || dogBreed.includes(query) || dogDesc.includes(query)) {
        card.style.display = 'block';
      } else {
        card.style.display = 'none';
      }
    });
  }
  
  // Функция для сортировки карточек собак
  function sortDogs(sortBy) {
    const dogCardsContainer = document.getElementById('dog-cards');
    if (!dogCardsContainer) return;
    
    const dogCards = Array.from(dogCardsContainer.querySelectorAll('.col'));
    
    dogCards.sort((a, b) => {
      let valueA, valueB;
      
      if (sortBy === 'name') {
        valueA = a.querySelector('.card-title').textContent;
        valueB = b.querySelector('.card-title').textContent;
        return valueA.localeCompare(valueB);
      } else if (sortBy === 'age') {
        valueA = parseInt(a.querySelector('.dog-age').textContent);
        valueB = parseInt(b.querySelector('.dog-age').textContent);
        return valueA - valueB;
      }
      
      return 0;
    });
    
    // Очистка и добавление отсортированных карточек
    dogCardsContainer.innerHTML = '';
    dogCards.forEach(card => {
      dogCardsContainer.appendChild(card);
    });
  }
  