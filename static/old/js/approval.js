var csrftoken = Cookies.get('csrftoken');
var armed = true;
var politician_id = 0;
var promise_id = 0;

function promise() {
	sendData = {
		promise_text: $('#promise-text').val(),
		politician_id: politician_id,
		source: $('#source-text').val(),
	}
	$.ajax({
		url: "/api/v1/sec/promise/",
		type: "POST",
		headers: {"X-CSRFToken": csrftoken},
		data: JSON.stringify(sendData),
		dataType: "json",
		contentType: "application/json",
		success: function(data, textStatus, jqXHR) {
			if (data.info_type == "error") {
				console.log(data.error);
			} else {
				window.location.reload();
			}
		}
	});
}

function update() {
	sendData = {
		promise_id: promise_id,
		update_text: $('#update-text').val(),
	}
	$.ajax({
		url: "/api/v1/sec/update/",
		type: "POST",
		headers: {"X-CSRFToken": csrftoken},
		data: JSON.stringify(sendData),
		dataType: "json",
		contentType: "application/json",
		success: function(data, textStatus, jqXHR) {
			if (data.info_type == "error") {
				console.log(data.error);
			} else {
				window.location = "/promise/"+promise_id;
			}
		}
	});
}

function decide(decision, questid) {
	sendData = {
		question_id: questid,
		approval: decision,
	}
	$.ajax({
		url: "/api/v1/sec/approval/",
		type: "POST",
		headers: {"X-CSRFToken": csrftoken},
		data: JSON.stringify(sendData),
		dataType: "json",
		contentType: "application/json",
		success: function (data, textStatus, jqXHR) {
			if (data.info_type == "error") {
				console.log(data.error);
			} else {
				$("#par"+questid).empty();
			}
		}
	});
}

$(function () {
  promdial = $("#prom-dialog").dialog({
    autoOpen: false,
    width: 500,
    modal: true,
    buttons: {
      "Pridėti": promise,
      "Atšaukti": function () {
        promdial.dialog("close");
      }
    },
  });
  upddial = $("#upd-dialog").dialog({
    autoOpen: false,
    width: 500,
    modal: true,
    buttons: {
      "Atnaujinti": update,
      "Atšaukti": function () {
        upddial.dialog("close");
      }
    },
  });
	$(".new-promise").click(function() {
		politician_id = parseInt($(this).data('politician'));
		console.log(politician_id);
		promdial.dialog("open");
	});
	$(".new-update").click(function() {
		promise_id = parseInt($(this).data('promise'));
		upddial.dialog("open");
	});
	$(".priimti").click(function () {
		questid = parseInt($(this).data("question"));
		decide("approved", questid);
	});
	$(".atmesti").click(function () {
		questid = parseInt($(this).data("question"));
		decide("remove", questid);
	});
});
