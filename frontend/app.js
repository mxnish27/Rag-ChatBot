// API Configuration
let API_URL = localStorage.getItem('apiUrl') || 'http://localhost:8000';
let API_KEY = localStorage.getItem('apiKey') || '';

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const questionInput = document.getElementById('questionInput');
const uploadBtn = document.getElementById('uploadBtn');
const uploadModal = document.getElementById('uploadModal');
const closeModal = document.getElementById('closeModal');
const fileInput = document.getElementById('fileInput');
const uploadSubmit = document.getElementById('uploadSubmit');
const uploadStatus = document.getElementById('uploadStatus');
const uploadMessage = document.getElementById('uploadMessage');
const apiUrlInput = document.getElementById('apiUrl');
const apiKeyInput = document.getElementById('apiKey');
const refreshStats = document.getElementById('refreshStats');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    apiUrlInput.value = API_URL;
    apiKeyInput.value = API_KEY;
    loadStats();
});

// Save settings on change
apiUrlInput.addEventListener('change', () => {
    API_URL = apiUrlInput.value;
    localStorage.setItem('apiUrl', API_URL);
});

apiKeyInput.addEventListener('change', () => {
    API_KEY = apiKeyInput.value;
    localStorage.setItem('apiKey', API_KEY);
});

// Chat functionality
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const question = questionInput.value.trim();
    
    if (!question) return;
    
    // Clear input
    questionInput.value = '';
    
    // Add user message
    addMessage(question, 'user');
    
    // Show typing indicator
    const typingId = addTypingIndicator();
    
    try {
        const response = await fetch(`${API_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(API_KEY && { 'X-API-Key': API_KEY })
            },
            body: JSON.stringify({ question })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        // Add bot response
        addMessage(data.answer, 'bot', data.sources);
        
    } catch (error) {
        removeTypingIndicator(typingId);
        addMessage(`Error: ${error.message}. Please check your API URL and try again.`, 'error');
    }
});

// Add message to chat
function addMessage(text, type, sources = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message flex ${type === 'user' ? 'justify-end' : 'justify-start'}`;
    
    let content = '';
    
    if (type === 'user') {
        content = `
            <div class="bg-indigo-600 text-white rounded-lg px-4 py-3 max-w-md">
                <p>${escapeHtml(text)}</p>
            </div>
        `;
    } else if (type === 'bot') {
        const sourcesHtml = sources && sources.length > 0 ? `
            <div class="mt-3 pt-3 border-t border-gray-200">
                <p class="text-xs font-semibold text-gray-600 mb-2">Sources (${sources.length}):</p>
                ${sources.map((source, idx) => `
                    <div class="text-xs text-gray-600 mb-1">
                        <i class="fas fa-file-alt mr-1"></i>
                        <span class="font-medium">${escapeHtml(source.source.split('/').pop())}</span>
                    </div>
                `).join('')}
            </div>
        ` : '';
        
        content = `
            <div class="bg-gray-100 text-gray-800 rounded-lg px-4 py-3 max-w-2xl">
                <div class="flex items-start space-x-2 mb-2">
                    <i class="fas fa-robot text-indigo-600 mt-1"></i>
                    <p class="flex-1">${escapeHtml(text).replace(/\n/g, '<br>')}</p>
                </div>
                ${sourcesHtml}
            </div>
        `;
    } else if (type === 'error') {
        content = `
            <div class="bg-red-100 text-red-800 rounded-lg px-4 py-3 max-w-md">
                <i class="fas fa-exclamation-circle mr-2"></i>
                <span>${escapeHtml(text)}</span>
            </div>
        `;
    }
    
    messageDiv.innerHTML = content;
    
    // Remove welcome message if exists
    const welcomeMsg = chatMessages.querySelector('.text-center');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Typing indicator
function addTypingIndicator() {
    const id = 'typing-' + Date.now();
    const typingDiv = document.createElement('div');
    typingDiv.id = id;
    typingDiv.className = 'chat-message flex justify-start';
    typingDiv.innerHTML = `
        <div class="bg-gray-100 text-gray-800 rounded-lg px-4 py-3">
            <div class="typing-indicator flex space-x-1">
                <span class="w-2 h-2 bg-gray-500 rounded-full"></span>
                <span class="w-2 h-2 bg-gray-500 rounded-full"></span>
                <span class="w-2 h-2 bg-gray-500 rounded-full"></span>
            </div>
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}

// Upload modal
uploadBtn.addEventListener('click', () => {
    uploadModal.classList.remove('hidden');
});

closeModal.addEventListener('click', () => {
    uploadModal.classList.add('hidden');
    uploadStatus.classList.add('hidden');
});

uploadSubmit.addEventListener('click', async () => {
    const files = fileInput.files;
    
    if (files.length === 0) {
        showUploadStatus('Please select at least one file', 'error');
        return;
    }
    
    const formData = new FormData();
    for (let file of files) {
        formData.append('files', file);
    }
    
    uploadSubmit.disabled = true;
    uploadSubmit.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Uploading...';
    
    try {
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            headers: {
                ...(API_KEY && { 'X-API-Key': API_KEY })
            },
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        showUploadStatus(
            `Success! Processed ${data.files_processed} files into ${data.chunks_created} chunks.`,
            'success'
        );
        
        // Reset form
        fileInput.value = '';
        
        // Refresh stats
        loadStats();
        
        // Close modal after 2 seconds
        setTimeout(() => {
            uploadModal.classList.add('hidden');
            uploadStatus.classList.add('hidden');
        }, 2000);
        
    } catch (error) {
        showUploadStatus(`Error: ${error.message}`, 'error');
    } finally {
        uploadSubmit.disabled = false;
        uploadSubmit.innerHTML = '<i class="fas fa-upload mr-2"></i>Upload Files';
    }
});

function showUploadStatus(message, type) {
    uploadStatus.classList.remove('hidden');
    uploadMessage.textContent = message;
    
    if (type === 'success') {
        uploadStatus.querySelector('div').className = 'bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded';
    } else {
        uploadStatus.querySelector('div').className = 'bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded';
    }
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/stats`, {
            headers: {
                ...(API_KEY && { 'X-API-Key': API_KEY })
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        document.getElementById('docCount').textContent = data.documents_in_library;
        document.getElementById('uploadCount').textContent = data.uploaded_documents;
        document.getElementById('vectorStore').textContent = data.vector_store;
        
    } catch (error) {
        console.error('Error loading stats:', error);
        document.getElementById('docCount').textContent = 'Error';
        document.getElementById('uploadCount').textContent = 'Error';
        document.getElementById('vectorStore').textContent = 'Error';
    }
}

refreshStats.addEventListener('click', loadStats);

// Utility function
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
