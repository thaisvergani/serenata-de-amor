var svg = d3.select('#twitter-data-url'),
    chart_container = d3.select("#chart"),
    tooltip_container = d3.select("#tooltip"),
    congressperson_info = d3.select(".congressperson-info"),
    congressperson_select = d3.select("#congressperson"),
    congressperson_url = congressperson_select.attr('data-url');

congressperson_select
    .on('change', function () {
        var congressperson_id = congressperson_select.property('value');

        show_congressperson_info(congressperson_id);
        apply_congressperson_filter(congressperson_id);
    });

function show_congressperson_info(congressperson_id) {

    var url = congressperson_url + "?congressperson_id=" + congressperson_id;
    // todo: how to pass params on dict format (like ajax)
    d3.request(url)
        .send(
            "GET",
            function (error, data) {
                if (error) throw error;
                congressperson_info.html(data.response);
            });
};

function apply_congressperson_filter(congressperson_id) {
    var tweets_url = svg.attr('data-url')+ "?congressperson_id=" + congressperson_id;
    d3.json(tweets_url, function (error, data) {

        if (error) throw error;

        var width = chart_container.node().getBoundingClientRect().width - 50;
        var height = 300;
        var margin = 50;
        var duration = 250;

        var lineOpacity = "0.25";
        var lineOpacityHover = "0.85";
        var otherLinesOpacityHover = "0.1";
        var lineStroke = "1.5px";
        var lineStrokeHover = "2.5px";

        var circleOpacity = '0.85';
        var circleOpacityOnLineHover = "0.25"
        var circleRadius = 3;
        var circleRadiusHover = 6;


        /* Format Data */
        function sortByDateAscending(a, b) {
            return a.date - b.date;
        }

        data.forEach(function (d) {

            d.values.forEach(function (d) {
                d.date = Date.parse(d.initial_date);
                d.price = +d.mean_per_day;
            });

            d.values = d.values.sort(sortByDateAscending);

        });

        /* Scale */
        var xScale = d3.scaleTime()
            .domain(d3.extent(data[0].values, d => d.date))
            .range([0, width - margin]);

        var yScale = d3.scaleLinear()
            .domain([0, d3.max(data[0].values, d => d.price)])
            .range([height - margin, 0]);

        var color = d3.scaleOrdinal(d3.schemeCategory10);

        /* Add SVG */
        var svg = chart_container.append("svg")
            .attr("width", (width + margin) + "px")
            .attr("height", (height + margin) + "px")
            .append('g')
            .attr("transform", `translate(${margin}, ${margin})`)
            .attr("width", '100%')
            .attr('preserveAspectRatio', 'xMinYMin');


        /* Add line into SVG */
        var line = d3.line()
            .x(d => xScale(d.date))
            .y(d => yScale(d.price));

        let lines = svg.append('g')
            .attr('class', 'lines');

        lines.selectAll('.line-group')
            .data(data).enter()
            .append('g')
            .attr('class', 'line-group')
            .on("mouseover", function (d, i) {
                svg.append("text")
                    .attr("class", "title-text")
                    .style("fill", color(i))
                    .text(d.name)
                    .attr("text-anchor", "middle")
                    .attr("x", (width - margin) / 2)
                    .attr("y", 5);
            })
            .on("mouseout", function (d) {
                svg.select(".title-text").remove();
            })
            .append('path')
            .attr('class', 'line')
            .attr('d', d => line(d.values))
            .style('stroke', (d, i) => color(i))
            .style('opacity', lineOpacity)
            .on("mouseover", function (d) {
                d3.selectAll('.line')
                    .style('opacity', otherLinesOpacityHover);
                d3.selectAll('.circle')
                    .style('opacity', circleOpacityOnLineHover);
                d3.select(this)
                    .style('opacity', lineOpacityHover)
                    .style("stroke-width", lineStrokeHover)
                    .style("cursor", "pointer");
            })
            .on("mouseout", function (d) {
                d3.selectAll(".line")
                    .style('opacity', lineOpacity);
                d3.selectAll('.circle')
                    .style('opacity', circleOpacity);
                d3.select(this)
                    .style("stroke-width", lineStroke)
                    .style("cursor", "none");
            });


        /* Add circles in the line */
        lines.selectAll("circle-group")
            .data(data).enter()
            .append("g")
            .style("fill", (d, i) => color(i))
            .selectAll("circle")
            .data(d => d.values).enter()
            .append("g")
            .attr("class", "circle")
            .on("mouseover", function (d) {
                tooltip_container.node().hidden = false;
                var price = d.price;
                price = price.toLocaleString('pt-br', {style: 'currency', currency: 'BRL'});
                var date = d.final_date;
                var favorite = d.favorite_count;
                var suspicions = d.suspicions;
                tooltip_container.select("#tweet-date").node().textContent = date;
                tooltip_container.select("#tweet-favorites").node().textContent = favorite;
                tooltip_container.select("#reimbursement-price").node().textContent = price;
                tooltip_container.select("#suspicious-reason").node().textContent = suspicions;

                d3.select(this)
                    .style("cursor", "pointer")
                    .append("text")
                    .style("opacity", 1)
                    .attr("x", d => xScale(d.date) + 5)
                    .attr("y", d => yScale(d.price) - 10);
            })
            .on("mouseout", function (d) {
                tooltip_container.node().hidden = true;

            })
            .append("circle")
            .attr("cx", d => xScale(d.date))
            .attr("cy", d => yScale(d.price))
            .attr("r", circleRadius)
            .style('opacity', circleOpacity)
            .style("fill", function (d, i) {

                if (d.status != "0") {
                    '#ff1533'
                } else {
                    color(i);
                }

            })
            .on("mouseover", function (d) {
                d3.select(this)
                    .transition()
                    .duration(duration)
                    .attr("r", circleRadiusHover);
            })
            .on("mouseout", function (d) {
                d3.select(this)
                    .transition()
                    .duration(duration)
                    .attr("r", circleRadius);
            });


        /* Add Axis into SVG */
        var xAxis = d3.axisBottom(xScale).ticks(5);
        var yAxis = d3.axisLeft(yScale).ticks(5);

        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", `translate(0, ${height - margin})`)
            .call(xAxis);

        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
            .append('text')
            .attr("y", 15)
            .attr("transform", "rotate(-90)")
            .attr("fill", "#000")
            .text("Total values");
    });
}
