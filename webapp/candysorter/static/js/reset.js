$(function() {
  var resetUrl = "/api/_reset";
  var resetSec = 1000;

  // reset
  $(".reset-start").click(function() {
    console.log('test');
    $("body").addClass("mode-loading");
    $.ajax({
      type: "POST",
      contentType: "application/json",
      dataType: "json",
      url: resetUrl,
      error: function(textStatus) {
        console.log(textStatus);
        sorry();
      },
      success: function(data) {
        setTimeout(function() {
          location.href = "/learn";
          $("body").removeClass("mode-loading");
        }, resetSec);
      }
    });
  });

  // draw sorry
  var sorry = function() {
    $("body").addClass("mode-sorry-r");
  };
});
