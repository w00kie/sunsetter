import * as tools from './tools'

// povicon url from index.html
declare const povicon: string

const tokyo = new google.maps.LatLng(35.41, 139.44)

window.onload = () => {
    // Create map

    const map = new google.maps.Map(document.getElementById("map_canvas") as HTMLElement, {
        center: tokyo,
        zoom: 9,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    })

    // Default marker position
    const markerpos = new google.maps.LatLng(1, 1)

    // Initialize POV and POI Markers as well as LOS Polyline
    const povmarker = new google.maps.Marker({
        position: markerpos,
        map: map,
        icon: povicon,
        draggable: true,
        visible: false
    })

    const poimarker = new google.maps.Marker({
        position: markerpos,
        map: map,
        draggable: true,
        visible: false
    })

    const los = new google.maps.Polyline({
        path: [
            povmarker.getPosition(),
            poimarker.getPosition()
        ],
        strokeColor: "#FF0000",
        strokeOpacity: 0.6,
        strokeWeight: 6,
        visible: false
    })

    los.setMap(map)

    const resultsDOM = document.getElementById('results')
    const azimuthDOM = document.getElementById('azimuth')

    // Click on the map event - works only 2 first times
    google.maps.event.addListener(map, 'click', (event) => {
        // First click, show POV marker
        if (!povmarker.getVisible()) {
            povmarker.setPosition(event.latLng)
            povmarker.setVisible(true)
            document.getElementById("step1").classList.remove("active")
            document.getElementById("step2").classList.add("active")
            // Second click, show POI marker
        } else if (!poimarker.getVisible()) {
            poimarker.setPosition(event.latLng)
            poimarker.setVisible(true)
            los.setVisible(true)
            document.getElementById("azimuth").style.display = 'block'
            tools.queryMatch(povmarker, poimarker)
            document.getElementById("step2").classList.remove("active")
            document.getElementById("step3").classList.add("active")
        }
    })

    // Move markers event
    for (const marker of [povmarker, poimarker]) {
        google.maps.event.addDomListener(marker, 'position_changed', () => {
            los.setPath([povmarker.getPosition(), poimarker.getPosition()])
            let az = tools.getAzimuth(povmarker.getPosition(), poimarker.getPosition())
            azimuthDOM.innerText = `${az.round(2)}º`
            // Clear results
            resultsDOM.innerHTML = ''
        })
    }

    // Query for a match on drop
    for (const marker of [povmarker, poimarker]) {
        google.maps.event.addDomListener(marker, 'dragend', () => {
            tools.queryMatch(povmarker, poimarker)
        })
    }

    // Reset button action
    document.getElementById('reset').addEventListener('click', () => {
        povmarker.setVisible(false)
        poimarker.setVisible(false)
        los.setVisible(false)
        document.getElementById('step1').classList.add('active')
        document.getElementById('step2').classList.remove('active')
        document.getElementById('step3').classList.remove('active')
        document.getElementById('azimuth').style.display = 'none'
        document.getElementById('results').innerHTML = ''
        window.location.hash = ''
    })

    // Setup map if vars passed in URL hash
    let hash = tools.getHash()
    if (hash.pov && hash.poi) {
        // Parse locations from URL
        let povpos = tools.strToLatLng(hash.pov)
        let poipos = tools.strToLatLng(hash.poi)
        // Move markers to locations
        povmarker.setPosition(povpos)
        poimarker.setPosition(poipos)
        // Make elements visible
        povmarker.setVisible(true)
        poimarker.setVisible(true)
        los.setVisible(true)
        // Zoom map to fit both markers
        let bounds = new google.maps.LatLngBounds()
        bounds.extend(povpos)
        bounds.extend(poipos)
        map.fitBounds(bounds)
        // Increment instruction steps
        document.getElementById("step1").classList.remove("active")
        document.getElementById("step3").classList.add("active")
        document.getElementById("azimuth").style.display = 'block'
        // Finally call the backend
        tools.queryMatch(povmarker, poimarker)
    } else {
        // Try HTML5 geolocation
        // Do it only if no location in URL as asynchronous geoloc messes with fitBounds
        tools.askGeolocation(map)
    }
}
