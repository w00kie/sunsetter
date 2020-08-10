import { Spinner } from 'spin.js'

// extend Number object with methods for converting degrees / radians
declare global {
    interface Number {
        toRad: () => number;
        toDeg: () => number;
        toBrng: () => number;
        round: (decimals: number) => number;
    }
}

export function askGeolocation(map: google.maps.Map): void {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position: Position) => {
                let latlng = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
                map.panTo(latlng)
            }
        )
    }
}

export function getAzimuth(pov: google.maps.LatLng, poi: google.maps.LatLng): number {
    let povLat = pov.lat().toRad()
    let poiLat = poi.lat().toRad()
    let dLon = (poi.lng() - pov.lng()).toRad()
    let y = Math.sin(dLon) * Math.cos(poiLat)
    let x = Math.cos(povLat) * Math.sin(poiLat) - Math.sin(povLat) * Math.cos(poiLat) * Math.cos(dLon)
    return Math.atan2(y, x).toBrng()
}

// Sets the marker positions in the URL
export function setHash(pov: google.maps.Marker, poi: google.maps.Marker): void {
    let povpos = pov.getPosition().toUrlValue()
    let poipos = poi.getPosition().toUrlValue()
    window.location.hash = `pov=${povpos}&poi=${poipos}`
}

// Decode parameters from hash
export function getHash(): {pov: string, poi: string} {
    // Remove # first character of hash that URLSearchParams does not support
    const parser = new URLSearchParams(window.location.hash.substring(1))
    return {
        pov: parser.get('pov'),
        poi: parser.get('poi')
    }
}

// Make a Google Maps LatLng object from a string
export function strToLatLng(str: string) {
    let coord = str.split(",")
    return new google.maps.LatLng(+coord[0], +coord[1])
}
    
export function queryMatch(pov: google.maps.Marker, poi: google.maps.Marker) {
    // Set the spinner
    let spinner = new Spinner({
        lines: 13, // The number of lines to draw
		length: 7, // The length of each line
		width: 4, // The line thickness
		radius: 10, // The radius of the inner circle
		rotate: 0, // The rotation offset
		color: '#333', // #rgb or #rrggbb
		speed: 1, // Rounds per second
		shadow: false, // Whether to render a shadow
		className: 'spinner', // The CSS class to assign to the spinner
		zIndex: 2e9, // The z - index(defaults to 2000000000)
		top: '50%', // Top position relative to parent in px
        left: '50%', // Left position relative to parent in px
    }).spin(document.getElementById('results'))

    // Log a request to Google Analytics
    _gaq.push(['_trackEvent', 'Interaction', 'Request'])

    let povlat = pov.getPosition().lat().round(1)
    const results = document.getElementById('results')

    window.fetch('/findMatch', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ lat: povlat, az: getAzimuth(pov.getPosition(), poi.getPosition()) })
    })
    .then(response => response.json())
    .then(data => {
        if (data.matches) {
            // Create HTML for the result days list
            const daylist = document.createElement('ul')
            daylist.classList.add('matches')
            for (const day of data.matches) {
                const dayli = document.createElement('li')
                dayli.innerText = day
                daylist.append(dayli)
            }
            // Write the type(sunrise or sunset) and results to the screen
            results.innerText = `${data.suntype} on:`
            results.appendChild(daylist)
            // Log the result to Google Analytics
            _gaq.push(['_trackEvent', 'Interaction', 'Success', data.suntype])
        } else {
            results.innerText = `Sorry, there is no ${data.suntype} in this direction.`
            _gaq.push(['_trackEvent', 'Interaction', 'Success', 'Out of Bounds'])
        }
    })
    .then(() => {
        spinner.stop()
        setHash(pov, poi)
    })
    .catch((error) => {
        results.innerText = "ERROR in the Request."
        // Log the error to Google Analytics
        _gaq.push(['_trackEvent', 'Interaction', 'Error'])
    })
}

Number.prototype.toRad = function (): number { // convert degrees to radians
    return this * Math.PI / 180;
}

Number.prototype.toDeg = function (): number { // convert radians to degrees(signed)
    return this * 180 / Math.PI;
}

Number.prototype.toBrng = function (): number { // convert radians to degrees(as bearing: 0...360)
    return (this.toDeg() + 360) % 360;
}

Number.prototype.round = function (decimals: number): number {
    return Math.round(this * Math.pow(10, decimals)) / Math.pow(10, decimals)
}	
