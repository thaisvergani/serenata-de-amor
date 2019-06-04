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

    d3.request(url)
        .send(
            "GET",
            function (error, data) {
                if (error) throw error;
                congressperson_info.html(data.response);
            });
}

function apply_congressperson_filter(congressperson_id) {
    var tweets_url = svg.attr('data-url') + "?congressperson_id=" + congressperson_id;

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

        var div = d3.select("body").append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);

        /* Order data */
        function sort_means(a, b) {
            return a.period_final_date - b.period_final_date;
        }

        function sort_reimbursements(a, b) {
            return a.parsed_issue_date - b.parsed_issue_date;
        }

        data.forEach(function (d) {
            d.means.forEach(function (d) {
                d.period_final_date = Date.parse(d.final_date);
                d.period_mean_price_day = +d.mean_per_day;
                d.tweet_circle_r = +d.total_net_value / 10;
                d.tweet_date = d.final_date;
            });
            d.means = d.means.sort(sort_means);

            d.reimbursements.forEach(function (d) {
                d.parsed_issue_date = Date.parse(d.issue_date);
                d.value = +d.value;
            });
            d.reimbursements = d.reimbursements.sort(sort_reimbursements);
        });

        /* Scale - from all reimbursements*/
        var xScale = d3.scaleTime()
            .domain(d3.extent(data[0].means, d => d.period_final_date))
            .range([0, width - margin]);

        var yScale = d3.scaleLinear()
            .domain([0, d3.max(data[0].means, d => d.total_net_value)])
            .range([height - margin, 0]);

        var color = d3.scaleOrdinal(d3.schemeCategory10);

        chart_container.html('');
        var svg = chart_container.append("svg")
            .attr("width", (width + margin) + "px")
            .attr("height", (height + margin) + "px")
            .append('g')
            .attr("transform", `translate(${margin}, ${margin})`)
            .attr("width", '100%')
            .attr('preserveAspectRatio', 'xMinYMin');

        /* Add means line */
        var line = d3.line()
            .x(d => xScale(d.period_final_date))
            .y(d => yScale(d.period_mean_price_day));

        var lines = svg.append('g')
            .attr('class', 'lines');

        lines.selectAll('.line-group')
            .data(data).enter()
            .append('g')
            .attr('class', 'line-group')
            .on("mouseover", function (d, i) {
                svg.append("text")
                    .attr("class", "title-text")
                    .style("fill", color(i))
                    .text(d.period_mean_price_day)
                    .attr("text-anchor", "middle")
                    .attr("x", (width - margin) / 2)
                    .attr("y", 5);
            })
            .on("mouseout", function (d) {
                svg.select(".title-text").remove();
            })
            .append('path')
            .attr('class', 'line')
            .attr('d', d => line(d.means))
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

        var tweetRelevanceColor = d3.scaleLinear().domain([1,20])
            .range(["white", "purple"]);


        /* Add tweets circles in the line */
        lines.selectAll("circle-group")
            .data(data).enter()
            .append("g")
            .style("fill", (d, i) => color(i))
            .selectAll("circle")
            .data(d => d.means).enter()
            .append("g")
            .attr("class", "circle")
            .on("mouseover", function (d, index) {
                var price = d.total_net_value.toLocaleString('pt-br', {style: 'currency', currency: 'BRL'});
                var date = d.tweet_date;
                var favorite = d.favorite_count;
                var retweets = d.retweet_count;
                var suspicions = d.suspicions;
                div.transition()
                    .duration(200)
                    .style("opacity", .9);

                div.html("Data do Tweet: " + date
                    + "<br/>" + "Favoritos (Twitter): " + favorite
                    + "<br/>" + "Retweets (Twitter): " + retweets
                    + "<br/>" + "Valor do Reembolso: " + price
                    + "<br/>" + "Motivo da Suspeita: " + suspicions
                )
                    .style("left", (d3.event.pageX - 60) + "px")
                    .style("top", (d3.event.pageY - 150) + "px");

            })
            .on("click", function (d) {
                window.open(d.tweet_url, '_blank');
            })
            .on("mouseout", function (thisElement, index) {
                div.transition()
                    .duration(500)
                    .style("opacity", 0);
            })
            .append("circle")
            .attr("cx", d => xScale(d.period_final_date))
            .attr("cy", d => yScale(d.period_mean_price_day))
            .attr("r", d => d.tweet_circle_r)
            .style('opacity', circleOpacity)
            .style("fill", function (d, i) {
                return tweetRelevanceColor(d.favorite_count/10)
            })
            .on("mouseover", function (d) {
                d3.select(this)
                    .transition()
                    .duration(duration)
                    .attr("r", d.tweet_circle_r + 1);
            })
            .on("mouseout", function (d) {
                d3.select(this)
                    .transition()
                    .duration(duration)
                    .attr("r", d.tweet_circle_r);
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
            .text("Valor médio diário da Refeição no período entre tweets");
    });
}
