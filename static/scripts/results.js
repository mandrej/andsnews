/**
 * Created by milan on 12/14/13.
 */
var match = location.search.match(/find=([^&]+)/i);
if (match) {
    $(function(){
        var options = {exact: "partial", highlight: "#main",
            keys: decodeURIComponent(match[1])};
        $(document).SearchHighlight(options);
    });
}