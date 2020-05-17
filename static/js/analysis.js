// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

$(function () {
    var chart;
    var analysisEndpoint = '/analysis/';
    var selCategory = $('input:radio[name="strategy-ctg"]:checked').val();

    var fetchStrategyByCtg = function (category) {
        var strategyDiv = $("#strategyList");
        $.ajax(
            {
                url: analysisEndpoint + 'strategies/category/' + category + "/",
                method: 'GET',
                success: function (data) {
                    var strategiesTag = '<div class="col-lg-12">';
                    $(data).each(function (idx, obj) {
                        strategiesTag += '<div class="btn-group btn-group-sm btn-group-toggle" data-toggle="buttons">' +
                            '<label class="btn btn-light active">' +
                            '<input type="radio" name="strategy-name" id="' + obj.id + '" autocomplete="off" value="' + obj.strategy_name + '" checked>' + obj.strategy_name +
                            '</label>' +
                            '</div>';
                    });
                    strategiesTag += "</div>";
                    strategyDiv.html(strategiesTag);
                },
                statusCode: {
                    403: function () {
                        alert("403 forbidden");
                    },
                    404: function () {
                        strategyDiv.html("系统无法找到相关策略");
                    },
                    500: function () {
                        strategyDiv.html("系统错误，请稍后再试");
                    }
                }
            }
        );
    }

    // 根据默认策略分类显示该分类下的默认策略
    // fetchStrategyByCtg(selCategory);

    $('#searchForAnalysis').autoComplete({
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

    $('#searchForAnalysis').on('autocomplete.select', function (evt, item) {
        var code = item.id;
        var showCode = item.ts_code;
        var showName = item.text;
        var market = item.market;
    });

    $("button").click(function () {
        var strategy = "jz_b";
        var stock_symbol = "000001.SZ";
        var period = $('input:radio[name="period"]:checked').val();
        var freq = "D";
        $.ajax({
            url: analysisEndpoint + "b-test/strategy/" + strategy + "/" + stock_symbol + "/" + freq + "/" + period + '/',
            // headers: { 'X-CSRFToken': csrftoken },
            method: 'GET',
            dataType: 'json',
            success: function (data) {
                if (data == 200) {
                    showIncrDistChart();
                    showDropDistChart();
                    showIncrPctByDayChart()
                }
            },
            statusCode: {
                403: function () {
                    $("#messages").removeClass('d-none');
                    // $("#messages").addClass('d-block');
                    $("#messageText").html('<strong>403 forbidden</strong>.');
                },
                404: function () {
                    $("#messages").removeClass('d-none');
                    // $("#messages").addClass('d-block');
                    $("#messageText").html('<strong>404 page not found</strong>.');
                },
                500: function () {
                    $("#messages").removeClass('d-none');
                    // $("#messages").addClass('d-block');
                    $("#messageText").html('<strong>500 internal server error</strong>.');
                }
            }
        });
    });

    // 涨幅分布
    var showIncrDistChart = function () {
        if ($("#incrDist").length) {
            var incrChartCanvas = $("#incrDist")
                .get(0)
                .getContext("2d");
            var strategy = "9";
            var stock_symbol = "000001.SZ"
            var period = $('input:radio[name="period"]:checked').val();
            $.ajax({
                url: analysisEndpoint + "b-test-result-incr/strategy/" + strategy + "/" + stock_symbol + "/" + period + '/',
                // headers: { 'X-CSRFToken': csrftoken },
                method: 'GET',
                dataType: 'json',
                success: function (data) {
                    // 亏损的字体颜色为绿
                    // if (data.avg_profit < 0) {
                    //     $("#prfAvgProfit").removeClass("text-danger");
                    //     $("#prfAvgProfit").addClass("text-success");
                    // }
                    // $("#prfAvgProfit").text(data.avg_profit.toLocaleString());
                    // // 亏损的字体颜色为绿
                    // if (data.profit_ratio < 0) {
                    //     $("#prfProfitRatio").removeClass("text-danger");
                    //     $("#prfProfitRatio").addClass("text-success");
                    // }
                    // $("#prfProfitRatio").text(data.profit_ratio + '%');

                    incrChart = new Chart(incrChartCanvas, {
                        type: "line",
                        data: {
                            labels: data.label,
                            datasets: [
                                {
                                    fill: true,
                                    label: "最大涨幅%",
                                    data: data.value,
                                    borderColor: "#1cbccd",
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
            });
        }
    }

    // 跌幅分布
    var showDropDistChart = function () {
        if ($("#dropDist").length) {
            var dropChartCanvas = $("#dropDist")
                .get(0)
                .getContext("2d");
            var strategy = "9";
            var stock_symbol = "000001.SZ"
            var period = $('input:radio[name="period"]:checked').val();
            $.ajax({
                url: analysisEndpoint + "b-test-result-drop/strategy/" + strategy + "/" + stock_symbol + "/" + period + '/',
                // headers: { 'X-CSRFToken': csrftoken },
                method: 'GET',
                dataType: 'json',
                success: function (data) {
                    // 亏损的字体颜色为绿
                    // if (data.avg_profit < 0) {
                    //     $("#prfAvgProfit").removeClass("text-danger");
                    //     $("#prfAvgProfit").addClass("text-success");
                    // }
                    // $("#prfAvgProfit").text(data.avg_profit.toLocaleString());
                    // // 亏损的字体颜色为绿
                    // if (data.profit_ratio < 0) {
                    //     $("#prfProfitRatio").removeClass("text-danger");
                    //     $("#prfProfitRatio").addClass("text-success");
                    // }
                    // $("#prfProfitRatio").text(data.profit_ratio + '%');

                    dropChart = new Chart(dropChartCanvas, {
                        type: "line",
                        data: {
                            labels: data.label,
                            datasets: [
                                {
                                    fill: true,
                                    label: "最大跌幅%",
                                    data: data.value,
                                    borderColor: "#1cbccd",
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
            });
        }
    }

    // 达到预期涨幅天数
    var showIncrPctByDayChart = function () {
        if ($("#expIncrPct").length) {
            var pctIncrChartCanvas = $("#expIncrPct")
                .get(0)
                .getContext("2d");
            var strategy = "9";
            var stock_symbol = "000001.SZ"
            var period = $('input:radio[name="pct_period"]:checked').val();
            $.ajax({
                url: analysisEndpoint + "b-test-result-incr-pct/strategy/" + strategy + "/" + stock_symbol + "/" + period + '/',
                // headers: { 'X-CSRFToken': csrftoken },
                method: 'GET',
                dataType: 'json',
                success: function (data) {
                    pctIncrChart = new Chart(pctIncrChartCanvas, {
                        type: "bar",
                        data: {
                            labels: data.label,
                            datasets: [
                                {
                                    label: "最小周期",
                                    data: data.v_min,
                                    barPercentage: 0.9,
                                    categoryPercentage: 0.7,
                                    backgroundColor: "#4472C4"
                                },
                                {
                                    label: "最大周期",
                                    data: data.v_max,
                                    barPercentage: 0.9,
                                    categoryPercentage: 0.7,
                                    backgroundColor: "#ED7D31"

                                },
                                {
                                    label: "平均周期",
                                    data: data.v_mean,
                                    barPercentage: 0.9,
                                    categoryPercentage: 0.7,
                                    backgroundColor: "#A5A5A5"

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
            });
        }
    }
});  