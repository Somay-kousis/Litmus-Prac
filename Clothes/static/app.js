// Frontend Application Controller

// Mock Catalog Data (Synchronized with Backend catalog)
const CLOTHING_CATALOG = [
    {item_id: "c1", name: "Classic Denim Jacket", category: "jacket", color: "blue", size: "M/L/XL"},
    {item_id: "c2", name: "Slim Fit Beige Chinos", category: "pants", color: "beige", size: "S/M/L/XL"},
    {item_id: "c3", name: "White Linen Shirt", category: "shirt", color: "white", size: "M/L/XL"},
    {item_id: "c4", name: "Black Leather Boots", category: "shoes", color: "black", size: "9/10/11"},
    {item_id: "c5", name: "Minimalist Crewneck Tee", category: "shirt", color: "grey", size: "S/M/L"},
    {item_id: "c6", name: "Khaki Utility Jacket", category: "jacket", color: "khaki", size: "M/L"},
];

// App Local State
let appState = {
    cart: [],
    clicks: [],
    previous_chats: [],
    chat_history: [],
    recipient: "self",
    recipient_profiles: {},
    summary: null
};

// DOM References
const catalogContainer = document.getElementById("catalog-container");
const cartContainer = document.getElementById("cart-container");
const cartCountBadge = document.getElementById("cart-count-badge");
const suggestionsContainer = document.getElementById("suggestions-container");
const chatMessagesContainer = document.getElementById("chat-messages-container");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const btnRefreshSuggestions = document.getElementById("btn-refresh-suggestions");
const activeRecipientEl = document.getElementById("active-recipient");
const recipientDetailsEl = document.getElementById("recipient-details");
const storedProfilesListEl = document.getElementById("stored-profiles-list");

// Initialize Frontend
function init() {
    renderCatalog();
    updateCartView();
    fetchDailySuggestions();
    setupEventListeners();
}

// Render Catalog Cards
function renderCatalog() {
    catalogContainer.innerHTML = "";
    CLOTHING_CATALOG.forEach(item => {
        const card = document.createElement("div");
        card.className = "catalog-card";
        card.innerHTML = `
            <div>
                <div class="name">${item.name}</div>
                <div class="cat">${item.category}</div>
            </div>
            <div class="meta">Color: ${item.color} | Sizes: ${item.size}</div>
        `;
        card.addEventListener("click", () => addToCart(item));
        catalogContainer.appendChild(card);
    });
}

// Add Item to Cart
function addToCart(item) {
    // Avoid exact duplicate items in cart to keep it simple
    if (appState.cart.some(cartItem => cartItem.item_id === item.item_id)) {
        return;
    }
    appState.cart.push(item);
    
    // Log click metadata
    if (!appState.clicks.includes(item.item_id)) {
        appState.clicks.push(item.item_id);
    }
    
    updateCartView();
    fetchDailySuggestions();
}

// Remove Item from Cart
function removeFromCart(itemId) {
    appState.cart = appState.cart.filter(item => item.item_id !== itemId);
    updateCartView();
    fetchDailySuggestions();
}

// Update Cart DOM
function updateCartView() {
    cartContainer.innerHTML = "";
    cartCountBadge.textContent = `${appState.cart.length} item${appState.cart.length === 1 ? '' : 's'}`;
    
    if (appState.cart.length === 0) {
        cartContainer.innerHTML = `<div class="empty-cart-msg">Your cart is currently empty.</div>`;
        return;
    }
    
    appState.cart.forEach(item => {
        const row = document.createElement("div");
        row.className = "cart-item";
        row.innerHTML = `
            <div class="info">
                <span class="name">${item.name}</span>
                <span class="meta">${item.category} | size ${item.size.split('/')[0]}</span>
            </div>
            <button class="btn-remove" title="Remove item">&times;</button>
        `;
        row.querySelector(".btn-remove").addEventListener("click", () => removeFromCart(item.item_id));
        cartContainer.appendChild(row);
    });
}

// Fetch Daily suggestions from backend API
async function fetchDailySuggestions() {
    suggestionsContainer.innerHTML = `<div class="loading-spinner">Analyzing profile and cart items...</div>`;
    
    try {
        const response = await fetch("/suggestions", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                cart: appState.cart,
                clicks: appState.clicks,
                previous_chats: appState.previous_chats
            })
        });
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to fetch suggestions");
        }
        
        const data = await response.json();
        renderSuggestions(data.suggestions[0]);
    } catch (error) {
        suggestionsContainer.innerHTML = `<div style="color: #ef4444;">Error fetching recommendations: ${error.message}</div>`;
    }
}

// Basic Markdown parser for daily suggestions output
function renderSuggestions(text) {
    if (!text) {
        suggestionsContainer.innerHTML = "No suggestions generated yet.";
        return;
    }
    
    // Clean escape text
    let html = text
        .replace(/\n/g, "<br>")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>")
        .replace(/- (.*?)(<br>|$)/g, "<li>$1</li>");
        
    // Wrap consecutive list items in ul tags
    html = html.replace(/(<li>.*?<\/li>)+/g, "<ul>$&</ul>");
    
    suggestionsContainer.innerHTML = html;
}

// Setup listeners
function setupEventListeners() {
    btnRefreshSuggestions.addEventListener("click", fetchDailySuggestions);
    chatForm.addEventListener("submit", handleChatSubmit);
}

// Handle Chat Submission
async function handleChatSubmit(e) {
    e.preventDefault();
    const text = chatInput.value.trim();
    if (!text) return;
    
    // 1. Render User Message
    appendMessage("user", text);
    chatInput.value = "";
    
    // 2. Render Loading/Thinking bubble
    const loadingId = appendLoadingBubble();
    
    try {
        // 3. Make POST call to endpoint
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_query: text,
                cart: appState.cart,
                clicks: appState.clicks,
                previous_chats: appState.previous_chats,
                chat_history: appState.chat_history,
                recipient: appState.recipient,
                recipient_profiles: appState.recipient_profiles,
                summary: appState.summary
            })
        });
        
        removeLoadingBubble(loadingId);
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Stylist response failed");
        }
        
        const data = await response.json();
        
        // 4. Update memory state
        appState.recipient = data.recipient;
        appState.recipient_profiles = data.recipient_profiles;
        appState.chat_history = data.chat_history;
        appState.summary = data.summary;
        
        // 5. Render response
        appendMessage("stylist", data.response);
        updateMemoryDisplay();
        
    } catch (error) {
        removeLoadingBubble(loadingId);
        appendMessage("stylist", `Sorry, I encountered an issue: ${error.message}`);
    }
}

// Append Chat Bubbles
function appendMessage(role, content) {
    const msg = document.createElement("div");
    msg.className = `msg msg-${role}`;
    
    // Format text coordinates (bullet points, bold text)
    let formattedContent = content
        .replace(/\n/g, "<br>")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>");

    msg.innerHTML = `<div class="msg-bubble">${formattedContent}</div>`;
    chatMessagesContainer.appendChild(msg);
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
}

// Loading Bubbles
function appendLoadingBubble() {
    const id = "loading-" + Date.now();
    const bubble = document.createElement("div");
    bubble.className = "msg msg-stylist";
    bubble.id = id;
    bubble.innerHTML = `
        <div class="msg-bubble loading-bubble">
            <span class="loading-dot"></span>
            <span class="loading-dot"></span>
            <span class="loading-dot"></span>
        </div>
    `;
    chatMessagesContainer.appendChild(bubble);
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    return id;
}

function removeLoadingBubble(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// Update left profile sidebar panels
function updateMemoryDisplay() {
    const recipient = appState.recipient;
    activeRecipientEl.textContent = recipient;
    
    if (recipient === "self") {
        recipientDetailsEl.innerHTML = "Shopping using items in your current cart.";
    } else {
        const pref = appState.recipient_profiles[recipient]?.preferences || "No styling preferences recorded yet. Tell the stylist what they like!";
        recipientDetailsEl.innerHTML = `
            <strong>Ignored Cart Items (for self).</strong><br>
            <span style="display: block; margin-top: 6px; color: #a5b4fc;">Memory details for ${recipient}:</span>
            "${pref}"
        `;
    }
    
    // Stored profiles pills list
    storedProfilesListEl.innerHTML = "";
    Object.keys(appState.recipient_profiles).forEach(profName => {
        const pill = document.createElement("span");
        pill.className = "profile-pill";
        pill.textContent = profName;
        pill.addEventListener("click", () => {
            appState.recipient = profName;
            updateMemoryDisplay();
            appendMessage("stylist", `Switched styling focus to: **${profName}**.`);
        });
        storedProfilesListEl.appendChild(pill);
    });
}

// Boot application
window.addEventListener("DOMContentLoaded", init);
