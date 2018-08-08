var map;

require([
	"esri/map", "esri/layers/FeatureLayer", "esri/tasks/IdentifyTask", "esri/tasks/IdentifyParameters",
	"dojo/parser", "dojo/dom-style",

	"dijit/layout/BorderContainer", "dijit/layout/ContentPane", "dojo/domReady!"
], function(
	Map, FeatureLayer, IdentifyTask, IdentifyParamenters
) {
	map = new Map("mapdiv", {
		basemap: "gray",
		center: [23.905, 55.32],
		zoom: 7
	});

	var vienmandates = new FeatureLayer("http://zinaukarenku.maps.arcgis.com/sharing/rest/content/items/41f9057adace4f63bf89f716de89a206");
	vienmandates.setOpacity(0.5);
	map.addLayer(vienmandates);


});
