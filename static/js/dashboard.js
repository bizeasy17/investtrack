// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

$(function () {
    var chart;

    var csrftoken = Cookies.get('csrftoken');
    var userBaseEndpoint = '/user/';
    var investBaseEndpoint = '/invest/stocks/';

    var chartShowDays15 = 5
    var chartShowDays30 = 10
    var chartShowDays60 = 15
    var chartShowDays = 60
    var chartShowDaysW = 180
    var chartShowDaysM = 720

    if ($("#profitDevChart").length) {
        var profitDevChartCanvas = $("#profitDevChart").get(0).getContext("2d");
        var profitDevChart = new Chart(profitDevChartCanvas, {
          type: "bar",
          data: {
            labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            datasets: [
              {
                type: "line",
                fill: false,
                label: "Total YTD Sales",
                data: [330, -60, 370, 1400, 1700, 2630],
                borderColor: "#00ff00"
              },
              {
                type: "line",
                fill: false,
                label: "Current Month Sales",
                data: [330, -270, 430, 930, 330, 930],
                borderColor: "#ff4c5b"
              },
              {
                label: "Other Sales",
                data: [100, -230, 340, 340, 260, 340],
                backgroundColor: "#6640b2"
              },
              {
                label: "Offline Sales",
                data: [100, -230, 340, 340, 260, 340],
                backgroundColor: "#1234b2"
              },
              {
                label: "Online Sales",
                data: [130, 190, -250, 250, -190, 260],
                backgroundColor: "#1cbccd"
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: true,
            layout: {
              padding: {
                left: 0,
                right: 0,
                top: 20,
                bottom: 0
              }
            },
            scales: {
              yAxes: [
                {
                  display: true,
                  gridLines: {
                    display: true,
                    drawBorder: false,
                    color: "#f8f8f8",
                    zeroLineColor: "#f8f8f8"
                  },
                  ticks: {
                    display: true,
                    min: -500,
                    max: 3000,
                    stepSize: 100,
                    fontColor: "#b1b0b0",
                    fontSize: 10,
                    padding: 10
                  }
                }
              ],
              xAxes: [
                {
                  stacked: false,
                  ticks: {
                    beginAtZero: true,
                    fontColor: "#b1b0b0",
                    fontSize: 10
                  },
                  gridLines: {
                    color: "rgba(0, 0, 0, 0)",
                    display: false
                  },
                }
              ]
            },
            legend: {
              display: true
            },
            elements: {
              point: {
                radius: 3,
                backgroundColor: "#ff4c5b"
              }
            }
          }
        });
    }
    var profitWeekChart;
    $('input:radio[name="period"]').change(function () {
      // 设置当前选定利润分析周期
      var period = $(this).val();
      $.ajax({
        url: userBaseEndpoint + 'profit-trend/period/' + period + '/',
        success: function (data) {
          // 亏损的字体颜色为绿
          if(data.avg_profit<0){
            $("#prfAvgProfit").removeClass("text-danger");
            $("#prfAvgProfit").addClass("text-success");
          }
          $("#prfAvgProfit").text(data.avg_profit);
          // 亏损的字体颜色为绿
          if (data.profit_ratio<0){
            $("#prfProfitRatio").removeClass("text-danger");
            $("#prfProfitRatio").addClass("text-success");
          }
          $("#prfProfitRatio").text(data.profit_ratio + "%");
          // 更新利润趋势图
          profitWeekChart.data.labels = data.label;
          // profitWeekChart.data.datasets.forEach((dataset) => {
          //   dataset.data.push(data);
          // });
          profitWeekChart.data.datasets[0].data = data.profit_trend;
          profitWeekChart.data.datasets[1].data = data.previous_profit_trend;
          // profitWeekChart.options = {
          //   scales: {
          //       yAxes: [{
          //           ticks: {
          //             min: data.min_profit,
          //             max: data.max_profit,
          //             stepSize: data.max_profit / 10,
          //           }
          //       }]
          //   }
          // };
          profitWeekChart.update();
        }
      })
    });

    if ($("#profitDevChartWeek").length) {
      var profitWeekChartCanvas = $("#profitDevChartWeek")
        .get(0)
        .getContext("2d");
      var period = $('input:radio[name="period"]:checked').val();
      $.ajax({
        url: userBaseEndpoint + 'profit-trend/period/' + period + '/',
        // headers: { 'X-CSRFToken': csrftoken },
        method: 'GET',
        dataType: 'json',
        success: function (data) {
          // 亏损的字体颜色为绿
          if(data.avg_profit<0){
            $("#prfAvgProfit").removeClass("text-danger");
            $("#prfAvgProfit").addClass("text-success");
          }
          $("#prfAvgProfit").text(data.avg_profit);
          // 亏损的字体颜色为绿
          if (data.profit_ratio<0){
            $("#prfProfitRatio").removeClass("text-danger");
            $("#prfProfitRatio").addClass("text-success");
          }
          $("#prfProfitRatio").text(data.profit_ratio + "%");
          
          profitWeekChart = new Chart(profitWeekChartCanvas, {
            type: "bar",
            data: {
              labels: data.label,
              datasets: [
                {
                  type: "line",
                  fill: false,
                  label: "收益",
                  data: data.profit_trend,
                  borderColor: "#1cbccd",
                  barPercentage: 0.9,
                  categoryPercentage: 0.7
                },
                {
                  label: "同/环比收益",
                  data: data.previous_profit_trend,
                  backgroundColor: "#ffbf36",
                  barPercentage: 0.9,
                  categoryPercentage: 0.7
                }
              ]
            },
            options: {
              responsive: true,
              maintainAspectRatio: true,
              layout: {
                padding: {
                  left: 0,
                  right: 0,
                  top: 20,
                  bottom: 0
                }
              },
              scales: {
                yAxes: [
                  {
                    display: true,
                    gridLines: {
                      display: true,
                      drawBorder: false,
                      color: "#f8f8f8",
                      zeroLineColor: "#f8f8f8"
                    },
                    ticks: {
                      display: true,
                      min: data.min_profit,
                      max: data.max_profit,
                      stepSize: data.max_profit / 10,
                      fontColor: "#b1b0b0",
                      fontSize: 10,
                      padding: 10
                    }
                  }
                ],
                xAxes: [
                  {
                    stacked: false,
                    ticks: {
                      beginAtZero: true,
                      fontColor: "#b1b0b0",
                      fontSize: 10
                    },
                    gridLines: {
                      color: "rgba(0, 0, 0, 0)",
                      display: false
                    },
                  }
                ]
              },
              legend: {
                display: false
              },
              elements: {
                point: {
                  radius: 3,
                  backgroundColor: "#ff4c5b"
                }
              }
            }
          });
        }
      });
    }
    
    if ($("#tradeSuccessRatio").length) {
      var tradeSuccessRatioChartCanvas = $("#tradeSuccessRatio")
        .get(0)
        .getContext("2d");
      var defaultPeriod = 'y'; //all stock shares
      $.ajax({
        url: userBaseEndpoint + 'invest-attempt-trend/period/' + defaultPeriod + '/',
        // headers: { 'X-CSRFToken': csrftoken },
        method: 'GET',
        dataType: 'json',
        success: function (data) {
          $("#invAvgAttempt").text(data.avg_attempt);
          $("#invRelAttemptRatio").text(data.yoy_ratio);
          var tradeSuccessRatiohChart = new Chart(tradeSuccessRatioChartCanvas, {
            type: "bar",
            data: {
              labels: data.label,
              datasets: [
                {
                  type: "line",
                  fill: false,
                  label: "同比（成功）",
                  data: data.yoy_success_rate,
                  borderColor: "#1cbccd"
                },
                {
                  type: "line",
                  fill: false,
                  label: "同比（失败）",
                  data: data.yoy_fail_rate,
                  borderColor: "#ffbf36"
                },
                {
                  label: "今年（成功）",
                  data: data.success_rate,
                  backgroundColor: "#ffbf36"
                },
                {
                  label: "今年（失败）",
                  data: data.fail_rate,
                  backgroundColor: "#1cbccd"
                }
              ]
            },
            options: {
              responsive: true,
              maintainAspectRatio: true,
              layout: {
                padding: {
                  left: 0,
                  right: 0,
                  top: 20,
                  bottom: 0
                }
              },
              scales: {
                yAxes: [
                  {
                    display: true,
                    gridLines: {
                      display: true,
                      drawBorder: false,
                      color: "#f8f8f8",
                      zeroLineColor: "#f8f8f8"
                    },
                    ticks: {
                      display: true,
                      min: data.min_attempt,
                      max: data.max_attempt,
                      stepSize: 1,
                      fontColor: "#b1b0b0",
                      fontSize: 10,
                      padding: 10
                    }
                  }
                ],
                xAxes: [
                  {
                    stacked: false,
                    ticks: {
                      beginAtZero: true,
                      fontColor: "#b1b0b0",
                      fontSize: 10
                    },
                    gridLines: {
                      color: "rgba(0, 0, 0, 0)",
                      display: false
                    },
                    
                    // categoryPercentage: 0.7
                  }
                ]
              },
              legend: {
                display: false
              },
              elements: {
                point: {
                  radius: 3,
                  backgroundColor: "#ff4c5b"
                }
              }
            }
          });
        }
      });   
    }

    if ($("#positionChart").length) {
        var positionChartCanvas = $("#positionChart").get(0).getContext("2d");
        var account = 'a'; //all account
        var stock_symbol = 'a'; //all stock shares
        $.ajax({
          url: userBaseEndpoint + 'position-vs-status/' + account + '/' + stock_symbol + '/',
          // headers: { 'X-CSRFToken': csrftoken },
          method: 'GET',
          dataType: 'json',
          success: function (data) {
            $("#pTotalAvailPerTarget").text(data.total_percentage);
            var positionChart = new Chart(positionChartCanvas, {
              type: 'horizontalBar',
              data: {
                labels: data.label,
                datasets: [
                  {
                    label: '目标仓位',
                    data: data.target_position,
                    backgroundColor: '#1cbccd',
                  },
                  {
                    label: '已有仓位',
                    data: data.available_position,
                    backgroundColor: '#ffbf36',
                  }
                ]
              },
              options: {
                responsive: true,
                maintainAspectRatio: true,
                layout: {
                  padding: {
                    left: -7,
                    right: 0,
                    top: 0,
                    bottom: 0
                  }
                },
                scales: {
                  yAxes: [{
                    display: true,
                    gridLines: {
                      display: false,
                      drawBorder: false
                    },
                    ticks: {
                      display: true,
                      min: 0,
                      max: 400,
                      stepSize: 100,
                      fontColor: "#b1b0b0",
                      fontSize: 10,
                      padding: 10
                    },
                  }],
                  xAxes: [{
                    display: true,
                    stacked: false,
                    ticks: {
                      display: false,
                      beginAtZero: true,
                      fontColor: "#b1b0b0",
                      fontSize: 10
                    },
                    gridLines: {
                      display: true,
                      drawBorder: false,
                      lineWidth: 1,
                      color: "#f5f5f5",
                      zeroLineColor: "#f5f5f5"
                    }
                  }]
                },
                legend: {
                  display: true
                },
                elements: {
                  point: {
                    radius: 3,
                    backgroundColor: '#ff4c5b'
                  }
                },
                legendCallback: function (chart) {
                  var text = [];
                  text.push('<div class="item mr-4 d-flex align-items-center small">');
                  text.push(
                    '<div class="item-box mr-2" data-color="' +
                    chart.data.datasets[0].backgroundColor +
                    ' "></div><p class="text-black mb-0"> ' +
                    chart.data.datasets[0].label +
                    "</p>"
                  );
                  text.push('</div>');
                  text.push('<div class="item d-flex align-items-center small">');
                  text.push(
                    '<div class="item-box mr-2" data-color="' +
                    chart.data.datasets[1].backgroundColor +
                    '"></div><p class="text-black mb-0"> ' +
                    chart.data.datasets[1].label +
                    " </p>"
                  );
                  text.push('</div>');
                  return text.join('');
                }
              },
            });
          }
        });
        
        // document.getElementById('positionLegend').innerHTML = positionChart.generateLegend();
    }
});
    