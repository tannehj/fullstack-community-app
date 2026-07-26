const isLocal =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1";

const API_BASE_URL = isLocal
  ? "http://127.0.0.1:5000"
  : "https://your-backend-url.onrender.com";