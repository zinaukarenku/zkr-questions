var csrftoken = Cookies.get('csrftoken');
var questid;
var armed = true;

function setBio() {
	if(armed) {
		armed = false;
		var newBio = $("#new-bio").val();
		sendData = {
			new_bio: newBio,
		}
		$.ajax({
			url: "/api/v1/sec/bio_change/",
			headers: {
				"X-CSRFToken": csrftoken,
			},
			type: "POST",
			dataType: "json",
			contentType: "application/json",
			data: JSON.stringify(sendData),
			success: function (data, textStatus, jqXHR) {
				if (data.info_type == "error") {
					console.log(data.error);
				} else {
					window.location.reload();
				}
			},
		});
	}
}

function sendAnswer() {
	if(armed) {
		armed = false;
		var newAnswer = $("#new-answer").val();
		if (newAnswer == "") {
			alert("Neparašėte atsakymo!");
		}
		else {
			sendData = {
				question_id: questid,
				answer_text: newAnswer,
			}
			$.ajax({
				url: "/api/v1/sec/answer/",
				type: "POST",
				headers: {"X-CSRFToken": csrftoken},
				data: JSON.stringify(sendData),
				dataType: "json",
				contentType: "application/json",
				success: function (data, textStatus, jqXHR) {
					if (data.info_type == "error") {
						console.log(data.error);
					} else {
						window.location = "/question/"+questid+"#"+polit;
					} 
				},
			});
		}
	}
}

function onAnswer() {
	questid = parseInt($(this).attr('id'));
	$("#answer-dialog").dialog("open");
}

$(function () {
	biodial = $("#bio-dialog").dialog({
		autoOpen: false,
		width: 500,
		modal: true,
		buttons: {
			"Nustatyti": setBio,
			"Atšaukti": function () {
				biodial.dialog("close");
			}
		},
	});
	answerdial = $("#answer-dialog").dialog({
		autoOpen: false,
		width: 500,
		modal: true,
		buttons: {
			"Atsakyti": sendAnswer,
			"Atšaukti": function () {
				answerdial.dialog("close");
			}
		},
	});
	$(".atsakbtn").click(onAnswer);
	$("#biobtn").click(function () {
		biodial.dialog("open");
		$("#new-bio").val(biography_old); //inserted in template
	});
});
