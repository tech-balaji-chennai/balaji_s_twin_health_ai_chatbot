// --- 1. Global Variables and Session ID Generation ---
const chatWindow = document.getElementById('chat-window');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const scrollUpBtn = document.getElementById('scroll-up-btn');
const scrollDownBtn = document.getElementById('scroll-down-btn');

// IMPORTANT: Set the API URL for your *future* deployed Django Backend
// NOTE: When testing locally, use http://127.0.0.1:8000
// After deployment (e.g., Render/Heroku), replace this with your LIVE URL!
const API_URL = 'http://127.0.0.1:8000/api/classify/';

// Generate a unique session ID for the conversation (for history/context management on the backend)
const SESSION_ID = crypto.randomUUID();
document.getElementById('session-display').textContent = `Session ID: ${SESSION_ID}`;

// --- 2. Core Chat Functionality ---

/**
 * Creates and appends a chat bubble to the chat window.
 * @param {string} message The text content.
 * @param {string} sender 'user' or 'ai'.
 */
function appendMessage(message, sender) {
    const messageWrapper = document.createElement('div');
    messageWrapper.classList.add('message', `${sender}-message`);

    const messageContent = document.createElement('div');
    messageContent.classList.add('message-content');
    messageContent.textContent = message;

    const actionContainer = document.createElement('div');
    actionContainer.classList.add('chat-actions');

    const copyBtn = createActionButton('copy', 'fas fa-copy', () => copyToClipboard(message));
    const shareBtn = createActionButton('share', 'fas fa-share-alt', () => alert('Share functionality is a future feature!'));
    const editBtn = createActionButton('edit', 'fas fa-edit', () => alert('Editing historical messages is a future feature!'));

    actionContainer.append(copyBtn, shareBtn, editBtn);
    messageWrapper.append(messageContent, actionContainer);
    chatWindow.appendChild(messageWrapper);

    scrollToBottom(chatWindow);
}

/** Helper to create action buttons */
function createActionButton(type, iconClass, handler) {
    const btn = document.createElement('button');
    btn.classList.add('action-btn', `${type}-btn`);
    btn.title = type.charAt(0).toUpperCase() + type.slice(1);
    btn.innerHTML = `<i class="${iconClass}"></i>`;
    btn.addEventListener('click', handler);
    return btn;
}

/** Sends the message to the Django API backend */
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    // 1. Display user message immediately
    appendMessage(message, 'user');
    userInput.value = ''; // Clear input

    // Simulate AI typing indicator (optional, but good UX)
    appendMessage("AI is thinking...", 'ai');
    const typingIndicator = chatWindow.lastChild;

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_message: message,
                session_id: SESSION_ID // Pass session ID for context tracking
                // You can add conversation history here if needed
            }),
        });

        // 2. Remove typing indicator
        chatWindow.removeChild(typingIndicator);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `API Error: ${response.status}`);
        }

        const data = await response.json();
        const aiResponse = data.response_message || "I apologize, I received an unclear response.";

        // 3. Display AI response
        if (data.status !== 'no_response') {
            appendMessage(aiResponse, 'ai');
        }

    } catch (error) {
        console.error('Fetch error:', error);
        // Display a system error message to the user
        chatWindow.removeChild(typingIndicator);
        appendMessage("I'm sorry, there was a system error. Please try again later.", 'ai');
    }
}

// Event Listeners for Send
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// --- 3. Scroll & Utility Functions ---

/** Scrolls the chat window to the bottom */
function scrollToBottom(element) {
    element.scrollTop = element.scrollHeight;
}

/** Handles the scroll up/down button visibility and actions */
function updateScrollButtons() {
    const { scrollTop, scrollHeight, clientHeight } = chatWindow;
    const scrollTolerance = 5;

    // Hide Scroll Down button if at bottom
    if (scrollHeight - scrollTop - clientHeight < scrollTolerance) {
        scrollDownBtn.classList.add('hidden');
    } else {
        scrollDownBtn.classList.remove('hidden');
    }

    // Hide Scroll Up button if at top
    if (scrollTop < scrollTolerance) {
        scrollUpBtn.classList.add('hidden');
    } else {
        scrollUpBtn.classList.remove('hidden');
    }
}

/** Smoothly scrolls the window by a fixed amount */
function scrollBy(amount) {
    chatWindow.scrollBy({ top: amount, behavior: 'smooth' });
}

// Event Listeners for Scroll Controls
scrollDownBtn.addEventListener('click', () => scrollBy(300));
scrollUpBtn.addEventListener('click', () => scrollBy(-300));
chatWindow.addEventListener('scroll', updateScrollButtons);

// Utility function for copy button
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('Message copied to clipboard!');
    }).catch(err => {
        console.error('Could not copy text: ', err);
    });
}

// Initial call to hide buttons if content is short
document.addEventListener('DOMContentLoaded', () => {
    scrollToBottom(chatWindow);
    updateScrollButtons();
});
