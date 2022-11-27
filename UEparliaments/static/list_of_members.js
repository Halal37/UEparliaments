function select_party(par) {
    if (par.selectedIndex !== 0) {
        var text = par.options[par.selectedIndex].text;
        var url = window.location.href;
        var term = url.split("=")[3]
        url = url.split("?")[0]
        url = url.replace("list-of-members/", +term + "/" + text + "/list-of-members/")
        window.location.replace(url);
    }
}