function validateForm() {
    let x = document.forms["myForm"]["userid"].value;
    if (x == "") {
        alert("Please enter a user id!");
        return false;
    }
}


//for autocomplete
function autocomplete(inp, arr) {
    /*the autocomplete function takes two arguments,
    the text field element and an array of possible autocompleted values:*/
    var currentFocus;
    /*execute a function when someone writes in the text field:*/
    inp.addEventListener("input", function(e) {
        var a, b, i, val = this.value;
        /*close any already open lists of autocompleted values*/
        closeAllLists();
        if (!val) { return false;}
        currentFocus = -1;
        /*create a DIV element that will contain the items (values):*/
        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");
        /*append the DIV element as a child of the autocomplete container:*/
        this.parentNode.appendChild(a);
        /*for each item in the array...*/
        for (i = 0; i < arr.length; i++) {
          /*check if the item starts with the same letters as the text field value:*/
          if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
            /*create a DIV element for each matching element:*/
            b = document.createElement("DIV");
            /*make the matching letters bold:*/
            b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
            b.innerHTML += arr[i].substr(val.length);
            /*insert a input field that will hold the current array item's value:*/
            b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
            /*execute a function when someone clicks on the item value (DIV element):*/
                b.addEventListener("click", function(e) {
                /*insert the value for the autocomplete text field:*/
                inp.value = this.getElementsByTagName("input")[0].value;
                /*close the list of autocompleted values,
                (or any other open lists of autocompleted values:*/
                closeAllLists();
            });
            a.appendChild(b);
          }
        }
    });
    /*execute a function presses a key on the keyboard:*/
    inp.addEventListener("keydown", function(e) {
        var x = document.getElementById(this.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        if (e.keyCode == 40) {
          /*If the arrow DOWN key is pressed,
          increase the currentFocus variable:*/
          currentFocus++;
          /*and and make the current item more visible:*/
          addActive(x);
        } else if (e.keyCode == 38) { //up
          /*If the arrow UP key is pressed,
          decrease the currentFocus variable:*/
          currentFocus--;
          /*and and make the current item more visible:*/
          addActive(x);
        } else if (e.keyCode == 13) {
          /*If the ENTER key is pressed, prevent the form from being submitted,*/
          e.preventDefault();
          if (currentFocus > -1) {
            /*and simulate a click on the "active" item:*/
            if (x) x[currentFocus].click();
          }
        }
    });
    function addActive(x) {
      /*a function to classify an item as "active":*/
      if (!x) return false;
      /*start by removing the "active" class on all items:*/
      removeActive(x);
      if (currentFocus >= x.length) currentFocus = 0;
      if (currentFocus < 0) currentFocus = (x.length - 1);
      /*add class "autocomplete-active":*/
      x[currentFocus].classList.add("autocomplete-active");
    }
    function removeActive(x) {
      /*a function to remove the "active" class from all autocomplete items:*/
      for (var i = 0; i < x.length; i++) {
        x[i].classList.remove("autocomplete-active");
      }
    }
    function closeAllLists(elmnt) {
      /*close all autocomplete lists in the document,
      except the one passed as an argument:*/
      var x = document.getElementsByClassName("autocomplete-items");
      for (var i = 0; i < x.length; i++) {
        if (elmnt != x[i] && elmnt != inp) {
        x[i].parentNode.removeChild(x[i]);
      }
    }
  }
  /*execute a function when someone clicks in the document:*/
  document.addEventListener("click", function (e) {
      closeAllLists(e.target);
  });
  }

  let animeList;
  let ratings_df;


async function fetchAnime() {
    try {
        const response = await fetch(`/get_anime`, {
            method: 'GET',
            credentials: 'same-origin'
        });
        animeList = await response.json();
        return animeList;
    } catch (error) {
        console.error(error);
    }
}

async function fetchRatings() {
    try {
        const response = await fetch(`/get_ratings`, {
            method: 'GET',
            credentials: 'same-origin'
        });
        ratings_df = await response.json();
        return ratings_df;
    } catch (error) {
        console.error(error);
    }
}

let animeLikes = [];
const form = document.getElementById('animeForm');

function addNewAnime(event) {
    event.preventDefault();
        // Retrieve input values
        const animeLike = document.getElementById('animeInput').value;
        const animeRating = document.getElementById('ratingInput').value;

        // Validation
        if (animeLike == "") {
            alert("Please enter an anime!")
        } else if (animeLikes.includes(animeLike)) {
            alert("You have already entered this anime!")
        } else if (!animeList.includes(animeLike)) {
            alert("This anime does not exist in our database!")
        }else if (animeRating == ""){
            alert("Please enter a rating for the anime!")
        } else if (animeRating < 0 || animeRating > 10) {
            alert("The rating must be between 0-10!")
        } else {
            // Push input values into the array
            animeLikes.push([animeLike, animeRating]);

            let list = document.getElementById('likedAnimeList')

            let li = document.createElement('li');
            li.innerText = "Anime Name: " + animeLike + " Rating: " + animeRating + "/10";
            list.appendChild(li);
    
            // Clear form fields if needed
            form.reset();
    
            // Optional: Display the array content
            console.log(animeLikes);
        }
}

function submitForm() {
    const form = document.getElementById('animeForm');
    form.reset()

    let list = document.getElementById('likedAnimeList')

    while(list.firstChild)
    {
        list.removeChild(list.firstChild)
    }

    var counterElement = document.getElementById('personal_user_id'); // Get the paragraph element
    var currentValue = parseInt(counterElement.textContent); // Get the current value and convert it to an integer
    var newValue = currentValue + 1; // Increment the value
    counterElement.textContent = newValue; // Update the content of the paragraph with the new value

    // Make a POST request to the server
    fetch('/submit_anime_likes', {
        method: 'POST',                     // HTTP method
        headers: {
            'Content-Type': 'application/json' // Content type
        },
        body: JSON.stringify(animeLikes)          // Data to be sent, converted to JSON
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json(); // Parse response JSON
    })
    .then(data => {
        // Handle success response from the server
        console.log(data);
    })
    .catch(error => {
        // Handle error response from the server
        console.error('There was a problem with the fetch operation:', error);
    });
}

form.addEventListener('submit', addNewAnime)

window.onload = async function() {
    animeList = await fetchAnime();
    autocomplete(document.getElementById("animeInput"), animeList);
}
