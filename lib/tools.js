(function() {
  var getAzimuth, queryEphemerides, queryMatch;

  $(function() {
    var latlng, los, map, myOptions, poimarker, povmarker;
    var _this = this;
    if (google.loader.ClientLocation) {
      latlng = new google.maps.LatLng(google.loader.ClientLocation.latitude, google.loader.ClientLocation.longitude);
    } else {
      latlng = new google.maps.LatLng(35.41, 139.44);
    }
    myOptions = {
      zoom: 9,
      center: latlng,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(function(position) {
        latlng = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
        return map.panTo(latlng);
      });
    }
    povmarker = new google.maps.Marker({
      position: new google.maps.LatLng(35.41, 139.44),
      map: map,
      icon: '/static/img/man.png',
      draggable: true,
      visible: false
    });
    poimarker = new google.maps.Marker({
      position: new google.maps.LatLng(35.41, 140.44),
      map: map,
      draggable: true,
      visible: false
    });
    los = new google.maps.Polyline({
      path: [povmarker.getPosition(), poimarker.getPosition()],
      strokeColor: "#FF0000",
      strokeOpacity: 0,
      strokeWeight: 6
    });
    los.setMap(map);
    google.maps.event.addListener(map, 'click', function(event) {
      if (!povmarker.getVisible()) {
        povmarker.setPosition(event.latLng);
        povmarker.setVisible(true);
        $("#step1").removeClass("active", 500);
        return $("#step2").addClass("active", 500);
      } else if (!poimarker.getVisible()) {
        poimarker.setPosition(event.latLng);
        poimarker.setVisible(true);
        los.setOptions({
          strokeOpacity: 0.6
        });
        $("#azimuth").show();
        queryMatch(povmarker, poimarker);
        $("#step2").removeClass("active", 500);
        return $("#step3").addClass("active", 500);
      }
    });
    $([povmarker, poimarker]).each(function(i, marker) {
      return google.maps.event.addListener(marker, 'position_changed', function() {
        los.setPath([povmarker.getPosition(), poimarker.getPosition()]);
        document.az = getAzimuth(povmarker.getPosition(), poimarker.getPosition());
        return $("#azimuth").text(document.az.round(2) + "º");
      });
    });
    return $([povmarker, poimarker]).each(function(i, marker) {
      return google.maps.event.addListener(marker, 'dragend', function() {
        return queryMatch(povmarker, poimarker);
      });
    });
  });

  getAzimuth = function(pov, poi) {
    var dLon, poiLat, povLat, x, y;
    povLat = pov.lat().toRad();
    poiLat = poi.lat().toRad();
    dLon = (poi.lng() - pov.lng()).toRad();
    y = Math.sin(dLon) * Math.cos(poiLat);
    x = Math.cos(povLat) * Math.sin(poiLat) - Math.sin(povLat) * Math.cos(poiLat) * Math.cos(dLon);
    return Math.atan2(y, x).toBrng();
  };

  queryEphemerides = function(pov) {
    var povlat;
    var _this = this;
    povlat = pov.getPosition().lat().round(1);
    return $.ajax({
      type: "POST",
      url: "/getEphemerides",
      data: {
        lat: povlat
      },
      dataType: "json",
      success: function(reply) {
        return document.ephemerides = reply;
      }
    });
  };

  queryMatch = function(pov, poi) {
    var povlat;
    var _this = this;
    povlat = pov.getPosition().lat().round(1);
    return $.ajax({
      type: "POST",
      url: "/findMatch",
      data: {
        lat: povlat,
        az: document.az
      },
      dataType: "json",
      success: function(reply) {
        var day, daylist, _i, _len, _ref;
        document.matches = reply;
        if (reply.matches != null) {
          daylist = $("<ul>").addClass("matches");
          _ref = reply.matches;
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            day = _ref[_i];
            daylist.append($("<li>").text(day));
          }
          return $("#results").text("" + reply.suntype + " on:").append(daylist);
        } else {
          return $("#results").text("Sorry, there is no " + reply.suntype + " in this direction.");
        }
      }
    });
  };

  Number.prototype.toRad = function() {
    return this * Math.PI / 180;
  };

  Number.prototype.toDeg = function() {
    return this * 180 / Math.PI;
  };

  Number.prototype.toBrng = function() {
    return (this.toDeg() + 360) % 360;
  };

  Number.prototype.round = function(decimals) {
    return Math.round(this * Math.pow(10, decimals)) / Math.pow(10, decimals);
  };

}).call(this);
