//function to sort list 

let list = document.querySelectorAll(".row-to-sort");
let ord = [...list].sort((a, b)=> a.childNodes[7].innerHTML.length - b.childNodes[7].innerHTML.length);

for (i = 0; i < list.length; i++) {
    console.log(ord[i].childNodes[7].innerHTML.length)
    list[i].outerHTML = ord[i].outerHTML
}

