import axios from "axios";

const api = axios.create({ baseURL: "/api", timeout: 60000 }); // GAE timeout 60 sec
export default api;
