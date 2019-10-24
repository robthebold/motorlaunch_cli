map1 = """
<!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8' />
    <title>Add a GeoJSON polygon</title>
    <meta name='viewport' content='initial-scale=1,maximum-scale=1,user-scalable=no' />
    <script src='https://api.tiles.mapbox.com/mapbox-gl-js/v1.3.2/mapbox-gl.js'></script>
    <link href='https://api.tiles.mapbox.com/mapbox-gl-js/v1.3.2/mapbox-gl.css' rel='stylesheet' />
    <style>
        body { margin:0; padding:0; }
        #map { position:absolute; top:0; bottom:0; width:100%; }
    </style>
</head>
<body>

<div id='map'></div>
<script>
mapboxgl.accessToken = 'pk.eyJ1Ijoicm9idGhlYm9sZCIsImEiOiJjazEyYWdpankwMDN3M2VsbHJ3ajV3NWpkIn0.5o4Qq5m3VwFIFyWGE4NVsg';
var map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v11',
"""


map2 = """
    zoom: 5
});

map.on('load', function () {

    map.addLayer({
        'id': 'range',
        'type': 'fill',
        'source': {
            'type': 'geojson',
            'data': {
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': 
                        [
                        [
"""

map3 = """
                        ]
                        ]
                }
            }
        },
        'layout': {},
        'paint': {
            'fill-color': '#088',
            'fill-opacity': 0.8
        }
    });
});
</script>

</body>
</html>
"""