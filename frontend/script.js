let allPrograms = [];
let categories = [];
let currentCategory = 'Все';
let selectedProgram = null;

function initializeApp() {
    if (window.pywebview && typeof window.pywebview.api !== 'undefined') {
        startLoading();
    } else {
        setTimeout(initializeApp, 100);
    }
}

async function startLoading() {
    await loadCategoriesAndPrograms();
    setupEventListeners();
    if (allPrograms.length > 0) selectFirstGame();
}

async function loadCategoriesAndPrograms() {
    categories = await window.pywebview.api.getCategories();
    allPrograms = await window.pywebview.api.getPrograms();
    renderCategories();
    populateAddCategorySelect();
    currentCategory = 'Все';
    filterPrograms('');
}

function setupEventListeners() {
    document.getElementById('search').addEventListener('input', e => filterPrograms(e.target.value));

    document.getElementById('add-btn').addEventListener('click', () => {
        document.getElementById('add-name').value = '';
        document.getElementById('add-path').value = '';
        document.getElementById('add-modal').classList.remove('hidden');
    });

    document.getElementById('browse-btn').addEventListener('click', async () => {
        const path = await window.pywebview.api.openFileDialog();
        if (path) {
            document.getElementById('add-path').value = path;
            const filename = path.split(/[\\/]/).pop();
            const name = filename.replace(/\.(exe|jar|bat)$/i, '').replace(/[_.-](x64|x86|portable)/gi, '').trim();
            document.getElementById('add-name').value = name;
        }
    });

    document.getElementById('add-cancel').addEventListener('click', () => {
        document.getElementById('add-modal').classList.add('hidden');
    });

    document.getElementById('add-confirm').addEventListener('click', async () => {
        const name = document.getElementById('add-name').value.trim();
        const path = document.getElementById('add-path').value.trim();
        const category = document.getElementById('add-category').value;
        if (!name || !path) return alert('Заполните поля');
        const res = await window.pywebview.api.addProgram(name, path, category);
        if (res.success) {
            await loadCategoriesAndPrograms();
            document.getElementById('add-modal').classList.add('hidden');
        } else alert('Ошибка добавления');
    });

    document.getElementById('rescan-btn').addEventListener('click', async () => {
        await window.pywebview.api.rescan();
        await loadCategoriesAndPrograms();
    });
}

function renderCategories() {
    const container = document.getElementById('categories-container');
    container.innerHTML = '';

    categories.forEach(cat => {
        const details = document.createElement('details');
        details.open = false;

        const summary = document.createElement('summary');
        summary.textContent = cat.name;
        summary.addEventListener('click', e => {
            e.preventDefault();
            currentCategory = cat.name;
            document.querySelectorAll('summary').forEach(s => s.classList.remove('active'));
            summary.classList.add('active');
            document.querySelectorAll('details').forEach(d => d.open = false);
            details.open = true;
            filterPrograms(document.getElementById('search').value);
        });
        if (cat.name === 'Все') summary.classList.add('active');

        details.appendChild(summary);

        const ul = document.createElement('ul');
        ul.className = 'games';
        ul.id = `games-${cat.name.replace(/\s/g, '-')}`;
        details.appendChild(ul);

        container.appendChild(details);
    });
}

function renderProgramsInCategories(filtered) {
    categories.forEach(cat => {
        const ul = document.getElementById(`games-${cat.name.replace(/\s/g, '-')}`);
        if (ul) ul.innerHTML = '';
    });

    const programsToShow = currentCategory === 'Все' ? filtered : filtered.filter(p => p.category === currentCategory);
    const unique = [...new Map(programsToShow.map(p => [p.id, p])).values()];

    const ul = document.getElementById(`games-${currentCategory.replace(/\s/g, '-')}`);
    if (ul && unique.length > 0) {
        unique.forEach(program => {
            const li = document.createElement('li');
            li.textContent = program.name;
            li.dataset.id = program.id;
            li.addEventListener('click', () => {
                document.querySelectorAll('.games li').forEach(l => l.classList.remove('active'));
                li.classList.add('active');
                selectedProgram = program;
                showDetail(program);
            });
            ul.appendChild(li);
        });
        ul.querySelector('li').classList.add('active');
        selectedProgram = unique[0];
        showDetail(unique[0]);
    }

    const empty = unique.length === 0;
    document.getElementById('empty-state').classList.toggle('hidden', !empty);
    document.getElementById('detail').classList.toggle('hidden', empty);
}

function filterPrograms(query) {
    let filtered = allPrograms;
    if (query.trim()) {
        const q = query.toLowerCase();
        filtered = filtered.filter(p => p.name.toLowerCase().includes(q));
    }
    renderProgramsInCategories(filtered);
}

function showDetail(program) {
    document.getElementById('detail-cover').src = program.cover || 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9IiMyZDMyM2EiLz48dGV4dCB4PSI1MCUiIHk9IjUwJSIgZm9udC1zaXplPSIzMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iIGZpbGw9IiNhMGEwYTAiPk5ldCBvYmxvemhrZTwvdGV4dD48L3N2Zz4=';
    document.getElementById('detail-name').textContent = program.name;
    document.getElementById('detail-source').textContent = `Источник: ${program.source.toUpperCase()}`;

    const playBtn = document.getElementById('detail-play');
    playBtn.onclick = async () => {
        const res = await window.pywebview.api.launchProgram(program.path, program.source, program.id);
        if (!res.success) alert('Ошибка запуска');
    };
}

function selectFirstGame() {
    const first = allPrograms.find(p => currentCategory === 'Все' || p.category === currentCategory);
    if (first) {
        selectedProgram = first;
        showDetail(first);
        const li = document.querySelector('.games li');
        if (li) li.classList.add('active');
    }
}

function populateAddCategorySelect() {
    const select = document.getElementById('add-category');
    select.innerHTML = '';
    categories.filter(c => c.name !== 'Все').forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.name;
        opt.textContent = c.name;
        select.appendChild(opt);
    });
}

document.addEventListener('DOMContentLoaded', initializeApp);
window.addEventListener('pywebviewready', initializeApp);