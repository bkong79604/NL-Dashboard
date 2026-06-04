import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 60000,
});

/**
 * Step 1 — Classify if the query is data-related, off-topic, or meta.
 * @param {string} query
 * @returns {Promise<{ intent: string, message: string }>}
 */
export async function classifyQuery(query) {
  const response = await api.post("/classify", { query });
  return response.data;
}

/**
 * Step 2 — Execute the data query and return results.
 * @param {string} query
 * @returns {Promise<QueryResponse>}
 */
export async function sendQuery(query) {
  const response = await api.post("/query", { query });
  return response.data;
}

/**
 * Check if the backend and Ollama are healthy.
 * @returns {Promise<HealthResponse>}
 */
export async function checkHealth() {
  const response = await api.get("/health");
  return response.data;
}