function GetVersion()
{
    $.getJSON("https://api.github.com/repos/Macquarie-MEG-Research/Biscuit/releases").done(function (json){
        // most recent release will be first entry in list
        var release = json[0];
        if (release.assets.length === 0){
            alert('Something went wrong! Please raise an issue on GitHub!');
        }
        var version = release.tag_name;

        document.getElementById("complete_link").innerText = "Complete install (" + version + ")";
        document.getElementById("standard_link").innerText = "Standard install (" + version + ")";
    });
}
