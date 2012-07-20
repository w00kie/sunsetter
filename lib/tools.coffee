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
	
	# Default marker position
	markerpos = new google.maps.LatLng 1, 1
	
	# Initialize POV and POI Markers as well as LOS Polyline
	povmarker = new google.maps.Marker(
		position: markerpos
		map: map
		icon: '/static/img/man.png'
		draggable: true
		visible: false
	)
	
	poimarker = new google.maps.Marker(
		position: markerpos
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
			# Clear results
			$("#results").html("")
	
	# Query for a match on drop
	$([povmarker, poimarker]).each (i,marker) =>
		google.maps.event.addListener marker, 'dragend', () =>
			#queryEphemerides(povmarker)
			queryMatch povmarker, poimarker
	
	# Reset button action
	$("#reset").click () ->
		povmarker.setOptions {position: markerpos, visible: false}
		poimarker.setOptions {position: markerpos, visible: false}
		los.setOptions {strokeOpacity: 0}
		$("#step1").addClass("active", 500)
		$("#step2").removeClass("active", 500)
		$("#step3").removeClass("active", 500)
		$("#azimuth").text("")
		$("#results").html("")
	
	# Setup map if vars passed in URL hash
	hash = getHash()
	if "pov" in Object.keys(hash) and "poi" in Object.keys(hash)
		# Parse locations from URL
		povpos = strToLatLng hash.pov
		poipos = strToLatLng hash.poi
		# Move markers to locations
		povmarker.setPosition povpos
		poimarker.setPosition poipos
		# Make elements visible
		povmarker.setVisible true
		poimarker.setVisible true
		los.setOptions {strokeOpacity: 0.6}
		# Zoom map to fit both markers
		bounds = new google.maps.LatLngBounds()
		bounds.extend povpos
		bounds.extend poipos
		#map.panTo bounds.getCenter()
		map.fitBounds bounds
		# Increment instruction steps
		$("#step1").removeClass("active", 500)
		$("#step3").addClass("active", 500)
		$("#azimuth").show()
		# Finally call the backend
		queryMatch povmarker, poimarker
	else	
		# Try HTML5 geolocation
		# Do it only if no location in URL as asynchronous geoloc messes with fitBounds
		if navigator.geolocation
			navigator.geolocation.getCurrentPosition (position) =>
				latlng = new google.maps.LatLng position.coords.latitude, position.coords.longitude
				map.panTo latlng


getAzimuth = (pov, poi) ->
	povLat = pov.lat().toRad()
	poiLat = poi.lat().toRad()
	dLon = (poi.lng() - pov.lng()).toRad()
	y = Math.sin(dLon) * Math.cos(poiLat)
	x = Math.cos(povLat) * Math.sin(poiLat) - Math.sin(povLat) * Math.cos(poiLat) * Math.cos(dLon)
	return Math.atan2(y, x).toBrng()

# Sets the marker positions in the URL
setHash = (pov, poi) ->
	povpos = pov.getPosition().toUrlValue()
	poipos = poi.getPosition().toUrlValue()
	window.location.hash = "pov=#{povpos}&poi=#{poipos}"

# Decode paramenters from hash
# shamelessly stolen from http://papermashup.com/read-url-get-variables-withjavascript/
getHash = () ->
	vars = {}
	window.location.hash.replace /[#&]+([^=&]+)=([^&]*)/gi, (m, key, value) =>
		vars[key] = value
	return vars

# Make a Google Maps LatLng object from a string
strToLatLng = (str) ->
	coord = str.split(",")
	new google.maps.LatLng coord[0], coord[1]

# NOT USED
queryEphemerides = (pov) ->
	povlat = pov.getPosition().lat().round(1)
	$.ajax(
		type: "POST"
		url: "/GetEphemerides"
		data: {lat: povlat}
		dataType: "json"
		success: (reply) =>
			document.ephemerides = reply
	)

queryMatch = (pov, poi) ->
	# Set the spinner
	document.spinner = new Spinner(
		lines: 13 # The number of lines to draw
		length: 7 # The length of each line
		width: 4 # The line thickness
		radius: 10 # The radius of the inner circle
		rotate: 0 # The rotation offset
		color: '#333' # #rgb or #rrggbb
		speed: 1 # Rounds per second
		trail: 60 # Afterglow percentage
		shadow: false # Whether to render a shadow
		hwaccel: true # Whether to use hardware acceleration
		className: 'spinner' # The CSS class to assign to the spinner
		zIndex: 2e9 # The z-index (defaults to 2000000000)
		top: 'auto' # Top position relative to parent in px
		left: 'auto' # Left position relative to parent in px
	).spin($("#menu")[0])
	
	# Log a request to Google Analytics
	_gaq.push ['_trackEvent', 'Interaction', 'Request']
	
	povlat = pov.getPosition().lat().round(1)
	$.ajax(
		type: "POST"
		url: "/findMatch"
		data: {lat: povlat, az: document.az}
		dataType: "json"
		success: (reply) =>
			if reply.matches?
				daylist = $("<ul>").addClass("matches")
				daylist.append($("<li>").text(day)) for day in reply.matches
				$("#results").text("#{reply.suntype} on:").append(daylist)
				# Log the result to Google Analytics
				_gaq.push ['_trackEvent', 'Interaction', 'Success', reply.suntype]
			else
				$("#results").text("Sorry, there is no #{reply.suntype} in this direction.")
				# Log the result to Google Analytics
				_gaq.push ['_trackEvent', 'Interaction', 'Success', 'Out of Bounds']
		error: () =>
			$("#results").text("ERROR in the Request.")
			# Log the error to Google Analytics
			_gaq.push ['_trackEvent', 'Interaction', 'Error']
		complete: () =>
			document.spinner.stop()
			setHash pov, poi
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