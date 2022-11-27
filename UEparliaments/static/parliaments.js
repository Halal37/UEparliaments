function select(par) {
  if (par.selectedIndex !== 0) {
    par.nextElementSibling.className = "selectOption";
    alert(par.options[par.selectedIndex].text);
    var text = par.options[par.selectedIndex].text;
    console.log(text);
   } 
}

function select_country(par) {
  if (par.selectedIndex !== 0) {
      var text = par.options[par.selectedIndex].text;
    window.location.replace(window.location.href +"/"+text)
   }
}