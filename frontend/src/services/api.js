import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 60000, // LLM calls can take a while locally
});

/**
 * Send a plain English query to the backend.
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
