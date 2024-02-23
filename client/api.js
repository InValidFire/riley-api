API_URL = "http://localhost:8000";

function getApiKey() {
    apiKeyBox = document.getElementById("api-key-box");
    return {"X-API-Key": apiKeyBox.value};
}

async function makeGetRequest(endpoint, headers) {
    response = await fetch(API_URL + endpoint, {headers});
    return response.json();
}

async function makePostRequest(endpoint, headers, body) {
    response = await fetch(API_URL + endpoint, {headers: headers, method: 'POST', body: body});
    return response.json();
}

async function makeDeleteRequest(endpoint, headers) {
    response = await fetch(API_URL + endpoint, {headers: headers, method: 'DELETE'});
    return response.json();
}

async function getGuests() {
    return await makeGetRequest("/me/guest", getApiKey());
}

async function signIn() {
    console.log(await getGuests());
}