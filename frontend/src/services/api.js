const API_BASE = '/api/v1';

export async function fetchSystems() {
  const res = await fetch(`${API_BASE}/systems`);
  if (!res.ok) throw new Error(`Failed to fetch systems: ${res.statusText}`);
  return res.json();
}

export async function fetchSystemDetail(serverId) {
  const res = await fetch(`${API_BASE}/systems/${serverId}`);
  if (!res.ok) throw new Error(`Failed to fetch server ${serverId}: ${res.statusText}`);
  return res.json();
}

export async function fetchServerCompliance(serverId) {
  const res = await fetch(`${API_BASE}/compliance/scans/${serverId}`);
  if (!res.ok) throw new Error(`Failed to fetch compliance for ${serverId}`);
  return res.json();
}

export async function fetchServerErrata(serverId) {
  const res = await fetch(`${API_BASE}/compliance/errata/${serverId}`);
  if (!res.ok) throw new Error(`Failed to fetch errata for ${serverId}`);
  return res.json();
}

export async function fetchPendingApprovals() {
  const res = await fetch(`${API_BASE}/approvals/pending`);
  if (!res.ok) throw new Error('Failed to fetch pending approvals');
  return res.json();
}

export async function submitApprovalAction(token, approved, comment = '') {
  const res = await fetch(`${API_BASE}/approvals/${token}/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ approved, operator: 'SecOps Lead', comment })
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Approval submission failed');
  }
  return res.json();
}

export async function fetchReports() {
  const res = await fetch(`${API_BASE}/reports`);
  if (!res.ok) throw new Error('Failed to fetch reports');
  return res.json();
}

export async function generateReport(payload) {
  const res = await fetch(`${API_BASE}/reports/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Report generation failed');
  return res.json();
}

export async function fetchChatSessions() {
  const res = await fetch(`${API_BASE}/chat/sessions`);
  if (!res.ok) return [];
  return res.json();
}

export async function fetchSessionMessages(sessionId) {
  const res = await fetch(`${API_BASE}/chat/sessions/${sessionId}/messages`);
  if (!res.ok) return [];
  return res.json();
}

export function streamChatMessage(message, sessionId, onEvent) {
  const controller = new AbortController();
  
  fetch(`${API_BASE}/chat/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId }),
    signal: controller.signal
  }).then(async (response) => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop(); // keep partial line

      let currentEvent = null;
      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;
        if (trimmed.startsWith('event:')) {
          currentEvent = trimmed.replace('event:', '').trim();
        } else if (trimmed.startsWith('data:') && currentEvent) {
          try {
            const data = JSON.parse(trimmed.replace('data:', '').trim());
            onEvent(currentEvent, data);
          } catch (e) {
            // raw string fallback
            onEvent(currentEvent, trimmed.replace('data:', '').trim());
          }
        }
      }
    }
  }).catch((err) => {
    if (err.name !== 'AbortError') {
      onEvent('error', { error: err.message });
    }
  });

  return controller;
}
