// --- 1. Global Variables and Session ID Generation ---
const chatWindow = document.getElementById('chat-window');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const scrollUpBtn = document.getElementById('scroll-up-btn');
const scrollDownBtn = document.getElementById('scroll-down-btn');
const deleteHistoryBtn = document.getElementById('delete-history-btn');

// IMPORTANT: Set the API URL for your *future* deployed Django Backend
// NOTE: When testing locally, use http://127.0.0.1:8000
// After deployment (e.g., Render/Heroku), replace this with your LIVE URL!
const API_URL = 'http://127.0.0.1:8000/api/classify/';

let SESSION_ID = crypto.randomUUID();

function updateSessionDisplay() {
    document.getElementById('session-display').textContent = `Session ID: ${SESSION_ID}`;
}
updateSessionDisplay(); // Initial display

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

    // Action buttons implementation
    const copyBtn = createActionButton('copy', 'fas fa-copy', () => copyToClipboard(message));
    const shareBtn = createActionButton('share', 'fas fa-share-alt', () => handleShare(message));
    const editBtn = createActionButton('edit', 'fas fa-edit', () => handleEdit(message, messageContent));

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

    // Simulate AI typing indicator
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
        // Ensure typing indicator is removed before adding error message
        if (chatWindow.contains(typingIndicator)) {
            chatWindow.removeChild(typingIndicator);
        }
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

// --- 3. Action Button Implementations ---

/** Copies message text to the clipboard */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('Message copied to clipboard!');
    }).catch(err => {
        console.error('Could not copy text: ', err);
        alert('Failed to copy text.');
    });
}

/** Placeholder for Share functionality (uses Web Share API if available) */
function handleShare(text) {
    if (navigator.share) {
        navigator.share({
            title: 'Twin Health Chat Message',
            text: text,
        }).catch((error) => console.log('Error sharing', error));
    } else {
        // Fallback for browsers without Web Share API
        prompt("Copy this message to share:", text);
    }
}

/** Placeholder for Edit functionality (allows editing in place) */
function handleEdit(originalText, messageElement) {
    const newText = prompt("Edit your message:", originalText);
    if (newText !== null && newText.trim() !== originalText.trim()) {
        messageElement.textContent = newText.trim();
        // NOTE: If this were a true RAG app, you would need to send this edit
        // back to the backend to update the conversation history for the SESSION_ID.
        alert("Message updated locally. Note: This edit is not saved on the server yet.");
    }
}

/** Deletes all messages and resets the session */
function deleteHistory() {
    if (confirm("Are you sure you want to delete the entire conversation history? This will reset your session.")) {
        chatWindow.innerHTML = ''; // Clear all messages
        SESSION_ID = crypto.randomUUID(); // Generate a brand new session ID
        updateSessionDisplay();

        // Re-add the initial welcome message
        appendMessage("Hello! I am your dedicated Twin Health AI Assistant. How can I help you today regarding your appointments or lab work?", 'ai');

        alert("Conversation history deleted and new session started.");
    }
}
deleteHistoryBtn.addEventListener('click', deleteHistory);
document.getElementById('history-btn').addEventListener('click', () => alert('History retrieval is not yet implemented. Use the trash icon to delete.'));


// --- 4. Scroll Functions ---

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
chatWindow.addEventListener('scroll', updateScrollButtons);cls

// Initial call to hide buttons if content is short
document.addEventListener('DOMContentLoaded', () => {
    scrollToBottom(chatWindow);
    updateScrollButtons();
});
