// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

$(function () {
    var chart;
    var analysisEndpoint = '/analysis/';
    var stockmarketEndpoint = '/stockmarket/';
    var selCategory = $('input:radio[name="strategy-ctg"]:checked').val();

    var fetchStrategyByCtg = function (strategyId) {
        var strategyDiv = $("#strategyList");
        $.ajax(
            {
                url: analysisEndpoint + 'strategies/category/' + category + "/",
                method: 'GET',
                success: function (data) {
                    var strategiesTag = '<div class="col-lg-12">';
                    $(data).each(function (idx, obj) {
                        strategiesTag += 
                            '<div class="btn-group btn-group-sm btn-group-toggle" data-toggle="buttons">' +
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
                    stockmarketEndpoint + 'listed_companies/' + $('#searchForAnalysis').val(),
                ).done(function (res) {
                    callback(res.results)
                });
            }
        }
    });

    $('#searchForAnalysis').on('autocomplete.select', function (evt, item) {
        var code = item.id;
        var tsCode = item.ts_code;
        var showName = item.text;
        var market = item.market;
        var pctPeriod = $('input:radio[name="pct_period"]:checked').val();
        var period = $('input:radio[name="period"]:checked').val();
        var strategyCode = $('#hiddenStrategyCode').val();
        $('#hiddenTsCode').val(tsCode);
        showExpectedPctChart(tsCode, strategyCode, pctPeriod);
        showHighPeriodChart(tsCode, strategyCode, period);
        showLowPeriodDistChart(tsCode, strategyCode, period);
    });


    $("button").click(function () {
        // var strategy = "jz_b";
        var tsCode =  $('#hiddenTsCode').val();
        var pctPeriod = $('input:radio[name="pct_period"]:checked').val();
        var period = $('input:radio[name="period"]:checked').val();
        var strategyCode = $('#hiddenStrategyCode').val();
        // var freq = "D";
        showExpectedPctChart(tsCode, strategyCode, pctPeriod);
        showHighPeriodChart(tsCode, strategyCode, period);
        showLowPeriodDistChart(tsCode, strategyCode, period);
    });

    // 涨幅分布
    var showHighPeriodChart = function (tsCode, strategyCode, period) {
        if ($("#incrDist").length) {
            var incrChartCanvas = $("#incrDist")
                .get(0)
                .getContext("2d");
            // var strategy = "9";
            // var stock_symbol = "600626.SH"
            // var period = $('input:radio[name="period"]:checked').val();
            $.ajax({
                url: analysisEndpoint + "high-pct-data/strategy/" + strategyCode + "/" + tsCode + "/" + period + '/',
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
                },
                statusCode: {
                    403: function () {
                    },
                    404: function () {
                    },
                    500: function () {
                    }
                }
            });
        }
    }

    // 跌幅分布
    var showLowPeriodDistChart = function (tsCode, strategyCode, period) {
        if ($("#dropDist").length) {
            var dropChartCanvas = $("#dropDist")
                .get(0)
                .getContext("2d");
            // var strategy = "9";
            // var stock_symbol = "600626.SH"
            // var period = $('input:radio[name="period"]:checked').val();
            $.ajax({
                url: analysisEndpoint + "low-pct-data/strategy/" + strategyCode + "/" + tsCode + "/" + period + '/',
                // url: analysisEndpoint + "b-test-result-drop/strategy/" + strategy + "/" + stock_symbol + "/" + period + '/',
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
                },
                statusCode: {
                    403: function () {
                    },
                    404: function () {
                    },
                    500: function () {
                    }
                }
            });
        }
    }

    // 达到预期涨幅天数
    var showExpectedPctChart = function (tsCode, strategyCode, expPct) {
        if ($("#expIncrPct").length) {
            var pctIncrChartCanvas = $("#expIncrPct")
                .get(0)
                .getContext("2d");
            // var strategy = "jiuzhuan_b";
            // var stock_symbol = "600626.SH"
            // var pctPeriod = $('input:radio[name="pct_period"]:checked').val();
            $.ajax({
                url: analysisEndpoint + "expected-pct-data/strategy/" + strategyCode + "/" + tsCode + "/D/" + expPct + '/',
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
                                    label: "涨幅天数",
                                    data: data.value,
                                    barPercentage: 0.9,
                                    categoryPercentage: 0.7,
                                    backgroundColor: "#4472C4"
                                },
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

                },
                statusCode: {
                    403: function () {
                    },
                    404: function () {
                    },
                    500: function () {
                    }
                }
            });
        }
    }

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="strategy-ctg"]').change(function () {
        // 页面默认加载上证指数日K（D)
        var parentStrategyId = this.value;
        fetchStrategyByCtg(parentStrategyId);
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="pct_period"]').change(function () {
        // 页面默认加载上证指数日K（D)
        var expPct = this.value;
        var tsCode = $('#hiddenTsCode').val();
        var strategyCode = $('#hiddenStrategyCode').val();
        showExpectedPctChart(tsCode, strategyCode, expPct);
    });

    // 根据选择的周期，显示该周期中最大跌幅，最大涨幅
    $('input:radio[name="period"]').change(function () {
        // 页面默认加载上证指数日K（D)
        var period = this.value;
        var tsCode = $('#hiddenTsCode').val();
        var strategyCode = $('#hiddenStrategyCode').val();
        showHighPeriodChart(tsCode, strategyCode, period);
        showLowPeriodDistChart(tsCode, strategyCode, period);
    });
    
    // showHighPeriodChart();
    // showLowPeriodDistChart();
    // showExpectedPctChart();
});  