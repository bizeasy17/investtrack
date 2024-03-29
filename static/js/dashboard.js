// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

$(function () {
  var chart;

  var csrftoken = Cookies.get('csrftoken');
  var userBaseEndpoint = '/user/';
  var investBaseEndpoint = '/invest/stocks/';
  var stockmarketEndpoint = '/stockmarket/';
  var dashboardEndpoint = '/dashboard/';
  var stocktradeEndpoint = '/stocktrade/';
  var tradeAccEndpoint = '/tradeaccounts/';


  var chartShowDays15 = 5
  var chartShowDays30 = 10
  var chartShowDays60 = 15
  var chartShowDays = 60
  var chartShowDaysW = 180
  var chartShowDaysM = 720

  $('#searchForTrade').autoComplete({
    resolver: 'custom',
    formatResult: function (item) {
      return {
        value: item.id,
        text: item.id + " - " + item.text,
        html: [
          item.id + ' - ' + item.text,// +  '[' + item.market + ']',
        ]
      };
    },
    events: {
      search: function (qry, callback) {
        // let's do a custom ajax call
        $.ajax(
          stockmarketEndpoint + 'listed_companies/' + $('#searchForTrade').val(),
        ).done(function (res) {
          callback(res.results)
        });
      }
    }
  });

  $('#searchForTrade').on('autocomplete.select', function (evt, item) {
    var code = item.id;
    var showCode = item.ts_code;
    var showName = item.text;
    var market = item.market;
    window.location.href = stocktradeEndpoint + code + "/account/" + $("#defaultAccount").val();
    // window.location.href = userBaseEndpoint + "account/" + $("#defaultAccount").val() + "/trade/" + code + "/";
  });

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
      url: dashboardEndpoint + 'profit-trend/period/' + period + '/',
      success: function (data) {
        // 亏损的字体颜色为绿
        if (data.max_profit < 0) {
          $("#prfMaxProfit").removeClass("text-danger");
          $("#prfMaxProfit").addClass("text-success");
        }
        $("#prfMaxProfit").text(data.max_profit.toLocaleString());
        // 亏损的字体颜色为绿
        if (data.profit_ratio < 0) {
          $("#prfProfitRatio").removeClass("text-danger");
          $("#prfProfitRatio").addClass("text-success");
        }
        $("#prfProfitRatio").text(data.profit_ratio + '%');
        // 更新利润趋势图
        profitWeekChart.data.labels = data.label;
        // profitWeekChart.data.datasets.forEach((dataset) => {
        //   dataset.data.push(data);
        // });
        profitWeekChart.data.datasets[1].data = data.profit_trend;
        profitWeekChart.data.datasets[0].data = data.previous_profit_trend;
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
      url: dashboardEndpoint + 'profit-trend/period/' + period + '/',
      // headers: { 'X-CSRFToken': csrftoken },
      method: 'GET',
      dataType: 'json',
      success: function (data) {
        if (data.code == "empty") {
          $("#noProfit").append("<span class='text-muted'>无交易信息</span>");
        } else {
          // 亏损的字体颜色为绿
          if (data.max_profit < 0) {
            $("#prfMaxProfit").removeClass("text-danger");
            $("#prfMaxProfit").addClass("text-success");
          }
          $("#prfMaxProfit").text(data.max_profit.toLocaleString());
          // 亏损的字体颜色为绿
          if (data.profit_ratio < 0) {
            $("#prfProfitRatio").removeClass("text-danger");
            $("#prfProfitRatio").addClass("text-success");
          }
          $("#prfProfitRatio").text(data.profit_ratio + '%');

          profitWeekChart = new Chart(profitWeekChartCanvas, {
            type: "bar",
            data: {
              labels: data.label,
              datasets: [
                {
                  type: "line",
                  fill: false,
                  label: "同/环比收益",
                  data: data.previous_profit_trend,
                  borderColor: "#1cbccd",
                  barPercentage: 0.9,
                  categoryPercentage: 0.7
                },
                {
                  label: "收益",
                  data: data.profit_trend,
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
                      // min: data.min_profit,
                      // max: data.max_profit,
                      // stepSize: data.max_profit / 10,
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
      }
    });
  }

  if ($("#tradeSuccessRatio").length) {
    var tradeSuccessRatioChartCanvas = $("#tradeSuccessRatio")
      .get(0)
      .getContext("2d");
    var defaultPeriod = 'y'; //all stock shares
    $.ajax({
      url: dashboardEndpoint + 'invest-attempt-trend/period/' + defaultPeriod + '/',
      // headers: { 'X-CSRFToken': csrftoken },
      method: 'GET',
      dataType: 'json',
      success: function (data) {
        if (data.code == "empty") {
          $("#noAttempt").append("<span class='text-muted'>无交易信息</span>");
        } else {
          $("#invAvgAttempt").text(data.avg_attempt);
          $("#invRelAttemptRatio").text(data.success_ratio);
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
                      // min: data.min_attempt,
                      // max: data.max_attempt,
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
      }
    });
  }

  if ($("#positionChart").length) {
    var positionChartCanvas = $("#positionChart").get(0).getContext("2d");
    var account = 'a'; //all account
    var stock_symbol = 'a'; //all stock shares
    $.ajax({
      url: dashboardEndpoint + 'position-vs-status/' + account + '/' + stock_symbol + '/',
      // headers: { 'X-CSRFToken': csrftoken },
      method: 'GET',
      dataType: 'json',
      success: function (data) {
        if (data.code == "empty") {
          $("#noPosition").append("<span class='text-muted'>无持仓信息</span>");
        } else {
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
      }
    });

    // document.getElementById('positionLegend').innerHTML = positionChart.generateLegend();
  }


  // var isOpenForTrade = function (inputDatetime) {
  //   // var dateAndTime = inputDatetime.split(" ");
  //   var date = formatDate(inputDatetime, "-");
  //   var openTime = new Date(date + " 9:30:00");
  //   var morningCloseTime = new Date(date + " 11:30:00");
  //   var afternoonOpenTime = new Date(date + " 13:00:00");
  //   var closeTime = new Date(date + " 15:00:00");
  //   var day = inputDatetime.getDay();
  //   var hour = inputDatetime.getHours();
  //   var min = inputDatetime.getMinutes();
  //   if (day == 0 || day == 6) return false; //周六周日不需要刷新
  //   if (inputDatetime >= openTime && inputDatetime <= morningCloseTime) {
  //     return true;
  //   }
  //   if (inputDatetime >= afternoonOpenTime && inputDatetime <= closeTime) {
  //       return true;
  //   }
  //   if(inputDatetime > date) {
  //       return false;
  //   }
  //   return false;
  // }
  var renderStockProfitChangeChart = function (chartId) {
    var arrId = chartId.split("_");
    var stock_code = arrId[0].substring(5);
    var pId = arrId[1];
    if ($("#" + chartId).length) {
      var profitChgCanvas = $("#" + chartId)
        .get(0)
        .getContext("2d");
      $.ajax({
        url: dashboardEndpoint + 'stock-profit-chg/' + pId + "/" + stock_code + '/',
        // headers: { 'X-CSRFToken': csrftoken },
        method: 'GET',
        dataType: 'json',
        success: function (data) {
          $("#" + chartId).removeClass("d-none");
          var profitChgChart = new Chart(profitChgCanvas, {
            type: "line",
            data: {
              labels: data.label,
              datasets: [
                {
                  type: "line",
                  fill: false,
                  label: "当前收益",
                  data: data.chg_seq,
                  borderColor: "#1cbccd",
                  barPercentage: 0.9,
                  categoryPercentage: 0.7
                },
                {
                  type: "line",
                  label: "目标收益",
                  fill: false,
                  data: data.chg_target_seq,
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
                      // min: data.min_profit,
                      max: 100,
                      // stepSize: data.max_profit / 10,
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
              tooltips: {
                callbacks: {
                  label: function (tooltipItem, data) {
                    var dataset = data.datasets[tooltipItem.datasetIndex];
                    var point = dataset.data[tooltipItem.index];
                    var label = data.datasets[tooltipItem.datasetIndex].label || '';
                    if (label) {
                      label += ': ';
                    }
                    if (!isNaN(point)) {
                      label += point + "%";
                    }
                    return label;
                  }
                }
              },
              legend: {
                display: false
              },
              elements: {
                point: {
                  radius: 0,
                  backgroundColor: "#ff4c5b",
                  display: false
                }
              }
            }
          });
        },
        statusCode: {
          404: function () {
            $("#noChg" + stock_code + "_" + pId).append("<span class='text-muted'>无收益分布信息</span>");
            $("#" + chartId).addClass("d-none");
          },
          500: function () {
            $("#noChg" + stock_code + "_" + pId).append("<span class='text-muted'>系统错误，请稍后再试</span>");
            $("#" + chartId).addClass("d-none");
          }
        }
      });
    }
  }

  var leavePositionComments = function (event) {
    // event.preventDefault();
    var id = $(this).attr("id");
    var arr = id.split("_");
    if (event.ctrlKey && event.keyCode == 13 && $(this).val() != "") {
      $.ajax(
        {
          url: tradeAccEndpoint + 'comments/' + arr[1] + "/" + arr[2] + "/",
          headers: { 'X-CSRFToken': csrftoken },
          method: 'POST',
          data: {
            comment: $(this).val()
          },
          success: function (data) {
            var cmtPanel = $("#cp_" + arr[1] + "_" + arr[2]);
            var html = "";
            html = "<div class='row col-lg-12'>"+
                      "<p class='col-lg-12'><span class='small'>"+data.comment[0].content+"</span></p>"+
                      "<p class='col-lg-12'><span class='small'>股价-"+data.comment[0].current_price+", 涨幅-"+data.comment[0].pct_chg+"%, 当前收益率-"+data.comment[0].position_pct_chg+"% (记录于 "+data.comment[0].created_time+")</span></p>"+
                    "</div>";
            cmtPanel.append(html);
            $("#messages").removeClass('d-none');
            $("#messageText").html("<strong>添加成功.</strong>");
          },
          statusCode: {
            403: function () {
              alert("403 forbidden");
            },
            404: function () {
              alert("404 page not found");
            },
            500: function () {
              alert("500 internal server error");
            }
          }
        }
      );
    }
  }


  var inputCmt = document.getElementsByName("input-comment");
  if (inputCmt.length > 0) {
    $(inputCmt).each(function (id, obj) {
      obj.addEventListener("keydown", leavePositionComments)
    });
  }

  var commentPanel = document.getElementsByName("comments-panel");
  if (commentPanel.length > 0) {
    $(commentPanel).each(function (id, obj) {
      var arr = $(obj).attr("id").split("_");
      $.ajax(
        {
          url: tradeAccEndpoint + 'comments/' + arr[1] + "/" + arr[2] + "/",
          success: function (data) {
            $(data.comments).each(function (iid, iobj) {
              var html = "";
              html = "<div class='row col-lg-12'>"+
                        "<p class='col-lg-12'><span class='small'>"+iobj.comment+"</span></p>"+
                        "<p class='col-lg-12'><span class='small'>股价-"+iobj.current_price+", 涨幅-"+iobj.pct_chg+"%, 当前收益率-"+iobj.position_pct_chg+"% (记录于 "+iobj.created_time+")</span></p>"+
                      "</div>";
              $(obj).append(html);
              // html = "";
            });
          },
          statusCode: {
            403: function () {
              alert("403 forbidden");
            },
            404: function () {
              alert("404 page not found");
            },
            500: function () {
              alert("500 internal server error");
            }
          }
        }
      );
    });
  }

  // 获取收益增长曲线数据
  var showProfitChgCanvas = document.getElementsByName("profit-chg-canvas");
  if (showProfitChgCanvas) {
    $(showProfitChgCanvas).each(function (id, obj) {
      renderStockProfitChangeChart(obj.id);
    });
  }

  var refreshRealtimeQuote = function () {
    $.ajax({
      url: dashboardEndpoint + 'positions/refresh/',
      success: function (data) {
        $(data).each(function (idx, obj) {
          // alert(idx);
          // alert(",id:" + obj.id + ",symbol:" + obj.symbol + ",name:" + obj.name + ",position_price:"
          //   + obj.position_price + ",realtime_price:" + obj.realtime_price + ",profit:" + obj.profit + ",profit_ratio:" + obj.profit_ratio
          //   + ",lots:" + obj.lots + ",target_position:" + obj.target_position + ",amount:" + obj.amount);
        });
      }
    })
  }

  var refreshInterval = setInterval(function () {
    var d = new Date();
    if (isOpenForTrade(d)) {
      refreshRealtimeQuote();
    }
  }, 5 * 60 * 1000);

  function stopRefresh() {
    clearInterval(refreshInterval);
  }
});
