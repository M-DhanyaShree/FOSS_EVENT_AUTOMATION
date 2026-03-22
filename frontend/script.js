const API_BASE = 'http://127.0.0.1:5000/api';
let currentEventId = null;

async function showDashboard() {
    currentEventId = null;
    document.getElementById('dashboard-view').style.display = 'block';
    document.getElementById('event-detail-view').style.display = 'none';
    document.getElementById('nav-actions').innerHTML = '';
    await loadEvents();
}

function openModal(id) { document.getElementById(id).style.display = 'flex'; }
function closeModal(id) { document.getElementById(id).style.display = 'none'; }

function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
    document.getElementById(`tab-${tabId}`).style.display = 'block';
    event.currentTarget.classList.add('active');
}

async function loadEvents() {
    const res = await fetch(`${API_BASE}/events`);
    const events = await res.json();
    const grid = document.getElementById('event-grid');
    grid.innerHTML = events.length ? '' : '<p style="color: grey;">No events found. Start by creating a new one.</p>';

    events.forEach(e => {
        const card = document.createElement('div');
        card.className = 'event-card';
        card.innerHTML = `
            <div class="event-card-dots">
                <div class="dot dot-red"></div>
                <div class="dot dot-yellow"></div>
                <div class="dot dot-green"></div>
            </div>
            <div class="event-card-content">
                <h3>${e.name}</h3>
                <p><strong>Mode:</strong> ${e.mode}</p>
                <div style="margin-top: 15px; font-size: 0.8rem; font-family: 'JetBrains Mono', monospace; color: var(--accent);">
                    View Details
                </div>
            </div>
        `;
        card.onclick = () => openEventDetail(e.id);
        grid.appendChild(card);
    });
}

async function createEventSubmit() {
    const name = document.getElementById('event-name').value;
    const mode = document.getElementById('event-mode').value;
    if (!name) return alert('Enter event name');

    const res = await fetch(`${API_BASE}/events`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, mode })
    });
    const data = await res.json();
    if (data.error) return alert(data.error);

    closeModal('createEventModal');
    openEventDetail(data.id);
}

async function openEventDetail(id) {
    currentEventId = id;
    const res = await fetch(`${API_BASE}/events/${id}`);
    const data = await res.json();

    document.getElementById('dashboard-view').style.display = 'none';
    document.getElementById('event-detail-view').style.display = 'block';

    document.getElementById('disp-name').innerText = data.event.name.toUpperCase();
    document.getElementById('disp-mode').innerText = `Mode: ${data.event.mode}`;

    document.getElementById('disp-venue').innerText = data.details.venue || '-';
    document.getElementById('disp-time').innerText = data.details.time || '-';
    document.getElementById('disp-type').innerText = data.details.type || '-';
    document.getElementById('disp-participants').innerText = data.details.expected_participants || '0+';
    document.getElementById('disp-description').innerText = data.details.description || 'No description provided.';

    document.getElementById('edit-organizers').setAttribute('data-current', data.details.organizers || '');

    renderFlow(data.flow);
    renderBudget(data.budget_items);
    renderTasks(data.tasks);
    renderResources(data.resources);

    lucide.createIcons();
}

function renderFlow(flow) {
    const list = document.getElementById('flow-list');
    list.innerHTML = `<tr><th>TIME</th><th>STEP</th><th>DESCRIPTION</th><th>ACTION</th></tr>`;
    flow.forEach(f => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${new Date(f.date_time).toLocaleString()}</td>
            <td style="color: var(--accent);">${f.round_name}</td>
            <td>${f.description}</td>
            <td><button class="btn btn-delete" onclick="deleteItem('flow', ${f.id})"><i data-lucide="trash-2" style="width: 14px;"></i></button></td>
        `;
        list.appendChild(row);
    });
    lucide.createIcons();
}

function renderBudget(items) {
    const list = document.getElementById('budget-list');
    let total = 0;
    list.innerHTML = `<tr><th>ITEM</th><th>COST</th><th>ACTION</th></tr>`;
    items.forEach(i => {
        total += i.cost;
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${i.item_name}</td>
            <td style="color: #27c93f;">₹${i.cost.toLocaleString()}</td>
            <td><button class="btn btn-delete" onclick="deleteItem('budget', ${i.id})"><i data-lucide="trash-2" style="width: 14px;"></i></button></td>
        `;
        list.appendChild(row);
    });
    const totalRow = document.createElement('tr');
    totalRow.innerHTML = `<td style="font-weight: bold; color: var(--accent);">TOTAL_COST</td><td style="color: #27c93f; font-weight: bold;">₹${total.toLocaleString()}</td><td></td>`;
    list.appendChild(totalRow);
    lucide.createIcons();
}

function renderTasks(tasks) {
    const list = document.getElementById('task-list');
    list.innerHTML = `<tr><th>ASSIGNEE</th><th>TASK</th><th>STATUS</th><th>ID</th><th>ACTION</th></tr>`;
    tasks.forEach(t => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td style="color: var(--accent);">${t.assigned_to}</td>
            <td>${t.title}</td>
            <td><select onchange="updateTask(${t.id}, this.value)" style="width: auto; font-size: 0.75rem; padding: 4px;">
                <option value="To Do" ${t.status === 'To Do' ? 'selected' : ''}>To Do</option>
                <option value="InProgress" ${t.status === 'InProgress' ? 'selected' : ''}>Doing</option>
                <option value="Done" ${t.status === 'Done' ? 'selected' : ''}>Done</option>
            </select></td>
            <td style="font-family: monospace; font-size: 0.7rem;">UID_${t.id}</td>
            <td><button class="btn btn-delete" onclick="deleteItem('tasks', ${t.id})"><i data-lucide="trash-2" style="width: 14px;"></i></button></td>
        `;
        list.appendChild(row);
    });
    lucide.createIcons();
}

function renderResources(res) {
    const list = document.getElementById('resource-list');
    list.innerHTML = `<tr><th>CATEGORY</th><th>FILENAME</th><th>LINK</th><th>ACTION</th></tr>`;
    res.forEach(r => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td style="color: var(--text-secondary); font-size: 0.75rem;">${r.category.toUpperCase()}</td>
            <td style="color: var(--accent);">${r.file_name || 'N/A'}</td>
            <td><a href="${r.drive_link}" target="_blank" style="color: #3b82f6; text-decoration: none;">[view_source]</a></td>
            <td><button class="btn btn-delete" onclick="deleteItem('resources', ${r.id})"><i data-lucide="trash-2" style="width: 14px;"></i></button></td>
        `;
        list.appendChild(row);
    });
    lucide.createIcons();
}


async function addFlowSubmit() {
    const round_name = document.getElementById('round-name').value;
    const date_time = document.getElementById('round-time').value;
    const description = document.getElementById('round-desc').value;
    await fetch(`${API_BASE}/events/${currentEventId}/flow`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ round_name, date_time, description })
    });
    closeModal('addFlowModal');
    openEventDetail(currentEventId);
}

async function addBudgetSubmit() {
    const item_name = document.getElementById('budget-item').value;
    const cost = parseFloat(document.getElementById('budget-cost').value);
    await fetch(`${API_BASE}/events/${currentEventId}/budget`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_name, cost })
    });
    closeModal('addBudgetModal');
    openEventDetail(currentEventId);
}

async function addTaskSubmit() {
    const title = document.getElementById('task-title').value;
    const assigned_to = document.getElementById('task-assignee').value;
    await fetch(`${API_BASE}/events/${currentEventId}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, assigned_to })
    });
    closeModal('addTaskModal');
    openEventDetail(currentEventId);
}

async function uploadResourceSubmit() {
    const category = document.getElementById('res-category').value;
    const file = document.getElementById('res-file').files[0];
    if (!file) return alert('Select a file');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);

    const btn = document.getElementById('upload-btn');
    btn.innerText = 'Uploading...';
    btn.disabled = true;

    try {
        await fetch(`${API_BASE}/events/${currentEventId}/upload`, {
            method: 'POST',
            body: formData
        });
        closeModal('uploadModal');
        openEventDetail(currentEventId);
    } catch (e) { alert(e); }
    btn.innerText = 'Upload_File';
    btn.disabled = false;
}

async function updateDetailsSubmit() {
    const venue = document.getElementById('edit-venue').value;
    const time = document.getElementById('edit-time').value;
    const type = document.getElementById('edit-type').value;
    const participants = document.getElementById('edit-participants').value;
    const description = document.getElementById('edit-description').value;
    const organizers = document.getElementById('edit-organizers').value;

    await fetch(`${API_BASE}/events/${currentEventId}/details`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ venue, time, type, expected_participants: participants, description, organizers })
    });
    closeModal('editDetailsModal');
    openEventDetail(currentEventId);
}

async function updateTask(id, status) {
    await fetch(`${API_BASE}/tasks/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
    });
}


async function deleteItem(type, id) {
    if (!confirm(`Confirm deletion of this ${type} record?`)) return;
    await fetch(`${API_BASE}/${type}/${id}`, { method: 'DELETE' });
    openEventDetail(currentEventId);
}

async function deleteCurrentEvent() {
    if (!confirm('EXTREME WARNING: All data for this event will be permanently deleted. Proceed?')) return;
    await fetch(`${API_BASE}/events/${currentEventId}`, { method: 'DELETE' });
    showDashboard();
}

function genReportSubmit() {
    const label = document.getElementById('rep-label').value;
    const url = document.getElementById('rep-url').value;
    let reportUrl = `${API_BASE}/events/${currentEventId}/report`;
    if (label || url) {
        reportUrl += `?link_name=${encodeURIComponent(label)}&link_url=${encodeURIComponent(url)}`;
    }
    window.open(reportUrl, '_blank');
    closeModal('reportPromptModal');
}

function openEditDetails() {
    document.getElementById('edit-venue').value = document.getElementById('disp-venue').innerText === '-' ? '' : document.getElementById('disp-venue').innerText;
    document.getElementById('edit-time').value = document.getElementById('disp-time').innerText === '-' ? '' : document.getElementById('disp-time').innerText;
    document.getElementById('edit-type').value = document.getElementById('disp-type').innerText === '-' ? '' : document.getElementById('disp-type').innerText;
    document.getElementById('edit-participants').value = document.getElementById('disp-participants').innerText.replace('+', '');
    document.getElementById('edit-description').value = document.getElementById('disp-description').innerText === 'No description provided.' ? '' : document.getElementById('disp-description').innerText;
    document.getElementById('edit-organizers').value = document.getElementById('edit-organizers').getAttribute('data-current');
    openModal('editDetailsModal');
}

window.onload = showDashboard;
