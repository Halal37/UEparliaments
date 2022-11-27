select_country(par)
{
    if (par.selectedIndex !== 0) {
        var text = par.options[par.selectedIndex].text;
        window.location.replace("http://127.0.0.1:8000/parliaments/" + text)
    }
}

function select_house(par) {
    if (par.selectedIndex !== 0) {
        var text = par.options[par.selectedIndex].text;
        window.location.replace(window.location.href + text)
    }
}