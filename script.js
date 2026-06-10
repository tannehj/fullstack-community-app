let storyId=1;
let storiesList=[];
let inputBox =document.getElementById("storyInput");
let button =document.getElementById("submitButton");
let list= document.getElementById("storyList");
let nameInput =document.getElementById("userName")



button.addEventListener("click", function()
{
    

    let story =inputBox.value.trim();
    let name =nameInput.value.trim();

    let hasError = false;

    if (name === "") {
        nameInput.placeholder = "Name required";
        hasError = true;
    }

    if (story === "") {
        inputBox.placeholder = "Story required";
        hasError = true;
    }

    if (hasError) {
        return;
    }
        
    
    let storyObject = {id: storyId, name:name, story:story };
    storyId++;

    storiesList.push(storyObject);
    console.log("After add:", [...storiesList]);

    let listItem =document.createElement("li");
    let deleteButton = document.createElement("button")

    listItem.textContent= storyObject.name + ":" + storyObject.story; //this is opening 
    // the object box and extracting the name ans story attached to that id
    deleteButton.textContent = "DELETE"



    list.appendChild(listItem);
    listItem.appendChild(deleteButton);
    inputBox.value= "";

    deleteButton.addEventListener("click", function()

    {
            listItem.remove();
            let index =storiesList.findIndex(function(item){
                return item.id===storyObject.id;
            });

            if (index !==-1)
            {
                storiesList.splice(index, 1);
            }
            
            console.log("After delete:", [...storiesList]);
   });



});

