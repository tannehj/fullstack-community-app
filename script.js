let storiesList=[];


let storyInput =document.getElementById("storyInput");
let submitButton =document.getElementById("submitButton");
let list= document.getElementById("storyList");
let nameInput =document.getElementById("userName");
let charCounter = document.getElementById("charCounter");
let errorMessage = document.getElementById("errorMessage");


//let savedStories = localStorage.getItem("storiesList");

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


console.log("is this new code working");

//if (savedStories !== null) {
   // storiesList = JSON.parse(savedStories);
//}

//if (storiesList.length > 0) {
   // storyId = Math.max(...storiesList.map(function(item) {
       // return item.id;
   // })) + 1;


     
//}
//console.log("storyId after load:", storyId);


    
//for (let storyObject of storiesList)
    //  {displayStory(storyObject)}



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
    

    //storiesList.push(storyObject);
    // console.log("After add:", [...storiesList]);
    // localStorage.setItem("storiesList", JSON.stringify(storiesList));
   
    // //calling function
    // displayStory(storyObject);
    
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
    
   
    //let listItem =document.createElement("li");
    //let deleteButton = document.createElement("button")

    //listItem.textContent= storyObject.name + ":" + storyObject.story; //this is opening 
    // the object box and extracting the name and story attached to that id
    //deleteButton.textContent = "DELETE"



    //list.appendChild(listItem);
    //listItem.appendChild(deleteButton);
    storyInput.value= "";

      });

function displayStory(storyObject)
   {
    //create li
     let listItem=document.createElement("li");
     listItem.classList.add("story-card");

     //name card
     let userName= document.createElement("h3");
     userName.textContent=storyObject.name;

     let storyText= document.createElement("p");
     storyText.textContent=storyObject.story;

     // add name and story in between the li element 
     //listItem.textContent=storyObject.name + ":" + storyObject.story;

     // create the delete button 
     let deleteButton =document.createElement("button");
     deleteButton.textContent="DELETE";
      
     listItem.appendChild(userName);
     listItem.appendChild(storyText);
     // put the button insde the li element 
     listItem.appendChild(deleteButton);
     // add the li element with all its contents into the list
     list.appendChild(listItem);
   
     
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

            console.log("After delete:", [...storiesList]);
        });
    });



        
//   delete frontend was not working last stoping point
            
        

}

storyInput.addEventListener("input", function(){
 let currentLength=storyInput.value.length;
 charCounter.textContent=currentLength + " / 500";
});

console.log("is this new edit wokring");

