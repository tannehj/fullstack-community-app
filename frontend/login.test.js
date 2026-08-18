const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");


const loginScript = fs.readFileSync(
    path.join(__dirname, "login.js"),
    "utf8"
);


function loadLogin(response) {
    let submitHandler;
    const elements = {
        username: {value: "tanneh"},
        password: {value: "password"},
        "login-message": {textContent: ""},
        "login-form": {
            addEventListener(eventName, handler) {
                submitHandler = handler;
            }
        }
    };
    const context = {
        API_BASE_URL: "https://api.example.test",
        console: {
            error() {},
            log() {}
        },
        document: {
            getElementById(id) {
                return elements[id];
            }
        },
        fetch: async () => response,
        getCsrfToken: async () => "csrf-token",
        window: {location: {href: "login.html"}}
    };

    vm.runInNewContext(loginScript, context);

    return {
        location: context.window.location,
        message: elements["login-message"],
        submit: () => submitHandler({preventDefault() {}})
    };
}


test("malformed 429 body displays the generic rate-limit message", async () => {
    const login = loadLogin({
        status: 429,
        json: async () => {
            throw new SyntaxError("Invalid JSON");
        }
    });

    await login.submit();

    assert.equal(
        login.message.textContent,
        "Too many login attempts. Please try again later."
    );
});


test("missing 429 body displays the generic rate-limit message", async () => {
    const login = loadLogin({
        status: 429,
        json: async () => null
    });

    await login.submit();

    assert.equal(
        login.message.textContent,
        "Too many login attempts. Please try again later."
    );
});


test("valid 429 JSON displays the backend-provided error", async () => {
    const login = loadLogin({
        status: 429,
        json: async () => ({error: "Backend rate-limit message"})
    });

    await login.submit();

    assert.equal(
        login.message.textContent,
        "Backend rate-limit message"
    );
});


test("other error responses keep their backend-provided message", async () => {
    const login = loadLogin({
        ok: false,
        status: 401,
        json: async () => ({error: "wrong username or password"})
    });

    await login.submit();

    assert.equal(
        login.message.textContent,
        "wrong username or password"
    );
});


test("successful responses still redirect to stories", async () => {
    const login = loadLogin({
        ok: true,
        status: 200,
        json: async () => ({message: "Login successful"})
    });

    await login.submit();

    assert.equal(login.location.href, "stories.html");
});
