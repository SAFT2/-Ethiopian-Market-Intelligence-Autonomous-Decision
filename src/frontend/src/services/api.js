import axios from "axios";
const api = axios.create({
    baseURL: import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8000/api/v1",
    timeout: 10000,
});
export function setAuthToken(token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
}
export async function login(email, password) {
    const response = await api.post("/auth/login", {
        email,
        password,
    });
    return { access_token: response.data.access_token, role: response.data.role };
}
export async function fetchMarketData(productId) {
    const response = await api.get("/market-data", {
        params: { product_id: productId, limit: 100 },
    });
    return response.data;
}
export async function evaluateIntelligence(payload) {
    const response = await api.post("/intelligence/evaluate", payload);
    return response.data;
}
