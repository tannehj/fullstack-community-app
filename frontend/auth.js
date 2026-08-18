const nameInput =document.getElementById("nameInput");
const usernameInput=document.getElementById("usernameInput");
const passwordInput=document.getElementById("passwordInput");
const registerButton=document.getElementById("registerButton");
const registerMessage=document.getElementById("registerMessage")

registerButton.addEventListener("click", registerUsers);

async function registerUsers(){
    
    const name = nameInput.value.trim();
    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    if (!name || !username || !password) {
        registerMessage.textContent = "Please fill out all fields.";
        return;
    }

    if (password.length < 8) {
        registerMessage.textContent="Password must be more than 8 character";
        return;
    }

    const userObject= {name:name,
        username:username,
        password:password

    };
   

    try{
    // form an object to easily send across http n to backend
        const csrfToken = await getCsrfToken();
        let response  = await fetch(`${API_BASE_URL}/register`,{
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-Token": csrfToken
            },
            body:JSON.stringify(userObject)
        });
        let data =await response.json();
        if (!response.ok) {
          throw new Error(data.message);

        
    }
    registerMessage.textContent="Acount Succesfully created";

    }catch (error) {
   registerMessage.textContent = error.message;
}
    
}
