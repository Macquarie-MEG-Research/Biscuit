function GetVersion()
{
    $.getJSON("https://api.github.com/repos/Macquarie-MEG-Research/Biscuit/releases").done(function (json){
        // most recent release will be first entry in list
        var release = json[0];
        if (release.assets.length === 0){
            alert('Something went wrong! Please raise an issue on GitHub!');
        }
        var version = release.tag_name;

        var asset_standard = release.assets[0];
        var asset_complete = release.assets[1];

        document.getElementById("complete_link").innerText = "Complete install (" + version + ")";
        document.getElementById("standard_link").innerText = "Standard install (" + version + ")";

        document.getElementById("gh_download_command_complete").innerText = "pip install -U " + asset_complete.browser_download_url;
        document.getElementById("gh_download_command_standard").innerText = "pip install -U " + asset_standard.browser_download_url;
    });
}
