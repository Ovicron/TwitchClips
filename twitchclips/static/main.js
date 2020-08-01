// Supposed to hide alert after few seconds!
window.setTimeout(function () {
    $(".zz").fadeTo(500, 0).slideUp(500, function () {
        $(this).remove();
    });
}, 4000);
