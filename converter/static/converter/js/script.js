// 🎵 HimigTube JavaScript Functions
// Main functionality for HimigTube - YouTube to MP3 Converter

// 📜 Modal Script
const infoBtn = document.getElementById("infoBtn");
const modal = document.getElementById("infoModal");
const closeModal = document.getElementById("closeModal");

if (infoBtn && modal && closeModal) {
  infoBtn.onclick = () => modal.classList.remove("hidden");
  closeModal.onclick = () => modal.classList.add("hidden");
  window.onclick = (e) => { if (e.target == modal) modal.classList.add("hidden"); };
}

// 🍪 Cookie Banner Logic
const cookieBanner = document.getElementById("cookieBanner");
const acceptBtn = document.getElementById("acceptCookies");
const declineBtn = document.getElementById("declineCookies");

// Check if user has already made a choice
function checkCookieConsent() {
  const consent = localStorage.getItem('himigtube_cookie_consent');
  if (!consent) {
    // First time user - show banner after 2 seconds
    setTimeout(() => {
      cookieBanner.classList.remove("hidden");
      cookieBanner.classList.add("animate-slide-up");
    }, 2000);
  }
}

// Handle accept cookies
if (acceptBtn) {
  acceptBtn.onclick = () => {
    localStorage.setItem('himigtube_cookie_consent', 'accepted');
    cookieBanner.classList.add("animate-fade-out");
    setTimeout(() => {
      cookieBanner.classList.add("hidden");
    }, 300);
  };
}

// Handle decline cookies
if (declineBtn) {
  declineBtn.onclick = () => {
    localStorage.setItem('himigtube_cookie_consent', 'declined');
    cookieBanner.classList.add("animate-fade-out");
    setTimeout(() => {
      cookieBanner.classList.add("hidden");
    }, 300);
  };
}

// Initialize cookie check when page loads
document.addEventListener('DOMContentLoaded', checkCookieConsent);

// 🎛️ Tab Switching Logic
function switchTab(tabType) {
  const youtubeTab = document.getElementById('youtubeTab');
  const videoTab = document.getElementById('videoTab');
  const youtubeSection = document.getElementById('youtubeSection');
  const videoSection = document.getElementById('videoSection');

  if (tabType === 'youtube') {
    youtubeTab.classList.add('active');
    videoTab.classList.remove('active');
    youtubeSection.classList.add('active');
    videoSection.classList.remove('active');
  } else {
    videoTab.classList.add('active');
    youtubeTab.classList.remove('active');
    videoSection.classList.add('active');
    youtubeSection.classList.remove('active');
  }
}

// 📁 File Upload Logic
const fileDropArea = document.getElementById('fileDropArea');
const videoFileInput = document.getElementById('videoFile');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');

// Drag and drop events
if (fileDropArea) {
  fileDropArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileDropArea.classList.add('drag-over');
  });

  fileDropArea.addEventListener('dragleave', () => {
    fileDropArea.classList.remove('drag-over');
  });

  fileDropArea.addEventListener('drop', (e) => {
    e.preventDefault();
    fileDropArea.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  });
}

// File input change event
if (videoFileInput) {
  videoFileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFileSelect(e.target.files[0]);
    }
  });
}

function handleFileSelect(file) {
  // Check file size (100MB limit)
  const maxSize = 100 * 1024 * 1024; // 100MB in bytes
  if (file.size > maxSize) {
    alert('File size too large! Maximum size is 100MB.');
    return;
  }

  // Check file type
  const allowedTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/mkv', 'video/wmv', 'video/flv', 'video/3gp', 'video/webm'];
  if (!allowedTypes.includes(file.type) && !file.name.match(/\.(mp4|avi|mov|mkv|wmv|flv|3gp|webm)$/i)) {
    alert('Unsupported file format! Please use MP4, AVI, MOV, MKV, WMV, FLV, 3GP, or WEBM.');
    return;
  }

  // Update file info display
  fileName.textContent = file.name;
  fileSize.textContent = formatFileSize(file.size);
  fileInfo.style.display = 'block';
  
  // Update the file input
  const dt = new DataTransfer();
  dt.items.add(file);
  videoFileInput.files = dt.files;
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// ⏳ Spinner Script
function showLoading(message = "Converting audio format…") {
  document.getElementById("loading").classList.remove("hidden");
  document.querySelector(".loading-comment").innerText = `🔧 ${message}`;
}

// 🔍 Search Suggestions Functionality
let searchTimeout;
const searchInput = document.getElementById('searchInput');
const searchSuggestions = document.getElementById('searchSuggestions');
const suggestionsList = document.getElementById('suggestionsList');

// Fetch suggestions from API
async function fetchSuggestions(query) {
  try {
    const response = await fetch(`/api/search-suggestions/?q=${encodeURIComponent(query)}`);
    const data = await response.json();
    return data.suggestions || [];
  } catch (error) {
    console.error('Error fetching suggestions:', error);
    return [];
  }
}

// Display suggestions
function displaySuggestions(suggestions) {
  suggestionsList.innerHTML = '';
  
  if (suggestions.length === 0) {
    searchSuggestions.classList.add('hidden');
    return;
  }
  
  suggestions.forEach(suggestion => {
    const item = document.createElement('div');
    item.className = 'suggestion-item';
    item.innerHTML = `
      <img src="${suggestion.thumbnail}" alt="Thumbnail" class="suggestion-thumbnail" onerror="this.style.display='none'">
      <span class="suggestion-text">${suggestion.title}</span>
    `;
    
    item.addEventListener('click', () => {
      searchInput.value = suggestion.title;
      searchSuggestions.classList.add('hidden');
      document.getElementById('searchForm').submit();
    });
    
    suggestionsList.appendChild(item);
  });
  
  searchSuggestions.classList.remove('hidden');
}

// Handle input events
if (searchInput) {
  searchInput.addEventListener('input', function() {
    const query = this.value.trim();
    
    clearTimeout(searchTimeout);
    
    if (query.length < 2) {
      searchSuggestions.classList.add('hidden');
      return;
    }
    
    searchTimeout = setTimeout(async () => {
      const suggestions = await fetchSuggestions(query);
      displaySuggestions(suggestions);
    }, 300);
  });

  // Show suggestions when focusing on input
  searchInput.addEventListener('focus', function() {
    if (this.value.trim().length >= 2) {
      const query = this.value.trim();
      setTimeout(async () => {
        const suggestions = await fetchSuggestions(query);
        displaySuggestions(suggestions);
      }, 100);
    }
  });
}

// Hide suggestions when clicking outside
document.addEventListener('click', function(e) {
  if (!e.target.closest('.search-container')) {
    searchSuggestions.classList.add('hidden');
  }
});

// Make functions globally available
window.switchTab = switchTab;
window.showLoading = showLoading;