/**
 * RallyLens AI - Frontend API Client
 * Member 2: Frontend Upload Lead (Hour 3)
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/health`);
    if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
    return await res.json();
  } catch (err) {
    return { status: 'offline', error: err.message };
  }
}

/**
 * Upload video as multipart field 'file'
 * POST /api/matches -> { match_id, status }
 */
export async function uploadMatch(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/matches`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errMsg = `Upload failed with status ${response.status}`;
    try {
      const errJson = await response.json();
      if (errJson.detail) errMsg = errJson.detail;
    } catch {
      // ignore
    }
    throw new Error(errMsg);
  }

  return await response.json();
}

/**
 * Start analysis with sport, court_corners, and court_type
 * POST /api/matches/{id}/analyze
 */
export async function startAnalysis(matchId, payload = {}) {
  const response = await fetch(`${API_BASE_URL}/api/matches/${matchId}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      sport: payload.sport || 'badminton',
      court_type: payload.court_type || 'doubles',
      court_corners: payload.court_corners || null,
    }),
  });

  if (!response.ok) {
    let errMsg = `Analysis request failed: ${response.status}`;
    try {
      const errJson = await response.json();
      if (errJson.detail) errMsg = errJson.detail;
    } catch {
      // ignore
    }
    throw new Error(errMsg);
  }

  return await response.json();
}

/**
 * Poll job status
 * GET /api/matches/{id}/status -> { match_id, status, error }
 */
export async function getStatus(matchId) {
  const response = await fetch(`${API_BASE_URL}/api/matches/${matchId}/status`);
  if (!response.ok) {
    throw new Error(`Failed to check status (${response.status})`);
  }
  return await response.json();
}

/**
 * Fetch completed results
 * GET /api/matches/{id}/results
 */
export async function getResults(matchId) {
  const response = await fetch(`${API_BASE_URL}/api/matches/${matchId}/results`);
  if (response.status === 409) {
    return { status: 'processing', message: 'Analysis is still in progress' };
  }
  if (!response.ok) {
    let errMsg = `Failed to fetch results (${response.status})`;
    try {
      const errJson = await response.json();
      if (errJson.detail) errMsg = errJson.detail;
    } catch {
      // ignore
    }
    throw new Error(errMsg);
  }
  return await response.json();
}

export function getMediaVideoUrl(matchId) {
  return `${API_BASE_URL}/media/${matchId}/video`;
}

export function getMediaAnnotatedUrl(matchId) {
  return `${API_BASE_URL}/media/${matchId}/annotated.mp4`;
}

export function getMediaPreviewUrl(matchId) {
  return `${API_BASE_URL}/media/${matchId}/annotated_preview.jpg`;
}

/**
 * Add manual observation note/event
 * POST /api/matches/{id}/manual-observation
 */
export async function addManualObservation(matchId, observation) {
  const response = await fetch(`${API_BASE_URL}/api/matches/${matchId}/manual-observation`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(observation),
  });
  if (!response.ok) throw new Error('Failed to save manual observation');
  return await response.json();
}

/**
 * Get 1-minute segmented tactical chunk summaries
 * GET /api/matches/{id}/minute-chunks
 */
export async function getMinuteChunks(matchId) {
  const response = await fetch(`${API_BASE_URL}/api/matches/${matchId}/minute-chunks`);
  if (!response.ok) throw new Error('Failed to fetch minute summaries');
  return await response.json();
}

/**
 * Trigger transfer learning / training job
 * POST /api/training/start
 */
export async function startTraining(datasetName, epochs = 10) {
  const response = await fetch(`${API_BASE_URL}/api/training/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dataset_name: datasetName, epochs: epochs }),
  });
  if (!response.ok) throw new Error('Failed to initialize dataset training');
  return await response.json();
}

/**
 * Get training progress status
 * GET /api/training/{job_id}
 */
export async function getTrainingStatus(jobId) {
  const response = await fetch(`${API_BASE_URL}/api/training/${jobId}`);
  if (!response.ok) throw new Error('Failed to get training status');
  return await response.json();
}
