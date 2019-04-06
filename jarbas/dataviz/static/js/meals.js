var svg = d3.select('#twitter-chart'),
    tweets_url = svg.attr('data-url'),
    margin = {top: 20, right: 20, bottom: 30, left: 40},
    width = svg.attr("width") - margin.left - margin.right,
    height = svg.attr("height") - margin.top - margin.bottom;




d3.json(tweets_url, function (error, data) {
    if (error) throw error;

    // parse and sort data
    data.forEach(function (d) {

        d.issue_date = Date.parse(d.issue_date);
        d.total_net_value = Number(d.total_net_value);
    });

    function sortByDateAscending(a, b) {
        return a.issue_date - b.issue_date;
    }

    data = data.sort(sortByDateAscending);

    // define chart domain
    var x = d3.scaleTime().range([0, width]);
    var y = d3.scaleLinear().range([height, 0]);

    var line = d3.line()
        .x(function (d) {
            return x(d.issue_date);
        })
        .y(function (d) {
            return y(d.total_net_value);
        });

    x.domain([
        d3.min(data, function (d) {
            return d.issue_date;
        }),
        d3.max(data, function (d) {
            return d.issue_date;
        })]);


    y.domain([
        d3.min(data, function (d) {
            return d.total_net_value;
        }),
        d3.max(data, function (d) {
            return d.total_net_value;
        })]);

// 3. Call the x axis in a group tag
svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(xScale)); // Create an axis component with d3.axisBottom

// 4. Call the y axis in a group tag
svg.append("g")
    .attr("class", "y axis")
    .call(d3.axisLeft(yScale)); // Create an axis component with d3.axisLeft


    svg.selectAll(".dot")
    .data(dataset)
  .enter().append("circle") // Uses the enter().append() method
    .attr("class", "dot") // Assign a class for styling
    .attr("cx", function(d, i) { return xScale(i) })
    .attr("cy", function(d) { return yScale(d.y) })
    .attr("r", 5)
      .on("mouseover", function(a, b, c) {
  			console.log(a)
        this.attr('class', 'focus')
		})
      .on("mouseout", function() {  })
});
