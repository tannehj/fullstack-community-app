let storiesList=[];


let storyInput =document.getElementById("storyInput");
let submitButton =document.getElementById("submitButton");
let list= document.getElementById("storyList");
let nameInput =document.getElementById("userName");
let charCounter = document.getElementById("charCounter");
let errorMessage = document.getElementById("errorMessage");

//Frontend asks Flask for stories
//Flask returns JSON
//Frontend displays them
 async function loadStories(){
        try{
            let response= await  fetch("http://127.0.0.1:5000/stories");
            let data = await response.json ();

            storiesList=data;

            
          /// this look like is slows this down and could be optimized 
            for (let storyObject of storiesList){
                displayStory(storyObject);
        }
     }  catch(error){
            console.log("Error loading stories:", error);

        }
        
    }
    loadStories()


submitButton.addEventListener("click", function()
{
    
//cleaning the data up
    let story =storyInput.value.trim();
    let name =nameInput.value.trim();

    //validating the data
    let hasError = false;

    if (name === "" || story === "") {
    errorMessage.textContent =
        "Please enter your name and story.";
    hasError = true;
}

    if (hasError) {
        return;
    }
        
    //create the story/name object
    let storyObject = {name:name, 
        story:story };
    
    fetch("http://127.0.0.1:5000/stories",{
        method:"POST",
        headers: {"Content-Type": "application/json"},
            body:JSON.stringify(storyObject)
        })
        .then(function(response){
            return response.json(); //reponse is "the story object
        })
        .then(function(savedStory) {
            storiesList.push(savedStory);
            displayStory(savedStory);
        });
    storyInput.value= "";

      });
// create the DOM ELements 
function createStoryElements(storyObject){
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
      
     listItem.appendChild(userName);
     listItem.appendChild(storyTextElement);
     // put the button insde the li element 
     listItem.appendChild(deleteButton);
     listItem.appendChild(editButton);
     // add the li element with all its contents into the list
      //ui list

     return{listItem,storyTextElement, editButton,deleteButton};
}

function setupEdit(storyElements, storyObject){
    let { listItem, storyTextElement, editButton } = storyElements;
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
                headers: {"Content-Type": "application/json"},
                    body:JSON.stringify({story:editText.value})
            })

            .then (function(response){
                    return response.json() // the repsonse in this case is the id and story
            })

            .then (function(data){
                storyObject.story=data.story;
                storyTextElement.textContent=storyObject.story;

                exitEditMode(storyTextElement, editText, saveButton, cancelButton,editButton);

                
                
                })
            
        })
          cancelButton.addEventListener("click", function(){
            storyTextElement.textContent=storyObject.story;
            
            exitEditMode(storyTextElement, editText, saveButton, cancelButton,editButton);
            
          });
         
    
});
}
function setupDelete(storyElements, storyObject){

    let {deleteButton, listItem}=storyElements;
     //acces listItem.
     deleteButton.addEventListener("click", function() {
        console.log("Deleting id:", storyObject.id);
        console.log("Delete button clicked");

        fetch(`http://127.0.0.1:5000/stories/${storyObject.id}`, {
            method: "DELETE"
        })
        .then(function(response) {
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

            
        });
    });                 

}

function displayStory(storyObject)
   { 
    let storyElements= createStoryElements(storyObject);
    list.appendChild(storyElements.listItem);
    setupEdit(storyElements, storyObject);
    setupDelete(storyElements, storyObject);

   }
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


storyInput.addEventListener("input", function(){
 let currentLength=storyInput.value.length;
 charCounter.textContent=currentLength + " / 500";
});


