function select_country(par) {
    if (par.selectedIndex !== 0) {
        var text = par.options[par.selectedIndex].text;
        window.location.replace("http://127.0.0.1:8000/parliaments/" + text)
    }
}

function select_house(par) {
    if (par.selectedIndex !== 0) {
        var text = par.options[par.selectedIndex].text;
        var url = window.location.href
        var house = url.split("/")
        url = url.replace(house[5] + "/", "")
        window.location.replace(url + text)
    }
}

function select_term(par) {
    if (par.selectedIndex !== 0) {
        par.nextElementSibling.className = "form-control";
        par.nextElementSibling.nextElementSibling.className = "form-control";
    }
}