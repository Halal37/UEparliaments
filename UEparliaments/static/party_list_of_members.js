function select_party(par) {
    if (par.selectedIndex !== 0) {
        var text = par.options[par.selectedIndex].text;
        var url = window.location.href;
        var party = url.split("/")[7];
        url = url.replace(party,text);
        window.location.replace(url);
    }
}