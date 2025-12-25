let allPrograms = [];
let currentCategory = 'Все';
let selectedProgram = null;

document.addEventListener('DOMContentLoaded', async () => {
    await loadCategories();
    await loadPrograms();
    selectFirstGame();

    // Поиск
    document.getElementById('search').addEventListener('input', (e) => {
        filterPrograms(e.target.value);
    });

    // Обновить (ресан)
    document.getElementById('rescan-btn').addEventListener('click', async () => {
        await window.pywebview.api.rescan();
        await loadPrograms();
        await loadCategories(); // На случай изменений
        selectFirstGame();
    });

    // Добавить (заглушка)
    document.getElementById('add-btn').addEventListener('click', () => {
        alert('Функция добавления программы — реализуйте в Python API (добавьте в Custom категорию)');
    });

    // PLAY кнопка (будет привязана при showDetail)
});

async function loadCategories() {
    const categoriesList = document.getElementById('categories-list');
    categoriesList.innerHTML = '';
    const categories = await window.pywebview.api.getCategories();

    categories.forEach(cat => {
        const li = document.createElement('li');
        li.textContent = cat.name;
        li.dataset.category = cat.name;
        li.addEventListener('click', () => {
            document.querySelectorAll('.categories li').forEach(el => el.classList.remove('active'));
            li.classList.add('active');
            currentCategory = cat.name;
            filterPrograms(document.getElementById('search').value);
        });
        if (cat.name === 'Все') li.classList.add('active');
        categoriesList.appendChild(li);
    });
}

async function loadPrograms() {
    allPrograms = await window.pywebview.api.getPrograms();
    filterPrograms(''); // Отобразить сразу
}

function renderPrograms(programs) {
    const gamesList = document.getElementById('games-list');
    const empty = document.getElementById('empty-state');
    const detail = document.getElementById('detail');
    gamesList.innerHTML = '';

    document.querySelectorAll('.games li').forEach(el => el.classList.remove('active'));

    if (programs.length === 0) {
        empty.classList.remove('hidden');
        detail.classList.add('hidden');
        return;
    }

    empty.classList.add('hidden');

    programs.forEach((program, index) => {
        const li = document.createElement('li');
        li.textContent = program.name;
        li.dataset.index = index;
        li.addEventListener('click', () => {
            document.querySelectorAll('.games li').forEach(el => el.classList.remove('active'));
            li.classList.add('active');
            selectedProgram = program;
            showDetail(program);
        });
        gamesList.appendChild(li);
    });
}

function showDetail(program) {
    const detail = document.getElementById('detail');
    document.getElementById('detail-cover').src = program.cover || 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9IiMyZDMyM2EiLz48dGV4dCB4PSI1MCUiIHk9IjUwJSIgZm9udC1zaXplPSIzMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iIGZpbGw9IiNhMGEwYTAiPk5ldCBvYmxvemhrZTwvdGV4dD48L3N2Zz4=';
    document.getElementById('detail-name').textContent = program.name;
    document.getElementById('detail-source').textContent = `Источник: ${program.source.toUpperCase()}`;
    detail.classList.remove('hidden');

    // Привязка PLAY
    const playBtn = document.getElementById('detail-play');
    playBtn.onclick = () => window.pywebview.api.launchProgram(program.path);
}

function selectFirstGame() {
    if (allPrograms.length > 0) {
        selectedProgram = allPrograms[0];
        showDetail(selectedProgram);
        const firstLi = document.querySelector('.games li');
        if (firstLi) firstLi.classList.add('active');
    }
}

function filterPrograms(query) {
    let filtered = allPrograms;

    if (currentCategory !== 'Все') {
        filtered = filtered.filter(p => p.category === currentCategory);
    }

    if (query.trim()) {
        const lowerQuery = query.toLowerCase();
        filtered = filtered.filter(p => p.name.toLowerCase().includes(lowerQuery));
    }

    renderPrograms(filtered);
}

async function loadPrograms() {
    allPrograms = await window.pywebview.api.getPrograms();
    filterPrograms('');
    if (allPrograms.length === 0) {
        document.getElementById('empty-state').classList.remove('hidden');
    } else {
        selectFirstGame();
    }
}