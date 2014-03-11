var mapOptions = {
    zoom: 14,
    maxZoom: 40,
    center: new google.maps.LatLng(40.908842, -73.125086),
    mapTypeId: google.maps.MapTypeId.ROADMAP
};

var map = new google.maps.Map(document.getElementById("map"), mapOptions);

var source_list = ['login', 'account', 'dashboard', 'dashboard-connect', 'dashboard-index', 'infowindow'];

var templates = {}

source_list.each(function (item) {
    var source = $(item + '-template').get('html');
    templates[item] = Handlebars.compile(source);
})


var render = function (container, content, data) {
    $(container).set('html', templates[content](data));
}


var session = null;


var check_login = function () {
    var request = new Request.JSON({
        'url': '/account/check_login/',
        'onComplete': function (data) {
            if (data && data.success) {
                session = data.session;
                dashboard();
                account();
            } else {
                login()
            }
        }
    }).get();
}


var login = function () {

    render('content_container', 'login', {});
    $('title').set('html', 'Login');

    $('login_button').addEvent('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        var username = $('username').get('value');
        var password = $('password').get('value');
        var request = new Request.JSON({
            'url': '/account/login/',
            'onComplete': function (data) {
                if (data && data.success) {
                    session = data.session;

                    dashboard();
                    account();
                }
            }
        })
        request.post({'username': username, 'password': password});
    });
}

var logout = function () {
    session = null;
    removeLine();
    var request = new Request.JSON({
        'url': '/account/logout/',
        'onComplete': function (data) {
            if (data && data.success) {
                session = null;
                login();
            }
        }
    }).post();
}

var account = function () {
    render('account_container', 'account', {username: session.email});
    $('account_logout_button').addEvent('click', logout);
}


var dashboard = function () {
    render('content_container', 'dashboard', {});
    $('title').set('html', 'Dashboard');
    if (!session.connected) {
        render('dashboard_content', 'dashboard-connect', {});
        $('title').set('html', 'Dashboard • Connect');
        $('connect_button').addEvent('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            var username = $('icloud-username').get('value');
            var password = $('icloud-password').get('value');
            var request = new Request.JSON({
                'url': '/account/connect_icloud/',
                'onComplete': function (data) {
                    if (data && data.success) {
                        session = data.session;
                        dashboard_index();
                    }
                }
            })
            request.post({'username': username, 'password': password});
        });
    } else {
        dashboard_index();
    }
}


var dashboard_index = function () {
    var request = new Request.JSON({
        'url': '/account/devices/',
        'onComplete': function (data) {
            if (data && data.success) {
                session = data.session;
                render('dashboard_content', 'dashboard-index', {'session': session});


                $('device-list').addEvent('click:relay(.device-cell)', function (e, target) {
                    var device_element = $(target).getParent();
                    var device_id = device_element.get('data-device-id');
                    $$('.device-detail-wrapper').addClass('close');
                    device_element.getFirst('.device-detail-wrapper').removeClass('close');
                    
                    location_list(device_id);
                })
            }
        }
    }).get();
    render('dashboard_content', 'dashboard-index', {'session': session});
    $('title').set('html', 'Dashboard');


}


var location_points = null;

var location_list = function (device_id) {
    var request = new Request.JSON({
        'url': '/account/devices/history',
        'onComplete': function (data) {
            if (data && data.success) {
                location_points = data.locations;
                if (location_points.length>0){
                    drawLines();
                    setup_slider(device_id);
                }else{
                    removeLine();
                }
            }
        }
    }).post({
            'device_id': device_id
    });
}

var setup_slider = function(device_id){
    var device_element = $('device-list').getElement('.device[data-device-id='+device_id+']');
    var control = device_element.getElement('.location-control');
    if (!control.get('slider')) {
        var slider = control.getElement('.cp_slider');
        var knob = control.getElement('.cp_knob');
        var mySlider = new Slider(slider, knob, {
            offset: 7,
            range: location_points.length-1,
            steps: location_points.length-1,
            initialStep: 0
            //snap: true
        });
        mySlider.addEvent('change', function(value){
            var device_detail = device_element.getElement('.device-detail');
            var time = device_detail.getElement('.time');
            var coordinates = device_detail.getElement('.coordinates');
            time.set('text', location_points[value].time);
            coordinates.set('text', location_points[value].lat+', '+location_points[value].lon);
            updateMarker(value);
        });
        control.set('slider', mySlider);
    }
}


var currentLine = null;
var currentMarker = null;
var infowindow = null;
var currentCircle = null;
var currentLocationPos = 0;

var drawLines = function () {

    var location_coordinates = location_points.map(function (item) {
        return new google.maps.LatLng(item.lat, item.lon);
    });


    map.setCenter(location_coordinates[0]);

    var lineSymbol = {
        path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
        scale: 2
    };

    if (currentLine)currentLine.setMap(null);

    currentLine = new google.maps.Polyline({
        path: location_coordinates,
        icons: [
            {
                icon: lineSymbol,
                offset: '10px',
                repeat: '50px'
            }
        ],
        strokeColor: "#5ca762",
        strokeOpacity: 0.9,
        strokeWeight: 4
    });
    currentLine.setMap(map);
    updateMarker(0);
}

var removeLine = function () {
    if (currentLine) {
        currentLine.setMap(null);
        currentLine = null;
    }
    if (currentMarker) {
        currentMarker.setMap(null);
        currentMarker = null;
    }
    if (infowindow) {
        infowindow.setMap(null);
        infowindow = null;
    }
    if (currentCircle) {
        currentCircle.setMap(null);
        currentCircle = null;
    }
}

var updateMarker = function (pos) {
    var point = location_points[pos];
    var currentCoordinate = new google.maps.LatLng(point.lat, point.lon);
   
    if (currentMarker) {
        
        currentMarker.setPosition(currentCoordinate);
        currentMarker.set('accuracy', point.accuracy);
        infowindow.setContent(templates['infowindow'](point));
    } else {
        var image = {
            url: 'static/img/point.png',
            size: new google.maps.Size(16, 16),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(8, 8)

        }

        currentMarker = new google.maps.Marker({
            position: currentCoordinate,
            map: map,
            icon: image,
            accuracy: point.accuracy
        });
        map.setCenter(currentCoordinate);
        currentCircle = new google.maps.Circle({
            map: map,
            radius: point.accuracy,
            fillColor: '#828282',
            strokeWeight: 2,
            strokeColor: '#5ca762',
            strokeOpacity: '0.7'
        });
        currentCircle.bindTo('center', currentMarker, 'position');
        currentCircle.bindTo('radius', currentMarker, 'accuracy');

        infowindow = new google.maps.InfoWindow({
            content: templates['infowindow'](point)
        });

        google.maps.event.addListener(currentMarker, 'click', function () {
            infowindow.open(map, currentMarker);
        });
    }

    if (!map.getBounds().contains(currentCoordinate)){
        map.setCenter(currentCoordinate);
    }
}


var account_detail = function(){
    
}

check_login();




