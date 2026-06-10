let storiesList=[];
let inputBox =document.getElementById("storyInput");
let button =document.getElementById("submitButton");
let list= document.getElementById("storyList");
let nameInput =document.getElementById("userName")
let stroyId=1;


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
        
    
    let fullStory = name + ":" + story;  
    storiesList.push(fullStory);
    console.log("After add:", storiesList);

    let listItem =document.createElement("li");
    let deleteButton = document.createElement("button")

    listItem.textContent= fullStory;
    deleteButton.textContent = "DELETE"



    list.appendChild(listItem);
    listItem.appendChild(deleteButton);
    inputBox.value= "";

    deleteButton.addEventListener("click", function()

    {
            listItem.remove();
            let index =storiesList.indexOf(fullStory);

            if (index !==-1)
            {
                storiesList.splice(index, 1);
            }
            console.log("After delete:", storiesList);
    });



});

