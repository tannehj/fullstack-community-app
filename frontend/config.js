const isLocal =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1";

const API_BASE_URL = isLocal
  ? "http://127.0.0.1:5000"
  : community-app-f4dee5bzaehyewb8.westus2-01.azurewebsites.net;

let csrfToken = null;

async function getCsrfToken() {
  if (csrfToken) {
    return csrfToken;
  }

  const response = await fetch(`${API_BASE_URL}/csrf-token`, {
    credentials: "include"
  });

  if (!response.ok) {
    throw new Error("Unable to initialize request security");
  }

  const data = await response.json();
  csrfToken = data.csrf_token;
  return csrfToken;
}
