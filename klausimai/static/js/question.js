var ansid;

var csrftoken = Cookies.get('csrftoken');
var armed = true;

function comment() {
	if (armed) {
		var comment = $("#comment_text").val();
		sendData = {
			answer_id: ansid,
			comment_text: comment,
		}
		$.ajax({
			url: "/api/v1/sec/comment/",
			type: "POST",
			headers: {"X-CSRFToken": csrftoken},
			data: JSON.stringify(sendData),
			contentType: "application/json",
			dataType: "json",
			success: function (data, textStatus, jqXHR) {
				if (data.info_type == "error") {
					console.log(data.error);
				} else {
					window.location.reload();
				}
			}
		});
	}
}

function onBtnClick() {
	ansid = parseInt($(this).attr('id'));
	$("#dialog").dialog("open");
}

$(function () {
	dialog = $("#dialog").dialog({
		autoOpen: false,
		width: 500,
		modal: true,
		buttons: {
			"Komentuoti": comment,
			"Atšaukti": function() {
				dialog.dialog("close");
			},
		},
	});
	$(".expert-btn").click(onBtnClick);
});
