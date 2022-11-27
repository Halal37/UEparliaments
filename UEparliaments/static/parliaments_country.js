select_country(par)
{
    if (par.selectedIndex !== 0) {
        var text = par.options[par.selectedIndex].text;
        var url = window.location.href
        var country = url.split("/")
        url = url.replace(country[4] + "/", "")
        window.location.replace(url + text)
    }
}

function select_house(par) {
    if (par.selectedIndex !== 0) {
        var text = par.options[par.selectedIndex].text;
        window.location.replace(window.location.href + text);
    }
}