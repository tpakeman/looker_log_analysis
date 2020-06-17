// var colours = JSON.stringify(['#6CF', '#39F', '#06C', '#036', '#000']);
var colours = JSON.stringify(['#6CF', '#39F', '#89023E', '#CC7178', '#004777', '#002642', '#114B5F']);

function dateChart(data_array, container, title, subtitle) {
    Highcharts.chart(container, {
        chart: {type: 'spline', zoomType: 'xy'},
        title: {text: title},
        subtitle: {text: subtitle},
        yAxis: {title: {text: 'Time (s)'},min: 0},
        plotOptions: {spline: {marker: {enabled: true}}},
        colors: JSON.parse(colours),
        tooltip: {headerFormat: '<b>{series.name}</b><br>',pointFormat: '{point.x:%e. %b %Y}: {point.y:.2f} s'},

        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: {
             day: '%d %b %Y'
         },
         title: {
            text: 'Date'
        }
    },

    series: JSON.parse(data_array)
});
};

function colChart(labels, values, container, title) {
    Highcharts.chart(container, {
        chart: {type: 'bar'},
        title: {text: title},
        xAxis: {
            categories: JSON.parse(labels)
        },
        yAxis: {min: 0},
        legend: {reversed: true},
        plotOptions: {series: {stacking: 'normal'}},
        colors: JSON.parse(colours),
        series: JSON.parse(values)
    });
};

function dashboardChart(labels, values, container, title) {
    Highcharts.chart(container, {
        chart: {type: 'bar'},
        title: {text: title},
        xAxis: {
            categories: JSON.parse(labels),
            labels: {
                formatter: function () {
                    return 'Dashboard: ' + this.value},
                    useHTML: false
                }
        },
        yAxis: {min: 0},
        legend: {reversed: true},
        plotOptions: {series: {stacking: 'normal'}},
        colors: JSON.parse(colours),
        series: JSON.parse(values)
    });
};


function threadChart(labels, values, container, title) {
    Highcharts.chart(container, {
        chart: {type: 'bar'},
        title: {text: title},
        subtitle: {text: 'Click a thread ID to load the thread explorer'},
        xAxis: {
            categories: JSON.parse(labels),
            labels: {
                formatter: function () {
                    return '<a href="/thread/' + this.value + '">' + this.value + '</a>'},
                    useHTML: true
                }
            },
            yAxis: {min: 0},
            legend: {reversed: true},
            plotOptions: {series: {stacking: 'normal'}},
            colors: JSON.parse(colours),
            series: JSON.parse(values)
        });
};



function searchTable(inputId, tableId) {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById(inputId);
    filter = input.value.toUpperCase();
    table = document.getElementById(tableId);
    tr = table.getElementsByTagName("tr");
    th = table.getElementsByTagName("th");

    // Loop through all table rows, and hide those who don't match the search query
    for (i = 1; i < tr.length; i++) {
        tr[i].style.display = "none";
        for(var j=0; j<th.length; j++){
            td = tr[i].getElementsByTagName("td")[j];      
            if (td) {
                if (td.innerHTML.toUpperCase().indexOf(filter.toUpperCase()) > -1)                               {
                    tr[i].style.display = "";
                    break;
                }
            }
        }
    }
};

function buildTable(selector, rawData, key) {
    for (var i in rawData) {
        var tsDate = new Date(i * 1);
        var formatted_date = tsDate.getFullYear() + "-" + (tsDate.getMonth() + 1) + "-" + tsDate.getDate() + " " + tsDate.getHours() + ":" + tsDate.getMinutes() + ":" + tsDate.getSeconds();
        var tr = $('<tr/> <th scope="row">' + tsDate +'</th>');
        for (var j = 0; j < 3; j++) {tr.append($('<td/>'));};
            tr.find('td:eq(0)').html(rawData[i].process_id);
        tr.find('td:eq(1)').html(rawData[i].total);
        $(selector).append(tr);
        console.log("appending");
    }
};

function loadThread(value) {
    window.location = "/thread/" + value;
};