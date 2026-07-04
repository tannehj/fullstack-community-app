const username =document.getElementById("username");
const password =document.getElementById("password");
const loginMessage=document.getElementById("login-message");
const loginForm = document.getElementById("login-form");

loginForm.addEventListener("submit", appLogin);

async function appLogin(event){
    event.preventDefault();

    const usernameValue=username.value.trim();
    const passwordValue =password.value.trim();

    if (usernameValue===""|| passwordValue==="")
    {
        loginMessage.textContent="Username or password is missing.";
        return;
    }

           const loginObject= { 
            username:usernameValue,
            password:passwordValue
                };

    try {
        const response=await fetch ("http://127.0.0.1:5000/login",{
        method:"POST",
         headers:{"Content-Type": "application/json"},
            body: JSON.stringify(loginObject)
        })
         const data= await response.json();

        if (!response.ok) {
        loginMessage.textContent = data.message;
        return;
        }
      
        window.location.href = "stories.html";
        
    }catch (error) {
    console.error(error); 

    loginMessage.textContent =
        "Unable to connect to the server. Please try again later.";
}

}