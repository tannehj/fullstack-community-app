let storiesList=[];
let storyInput =document.getElementById("storyInput");
let submitButton =document.getElementById("submitButton");
let storyListElement= document.getElementById("storyList");
let charCounter = document.getElementById("charCounter");
let errorMessage = document.getElementById("errorMessage");
const postError=document.getElementById("message");
const searchInput=document.getElementById("searchInput");
let logoutButton =document.getElementById("logout-button");
let authMessage=document.getElementById("auth-card");
const loginLink =document.getElementById("login-link");

let currentUser=null;



function updateAuthUI(){
    if (currentUser){

        authMessage.style.display="block";
        authMessage.textContent = `HI ${currentUser.name}`;
        logoutButton.style.display = "block";
        loginLink.style.display="none";
        submitButton.disabled = false;

    }
    else{
        authMessage.style.display="none"
        logoutButton.style.display = "none";
        loginLink.style.display="block";
        postError.textContent="please sign-in to post";

    }
}

async function loadCurrentUser(){
    try{
        const response =await fetch("http://127.0.0.1:5000/current-user",
            {
            credentials: "include"
            }

        )
        const data =await response.json();
        if (!response.ok){
            currentUser=null;
            updateAuthUI();
            return;
        }
        currentUser=data;
        updateAuthUI();



    }catch(error){
        console.error(error);
        currentUser=null;
        updateAuthUI();


    }

}






logoutButton.addEventListener("click", logout);

async function logout(){
    try{
        let response =await fetch("http://127.0.0.1:5000/logout", {
            method:"POST",
            credentials: "include"
        })
        let data =await response.json();
        if (!response.ok){
            throw new Error("Logout failed")


        }
        currentUser=null;
        updateAuthUI();
        window.location.href = "login.html";

    }catch(error){
        console.error(error)
        errorMessage.textContent="something went wrong whlie trying to logout"
    }
}
//Frontend asks Flask for stories
//Flask returns JSON
//Frontend displays them
async function loadStories(){
        try{
            // load the stories from the database after a refresh
            // and populate the page

            let response= await fetch("http://127.0.0.1:5000/stories", {
                 credentials: "include"});
            let stories = await response.json();

            if (!response.ok)
            {
                throw new Error( stories.error || "Could not load stories")
            }

            storiesList=stories;


          /// this look like is slows this down and could be optimized
            for (let storyObject of storiesList){
                displayStory(storyObject);

        }
     }  catch(error){
            console.log("Error loading stories:", error);

        }

    }

async function initializePage(){
   await loadCurrentUser();

  if (!currentUser){
    window.location.href = "login.html";
    return;
  }
  await loadStories();
}
 initializePage()


submitButton.addEventListener("click", function()
{

//cleaning the data up
    let story =storyInput.value.trim();


    //validating the data
    let hasError = false;

    if (!story) {
    errorMessage.textContent =
        "Please enter story .";
    hasError = true;
}

    if (hasError) {
        return;
    }

    //create the story/name object
    let storyObject = { story:story

     };
    submitButton.disabled=true;
    submitButton.textContent="Posting...";


        fetch("http://127.0.0.1:5000/stories",{
        method:"POST",
        credentials: "include",
        headers: {"Content-Type": "application/json"},
            body:JSON.stringify(storyObject)
        })
        .then(function(response){
            if (!response.ok){
                throw new Error("Failed to post story");
            }
            return response.json(); //reponse is "the story object

        })
        .then(function(savedStory) {
            storiesList.push(savedStory);
            displayStory(savedStory,"top");
            postError.textContent="Story Posted";
        })
        .catch(error=>{
            console.error(error);
            postError.textContent="Could not post story.";
    }) .finally(()=>{
     submitButton.disabled=false;
     submitButton.textContent="Submit";
    });

    storyInput.value= "";

      });
// create the DOM ELements
function createStoryElements(storyObject, isOwner){
    //create li
     let listItem=document.createElement("li");
     listItem.classList.add("story-card");

     //name card
     let userName= document.createElement("h3");
     userName.textContent=storyObject.name;

     let storyTextElement= document.createElement("p");
     storyTextElement.textContent=storyObject.story;


     let editButton= document.createElement("button");
     editButton.textContent ="EDIT";

     // create the delete button
     let deleteButton =document.createElement("button");
     deleteButton.textContent="DELETE";

     let TimeElement=document.createElement("p")
     TimeElement.textContent= formatTime(storyObject.created_at);

     let statusElement=document.createElement("p");


     listItem.appendChild(userName);
     listItem.appendChild(TimeElement)
     listItem.appendChild(storyTextElement);
     listItem.appendChild(statusElement);


    if (isOwner){
     listItem.appendChild(deleteButton);
     listItem.appendChild(editButton);
    }


    return{listItem, statusElement, storyTextElement, editButton,deleteButton};
}
//creating story
function setupEdit(storyElements, storyObject){
    let { listItem, statusElement,storyTextElement, editButton } = storyElements;

    //MY FAVORITE FEATURE SO FAR
     editButton.addEventListener("click", function() {
          editButton.disabled=true;
          storyTextElement.style.display="none";

          let editText= document.createElement("textarea");
          listItem.append(editText);
          editText.value=storyObject.story;

          let saveButton=document.createElement("button");
          let cancelButton =document.createElement("button");
          saveButton.textContent= "Save";
          cancelButton.textContent="Cancel";
          listItem.append(saveButton);
          listItem.append(cancelButton);
          saveButton.disabled=true;

          editText.addEventListener("input", function(){
              saveButton.disabled = storyObject.story === editText.value;
            });


          saveButton.addEventListener("click", function(){
             //validate newText
            if (editText.value.trim() === "") {
                return;
            }
            fetch(`http://127.0.0.1:5000/stories/${storyObject.id}`,{
                method: "PATCH",
                credentials: "include",
                headers: {"Content-Type": "application/json"},
                    body:JSON.stringify({story:editText.value})
            })

            .then (function(response){
                if (!response.ok){
                    throw new Error("Failed to edit story")
                    return;
                }
                    return response.json()
            })

            .then (function(data){
                storyObject.story=data.story;
                storyTextElement.textContent=storyObject.story;

                exitEditMode(storyTextElement, editText, saveButton, cancelButton,editButton);

                })
            .catch(error=>{
                console.error(error)
                statusElement.textContent="can not edit story";
            })



        })
          cancelButton.addEventListener("click", function(){
            storyTextElement.textContent=storyObject.story;

            exitEditMode(storyTextElement, editText, saveButton, cancelButton,editButton);

          });


});
}
//delete story
function setupDelete(storyElements, storyObject){

    let {deleteButton, listItem, statusElement}=storyElements;
     //acces listItem.
     deleteButton.addEventListener("click", function() {

        fetch(`http://127.0.0.1:5000/stories/${storyObject.id}`, {
            method: "DELETE",
            credentials: "include"
        })
        .then(function(response) {
            if (!response.ok){
                    throw new Error("Failed to delete story")
                    return;
                }
            return response.json();
        })
        .then(function(data) {
            listItem.remove();

            let index = storiesList.findIndex(function(item) {
                return item.id === storyObject.id;
            });

            if (index !== -1) {
                storiesList.splice(index, 1);
            }


        })
         .catch(error=>{
                console.error(error)
                statusElement.textContent="Could not delete story";
            })
    });

}

function displayStory(storyObject,position = "bottom")
   {
    const isOwner=
      currentUser!==null&&
      currentUser.id==storyObject.user_id;

    let storyElements= createStoryElements(storyObject, isOwner);


    if (position === "top") {
    storyListElement.prepend(storyElements.listItem);
    }else {
    storyListElement.appendChild(storyElements.listItem);
    }

   if (isOwner){
    setupEdit(storyElements, storyObject);
    setupDelete(storyElements, storyObject);
   }

   }
   //exit edit mode
function exitEditMode( storyTextElement,
    editText,
    saveButton,
    cancelButton,
    editButton){
     storyTextElement.style.display="block";
     editText.remove();

            saveButton.remove();
            cancelButton.remove();
            editButton.disabled=false;


}
// update the time a was posted
function formatTime(createdAt){
    const postTime = new Date(createdAt);
    const currentTime = new Date();




    const difference = currentTime - postTime;


    const minutes = Math.floor(difference / (1000 * 60));
    const hours = Math.floor(difference / (1000 * 60 * 60));
    const days = Math.floor(difference / (1000 * 60 * 60 * 24));


    if (minutes < 1) {
        return "just now";
    } else if (minutes < 60) {
        return `${minutes} minute${minutes === 1 ? "" : "s"} ago`;
    } else if (hours < 24) {
        return `${hours} hour${hours === 1 ? "" : "s"} ago`;
    } else {
        return `${days} day${days === 1 ? "" : "s"} ago`;
    }


}


storyInput.addEventListener("input", function(){
 let currentLength=storyInput.value.length;
 charCounter.textContent=currentLength + " / 500";
});


searchInput.addEventListener("input",  searchStories);

function searchStories() {

    const wordSearch = searchInput.value.toLowerCase().trim();

    const filteredStories = storiesList.filter(function (storyObject) {

        return storyObject.story
            .toLowerCase()
            .includes(wordSearch);

    });

    StoryList.innerHTML = "";

    filteredStories.forEach(function (storyObject) {
        displayStory(storyObject);
    });

}
