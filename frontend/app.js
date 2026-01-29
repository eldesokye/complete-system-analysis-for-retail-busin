// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// Global State
let currentLanguage = 'en';
let trafficChart = null;
let sectionChart = null;

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    initializeNavigation();
    initializeUpload();
    initializeChatbot();
    loadDashboard();
    
    // Auto-refresh dashboard every 30 seconds
    setInterval(loadDashboard, 30000);
});

// Navigation
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Update active link
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            // Show corresponding page
            const page = link.dataset.page;
            showPage(page);
        });
    });
}

function showPage(pageName) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.classList.remove('active'));
    
    const targetPage = document.getElementById(`${pageName}-page`);
    if (targetPage) {
        targetPage.classList.add('active');
        
        // Load page-specific data
        if (pageName === 'dashboard') {
            loadDashboard();
        } else if (pageName === 'upload') {
            loadUploadedVideos();
        }
    }
}

// Dashboard Functions
async function loadDashboard() {
    try {
        await Promise.all([
            loadLiveAnalytics(),
            loadTrafficChart(),
            loadSectionChart(),
            loadPredictions(),
            loadRecommendations()
        ]);
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

async function loadLiveAnalytics() {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/live`);
        const data = await response.json();
        
        if (data.success) {
            const analytics = data.data;
            
            // Update stats
            document.getElementById('total-visitors').textContent = analytics.total_visitors || 0;
            document.getElementById('queue-length').textContent = analytics.current_queue_length || 0;
            document.getElementById('conversion-rate').textContent = `${analytics.conversion_rate || 0}%`;
            document.getElementById('peak-hour').textContent = `${analytics.peak_hour || 0}:00`;
            document.getElementById('busiest-section').textContent = analytics.busiest_section || 'N/A';
            
            // Update queue status
            const queueStatus = document.getElementById('queue-status');
            if (analytics.is_cashier_busy) {
                queueStatus.textContent = 'Busy';
                queueStatus.classList.add('busy');
            } else {
                queueStatus.textContent = 'Normal';
                queueStatus.classList.remove('busy');
            }
        }
    } catch (error) {
        console.error('Error loading live analytics:', error);
    }
}

async function loadTrafficChart() {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/hourly`);
        const data = await response.json();
        
        if (data.success && data.data.length > 0) {
            const hours = data.data.map(d => `${d.hour}:00`);
            const visitors = data.data.map(d => d.visitor_count);
            
            const ctx = document.getElementById('traffic-chart').getContext('2d');
            
            if (trafficChart) {
                trafficChart.destroy();
            }
            
            trafficChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: hours,
                    datasets: [{
                        label: 'Visitors',
                        data: visitors,
                        borderColor: '#6366f1',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(255, 255, 255, 0.05)'
                            },
                            ticks: {
                                color: '#94a3b8'
                            }
                        },
                        x: {
                            grid: {
                                color: 'rgba(255, 255, 255, 0.05)'
                            },
                            ticks: {
                                color: '#94a3b8'
                            }
                        }
                    }
                }
            });
        }
    } catch (error) {
        console.error('Error loading traffic chart:', error);
    }
}

async function loadSectionChart() {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/sections`);
        const data = await response.json();
        
        if (data.success && data.data.length > 0) {
            const sections = data.data.map(d => d.section_name);
            const visitors = data.data.map(d => d.total_visitors);
            
            const ctx = document.getElementById('section-chart').getContext('2d');
            
            if (sectionChart) {
                sectionChart.destroy();
            }
            
            sectionChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: sections,
                    datasets: [{
                        label: 'Visitors',
                        data: visitors,
                        backgroundColor: [
                            'rgba(99, 102, 241, 0.8)',
                            'rgba(236, 72, 153, 0.8)',
                            'rgba(16, 185, 129, 0.8)',
                            'rgba(245, 158, 11, 0.8)',
                            'rgba(59, 130, 246, 0.8)'
                        ],
                        borderRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(255, 255, 255, 0.05)'
                            },
                            ticks: {
                                color: '#94a3b8'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                color: '#94a3b8'
                            }
                        }
                    }
                }
            });
        }
    } catch (error) {
        console.error('Error loading section chart:', error);
    }
}

async function loadPredictions() {
    try {
        const response = await fetch(`${API_BASE_URL}/predictions/traffic?days_ahead=1`);
        const data = await response.json();
        
        if (data.success && data.data.length > 0) {
            const predictionsHtml = data.data.slice(0, 5).map(pred => `
                <div class="prediction-item">
                    <div class="prediction-time">${pred.prediction_hour}:00</div>
                    <div class="prediction-value">${pred.predicted_visitors} visitors expected</div>
                </div>
            `).join('');
            
            document.getElementById('predictions-list').innerHTML = predictionsHtml;
        } else {
            document.getElementById('predictions-list').innerHTML = '<p style="color: var(--text-muted);">No predictions available</p>';
        }
    } catch (error) {
        console.error('Error loading predictions:', error);
    }
}

async function loadRecommendations() {
    try {
        const response = await fetch(`${API_BASE_URL}/chatbot/active-recommendations`);
        const data = await response.json();
        
        if (data.success && data.data.length > 0) {
            document.getElementById('recommendations-count').textContent = data.data.length;
            
            const recommendationsHtml = data.data.map(rec => `
                <div class="recommendation-item ${rec.priority}">
                    <div class="recommendation-title">${rec.title}</div>
                    <div class="recommendation-desc">${rec.description}</div>
                </div>
            `).join('');
            
            document.getElementById('recommendations-list').innerHTML = recommendationsHtml;
        } else {
            document.getElementById('recommendations-count').textContent = '0';
            document.getElementById('recommendations-list').innerHTML = '<p style="color: var(--text-muted);">No recommendations</p>';
        }
    } catch (error) {
        console.error('Error loading recommendations:', error);
    }
}

// Chatbot Functions
function initializeChatbot() {
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const langBtns = document.querySelectorAll('.lang-btn');
    
    // Send message on Enter
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Language toggle
    langBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            langBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentLanguage = btn.dataset.lang;
        });
    });
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    input.value = '';
    
    // Show typing indicator
    const typingId = addTypingIndicator();
    
    try {
        const response = await fetch(`${API_BASE_URL}/chatbot/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: message,
                language: currentLanguage,
                session_id: 'default'
            })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        if (data.success) {
            addMessageToChat(data.response, 'bot');
        } else {
            addMessageToChat('Sorry, I encountered an error. Please try again.', 'bot');
        }
    } catch (error) {
        removeTypingIndicator(typingId);
        addMessageToChat('Sorry, I could not connect to the server.', 'bot');
        console.error('Error sending message:', error);
    }
}

function sendQuickQuestion(question) {
    document.getElementById('chat-input').value = question;
    sendMessage();
}

function addMessageToChat(text, sender) {
    const messagesContainer = document.getElementById('chat-messages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'user' ? 'U' : 'AI';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = text;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function addTypingIndicator() {
    const messagesContainer = document.getElementById('chat-messages');
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot typing-indicator';
    typingDiv.id = 'typing-' + Date.now();
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = 'AI';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = 'Typing...';
    
    typingDiv.appendChild(avatar);
    typingDiv.appendChild(content);
    
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return typingDiv.id;
}

function removeTypingIndicator(id) {
    const indicator = document.getElementById(id);
    if (indicator) {
        indicator.remove();
    }
}

// Upload Functions
function initializeUpload() {
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');
    const roleSelect = document.getElementById('video-role');
    const sectionNameGroup = document.getElementById('section-name-group');
    
    // Click to browse
    uploadZone.addEventListener('click', () => {
        fileInput.click();
    });
    
    // File selection
    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });
    
    // Drag and drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });
    
    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });
    
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });
    
    // Show/hide section name based on role
    roleSelect.addEventListener('change', () => {
        if (roleSelect.value === 'section') {
            sectionNameGroup.style.display = 'block';
        } else {
            sectionNameGroup.style.display = 'none';
        }
    });
}

async function handleFiles(files) {
    if (files.length === 0) return;
    
    const file = files[0];
    const role = document.getElementById('video-role').value;
    const sectionName = document.getElementById('section-name').value;
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('role', role);
    if (role === 'section' && sectionName) {
        formData.append('section_name', sectionName);
    }
    
    // Show progress
    const progressContainer = document.getElementById('upload-progress');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    
    progressContainer.style.display = 'block';
    progressFill.style.width = '0%';
    progressText.textContent = 'Uploading...';
    
    try {
        const xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                progressFill.style.width = percentComplete + '%';
                progressText.textContent = `Uploading... ${Math.round(percentComplete)}%`;
            }
        });
        
        xhr.addEventListener('load', () => {
            if (xhr.status === 200) {
                progressText.textContent = 'Upload complete!';
                setTimeout(() => {
                    progressContainer.style.display = 'none';
                    loadUploadedVideos();
                }, 2000);
            } else {
                progressText.textContent = 'Upload failed!';
            }
        });
        
        xhr.open('POST', `${API_BASE_URL}/upload/video`);
        xhr.send(formData);
        
    } catch (error) {
        console.error('Error uploading file:', error);
        progressText.textContent = 'Upload failed!';
    }
}

async function loadUploadedVideos() {
    try {
        const response = await fetch(`${API_BASE_URL}/upload/videos`);
        const data = await response.json();
        
        if (data.success && data.data.length > 0) {
            const videosHtml = data.data.map(video => `
                <div class="video-item">
                    <div class="video-info">
                        <h4>${video.filename}</h4>
                        <p>${video.size_mb} MB • ${new Date(video.created).toLocaleDateString()}</p>
                    </div>
                    <button class="delete-btn" onclick="deleteVideo('${video.filename}')">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
                            <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                </div>
            `).join('');
            
            document.getElementById('videos-list').innerHTML = videosHtml;
        } else {
            document.getElementById('videos-list').innerHTML = '<p style="color: var(--text-muted); text-align: center;">No videos uploaded yet</p>';
        }
    } catch (error) {
        console.error('Error loading videos:', error);
    }
}

async function deleteVideo(filename) {
    if (!confirm('Are you sure you want to delete this video?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/upload/video/${filename}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadUploadedVideos();
        }
    } catch (error) {
        console.error('Error deleting video:', error);
    }
}
