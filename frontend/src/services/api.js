const API_BASE_URL = 'http://127.0.0.1:5000/api';

export async function fetchHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    return await res.json();
  } catch (error) {
    console.error('Error connecting to backend API:', error);
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
    if (!res.ok) throw new Error(`Chat API error: ${res.statusText}`);
    return await res.json();
  } catch (error) {
    console.error('Error sending chat message:', error);
    return {
      query,
      response: `Failed to connect to NOVA backend: ${error.message}. Make sure server.py is running.`,
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
