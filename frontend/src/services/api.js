// Default to live Render backend if in cloud/Vercel or if VITE_API_URL is provided, fallback to localhost for dev
function getBaseUrl() {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL.replace(/\/+$/, '');
  }
  if (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    return 'https://nova-backend-wi97.onrender.com';
  }
  return 'http://127.0.0.1:5000';
}

const BACKEND_URL = getBaseUrl();
const API_BASE_URL = `${BACKEND_URL}/api`;

console.log(`[NOVA Client] Connecting to Backend API: ${API_BASE_URL}`);

export async function fetchHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { method: 'GET' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (error) {
    console.warn('Backend connection ping:', error.message);
    return { status: 'offline', error: error.message };
  }
}

export async function fetchWeather() {
  try {
    const res = await fetch(`${API_BASE_URL}/weather`);
    if (!res.ok) throw new Error(`Weather error: ${res.statusText}`);
    return await res.json();
  } catch (error) {
    console.error('Error fetching weather telemetry:', error);
    return { weather: 'Weather Unavailable', location: 'Location Unknown' };
  }
}

export async function fetchChatHistory() {
  try {
    const res = await fetch(`${API_BASE_URL}/chat-history`);
    if (!res.ok) throw new Error(`History error: ${res.statusText}`);
    const data = await res.json();
    return data.history || [];
  } catch (error) {
    console.error('Error fetching chat history:', error);
    return [];
  }
}

export async function sendChatMessage(query, speak = true) {
  try {
    const res = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, speak })
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.error || `Server responded with ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    console.error('Error sending chat message:', error);
    return {
      query,
      response: `Failed to connect to NOVA backend at (${BACKEND_URL}): ${error.message}.\n\n(Note: If Render free instance is waking up from sleep, please allow ~15 seconds and try again).`,
      status: 'error'
    };
  }
}

export async function analyzeImage(file) {
  try {
    const formData = new FormData();
    formData.append('image', file);

    const res = await fetch(`${API_BASE_URL}/analyze-image`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) throw new Error(`Vision analysis error: ${res.statusText}`);
    return await res.json();
  } catch (error) {
    console.error('Error analyzing image:', error);
    return {
      analysis: `Error during image analysis: ${error.message}`,
      status: 'error'
    };
  }
}

export async function speakText(text) {
  try {
    const res = await fetch(`${API_BASE_URL}/speak`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    return await res.json();
  } catch (error) {
    console.error('Error triggering speech:', error);
  }
}
