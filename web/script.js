// Global variables
let currentSection = 'dashboard';
let botData = {
    vehicles: [],
    users: [],
    sessions: [],
    economy: [],
    moderation: []
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    loadDashboardData();
    setupEventListeners();
    populateStateSelects();
    
    // Auto-refresh data every 30 seconds
    setInterval(refreshCurrentSection, 30000);
});

// Initialize application
function initializeApp() {
    // Set up navigation
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.dataset.section;
            switchSection(section);
        });
    });

    // Set up modal close functionality
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            closeModal(e.target.id);
        }
    });

    // Set up mobile menu toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }

    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            const sidebar = document.querySelector('.sidebar');
            const menuToggle = document.querySelector('.menu-toggle');
            
            if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                sidebar.classList.remove('active');
            }
        }
    });
}

// Switch between sections
function switchSection(section) {
    // Update navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-section="${section}"]`).classList.add('active');

    // Update content
    document.querySelectorAll('.content-section').forEach(sec => {
        sec.classList.remove('active');
    });
    document.getElementById(section).classList.add('active');

    // Update page title
    const titles = {
        dashboard: 'Dashboard',
        vehicles: 'Vehicle Management',
        economy: 'Economy System',
        sessions: 'Session Management',
        moderation: 'Moderation Tools',
        users: 'User Management',
        settings: 'Bot Settings'
    };
    document.getElementById('page-title').textContent = titles[section];

    currentSection = section;

    // Load section-specific data
    loadSectionData(section);
    
    // Close mobile menu
    if (window.innerWidth <= 768) {
        document.querySelector('.sidebar').classList.remove('active');
    }
}

// Load section-specific data
function loadSectionData(section) {
    switch(section) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'vehicles':
            loadVehicleData();
            break;
        case 'economy':
            loadEconomyData();
            break;
        case 'sessions':
            loadSessionData();
            break;
        case 'moderation':
            loadModerationData();
            break;
        case 'users':
            loadUserData();
            break;
    }
}

// Refresh current section data
function refreshCurrentSection() {
    loadSectionData(currentSection);
}

// Load dashboard data
async function loadDashboardData() {
    try {
        showLoading('dashboard-stats');
        
        const stats = await apiCall('/api/stats');
        
        // Update stat cards with animation
        updateStatCard('total-vehicles', stats.totalVehicles);
        updateStatCard('total-users', stats.totalUsers);
        updateStatCard('active-sessions', stats.activeSessions);
        updateStatCard('total-warnings', stats.totalWarnings);
        
        updateStatCard('memory-usage', stats.memoryUsage);
        updateStatCard('cpu-usage', stats.cpuUsage);
        updateStatCard('uptime', stats.uptime);
        updateStatCard('guild-count', stats.guildCount);
        updateStatCard('member-count', stats.memberCount);

        // Update status indicator
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.querySelector('.status-indicator span:last-child');
        if (stats.botStatus === 'online') {
            statusDot.classList.add('online');
            statusText.textContent = 'Bot Online';
        } else {
            statusDot.classList.remove('online');
            statusText.textContent = 'Bot Offline';
        }

        await loadRecentActivity();
        hideLoading('dashboard-stats');
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showNotification('Error loading dashboard data', 'error');
        hideLoading('dashboard-stats');
    }
}

// Update stat card with animation
function updateStatCard(id, value) {
    const element = document.getElementById(id);
    if (element) {
        const currentValue = element.textContent;
        if (currentValue !== value.toString()) {
            element.style.transform = 'scale(1.1)';
            element.textContent = value;
            setTimeout(() => {
                element.style.transform = 'scale(1)';
            }, 200);
        }
    }
}

// Load recent activity from real data
async function loadRecentActivity() {
    try {
        const activities = await apiCall('/api/recent-activity');
        
        const activityList = document.getElementById('recent-activity');
        if (activities.length === 0) {
            activityList.innerHTML = '<div class="activity-item"><div class="activity-info"><p>No recent activity</p></div></div>';
            return;
        }
        
        activityList.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon">
                    <i class="${activity.icon}"></i>
                </div>
                <div class="activity-info">
                    <p>${activity.text}</p>
                    <span class="activity-time">${activity.time}</span>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading recent activity:', error);
        document.getElementById('recent-activity').innerHTML = 
            '<div class="activity-item"><div class="activity-info"><p>Error loading activity</p></div></div>';
    }
}

// Load vehicle data from real JSON
async function loadVehicleData() {
    try {
        showLoading('vehicles-table');
        
        const vehicles = await apiCall('/api/vehicles');
        botData.vehicles = vehicles;
        
        const tbody = document.querySelector('#vehicles-table tbody');
        if (vehicles.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="text-center">No vehicles registered</td></tr>';
        } else {
            tbody.innerHTML = vehicles.map((vehicle, index) => `
                <tr>
                    <td><strong>${vehicle.plate}</strong></td>
                    <td><span class="badge">${vehicle.state}</span></td>
                    <td>${vehicle.make}</td>
                    <td>${vehicle.model}</td>
                    <td>${vehicle.color}</td>
                    <td>
                        <div class="user-cell">
                            ${vehicle.ownerAvatar ? `<img src="${vehicle.ownerAvatar}" alt="Avatar" class="user-avatar-small">` : ''}
                            <span>${vehicle.ownerName || 'Unknown'}</span>
                        </div>
                    </td>
                    <td>${formatDate(vehicle.registeredAt)}</td>
                    <td>
                        <div class="action-buttons">
                            <button class="btn-icon btn-secondary" onclick="editVehicle(${index})" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn-icon btn-danger" onclick="deleteVehicle(${index})" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');
        }

        setupVehicleFilters();
        hideLoading('vehicles-table');
    } catch (error) {
        console.error('Error loading vehicle data:', error);
        showNotification('Error loading vehicle data', 'error');
        hideLoading('vehicles-table');
    }
}

// Load economy data from real JSON
async function loadEconomyData() {
    try {
        showLoading('economy-table');
        
        const economyData = await apiCall('/api/economy');
        botData.economy = economyData.users || [];
        
        // Update economy stats
        document.getElementById('total-money').textContent = `$${economyData.totalMoney.toLocaleString()}`;
        document.getElementById('avg-balance').textContent = `$${Math.round(economyData.averageWealth).toLocaleString()}`;
        document.getElementById('richest-user').textContent = economyData.richestUser;

        // Update economy table
        const tbody = document.querySelector('#economy-table tbody');
        if (economyData.users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No economy data available</td></tr>';
        } else {
            tbody.innerHTML = economyData.users.slice(0, 50).map(user => `
                <tr>
                    <td>
                        <div class="user-cell">
                            ${user.avatar ? `<img src="${user.avatar}" alt="Avatar" class="user-avatar-small">` : ''}
                            <span>${user.username}</span>
                        </div>
                    </td>
                    <td class="font-mono">$${user.balance.toLocaleString()}</td>
                    <td class="font-mono">$${user.bank.toLocaleString()}</td>
                    <td class="font-mono font-bold">$${user.total.toLocaleString()}</td>
                    <td>${formatDate(user.lastDaily || user.lastWork)}</td>
                    <td>
                        <button class="btn btn-primary btn-sm" onclick="openEconomyAction('${user.id}')">
                            <i class="fas fa-coins"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        }
        
        hideLoading('economy-table');
    } catch (error) {
        console.error('Error loading economy data:', error);
        showNotification('Error loading economy data', 'error');
        hideLoading('economy-table');
    }
}

// Load session data from real JSON
async function loadSessionData() {
    try {
        showLoading('sessions-list');
        
        const sessions = await apiCall('/api/sessions');
        botData.sessions = sessions;
        
        const sessionsList = document.getElementById('active-sessions-list');
        if (sessions.length === 0) {
            sessionsList.innerHTML = '<div class="empty-state"><p>No sessions found</p></div>';
        } else {
            sessionsList.innerHTML = sessions.filter(session => session.status !== 'Ended').map(session => `
                <div class="session-card glass">
                    <div class="session-header">
                        <h4>Session #${session.id}</h4>
                        <span class="session-status ${session.status.toLowerCase().replace(' ', '-')}">${session.status}</span>
                    </div>
                    <div class="session-info">
                        <div class="session-info-item">
                            <label>Host</label>
                            <span>${session.hostName || 'Unknown'}</span>
                        </div>
                        <div class="session-info-item">
                            <label>Priority</label>
                            <span>${session.priority || 'Unknown'}</span>
                        </div>
                        <div class="session-info-item">
                            <label>FRP Speed</label>
                            <span>${session.frp_speed || 'Unknown'} MPH</span>
                        </div>
                        <div class="session-info-item">
                            <label>Participants</label>
                            <span>${session.participants ? session.participants.length : 0}</span>
                        </div>
                    </div>
                    <div class="session-actions">
                        <button class="btn btn-primary btn-sm" onclick="editSession('${session.id}')">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="endSession('${session.id}')">
                            <i class="fas fa-stop"></i> End
                        </button>
                    </div>
                </div>
            `).join('');
        }
        
        hideLoading('sessions-list');
    } catch (error) {
        console.error('Error loading session data:', error);
        showNotification('Error loading session data', 'error');
        hideLoading('sessions-list');
    }
}

// Load moderation data from real JSON
async function loadModerationData() {
    try {
        showLoading('moderation-table');
        
        const moderationData = await apiCall('/api/moderation');
        botData.moderation = moderationData.warnings || [];
        
        // Update moderation stats
        document.getElementById('mod-total-warnings').textContent = moderationData.totalWarnings || '0';
        document.getElementById('active-timeouts').textContent = moderationData.activeTimeouts || '0';
        document.getElementById('recent-bans').textContent = moderationData.recentBans || '0';

        // Update moderation table
        const tbody = document.querySelector('#moderation-table tbody');
        if (moderationData.warnings.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No moderation actions found</td></tr>';
        } else {
            tbody.innerHTML = moderationData.warnings.map(action => `
                <tr>
                    <td>
                        <div class="user-cell">
                            ${action.userAvatar ? `<img src="${action.userAvatar}" alt="Avatar" class="user-avatar-small">` : ''}
                            <span>${action.userName}</span>
                        </div>
                    </td>
                    <td><span class="badge badge-warning">Warning</span></td>
                    <td>${action.reason}</td>
                    <td>${action.moderatorName}</td>
                    <td>${formatDate(action.timestamp)}</td>
                    <td>
                        <span class="status ${action.status.toLowerCase()}">${action.status}</span>
                    </td>
                </tr>
            `).join('');
        }
        
        hideLoading('moderation-table');
    } catch (error) {
        console.error('Error loading moderation data:', error);
        showNotification('Error loading moderation data', 'error');
        hideLoading('moderation-table');
    }
}

// Load user data
async function loadUserData() {
    try {
        showLoading('users-table');
        
        const users = await apiCall('/api/users');
        botData.users = users;
        
        const tbody = document.querySelector('#users-table tbody');
        if (users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No users found</td></tr>';
        } else {
            tbody.innerHTML = users.map(user => `
                <tr>
                    <td>
                        <div class="user-cell">
                            <img src="${user.avatar}" alt="${user.username}" class="user-avatar-small">
                            <div>
                                <div class="font-semibold">${user.username}</div>
                                <div class="text-xs text-gray-500">#${user.discriminator}</div>
                            </div>
                        </div>
                    </td>
                    <td class="font-mono text-sm">${user.id}</td>
                    <td>${formatDate(user.joinedAt)}</td>
                    <td>
                        <span class="badge">${user.roles.length} roles</span>
                        ${user.permissions.administrator ? '<span class="badge badge-danger">Admin</span>' : ''}
                    </td>
                    <td>
                        <span class="status ${user.status.toLowerCase()}">${user.status}</span>
                        ${user.isBot ? '<span class="badge badge-secondary">Bot</span>' : ''}
                    </td>
                    <td>
                        <div class="action-buttons">
                            <button class="btn-icon btn-primary" onclick="viewUser('${user.id}')" title="View">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn-icon btn-danger" onclick="moderateUser('${user.id}')" title="Moderate">
                                <i class="fas fa-gavel"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');
        }
        
        hideLoading('users-table');
    } catch (error) {
        console.error('Error loading user data:', error);
        showNotification('Error loading user data', 'error');
        hideLoading('users-table');
    }
}

// Setup event listeners
function setupEventListeners() {
    // Vehicle search
    const vehicleSearch = document.getElementById('vehicle-search');
    if (vehicleSearch) {
        vehicleSearch.addEventListener('input', debounce(filterVehicles, 300));
    }

    // State filter
    const stateFilter = document.getElementById('state-filter');
    if (stateFilter) {
        stateFilter.addEventListener('change', filterVehicles);
    }

    // Form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
        });
    });
}

// Setup vehicle filters
function setupVehicleFilters() {
    const searchInput = document.getElementById('vehicle-search');
    const stateFilter = document.getElementById('state-filter');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterVehicles, 300));
    }
    
    if (stateFilter) {
        stateFilter.addEventListener('change', filterVehicles);
    }
}

// Filter vehicles
function filterVehicles() {
    const searchTerm = document.getElementById('vehicle-search')?.value.toLowerCase() || '';
    const stateFilter = document.getElementById('state-filter')?.value || '';
    
    const rows = document.querySelectorAll('#vehicles-table tbody tr');
    
    rows.forEach(row => {
        if (row.cells.length < 8) return; // Skip empty state rows
        
        const plate = row.cells[0].textContent.toLowerCase();
        const state = row.cells[1].textContent;
        const make = row.cells[2].textContent.toLowerCase();
        const model = row.cells[3].textContent.toLowerCase();
        const color = row.cells[4].textContent.toLowerCase();
        const owner = row.cells[5].textContent.toLowerCase();
        
        const matchesSearch = !searchTerm || 
            plate.includes(searchTerm) || 
            make.includes(searchTerm) || 
            model.includes(searchTerm) || 
            color.includes(searchTerm) || 
            owner.includes(searchTerm);
            
        const matchesState = !stateFilter || state === stateFilter;
        
        row.style.display = matchesSearch && matchesState ? '' : 'none';
    });
}

// Populate state selects
function populateStateSelects() {
    const states = [
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL',
        'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT',
        'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI',
        'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
    ];

    const stateSelects = document.querySelectorAll('#state-filter, #vehicle-state');
    stateSelects.forEach(select => {
        if (select.id === 'state-filter') {
            select.innerHTML = '<option value="">All States</option>' + 
                states.map(state => `<option value="${state}">${state}</option>`).join('');
        } else {
            select.innerHTML = '<option value="">Select State</option>' + 
                states.map(state => `<option value="${state}">${state}</option>`).join('');
        }
    });
}

// Modal functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Focus first input
        const firstInput = modal.querySelector('input, select, textarea');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
        
        // Reset form if exists
        const form = modal.querySelector('form');
        if (form) {
            form.reset();
        }
    }
}

// Vehicle functions
async function addVehicle() {
    const form = document.getElementById('addVehicleForm');
    const formData = new FormData(form);
    
    const vehicleData = {
        owner: formData.get('owner'),
        make: formData.get('make'),
        model: formData.get('model'),
        color: formData.get('color'),
        state: formData.get('state'),
        plate: formData.get('plate')
    };

    // Validate required fields
    if (!vehicleData.owner || !vehicleData.make || !vehicleData.model || 
        !vehicleData.color || !vehicleData.state || !vehicleData.plate) {
        showNotification('Please fill in all required fields', 'error');
        return;
    }

    try {
        showButtonLoading('add-vehicle-btn');
        await apiCall('/api/vehicles', 'POST', vehicleData);
        showNotification('Vehicle added successfully!', 'success');
        closeModal('addVehicleModal');
        loadVehicleData();
    } catch (error) {
        showNotification('Error adding vehicle: ' + error.message, 'error');
    } finally {
        hideButtonLoading('add-vehicle-btn', 'Add Vehicle');
    }
}

function editVehicle(vehicleIndex) {
    showNotification('Edit vehicle functionality coming soon!', 'info');
}

async function deleteVehicle(vehicleIndex) {
    if (confirm('Are you sure you want to delete this vehicle?')) {
        try {
            await apiCall(`/api/vehicles/${vehicleIndex}`, 'DELETE');
            showNotification('Vehicle deleted successfully!', 'success');
            loadVehicleData();
        } catch (error) {
            showNotification('Error deleting vehicle: ' + error.message, 'error');
        }
    }
}

function exportVehicles() {
    if (botData.vehicles.length === 0) {
        showNotification('No vehicles to export', 'error');
        return;
    }
    
    const csv = convertToCSV(botData.vehicles);
    downloadCSV(csv, 'vehicles.csv');
    showNotification('Vehicles exported successfully!', 'success');
}

// Economy functions
function openEconomyAction(userId) {
    document.getElementById('economy-user').value = userId;
    openModal('economyActionModal');
}

async function performEconomyAction() {
    const form = document.getElementById('economyActionForm');
    const formData = new FormData(form);
    
    const actionData = {
        user: formData.get('user'),
        action: formData.get('action'),
        amount: parseInt(formData.get('amount')),
        target: formData.get('target'),
        reason: formData.get('reason')
    };

    if (!actionData.user || !actionData.action || !actionData.amount || !actionData.target) {
        showNotification('Please fill in all required fields', 'error');
        return;
    }

    try {
        showButtonLoading('economy-action-btn');
        await apiCall('/api/economy/action', 'POST', actionData);
        showNotification('Economy action performed successfully!', 'success');
        closeModal('economyActionModal');
        loadEconomyData();
    } catch (error) {
        showNotification('Error performing economy action: ' + error.message, 'error');
    } finally {
        hideButtonLoading('economy-action-btn', 'Execute');
    }
}

// Session functions
async function createSession() {
    const form = document.getElementById('createSessionForm');
    const formData = new FormData(form);
    
    const sessionData = {
        host: formData.get('host'),
        cohost: formData.get('cohost'),
        priority: formData.get('priority'),
        frpSpeed: parseInt(formData.get('frp')),
        houseClaming: formData.get('housing') === 'true',
        link: formData.get('link')
    };

    try {
        showButtonLoading('create-session-btn');
        await apiCall('/api/sessions', 'POST', sessionData);
        showNotification('Session created successfully!', 'success');
        closeModal('createSessionModal');
        loadSessionData();
    } catch (error) {
        showNotification('Error creating session: ' + error.message, 'error');
    } finally {
        hideButtonLoading('create-session-btn', 'Create Session');
    }
}

function editSession(sessionId) {
    showNotification('Edit session functionality coming soon!', 'info');
}

async function endSession(sessionId) {
    if (confirm('Are you sure you want to end this session?')) {
        try {
            await apiCall(`/api/sessions/${sessionId}/end`, 'POST');
            showNotification('Session ended successfully!', 'success');
            loadSessionData();
        } catch (error) {
            showNotification('Error ending session: ' + error.message, 'error');
        }
    }
}

// Moderation functions
async function performModerationAction() {
    const form = document.getElementById('moderationActionForm');
    const formData = new FormData(form);
    
    const actionData = {
        user: formData.get('user'),
        action: formData.get('action'),
        duration: formData.get('duration'),
        reason: formData.get('reason')
    };

    try {
        showButtonLoading('mod-action-btn');
        await apiCall('/api/moderation/action', 'POST', actionData);
        showNotification('Moderation action performed successfully!', 'success');
        closeModal('moderationActionModal');
        loadModerationData();
    } catch (error) {
        showNotification('Error performing moderation action: ' + error.message, 'error');
    } finally {
        hideButtonLoading('mod-action-btn', 'Execute');
    }
}

// User functions
function viewUser(userId) {
    showNotification('View user functionality coming soon!', 'info');
}

function moderateUser(userId) {
    document.getElementById('mod-user').value = userId;
    openModal('moderationActionModal');
}

function refreshUsers() {
    loadUserData();
    showNotification('User data refreshed!', 'success');
}

// Settings functions
async function saveSettings() {
    const settings = {
        botPrefix: document.getElementById('bot-prefix')?.value,
        currencySymbol: document.getElementById('currency-symbol')?.value,
        dailyReward: parseInt(document.getElementById('daily-reward')?.value || 0),
        weeklyReward: parseInt(document.getElementById('weekly-reward')?.value || 0),
        autobanThreshold: parseInt(document.getElementById('autoban-threshold')?.value || 0),
        defaultTimeout: parseInt(document.getElementById('default-timeout')?.value || 0)
    };

    try {
        await apiCall('/api/settings', 'POST', settings);
        showNotification('Settings saved successfully!', 'success');
    } catch (error) {
        showNotification('Error saving settings: ' + error.message, 'error');
    }
}

// Utility functions
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch {
        return 'Invalid Date';
    }
}

function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(n => n.remove());
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.opacity = '0.5';
        element.style.pointerEvents = 'none';
    }
}

function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.opacity = '1';
        element.style.pointerEvents = 'auto';
    }
}

function showButtonLoading(buttonId) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = true;
        button.innerHTML = '<span class="loading"></span> Loading...';
    }
}

function hideButtonLoading(buttonId, originalText) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = false;
        button.innerHTML = originalText;
    }
}

function convertToCSV(data) {
    if (!data.length) return '';
    
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
    ].join('\n');
    
    return csvContent;
}

function downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', filename);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// API functions
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(endpoint, options);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Add CSS for additional components
const additionalCSS = `
.user-cell {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.user-avatar-small {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: 1px solid var(--gray-300);
}

.badge {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    font-weight: 600;
    border-radius: 0.375rem;
    background: var(--gray-100);
    color: var(--gray-700);
}

.badge-danger {
    background: var(--apple-red);
    color: white;
}

.badge-warning {
    background: var(--apple-orange);
    color: white;
}

.badge-secondary {
    background: var(--gray-400);
    color: white;
}

.btn-icon {
    padding: 0.5rem;
    border: none;
    border-radius: 0.375rem;
    cursor: pointer;
    transition: all 0.2s;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
}

.btn-sm {
    padding: 0.375rem 0.75rem;
    font-size: 0.75rem;
}

.action-buttons {
    display: flex;
    gap: 0.25rem;
}

.empty-state {
    text-align: center;
    padding: 2rem;
    color: var(--gray-500);
}

.session-status {
    padding: 0.25rem 0.5rem;
    border-radius: 0.375rem;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}

.session-status.setting-up {
    background: var(--apple-orange);
    color: white;
}

.session-status.early-access {
    background: var(--apple-blue);
    color: white;
}

.session-status.public {
    background: var(--apple-green);
    color: white;
}

.session-status.ended {
    background: var(--gray-400);
    color: white;
}

.status.online {
    color: var(--apple-green);
    font-weight: 600;
}

.status.offline {
    color: var(--gray-400);
    font-weight: 600;
}

.status.active {
    color: var(--apple-green);
    font-weight: 600;
}
`;

// Inject additional CSS
const style = document.createElement('style');
style.textContent = additionalCSS;
document.head.appendChild(style);