$(document).ready(function(){
	// Create map
	// If geolocated, set current position as center
	if (google.loader.ClientLocation) {
		var latlng = new google.maps.LatLng(google.loader.ClientLocation.latitude, google.loader.ClientLocation.longitude);
	} else {	// Else center in Tokyo
		var latlng = new google.maps.LatLng(35.41, 139.44);
	}
	var myOptions = {
		zoom: 9,
		center: latlng,
		mapTypeId: google.maps.MapTypeId.ROADMAP
	};
	var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
	
	// Initialize POV and POI Markers as well as LOS Polyline
	var povmarker = new google.maps.Marker({
		position: new google.maps.LatLng(35.41, 139.44), 
		map: map,
		icon: '/static/man.png',
		draggable: true,
		visible: false
	});
	var poimarker = new google.maps.Marker({
		position: new google.maps.LatLng(35.41, 140.44), 
		map: map,
		draggable: true,
		visible: false
	});
	var los = new google.maps.Polyline({
		path: [povmarker.getPosition(), poimarker.getPosition()],
		strokeColor: "#FF0000",
		strokeOpacity: 0,
		strokeWeight: 6
	});
	los.setMap(map);
	
	// Click on the map event
	google.maps.event.addListener(map, 'click', function(event) {
		if ( povmarker.getVisible() == false ) {
			povmarker.setPosition(event.latLng);
			povmarker.setVisible(true);
		} else if ( poimarker.getVisible() == false ) {
			poimarker.setPosition(event.latLng);
			poimarker.setVisible(true);
			los.setOptions({strokeOpacity: 0.6});
			$("#azimuth").show();
			queryAzimuthMatch(povmarker, poimarker);
		}
	});
	// Move markers event
	$([povmarker, poimarker]).each(function(i,marker){
		google.maps.event.addListener(marker, 'position_changed', function() {
			los.setPath([povmarker.getPosition(), poimarker.getPosition()]);
			az = getAzimuth(povmarker.getPosition(), poimarker.getPosition());
			$("#azimuth").text(az.round(2) +"º");
		});
	});
	// Compute Azimuth between markers on drop
	$([povmarker, poimarker]).each(function(i,marker){
		google.maps.event.addListener(marker, 'dragend', function () {
			queryAzimuthMatch(povmarker, poimarker);
		});
	});
});

function getAzimuth (pov, poi) {
	povLat = pov.lat(); povLat = povLat.toRad();
	poiLat = poi.lat(); poiLat = poiLat.toRad();
	var dLon = (poi.lng() - pov.lng()).toRad();
	var y = Math.sin(dLon) * Math.cos(poiLat);
	var x = Math.cos(povLat) * Math.sin(poiLat) - Math.sin(povLat) * Math.cos(poiLat) * Math.cos(dLon);
	return Math.atan2(y, x).toBrng();
}
function queryAzimuthMatch (pov, poi) {
	povlat = pov.getPosition().lat().round(1);
	az = getAzimuth(pov.getPosition(), poi.getPosition());
	$.ajax({
		type: "GET",
		url: "/findmatch/",
		data: {lat: povlat, azimuth: az},
		dataType: "json",
		success: function(reply) {
			if (reply['matches'] == null) {
				$("#results").text(reply['suntype']+" is not visible in this direction.");
			} else {
				$("#results").text(reply['suntype']+": "+reply['matches']);
			}
		}
	});
}
function where () {
	if (google.loader.ClientLocation) {
		alert(google.loader.ClientLocation.latitude +", "+ google.loader.ClientLocation.longitude +"\n"+
			google.loader.ClientLocation.city +"\n"+
			google.loader.ClientLocation.country +"\n"+
			google.loader.ClientLocation.region
		);
	}
}

// extend Number object with methods for converting degrees/radians
Number.prototype.toRad = function() {  // convert degrees to radians
  return this * Math.PI / 180;
}
Number.prototype.toDeg = function() {  // convert radians to degrees (signed)
  return this * 180 / Math.PI;
}
Number.prototype.toBrng = function() {  // convert radians to degrees (as bearing: 0...360)
  return (this.toDeg()+360) % 360;
}
Number.prototype.round = function(decimals) {
	return Math.round(this * Math.pow(10, decimals)) / Math.pow(10, decimals);
}