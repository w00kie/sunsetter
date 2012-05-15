$ ->
	# Create map
	# If geolocated, set current position as center
	if google.loader.ClientLocation
		latlng = new google.maps.LatLng google.loader.ClientLocation.latitude, google.loader.ClientLocation.longitude
	else	#Else center in Tokyo
		latlng = new google.maps.LatLng(35.41, 139.44)
	
	myOptions =
		zoom: 9
		center: latlng
		mapTypeId: google.maps.MapTypeId.ROADMAP
	
	map = new google.maps.Map document.getElementById("map_canvas"), myOptions	
	
	# Try HTML5 geolocation
	if navigator.geolocation
		navigator.geolocation.getCurrentPosition (position) =>
			latlng = new google.maps.LatLng position.coords.latitude, position.coords.longitude
			map.panTo latlng

	# Initialize POV and POI Markers as well as LOS Polyline
	povmarker = new google.maps.Marker(
		position: new google.maps.LatLng 35.41, 139.44
		map: map
		icon: '/static/man.png'
		draggable: true
		visible: false
	)
	
	poimarker = new google.maps.Marker(
		position: new google.maps.LatLng 35.41, 140.44
		map: map
		draggable: true
		visible: false
	)
	
	los = new google.maps.Polyline(
		path: [
			povmarker.getPosition()
			poimarker.getPosition()
		]
		strokeColor: "#FF0000"
		strokeOpacity: 0
		strokeWeight: 6
	)
	
	los.setMap map

	# Click on the map event - works only 2 first times
	google.maps.event.addListener map, 'click', (event) =>
		# First click, show POV marker
		if not povmarker.getVisible()
			povmarker.setPosition event.latLng
			povmarker.setVisible true
			#queryEphemerides povmarker
			$("#step1").removeClass("active", 500)
			$("#step2").addClass("active", 500)
		# Second click, show POI marker
		else if not poimarker.getVisible()
			poimarker.setPosition event.latLng
			poimarker.setVisible true
			los.setOptions {strokeOpacity: 0.6}
			$("#azimuth").show()
			queryMatch povmarker, poimarker
			$("#step2").removeClass("active", 500)
			$("#step3").addClass("active", 500)
	
	# Move markers event
	$([povmarker, poimarker]).each (i,marker) =>
		google.maps.event.addListener marker, 'position_changed', () =>
			los.setPath [povmarker.getPosition(), poimarker.getPosition()]
			document.az = getAzimuth povmarker.getPosition(), poimarker.getPosition()
			$("#azimuth").text document.az.round(2)+"º"
	
	
	# Compute Azimuth between markers on drop
	$([povmarker, poimarker]).each (i,marker) =>
		google.maps.event.addListener marker, 'dragend', () =>
			#queryEphemerides(povmarker)
			queryMatch povmarker, poimarker

getAzimuth = (pov, poi) ->
	povLat = pov.lat().toRad()
	poiLat = poi.lat().toRad()
	dLon = (poi.lng() - pov.lng()).toRad()
	y = Math.sin(dLon) * Math.cos(poiLat)
	x = Math.cos(povLat) * Math.sin(poiLat) - Math.sin(povLat) * Math.cos(poiLat) * Math.cos(dLon)
	return Math.atan2(y, x).toBrng()

queryEphemerides = (pov) ->
	povlat = pov.getPosition().lat().round(1)
	$.ajax(
		type: "POST"
		url: "/getEphemerides"
		data: {lat: povlat}
		dataType: "json"
		success: (reply) =>
			document.ephemerides = reply
	)

queryMatch = (pov, poi) ->
	povlat = pov.getPosition().lat().round(1)
	$.ajax(
		type: "POST"
		url: "/findMatch"
		data: {lat: povlat, az: document.az}
		dataType: "json"
		success: (reply) =>
			document.matches = reply
			if reply.matches?
				daylist = $("<ul>").addClass("matches")
				daylist.append($("<li>").text(day)) for day in reply.matches
				$("#results").text("#{reply.suntype} on:").append(daylist)
			else
				$("#results").text("Sorry, there is no #{reply.suntype} in this direction.")
	)

# extend Number object with methods for converting degrees/radians
Number::toRad = () ->  # convert degrees to radians
  return this * Math.PI / 180

Number::toDeg = () ->  # convert radians to degrees (signed)
  return this * 180 / Math.PI

Number::toBrng = () ->  # convert radians to degrees (as bearing: 0...360)
  return (this.toDeg()+360) % 360

Number::round = (decimals) ->
	return Math.round(this * Math.pow(10, decimals)) / Math.pow(10, decimals)