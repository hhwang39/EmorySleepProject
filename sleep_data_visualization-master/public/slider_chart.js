function drawChart(arrayData) {
    data = google.visualization.arrayToDataTable(arrayData);
    data.addColumn({type:'string', role:'annotationText'});
    data.addColumn({type:'string', role:'annotation'});

    // data.addColumn({type:''})
    console.log(data);
    var chart = new google.visualization.ChartWrapper({
        chartType: 'LineChart',
        containerId: 'chart_div',
        options: {
            title: 'Sleep Like a Baby',
            hAxis: {title: 'Time (seconds)'},
            vAxis: {title: 'Acclerometer reading'},
            selectionMode: 'multiple',
            crosshair: {
              orientation: 'vertical',
              color: 'blue'
            },
            height: 400,
            // omit width, since we set this in CSS
            chartArea: {
                width: '75%' // this should be the same as the ChartRangeFilter
            }
        }
    });

    var control = new google.visualization.ControlWrapper({
        controlType: 'ChartRangeFilter',
        containerId: 'control_div',
        options: {
            filterColumnIndex: 0,
            ui: {
                chartOptions: {
                    height: 50,
                    // omit width, since we set this in CSS
                    chartArea: {
                        width: '75%' // this should be the same as the ChartRangeFilter
                    }
                }
            }
        }
    });

    var dashboard = new google.visualization.Dashboard(document.querySelector('#dashboard_div'));
    dashboard.bind([control], [chart]);
    dashboard.draw(data);

    //TODO decide how to format hAxis

    function zoom5Sec () {
        var range = data.getColumnRange(0);
        control.setState({
            range: {
                start: range.min,
                end: range.min + 5
            }
        });
        control.draw();
    }
    function zoom10Sec () {
        var range = data.getColumnRange(0);
        control.setState({
          range: {
              start: range.min,
              end: range.min + 10
          }
        });
        control.draw();
    }
    function zoom1Min () {
        // zoom here sets the month back 1, which can have odd effects when the last month has more days than the previous month
        // eg: if the last day is March 31, then zooming last month will give a range of March 3 - March 31, as this sets the start date to February 31, which doesn't exist
        // you can tweak this to make it function differently if you want
        var range = data.getColumnRange(0);
        control.setState({
          range: {
              start: range.min,
              end: range.min + 60
          }
        });
        control.draw();
    }
    function myClickHandler(){
      var selection = dashboard.getSelection();
      var range = {};
      var nums = [];

      for (var i = 0; i < selection.length; i++) {
        var item = selection[i];
        if (item.row != null) {
          nums.push(item.row);
        }
      }

      if (nums.length > 2) {
        alert('Please select 1 or 2 points');
      } else if (nums.length == 1) {

        var point = prompt("Data classification", "POI");
        data.setCell(nums[0], 5, 'True');
        data.setCell(nums[0], 6, point);
        dashboard.draw(data);
      } else {
        nums = nums.sort(function(a, b){
          return a - b;
        });
        range = {
          min: nums[0],
          max: nums[1]
        };
        // alert('You selected ' + JSON.stringify(range));
        // data.getValue(rowIndex, colIndex) -> get value from DataTable
        // data.getNumberOfColumns() -> can be used to iterate over cols
        var type = prompt("Data classification", "Kick");
        data.setCell(range.min, 5, 'True');
        data.setCell(range.min, 6, type + ' start');
        data.setCell(range.max, 5, 'True');
        data.setCell(range.max, 6, type + ' end');
        dashboard.draw(data);
      }
    }


    var runOnce = google.visualization.events.addListener(dashboard, 'ready', function () {
        google.visualization.events.removeListener(runOnce);

        if (document.addEventListener) {
            document.querySelector('#fiveSec').addEventListener('click', zoom5Sec);
            document.querySelector('#tenSec').addEventListener('click', zoom10Sec);
            document.querySelector('#oneMin').addEventListener('click', zoom1Min);
            document.querySelector('#myClickHandler').addEventListener('click', myClickHandler);

        }
        else if (document.attachEvent) {
            document.querySelector('#fiveSec').attachEvent('onclick', zoom5Sec);
            document.querySelector('#tenSec').attachEvent('onclick', zoom10Sec);
            document.querySelector('#oneMin').attachEvent('onclick', zoom1Min);
            document.querySelector('#myClickHandler').attachEvent('onclick', myClickHandler);
        }
        else {
            document.querySelector('#fiveSec').onclick = zoom5Sec;
            document.querySelector('#tenSec').onclick = zoom10Sec;
            document.querySelector('#oneMin').onclick = zoom1Min;
            document.querySelector('#myClickHandler').onclick = myClickHandler;
        }
    });
}

function getData() {
  $.ajax({
      method: "GET",
      url: "./api/parse_csv",
      contentType: "application/json",
    })
    .done(function(data) {
      drawChart(data);
    });
}

function exportCSV() {
  var csv = google.visualization.dataTableToCsv(data);
  var hiddenElement = document.createElement('a');
  hiddenElement.href = 'data:text/csv;charset=utf-8,' + encodeURI(csv);
  hiddenElement.target = '_blank';
  hiddenElement.download = 'data.csv';
  hiddenElement.click();
}

google.charts.load('visualization', '1', {packages:['controls'], callback: getData});
