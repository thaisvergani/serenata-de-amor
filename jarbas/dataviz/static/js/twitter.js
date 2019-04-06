var svg = d3.select('#twitter-data-url'),
    tweets_url = svg.attr('data-url');

d3.json(tweets_url, function (error, data) {
    if (error) throw error;

    // 2. Use the margin convention practice
    var margin = {top: 50, right: 100, bottom: 50, left: 100}
        , width = window.innerWidth - margin.left - margin.right // Use the window's width
        , height = 500 - margin.top - margin.bottom; // Use the window's height

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

    var line = d3.line()
        .x(function (d) {
            return x(d.issue_date);
        })
        .y(function (d) {
            return y(d.total_net_value);
        })
        .curve(d3.curveMonotoneX);


// 1. Add the SVG to the page and employ #2
    var svg = d3.select("body").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

// 3. Call the x axis in a group tag
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x)); // Create an axis component with d3.axisBottom

// 4. Call the y axis in a group tag
    svg.append("g")
        .attr("class", "y axis")
        .call(d3.axisLeft(y)); // Create an axis component with d3.axisLeft

// 9. Append the path, bind the data, and call the line generator
    svg.append("path")
        .datum(data) // 10. Binds data to the line
        .attr("class", "line") // Assign a class for styling
        .attr("d", line); // 11. Calls the line generator

// 12. Appends a circle for each datapoint
    svg.selectAll(".dot")
        .data(data)
        .enter().append("circle") // Uses the enter().append() method
        .attr("class", "dot") // Assign a class for styling
        .attr("cx", function (d, i) {
            return x(i)
        })
        .attr("cy", function (d) {
            return y(d.total_net_value)
        })
        .attr("r", 5)
        .on("mouseover", function (a, b, c) {
            console.log(a)
            this.attr('class', 'focus')
        })
        .on("mouseout", function () {
        })
});
