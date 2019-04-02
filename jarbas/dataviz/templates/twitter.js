    var tweets_url = "{% url 'dataviz:tweet_chart' %}";

// 2. Use the margin convention practice
var margin = {top: 50, right: 50, bottom: 50, left: 50}
  , width = window.innerWidth - margin.left - margin.right // Use the window's width
  , height = window.innerHeight - margin.top - margin.bottom; // Use the window's height


// 5. X scale will use the index of our data
var xScale = d3.scaleLinear()
    .range([0, width]); // output

// 6. Y scale will use the randomly generate number
var yScale = d3.scaleLinear()
    .range([height, 0]); // output




    d3.json(tweets_url, function (error, data) {
        console.log(data);
        xScale.domain(data.map(function(d) {
            return d.issue_date
        }));
        yScale.domain([0, d3.max(data, function(d) {
            return d.total_net_value
        })]);
    });
    // 7. d3's line generator
var line = d3.line()
    .x(function(d, i) { return xScale(i); }) // set the x values for the line generator
    .y(function(d) { return yScale(d.y); }) // set the y values for the line generator
    .curve(d3.curveMonotoneX) // apply smoothing to the line

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
    .call(d3.axisBottom(xScale)); // Create an axis component with d3.axisBottom

// 4. Call the y axis in a group tag
svg.append("g")
    .attr("class", "y axis")
    .call(d3.axisLeft(yScale)); // Create an axis component with d3.axisLeft

// 9. Append the path, bind the data, and call the line generator
svg.append("path")
    .datum(dataset) // 10. Binds data to the line
    .attr("class", "line") // Assign a class for styling
    .attr("d", line); // 11. Calls the line generator

</scrip
