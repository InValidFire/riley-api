function generateState() {
    let state = document.getElementById("state");
    let possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let text = "";

    for (let i = 0; i < 40; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    state.value = text;
}

generateState();