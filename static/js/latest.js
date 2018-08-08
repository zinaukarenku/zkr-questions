var step = 0;
var armed = true;
var selection = [polId];
var csrftoken = Cookies.get('csrftoken');

function ask() {
  if(armed) {
    armed = false;
    var email_in = $("#email").val();
    var question = $("#question_text").val();
    if (question == "") {
      alert("Neįvedėte klausimo!");
    }
    else {
      sendData = {
        email: email_in,
        question_text: question,
        politicians: selection,
      }
      $.ajax({
        url: "/api/v1/ask/",
        type: "POST",
        headers: {"X-CSRFToken": csrftoken},
        data: JSON.stringify(sendData),
        dataType: "json",
        contentType: "application/json",
        success: function (data, textStatus, jqXHR) {
          if (data.info_type == "error") {
            console.log(data.error);
          } else {
            window.location = "/latest/";
          }
        }
      });
    }
  }
}

//-- loadType and loadExtra are defined in template!

$(function () {
	$("#daugiau-btn").click(function() {
		step++;
		$.get(loadType + loadExtra + step, function(data) {
			$("#klaus-div").append(data);
		});
	});
	if(polId) {
		dialog = $("#dialog").dialog({
			autoOpen: false,
			width: 500,
			modal: true,
			buttons: {
				"Paklausti": ask,
				"Atšaukti": function() {
						dialog.dialog( "close" );
				},
			}
		});
		$("#question_text").keyup(function() {
			len = $("#question_text").val().length;
			if (len > 500) {
				$("#charcount-p").css('color', 'red');
			} else {
				$("#charcount-p").css('color', 'inherit');
			}
			$("#charcount-p").html(len+"/500 ženklų");
		});
		$("#popup").click(function() {
			$("#dialog").dialog("open");
		});
	}
});
