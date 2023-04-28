console.log("I am working")

const recipeBtns = document.getElementById("getRecipe")

for(let i = 0; i < recipeBtns.length; i++) {
    recipeBtns[i].addEventListener('click', function(event) {
        event.preventDefault()
        let recipe = this.dataset;
        console.log(recipe)
    })
}