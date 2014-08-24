/* If no visited cookie is found display first visit prompt
   Cookie duration set to 30 days
*/
(function() {
    function showFirstVisitDialog() {
        var cookie = PLYTOS.readCookie("visited");
        if (cookie === "true") {
            // do nothing, user has visited before
            return;
        }
        var modal = $("#first-visit-dialog");
        modal.on("hide", function() {
            PLYTOS.createCookie("visited", "true", 30);
        });
        modal.modal();
    };

    function setLinProfCookie() {
    };

    function clearFirstVisit() {
        PLYTOS.eraseCookie("visited");
    };

    PLYTOS.showFirstVisitDialog = showFirstVisitDialog;
    PLYTOS.clearFirstVisit = clearFirstVisit;
})();
