var svg = d3.select('#twitter-data-url'),
    tweet_chart = d3.select("#tweet_chart"),
    reimbursements_chart = d3.select("#reimbursements_chart"),
    refund_chart = d3.select("#refund_chart"),
    tooltip_container = d3.select("#tooltip"),
    congressperson_info = d3.select(".congressperson-info"),
    congressperson_select = d3.select("#congressperson"),
    congressperson_url = congressperson_select.attr('data-url');
var width = tweet_chart.node().getBoundingClientRect().width - 50;
var height = 300;
var margin = 50;
var duration = 250;

var defaultOpacity = "0.25";
var opacityHover = "0.85";
var otherLinesOpacityHover = "0.1";
var lineStroke = "1.5px";
var lineStrokeHover = "2.5px";

var circleOpacity = '0.85';
var circleOpacityHover = '1';
var circleOpacityOnLineHover = "0.25"
var circleRadius = 3;
var circleRadiusHover = 8;
var reimbursementsColor = "#949494";
var reimbursementsColorHover = "#8d0098";

var tweetRelevanceColor = d3.scaleLinear().domain([0, 20])
    .range(["white", "purple"]);
var color = d3.scaleOrdinal(d3.schemeCategory10);

var tooltip = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

$("#legislatures-select")
    .chosen({
        allow_single_deselect: true,
        placeholder_text_single: "Selecione uma Legislatura",
        no_results_text: "Sem Resultados"
    });

$("#congressperson")
    .chosen({
        allow_single_deselect: true,
        placeholder_text_single: "Selecione um Parlamentar",
        no_results_text: "Nenhum Parlamentar encontrado"

    })
    .change(function () {
        tweet_chart.html('');
        reimbursements_chart.html('');
        congressperson_info.html('');
        var congressperson_id = congressperson_select.property('value');

        show_congressperson_info(congressperson_id);
        apply_congressperson_filter(congressperson_id);
    });

$(document).ready(function () {
    show_refund_chart();
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

function show_refund_chart() {

    var refund_url = svg.attr('data-url-refund');
    moment.locale('pt-BR');
    var target = document.getElementById("refund_chart");
    var spinner = new Spinner({
        lines: 9, // The number of lines to draw
        length: 9, // The length of each line
        width: 5, // The line thickness
        radius: 14, // The radius of the inner circle
        color: '#711298', // #rgb or #rrggbb or array of colors
        speed: 1.9, // Rounds per second
        trail: 40, // Afterglow percentage
        className: 'spinner', // The CSS class to assign to the spinner
    }).spin(target);

    d3.json(refund_url, function (error, data) {
        spinner.stop();

        if (error) throw error;
        if (data.msg) {
            reimbursements_chart.html(data.msg);
            return
        }
        /* Order and parse data */
        data.forEach(function (d) {
            d.parsed_created_at = Date.parse(d.created_at);
            d.formatted_created_at = moment(d.parsed_created_at).format('DD/MM/YYYY');
            d.tweet_circle_r = 10;
            d.tweet_color = tweetRelevanceColor(d.favorite_count / 10);
        });
        data = data.sort(function (a, b) {
            return a.parsed_created_at - b.parsed_created_at;
        });

        var xScale = d3.scaleTime()
            .domain(d3.extent(data, d => d.parsed_created_at))
            .range([0, width - margin]);

        var yScale = d3.scaleLinear()
            .domain([0, d3.max(data, d => d.total_net_value)])
            .range([height - margin, 0]);

        var refund_svg = refund_chart.append("svg")
            .attr("width", (width + margin) + "px")
            .attr("height", (height + margin) + "px")
            .append('g')
            .attr("transform", `translate(${margin}, ${margin})`)
            .attr("width", '100%')
            .attr('preserveAspectRatio', 'xMinYMin');
        refund_svg.selectAll("dot")
            .data(data)
            .enter()
            .append("circle")
            .attr("r", 3.5)
            .attr("cx", function (d) {
                return x(d.parsed_created_at);
            })
            .attr("cy", function (d) {
                return y(d.total_net_value);
            });

    })

}

function apply_congressperson_filter(congressperson_id) {
    var tweets_url = svg.attr('data-url-tweets') + "?congressperson_id=" + congressperson_id;
    moment.locale('pt-BR');
    var target = document.getElementById("reimbursements_chart");

    var spinner = new Spinner({
        lines: 9, // The number of lines to draw
        length: 9, // The length of each line
        width: 5, // The line thickness
        radius: 14, // The radius of the inner circle
        color: '#711298', // #rgb or #rrggbb or array of colors
        speed: 1.9, // Rounds per second
        trail: 40, // Afterglow percentage
        className: 'spinner', // The CSS class to assign to the spinner
    }).spin(target);

    d3.json(tweets_url, function (error, data) {

        spinner.stop();

        if (error) throw error;
        if (data.msg) {
            reimbursements_chart.html(data.msg);
            return
        }

        /* Order and parse data */
        data.forEach(function (d) {
            d.means.forEach(function (d) {
                d.month = Date.parse(d.issue_date);
                d.formatted_period = moment(d.month).format('MMMM/YYYY');
            });
            d.means = d.means.sort(function (a, b) {
                return a.month - b.month;
            });

            d.reimbursements.forEach(function (d) {
                d.parsed_issue_date = Date.parse(d.issue_date);
                d.formatted_issue_date = moment(d.parsed_issue_date).format('DD/MM/YYYY');
                d.value = +d.value;
            });
            d.reimbursements = d.reimbursements.sort(function (a, b) {
                return a.parsed_issue_date - b.parsed_issue_date;
            });

            d.tweets.forEach(function (d) {
                d.parsed_created_at = Date.parse(d.created_at);
                d.parsed_issue_date = Date.parse(d.created_at);
                d.formatted_created_at = moment(d.parsed_created_at).format('DD/MM/YYYY');
                d.formatted_issue_date = moment(d.parsed_created_at).format('DD/MM/YYYY');
                d.tweet_circle_r = 10;
                d.tweet_color = tweetRelevanceColor(d.favorite_count / 10);

            });
            d.tweets = d.tweets.sort(function (a, b) {
                return a.parsed_created_at - b.parsed_created_at;
            });
        });

        /* Scale - from all reimbursements*/
        max_x = d3.max(data[0].tweets, d => d.parsed_created_at);
        if (!max_x) {
            max_x = d3.max(data[0].means, d => d.month);
        }
        var xScale = d3.scaleTime()
            .domain([d3.min(data[0].reimbursements, d => d.parsed_issue_date), max_x])
            .range([0, width - margin]);

        var yScaleMeans = d3.scaleLinear()
            .domain([0, d3.max(data[0].means, d => d.value)])
            .range([height - margin, 0]);

        var yScaleReimbursements = d3.scaleLinear()
            .domain([0, d3.max(data[0].reimbursements, d => d.value)])
            .range([height - margin, 0]);


        var tweet_svg = tweet_chart.append("svg")
            .attr("width", (width + margin) + "px")
            .attr("height", (height + margin) + "px")
            .append('g')
            .attr("transform", `translate(${margin}, ${margin})`)
            .attr("width", '100%')
            .attr('preserveAspectRatio', 'xMinYMin');

        var reimbursements_svg = reimbursements_chart.append("svg")
            .attr("width", (width + margin) + "px")
            .attr("height", (height + margin) + "px")
            .append('g')
            .attr("transform", `translate(${margin}, ${margin})`)
            .attr("width", '100%')
            .attr('preserveAspectRatio', 'xMinYMin');

        /* Add means line */
        var line = d3.line()
            .x(d => xScale(d.month))
            .y(d => yScaleMeans(d.value));

        var lines = tweet_svg.append('g')
            .attr('class', 'lines');
        var reimbusement_lines = reimbursements_svg.append('g')
            .attr('class', 'lines');

        /* Add Axis into SVG tweet_svg */
        var xAxis = d3.axisBottom(xScale)
            .ticks(10)
            .tickFormat(function (d) {

                return moment(d).format('DD/MMM/YY')
            });

        var yAxis = d3.axisLeft(yScaleMeans).ticks(5);

        tweet_svg.append("g")
            .attr("class", "x axis")
            .attr("transform", `translate(0, ${height - margin})`)
            .call(xAxis);

        tweet_svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
            .append('text')
            .attr("y", 15)
            .attr("transform", "rotate(-90)")
            .attr("fill", "#000")
            .text("Média diária no período entre tweets (reais)");

        /* Means Bars  */
        tweet_svg.append("g")
            .selectAll(".bar")
            .data(data[0].means).enter()
            .append("rect")
            .attr("class", "bar")
            .attr("x", function (d) {
                return xScale(d.month);
            })
            .attr("y", function (d) {
                return yScaleMeans(d.value);
            })
            .attr("width", 10)
            .style("fill", reimbursementsColor)
            .attr("height", function (d) {
                return height - margin - yScaleMeans(d.value);
            })
            .style('opacity', defaultOpacity)
            .on("mouseover", function (d) {
                var period = d.formatted_period,
                    mean = d.value.toLocaleString('pt-br', {style: 'currency', currency: 'BRL'});
                tooltip.transition()
                    .duration(200)
                    .style("opacity", .9);
                tooltip.html("Período: " + period
                    + "<br/>" + "Média de gasto diário no período: " + mean
                )
                    .style("left", (d3.event.pageX - 60) + "px")
                    .style("top", (d3.event.pageY - 150) + "px");

                d3.select(this)
                    .transition()
                    .duration(200)
                    .style("opacity", opacityHover)
                    .style("cursor", "pointer");
            })
            .on("mouseout", function (d) {
                tooltip.transition()
                    .duration(500)
                    .style("opacity", 0);
                d3.select(this)
                    .transition()
                    .duration(200)
                    .style("opacity", defaultOpacity)
                    .style("cursor", "normal");
            });


        /* Add tweets circles in the line */
        lines.selectAll("circle-group")
            .data(data).enter()
            .append("g")
            .selectAll("circle")
            .data(d => d.tweets).enter()
            .append("g")
            .attr("class", function (d, index) {
                return "tweet_" + d.id;
            })
            .on("mouseover", function (d, index) {
                var price = d.value.toLocaleString('pt-br', {style: 'currency', currency: 'BRL'});
                var date = d.formatted_created_at;
                var date_r = d.formatted_issue_date;
                var favorite = d.favorite_count;
                var retweets = d.retweet_count;
                var suspicions = d.suspicions;
                tooltip.transition()
                    .duration(200)
                    .style("opacity", .9);

                tooltip.html("Data do Tweet: " + date
                    + "<br/>" + "Data do Reembolso: " + date_r
                    + "<br/>" + "Favoritos (Twitter): " + favorite
                    + "<br/>" + "Retweets (Twitter): " + retweets
                    + "<br/>" + "Valor do Reembolso: " + price
                    + "<br/>" + "Motivo da Suspeita: " + suspicions
                )
                    .style("left", (d3.event.pageX - 60) + "px")
                    .style("top", (d3.event.pageY - 150) + "px");

            })
            .on("click", function (d) {
                tweet_url = "https://twitter.com/RosieDaSerenata/status/" + d.status;
                window.open(tweet_url, '_blank');
            })
            .on("mouseout", function (thisElement, index) {
                tooltip.transition()
                    .duration(500)
                    .style("opacity", 0);
            })
            .append("circle")
            .attr("cx", d => xScale(d.parsed_created_at))
            .attr("cy", 50)
            .attr("r", d => d.tweet_circle_r)
            .style('opacity', circleOpacity)
            .style("fill", d => d.tweet_color)
            .on("mouseover", function (d) {
                d3.select(this)
                    .transition()
                    .duration(duration)
                    .attr("r", d.tweet_circle_r + 1)
                    .style("cursor", "pointer");
                d3.select(".reimb_" + d.reimbursement_id)
                    .style("opacity", circleOpacityHover)
                    .select('circle')
                    .transition()
                    .duration(duration)
                    .attr('r', circleRadiusHover);

            })
            .on("mouseout", function (d) {
                d3.select(this)
                    .transition()
                    .duration(duration)
                    .attr("r", d.tweet_circle_r)
                    .style("cursor", "none");
                d3.selectAll('.circle')
                    .style('opacity', circleOpacity)
                    .transition()
                    .duration(duration)
                    .select('circle')
                    .attr('r', circleRadius);
            });


        /* Add reimbursement circles */
        reimbusement_lines.selectAll("circle-group")
            .data(data).enter()
            .append("g")
            .selectAll("circle")
            .data(d => d.reimbursements).enter()
            .append("g")
            .attr("class", function (d, index) {
                return "circle reimb_" + d.reimbursement_id;
            })
            .style("fill", function (d, i) {

                if (d.suspicions == 0) {
                    return reimbursementsColor
                } else {
                    return reimbursementsColorHover
                }
            })
            .on("mouseover", function (d, index) {
                var price = d.value.toLocaleString('pt-br', {style: 'currency', currency: 'BRL'});
                var date = d.formatted_issue_date;
                tooltip.transition()
                    .duration(200)
                    .style("opacity", .9);

                tooltip.html("Data do Reembolso: " + date
                    + "<br/>" + "Valor do Reembolso: " + price
                )
                    .style("left", (d3.event.pageX - 60) + "px")
                    .style("top", (d3.event.pageY - 80) + "px");

            })
            .on("click", function (d) {
                url = "https://jarbas.serenata.ai/layers/#/documentId/" + d.document_id;
                window.open(url, '_blank');
            })
            .on("mouseout", function (thisElement, index) {
                tooltip.transition()
                    .duration(500)
                    .style("opacity", 0);
            })
            .append("circle")
            .attr("cx", d => xScale(d.parsed_issue_date))
            .attr("cy", d => yScaleReimbursements(d.value))
            .attr("r", circleRadius)
            .style('opacity', circleOpacity)
            .on("mouseover", function (d) {
                d3.select(this)
                    .transition()
                    .duration(duration)
                    .attr("r", circleRadiusHover)
                    .style('opacity', circleOpacityHover)
                    .style("cursor", "pointer");

            })
            .on("mouseout", function (d) {
                d3.select(this)
                    .transition()
                    .duration(duration)
                    .attr("r", circleRadius)
                    .style('opacity', circleOpacity)
                    .style("cursor", "none");


            });

        /* Add Axis into SVG tweet_svg */
        var yAxis = d3.axisLeft(yScaleReimbursements).ticks(5);

        reimbusement_lines.append("g")
            .attr("class", "x axis")
            .attr("transform", `translate(0, ${height - margin})`)
            .call(xAxis);

        reimbusement_lines.append("g")
            .attr("class", "y axis")
            .call(yAxis)
            .append('text')
            .attr("y", 15)
            .attr("transform", "rotate(-90)")
            .attr("fill", "#000")
            .text("Valor da Refeição (em reais)");
    });
}
