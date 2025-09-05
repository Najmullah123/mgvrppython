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
    switch(section) {
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

// Load dashboard data
async function loadDashboardData() {
    try {
        // Simulate API calls - replace with actual API endpoints
        const stats = await fetchBotStats();
        
        document.getElementById('total-vehicles').textContent = stats.totalVehicles || '0';
        document.getElementById('total-users').textContent = stats.totalUsers || '0';
        document.getElementById('active-sessions').textContent = stats.activeSessions || '0';
        document.getElementById('total-warnings').textContent = stats.totalWarnings || '0';
        
        document.getElementById('memory-usage').textContent = stats.memoryUsage || 'N/A';
        document.getElementById('uptime').textContent = stats.uptime || 'N/A';

        loadRecentActivity();
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showNotification('Error loading dashboard data', 'error');
    }
}

// Load recent activity
function loadRecentActivity() {
    const activities = [
        { icon: 'fas fa-car', text: 'New vehicle registered by User#1234', time: '2 minutes ago' },
        { icon: 'fas fa-gamepad', text: 'Session started by Host#5678', time: '5 minutes ago' },
        { icon: 'fas fa-coins', text: 'Economy transaction: $1000', time: '10 minutes ago' },
        { icon: 'fas fa-exclamation-triangle', text: 'Warning issued to User#9999', time: '15 minutes ago' },
        { icon: 'fas fa-user-plus', text: 'New user joined the server', time: '20 minutes ago' }
    ];

    const activityList = document.getElementById('recent-activity');
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
}

// Load vehicle data
async function loadVehicleData() {
    try {
        const vehicles = await fetchVehicles();
        botData.vehicles = vehicles;
        
        const tbody = document.querySelector('#vehicles-table tbody');
        tbody.innerHTML = vehicles.map(vehicle => `
            <tr>
                <td>${vehicle.plate}</td>
                <td>${vehicle.state}</td>
                <td>${vehicle.make}</td>
                <td>${vehicle.model}</td>
                <td>${vehicle.color}</td>
                <td>${vehicle.owner || 'Unknown'}</td>
                <td>${formatDate(vehicle.registeredAt)}</td>
                <td>
                    <button class="btn btn-secondary" onclick="editVehicle('${vehicle.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-danger" onclick="deleteVehicle('${vehicle.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');

        setupVehicleFilters();
    } catch (error) {
        console.error('Error loading vehicle data:', error);
        showNotification('Error loading vehicle data', 'error');
    }
}

// Load economy data
async function loadEconomyData() {
    try {
        const economyData = await fetchEconomyData();
        botData.economy = economyData.users || [];
        
        // Update economy stats
        const totalMoney = economyData.users.reduce((sum, user) => sum + user.balance + user.bank, 0);
        const avgBalance = economyData.users.length > 0 ? totalMoney / economyData.users.length : 0;
        const richestUser = economyData.users.reduce((max, user) => 
            (user.balance + user.bank) > (max.balance + max.bank) ? user : max, 
            { balance: 0, bank: 0, username: 'None' }
        );

        document.getElementById('total-money').textContent = `$${totalMoney.toLocaleString()}`;
        document.getElementById('avg-balance').textContent = `$${Math.round(avgBalance).toLocaleString()}`;
        document.getElementById('richest-user').textContent = richestUser.username;

        // Update economy table
        const tbody = document.querySelector('#economy-table tbody');
        tbody.innerHTML = economyData.users.map(user => `
            <tr>
                <td>${user.username}</td>
                <td>$${user.balance.toLocaleString()}</td>
                <td>$${user.bank.toLocaleString()}</td>
                <td>$${(user.balance + user.bank).toLocaleString()}</td>
                <td>${formatDate(user.lastActive)}</td>
                <td>
                    <button class="btn btn-primary" onclick="openEconomyAction('${user.id}')">
                        <i class="fas fa-coins"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading economy data:', error);
        showNotification('Error loading economy data', 'error');
    }
}

// Load session data
async function loadSessionData() {
    try {
        const sessions = await fetchSessions();
        botData.sessions = sessions;
        
        const sessionsList = document.getElementById('active-sessions-list');
        sessionsList.innerHTML = sessions.map(session => `
            <div class="session-card">
                <div class="session-header">
                    <h4>Session #${session.id}</h4>
                    <span class="session-status ${session.status.toLowerCase()}">${session.status}</span>
                </div>
                <div class="session-info">
                    <div class="session-info-item">
                        <label>Host</label>
                        <span>${session.host}</span>
                    </div>
                    <div class="session-info-item">
                        <label>Priority</label>
                        <span>${session.priority}</span>
                    </div>
                    <div class="session-info-item">
                        <label>FRP Speed</label>
                        <span>${session.frpSpeed} MPH</span>
                    </div>
                    <div class="session-info-item">
                        <label>Participants</label>
                        <span>${session.participants || 0}</span>
                    </div>
                </div>
                <div class="session-actions">
                    <button class="btn btn-primary" onclick="editSession('${session.id}')">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-danger" onclick="endSession('${session.id}')">
                        <i class="fas fa-stop"></i> End
                    </button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading session data:', error);
        showNotification('Error loading session data', 'error');
    }
}

// Load moderation data
async function loadModerationData() {
    try {
        const moderationData = await fetchModerationData();
        botData.moderation = moderationData.actions || [];
        
        // Update moderation stats
        document.getElementById('mod-total-warnings').textContent = moderationData.totalWarnings || '0';
        document.getElementById('active-timeouts').textContent = moderationData.activeTimeouts || '0';
        document.getElementById('recent-bans').textContent = moderationData.recentBans || '0';

        // Update moderation table
        const tbody = document.querySelector('#moderation-table tbody');
        tbody.innerHTML = moderationData.actions.map(action => `
            <tr>
                <td>${action.user}</td>
                <td>${action.action}</td>
                <td>${action.reason}</td>
                <td>${action.moderator}</td>
                <td>${formatDate(action.date)}</td>
                <td>
                    <span class="status ${action.status.toLowerCase()}">${action.status}</span>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading moderation data:', error);
        showNotification('Error loading moderation data', 'error');
    }
}

// Load user data
async function loadUserData() {
    try {
        const users = await fetchUsers();
        botData.users = users;
        
        const tbody = document.querySelector('#users-table tbody');
        tbody.innerHTML = users.map(user => `
            <tr>
                <td>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <img src="${user.avatar}" alt="${user.username}" style="width: 30px; height: 30px; border-radius: 50%;">
                        ${user.username}
                    </div>
                </td>
                <td>${user.id}</td>
                <td>${formatDate(user.joinedAt)}</td>
                <td>${user.roles.length} roles</td>
                <td>
                    <span class="status ${user.status.toLowerCase()}">${user.status}</span>
                </td>
                <td>
                    <button class="btn btn-primary" onclick="viewUser('${user.id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-danger" onclick="moderateUser('${user.id}')">
                        <i class="fas fa-gavel"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading user data:', error);
        showNotification('Error loading user data', 'error');
    }
}

// Setup event listeners
function setupEventListeners() {
    // Vehicle search
    const vehicleSearch = document.getElementById('vehicle-search');
    if (vehicleSearch) {
        vehicleSearch.addEventListener('input', filterVehicles);
    }

    // State filter
    const stateFilter = document.getElementById('state-filter');
    if (stateFilter) {
        stateFilter.addEventListener('change', filterVehicles);
    }

    // Moderation action change
    const modAction = document.getElementById('mod-action');
    if (modAction) {
        modAction.addEventListener('change', function() {
            const durationGroup = document.getElementById('duration-group');
            if (this.value === 'timeout') {
                durationGroup.style.display = 'block';
            } else {
                durationGroup.style.display = 'none';
            }
        });
    }
}

// Setup vehicle filters
function setupVehicleFilters() {
    const searchInput = document.getElementById('vehicle-search');
    const stateFilter = document.getElementById('state-filter');
    
    if (searchInput) {
        searchInput.addEventListener('input', filterVehicles);
    }
    
    if (stateFilter) {
        stateFilter.addEventListener('change', filterVehicles);
    }
}

// Filter vehicles
function filterVehicles() {
    const searchTerm = document.getElementById('vehicle-search').value.toLowerCase();
    const stateFilter = document.getElementById('state-filter').value;
    
    const rows = document.querySelectorAll('#vehicles-table tbody tr');
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        const plate = cells[0].textContent.toLowerCase();
        const state = cells[1].textContent;
        const make = cells[2].textContent.toLowerCase();
        const model = cells[3].textContent.toLowerCase();
        const color = cells[4].textContent.toLowerCase();
        const owner = cells[5].textContent.toLowerCase();
        
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
        owner: document.getElementById('vehicle-owner').value,
        make: document.getElementById('vehicle-make').value,
        model: document.getElementById('vehicle-model').value,
        color: document.getElementById('vehicle-color').value,
        state: document.getElementById('vehicle-state').value,
        plate: document.getElementById('vehicle-plate').value
    };

    try {
        await apiCall('/api/vehicles', 'POST', vehicleData);
        showNotification('Vehicle added successfully!', 'success');
        closeModal('addVehicleModal');
        loadVehicleData();
    } catch (error) {
        showNotification('Error adding vehicle: ' + error.message, 'error');
    }
}

function editVehicle(vehicleId) {
    // Implementation for editing vehicle
    showNotification('Edit vehicle functionality coming soon!', 'info');
}

async function deleteVehicle(vehicleId) {
    if (confirm('Are you sure you want to delete this vehicle?')) {
        try {
            await apiCall(`/api/vehicles/${vehicleId}`, 'DELETE');
            showNotification('Vehicle deleted successfully!', 'success');
            loadVehicleData();
        } catch (error) {
            showNotification('Error deleting vehicle: ' + error.message, 'error');
        }
    }
}

function exportVehicles() {
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
    const actionData = {
        user: document.getElementById('economy-user').value,
        action: document.getElementById('economy-action').value,
        amount: parseInt(document.getElementById('economy-amount').value),
        target: document.getElementById('economy-target').value,
        reason: document.getElementById('economy-reason').value
    };

    try {
        await apiCall('/api/economy/action', 'POST', actionData);
        showNotification('Economy action performed successfully!', 'success');
        closeModal('economyActionModal');
        loadEconomyData();
    } catch (error) {
        showNotification('Error performing economy action: ' + error.message, 'error');
    }
}

// Session functions
async function createSession() {
    const sessionData = {
        host: document.getElementById('session-host').value,
        cohost: document.getElementById('session-cohost').value,
        priority: document.getElementById('session-priority').value,
        frpSpeed: parseInt(document.getElementById('session-frp').value),
        houseClaming: document.getElementById('session-housing').value === 'true',
        link: document.getElementById('session-link').value
    };

    try {
        await apiCall('/api/sessions', 'POST', sessionData);
        showNotification('Session created successfully!', 'success');
        closeModal('createSessionModal');
        loadSessionData();
    } catch (error) {
        showNotification('Error creating session: ' + error.message, 'error');
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
    const actionData = {
        user: document.getElementById('mod-user').value,
        action: document.getElementById('mod-action').value,
        duration: document.getElementById('mod-duration').value,
        reason: document.getElementById('mod-reason').value
    };

    try {
        await apiCall('/api/moderation/action', 'POST', actionData);
        showNotification('Moderation action performed successfully!', 'success');
        closeModal('moderationActionModal');
        loadModerationData();
    } catch (error) {
        showNotification('Error performing moderation action: ' + error.message, 'error');
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
        botPrefix: document.getElementById('bot-prefix').value,
        currencySymbol: document.getElementById('currency-symbol').value,
        dailyReward: parseInt(document.getElementById('daily-reward').value),
        weeklyReward: parseInt(document.getElementById('weekly-reward').value),
        autobanThreshold: parseInt(document.getElementById('autoban-threshold').value),
        defaultTimeout: parseInt(document.getElementById('default-timeout').value)
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
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
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
}

// API functions (mock implementations - replace with actual API calls)
async function apiCall(endpoint, method = 'GET', data = null) {
    // Mock API implementation
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (Math.random() > 0.1) { // 90% success rate
                resolve({ success: true, data: data });
            } else {
                reject(new Error('API call failed'));
            }
        }, 500);
    });
}

async function fetchBotStats() {
    // Mock data - replace with actual API call
    return {
        totalVehicles: 1247,
        totalUsers: 3456,
        activeSessions: 5,
        totalWarnings: 89,
        memoryUsage: '245 MB',
        uptime: '7d 14h 32m'
    };
}

async function fetchVehicles() {
    // Mock data - replace with actual API call
    return [
        {
            id: '1',
            plate: 'ABC123',
            state: 'TX',
            make: 'Ford',
            model: 'Explorer',
            color: 'Blue',
            owner: 'User#1234',
            registeredAt: '2024-01-15T10:30:00Z'
        },
        {
            id: '2',
            plate: 'XYZ789',
            state: 'CA',
            make: 'Chevrolet',
            model: 'Tahoe',
            color: 'Black',
            owner: 'User#5678',
            registeredAt: '2024-01-16T14:20:00Z'
        }
    ];
}

async function fetchEconomyData() {
    // Mock data - replace with actual API call
    return {
        users: [
            {
                id: '1',
                username: 'User#1234',
                balance: 5000,
                bank: 15000,
                lastActive: '2024-01-20T12:00:00Z'
            },
            {
                id: '2',
                username: 'User#5678',
                balance: 2500,
                bank: 7500,
                lastActive: '2024-01-19T18:30:00Z'
            }
        ]
    };
}

async function fetchSessions() {
    // Mock data - replace with actual API call
    return [
        {
            id: '1',
            host: 'Host#1234',
            status: 'Active',
            priority: 'High',
            frpSpeed: 80,
            participants: 15,
            createdAt: '2024-01-20T15:00:00Z'
        },
        {
            id: '2',
            host: 'Host#5678',
            status: 'Setup',
            priority: 'Medium',
            frpSpeed: 70,
            participants: 0,
            createdAt: '2024-01-20T16:00:00Z'
        }
    ];
}

async function fetchModerationData() {
    // Mock data - replace with actual API call
    return {
        totalWarnings: 89,
        activeTimeouts: 12,
        recentBans: 3,
        actions: [
            {
                user: 'User#1234',
                action: 'Warning',
                reason: 'Spam',
                moderator: 'Mod#5678',
                date: '2024-01-20T10:00:00Z',
                status: 'Active'
            },
            {
                user: 'User#9999',
                action: 'Timeout',
                reason: 'Inappropriate behavior',
                moderator: 'Mod#1111',
                date: '2024-01-20T11:30:00Z',
                status: 'Active'
            }
        ]
    };
}

async function fetchUsers() {
    // Mock data - replace with actual API call
    return [
        {
            id: '1',
            username: 'User#1234',
            avatar: 'https://cdn.discordapp.com/embed/avatars/0.png',
            joinedAt: '2024-01-01T00:00:00Z',
            roles: ['Member', 'Verified'],
            status: 'Online'
        },
        {
            id: '2',
            username: 'User#5678',
            avatar: 'https://cdn.discordapp.com/embed/avatars/1.png',
            joinedAt: '2024-01-02T00:00:00Z',
            roles: ['Member'],
            status: 'Offline'
        }
    ];
}