var _options = {
	group: true
}

var selection = new Array();
var shownsel = new Array();
var armed = true;
var followupbool = false;
var allselected = false;
var csrftoken = Cookies.get('csrftoken');

$.typeahead({
	input: "#js-typeahead-input",
	order: "desc",
	source: {
		teritorijos: {
			ajax: {
				url: "/json/init/",
				path: "data.teritorijos"
			}
		},
		partijos: {
			ajax: {
				url: "/json/init/",
				path: "data.partijos"
			}
		},
		politikai: {
			ajax: {
				url: "/json/init/",
				path: "data.politikai"
			}
		}
	},
	callback: {
		onClick: "polList"
	}
});

function fillSel() {
	selection.push("all");
	allselected = true;
	$("#popupdiv").css('display', 'block');
}

function updateCount() {
	if(allselected) {
		$("#sel-count").html("<p>Pasirinkti <b>"+totalPoliticianCount+"</b> politikai");
	} else if(selection.length > 0) {
		$("#sel-count").html("<p>Pasirinkti <b>"+selection.length+"</b> politikai");
	} else {
		$("#sel-count").html("<p>Pasirinktų politikų nėra ");
	}
}

function onDivClick () {
	var target = $(this);
	var id = target.data('id');
	if (target.hasClass("selected")) {
		index = selection.indexOf(parseInt(id));
		selection.splice(index, 1);
		target.removeClass("selected");
	}
	else {
		selection.push(parseInt(id));
		target.addClass("selected");
	}
	updateCount();
}
function getList(ajaxurl, name) {
	$.ajax({
		type: "POST",
		url: ajaxurl,
		headers: {"X-CSRFToken": csrftoken},
		data: {reqData: name},
		dataType: "json",
		success: function (data, textStatus, jqXHR) {
			if(followupbool == false) {
				$("#followup").append("<p>Dabar paspauskite ant Jus dominančių politikų vardų.");
				$("#popupdiv").css('display', 'block');
				followupbool = true;
			}
			$(".list-div").empty();
			for (i = 0; i < data.politicians.length; i++) {
				var curDiv = i % 4;
				$("#listdiv" + curDiv).append(templ.render(data.politicians[i]));
				shownsel.push(parseInt(data.politicians[i].id));
			}
			$(".politician-div").click(onDivClick);
			if (data.politicians.length == 1) {
				window.location = "/politician/"+data.politicians[0].id;
			}
		}
	});
}

function polList (node, a, item, event) {
	var recdata;
	var ajaxurl;
	if (item.group === "partijos") {
		ajaxurl = "/json/party/";
	} else if (item.group === "teritorijos") {
		ajaxurl = "/json/area/";
	} else {
		ajaxurl = "/json/politician/";
	}
	getList(ajaxurl, item.display);
}

function ask() {
	if(armed) {
		armed = false;
		var email_in = $("#email").val();
		var question = $("#question_text").val();
		if (question == "") {
			alert("Neįvedėte klausimo!");
		}
		else if (/^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(email_in) == false) {
			alert("Netinkamas el. paštas");
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
                             
$(function() {               
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
  $("#popup").click(function() {
		if (selection.length == 0) {
			alert("Nepasirinkote nei vieno politiko!");
		}
		else {
    	$("#dialog").dialog("open");
		}
  });                        
	$(".logo").click(function() {
		name = $(this).attr("id").replace(/@/g," ");
		console.log(name);
		getList("/json/party/", name);
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
	$("#sel-all").click(function() {
		fillSel();
		updateCount();
	});
	$("#sel-shown").click(function() {
		selection = [];
		for(i = 0; i < shownsel.length; i++) {
			selection.push(shownsel[i]);
		}
		$(".politician-div").addClass("selected");
		updateCount();
	});
	$("#sel-clear").click(function() {
		selection = [];
		shownsel = [];
		allselected = false;
		$(".politician-div").removeClass("selected");
		updateCount();
	});
});
