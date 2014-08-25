(function() {

    function choropleth(elem){
        var map = L.map(elem).setView([37.8, -96], 4);
        PLYTOS.map = map;

        L.tileLayer('https://{s}.tiles.mapbox.com/v3/{id}/{z}/{x}/{y}.png', {
            maxZoom: 18,
            attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
                '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
                'Imagery © <a href="http://mapbox.com">Mapbox</a>',
            id: 'examples.map-20v6611k'
        }).addTo(map);


        // control that shows state info on hover
        var info = L.control();

        info.onAdd = function (map) {
            this._div = L.DomUtil.create('div', 'info');
            this.update();
            return this._div;
        };

        info.update = function (props) {
            this._div.innerHTML = '<h4>US Population Density</h4>' +  (props ?
                '<b>' + props.name + '</b><br />' + props.density + ' people / mi<sup>2</sup>'
                : 'Hover over a state');
        };

        info.addTo(map);


        // get color depending on population density value
        function getColor(d) {
            return d > 1000 ? '#800026' :
                   d > 500  ? '#BD0026' :
                   d > 200  ? '#E31A1C' :
                   d > 100  ? '#FC4E2A' :
                   d > 50   ? '#FD8D3C' :
                   d > 20   ? '#FEB24C' :
                   d > 10   ? '#FED976' :
                              '#FFEDA0';
        }

        function style(feature) {
            return {
                weight: 2,
                opacity: 1,
                color: 'white',
                dashArray: '3',
                fillOpacity: 0.7,
                fillColor: getColor(feature.properties.density)
            };
        }

        function highlightFeature(e) {
            var layer = e.target;

            layer.setStyle({
                weight: 5,
                color: '#666',
                dashArray: '',
                fillOpacity: 0.7
            });

            if (!L.Browser.ie && !L.Browser.opera) {
                layer.bringToFront();
            }

            info.update(layer.feature.properties);
        }

        var geojson;

        function resetHighlight(e) {
            geojson.resetStyle(e.target);
            info.update();
        }

        function zoomToFeature(e) {
            map.fitBounds(e.target.getBounds());
        }

        function onEachFeature(feature, layer) {
            layer.on({
                mouseover: highlightFeature,
                mouseout: resetHighlight,
                click: zoomToFeature
            });
        }

        geojson = L.geoJson(statesData, {
            style: style,
            onEachFeature: onEachFeature
        }).addTo(map);

        map.attributionControl.addAttribution('Population data &copy; <a href="http://census.gov/">US Census Bureau</a>');


        var legend = L.control({position: 'bottomright'});

        legend.onAdd = function (map) {

            var div = L.DomUtil.create('div', 'info legend'),
                grades = [0, 10, 20, 50, 100, 200, 500, 1000],
                labels = [],
                from, to;

            for (var i = 0; i < grades.length; i++) {
                from = grades[i];
                to = grades[i + 1];

                labels.push(
                    '<i style="background:' + getColor(from + 1) + '"></i> ' +
                    from + (to ? '&ndash;' + to : '+'));
            }

            div.innerHTML = labels.join('<br>');
            return div;
        };

        //legend.addTo(map);      
    }

    function horizontalBarChart(w, h, barPadding, text_indent_x, color, divId, endpoint, key) {

        //Current logged in user's email
        console.log(EMAIL);
        console.log(SCRIPT_ROOT);

        var divId = "div#" + divId;

        var yScale = d3.scale.linear()
                       .range([0,h*2]);

        var svg = d3.select(divId)
                    .append("svg")
                    .attr("width", w)
                    .attr("height", h*2);

        d3.json(SCRIPT_ROOT + endpoint, function(error, data) {

          if (error) {
            console.log(error);
          }
          else {
            yScale.domain([0, data[key].length]);

            svg.selectAll("rect")
              .data(data[key])
              .enter()
              .append("rect")
              .attr("x", 0)
              .attr("y", function (d, i) {
                return yScale(i);
            })
              .attr("width", function(d) {
              return d.score * 4;
            })
              .attr("height", (h / data[key].length)*2 - barPadding)
              .attr("fill", function (d) {
                var palette = "rgb(150, " + (d.score * 8) + ", 0)";
                if (color === 'b') {
                  palette = "rgb(150, 0, " + (d.score * 8) + ")";
                }
                return palette;
            });

            svg.selectAll("text")
               .data(data[key])
               .enter()
               .append("text")
               .text(function (d) {
                  return d.name;
               })
              .attr("x", text_indent_x*d3.max(data[key], function(d) { return d.score; } ))
              .attr("y", function(d, i) {
                  return i * (h / data[key].length)*2 + ((h / data[key].length)*2 - barPadding) / 2;
               })
               .attr("font-family", "sans-serif")
               .attr("font-size", "13px")
               .attr("fill", "blue")
               .attr("text-anchor", "end");                
            }
        });
    };

    function showTopSkills() {
      horizontalBarChart(500, 100, 2, 8, 'g', 'skill-occupation-bar', '/analytics/skills/', 'skills');
    }

    function showRelatedOccupations() {
      horizontalBarChart(500, 100, 2, 12, 'b', 'related-occupation', '/analytics/occupations/', 'occupations');
    }
    
    PLYTOS.showTopSkills = showTopSkills;
    PLYTOS.showRelatedOccupations = showRelatedOccupations;
    PLYTOS.choropleth = choropleth;
})();