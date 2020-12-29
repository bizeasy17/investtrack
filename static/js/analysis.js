// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

window.chartColors = {
    red: 'rgb(255, 99, 132)',
    orange: 'rgb(255, 159, 64)',
    yellow: 'rgb(255, 205, 86)',
    green: 'rgb(75, 192, 192)',
    blue: 'rgb(54, 162, 235)',
    purple: 'rgb(153, 102, 255)',
    grey: 'rgb(201, 203, 207)',
    black: 'rgb(0, 0, 0)'
};

$(function () {
    var freq = "D";
    var market;
    var stockCode;
    var tsCode;
    var stockName;
    var period;
    var candlestickPeriod;
    var pctPeriod;
    var strategyCode;
    var strategyName;
    var bstr;
    var sstr;
    var analysisEndpoint = '/analysis/';
    var investorBaseEndpoint = '/investors/';
    var stockmarketEndpoint = '/stockmarket/';
    // var selCategory = $('input:radio[name="strategy-ctg"]:checked').val();

    var initParam = function () {
        // var strategy = "jz_b";
        // console.log($('#hiddenStrategyBtnId').val());
        // var strategyAnalyzeBtns = document.getElementsByName("show-analysis-hist");
        tsCode = $("#hiddenTsCode").val();
        stockCode = $.trim($("#searchForAnalysis").val().split("-")[0]);// 000001.SH";
        stockName = $.trim($("#searchForAnalysis").val().split("-")[1]);
        pctPeriod = $('input:radio[name="pct_period"]:checked').val();
        period = $('input:radio[name="period"]:checked').val();
        candlestickPeriod = 1
        strategyCode = $('input:radio[name="bstrategy"]:checked').val();;
        strategyName = $('input:radio[name="bstrategy"]:checked').next().text();
        // var freq = "D";
        // showExpectedPctChart(tsCode, strategyCode, pctPeriod);
        // showHighPeriodChart(tsCode, strategyCode, period);
        // showLowPeriodDistChart(tsCode, strategyCode, period);
    }
    initParam();


    // 更新当前所选股票信息
    var chartShowDays60 = 30
    var chartShowDays = 60
    var chartShowDaysW = 180
    var chartShowDaysM = 720
    var dt = new Date();
    var endDate = formatDate(dt, '-');
    var getStartDate = function (period, format) {
        var priorDate;
        if (period == '60')
            priorDate = new Date(dt.getTime() - (chartShowDays60 * 24 * 60 * 60 * 1000));
        else if (period == 'D')
            priorDate = new Date(dt.getTime() - (chartShowDays * 24 * 60 * 60 * 1000));
        else if (period == 'W')
            priorDate = new Date(dt.getTime() - (chartShowDaysW * 24 * 60 * 60 * 1000));
        else if (period == 'M')
            priorDate = new Date(dt.getTime() - (chartShowDaysM * 24 * 60 * 60 * 1000));

        return formatDate(priorDate, format);
    }

    // 股票历史收盘数据
    var stockHistChartK;
    var stockHistChartC;
    // var canvasKChart = $("#stockHistCanvK")
    //     .get(0)
    //     .getContext("2d");
    var canvasCloseChart = $("#stockHistCanvC")
        .get(0)
        .getContext("2d");
    var drawStockChart = function () {
        drawStockHistCloseChart(tsCode, strategyCode, freq, candlestickPeriod)
    }


    var drawStockHistCloseChart = function (tsCode, strategyCode, freq, period) {
        if ($("#stockHistCanvC").length) {
            // var strategy = "9";
            // var stock_symbol = "600626.SH"
            // var period = $('input:radio[name="period"]:checked').val();
            $.ajax({
                url: analysisEndpoint + "stock-hist/strategy/" + strategyCode + "/" + tsCode + "/" + freq + '/close/' + period + "/",
                // url: analysisEndpoint + "b-test-result-drop/strategy/" + strategy + "/" + stock_symbol + "/" + period + '/',
                // headers: { 'X-CSRFToken': csrftoken },
                method: 'GET',
                dataType: 'json',
                success: function (data) {
                    // $("#drop25ile").text(data.quantile[0] + '%');
                    // $("#drop50ile").text(data.quantile[1] + '%');
                    // $("#drop75ile").text(data.quantile[2] + '%');
                    // $("#avgDrop").text(data.quantile[3] + '%');
                    // $("#stockHistCanv").removeClass("d-none");
                    if (stockHistChartC) {
                        // update chart
                        stockHistChartC.data.labels = data.label;
                        stockHistChartC.data.datasets[0].data = data.ma25;
                        stockHistChartC.data.datasets[1].data = data.ma60;
                        stockHistChartC.data.datasets[2].data = data.ma200;
                        stockHistChartC.data.datasets[3].data = data.close;
                        stockHistChartC.update();
                    } else {
                        stockHistChartC = new Chart(canvasCloseChart, {
                            type: "line",
                            data: {
                                labels: data.label,
                                datasets: [{
                                    label: 'MA25',
                                    backgroundColor: window.chartColors.red,
                                    borderColor: window.chartColors.green,
                                    data: data.ma25,
                                    fill: false,
                                }, {
                                    label: 'MA60',
                                    backgroundColor: window.chartColors.red,
                                    borderColor: window.chartColors.blue,
                                    data: data.ma60,
                                    fill: false,
                                }, {
                                    label: 'MA200',
                                    backgroundColor: window.chartColors.red,
                                    borderColor: window.chartColors.orange,
                                    data: data.ma200,
                                    fill: false,
                                }, {
                                    label: '收盘价',
                                    fill: false,
                                    backgroundColor: window.chartColors.blue,
                                    borderColor: window.chartColors.black,
                                    data: data.close
                                    // borderWidth: 2
                                }]
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
                                                // callback: function (value) {
                                                //     return value.toFixed(0) + '%'; // convert it to percentage
                                                // },
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
                                elements: {
                                    point: {
                                        radius: 1,
                                        backgroundColor: "#ff4c5b",
                                        display: false
                                    }
                                }
                            }
                        });
                    }
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

    // 页面加载时 初始显示的收盘线为上证
    drawStockChart();

    // 刷新自选股
    var refreshFollowing = function () {
        var stocks = "";
        $.ajax({
            url: investorBaseEndpoint + "stocks-following/",
            success: function (data) {
                $(data.results).each(function (idx, code) {
                    // alert(idx);   
                    stocks += code + ",";
                });

                $.ajax({
                    url: stockmarketEndpoint + 'realtime-quotes/' + stocks + '/',
                    success: function (data) {
                        var index = "sh"
                        $(data).each(function (idx, stock) {
                            var change = parseFloat(stock.price) - parseFloat(stock.pre_close);
                            var pct = Math.round((parseFloat(stock.price) - parseFloat(stock.pre_close)) / parseFloat(stock.pre_close) * 10000) / 100;
                            if (pct < 0) {
                                $("#real" + stock.code).removeClass("text-danger");
                                $("#chg" + stock.code).removeClass("text-danger");
                                $("#pct" + stock.code).removeClass("text-danger");

                                $("#real" + stock.code).addClass("text-success");
                                $("#chg" + stock.code).addClass("text-success");
                                $("#pct" + stock.code).addClass("text-success");
                            } else {
                                $("#real" + stock.code).removeClass("text-success");
                                $("#chg" + stock.code).removeClass("text-success");
                                $("#pct" + stock.code).removeClass("text-success");

                                $("#real" + stock.code).addClass("text-danger");
                                $("#chg" + stock.code).addClass("text-danger");
                                $("#pct" + stock.code).addClass("text-danger");
                            }
                            $("#real" + stock.code).text(stock.price);
                            $("#chg" + stock.code).text(change.toFixed(2));
                            $("#pct" + stock.code).text(pct.toString() + "%");
                        });
                    }
                });
            }
        });
    }
    refreshFollowing();

    // 每隔5min刷新一次
    var refreshRealtimeQ = setInterval(function () {
        var d = new Date();
        if (isOpenForTrade(d)) {
            refreshFollowing();
        }
    }, refreshInterval * 60 * 1000);

    var showHelpInfo =  function(){
        $(".cur-strategy").text(strategyName);
        $(".cur-stock").text(stockName);
        $("#stockNameCodeLabel").text(stockName + " - " + stockCode);
    }

    var showAnalysisResult = function(){
        showHelpInfo();
        showHighPeriodChart(tsCode, strategyCode, period);
        showLowPeriodDistChart(tsCode, strategyCode, period);
        showExpectedPctChart(tsCode, strategyCode, pctPeriod);
        drawStockChart();
    }

    // 涨幅分布
    var incrChart;
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
                    $("#incr25ile").text(data.quantile[0] + '%');
                    $("#incr50ile").text(data.quantile[1] + '%');
                    $("#incr75ile").text(data.quantile[2] + '%');
                    $("#avgIncr").text(data.quantile[3] + '%');
                    if (incrChart) {
                        // update chart
                        incrChart.data.labels = data.label;
                        incrChart.data.datasets[0].data = data.value;
                        incrChart.update();
                    } else {
                        // new chart
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
                                                padding: 10,
                                                callback: function (value) {
                                                    return value.toFixed(0) + '%'; // convert it to percentage
                                                },
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
                                        radius: 1,
                                        backgroundColor: "#ff4c5b",
                                        display: false
                                    }
                                }
                            }
                        });
                    }
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
    var dropChart;
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
                    $("#drop25ile").text(data.quantile[0] + '%');
                    $("#drop50ile").text(data.quantile[1] + '%');
                    $("#drop75ile").text(data.quantile[2] + '%');
                    $("#avgDrop").text(data.quantile[3] + '%');
                    if (dropChart) {
                        // update chart
                        dropChart.data.labels = data.label;
                        dropChart.data.datasets[0].data = data.value;
                        dropChart.update();
                    } else {
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
                                                padding: 10,
                                                callback: function (value) {
                                                    return value.toFixed(0) + '%'; // convert it to percentage
                                                },
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
                                        radius: 1,
                                        backgroundColor: "#ff4c5b",
                                        display: false
                                    }
                                }
                            }
                        });
                    }
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
    var pctIncrChart;
    var showExpectedPctChart = function (tsCode, strategyCode, pctPeriod) {
        if ($("#expIncrPct").length) {
            var pctIncrChartCanvas = $("#expIncrPct")
                .get(0)
                .getContext("2d");
            // var strategy = "jiuzhuan_b";
            // var stock_symbol = "600626.SH"
            // var pctPeriod = $('input:radio[name="pct_period"]:checked').val();
            $.ajax({
                url: analysisEndpoint + "expected-pct-data/strategy/" + strategyCode + "/" + tsCode + "/D/" + pctPeriod + '/',
                // headers: { 'X-CSRFToken': csrftoken },
                method: 'GET',
                dataType: 'json',
                success: function (data) {
                    $("#expPct25ile").text(data.quantile[0] + '天');
                    $("#expPct50ile").text(data.quantile[1] + '天');
                    $("#expPct75ile").text(data.quantile[2] + '天');
                    $("#avgExpPct").text(data.quantile[3] + '天');
                    if (pctIncrChart) {
                        // update chart
                        pctIncrChart.data.labels = data.label;
                        pctIncrChart.data.datasets[0].data = data.value;
                        pctIncrChart.update();
                    } else {
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
                                                padding: 10,
                                                callback: function (value) {
                                                    return value.toFixed(0) + '天'; // convert it to day
                                                },
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
                                        radius: 1,
                                        backgroundColor: "#ff4c5b",
                                        display: false
                                    }
                                }
                            }
                        });
                    }

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
    // $('input:radio[name="strategy-ctg"]').change(function () {
    //     // 页面默认加载上证指数日K（D)
    //     var parentStrategyId = this.value;
    //     fetchStrategyByCtg(parentStrategyId);
    // });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="bstrategy"]').change(function () {
        // 页面默认加载上证指数日K（D)
        // 页面默认加载上证指数日K（D)
        bstr = $(this)
        if (sstr != undefined) {
            $(sstr).removeAttr("checked")
            $(sstr).parent("label").removeClass("active");
        } 

        strategyCode = this.value;
        strategyName = $(this).next().text();
        // showHelpInfo();
        showAnalysisResult();
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="sstrategy"]').change(function () {
        // 页面默认加载上证指数日K（D)
        sstr = $(this);
        if (bstr != undefined) {
            $(bstr).removeAttr("checked")
            $(bstr).parent("label").removeClass("active");
        } 

        strategyCode = this.value;
        strategyName = $(this).next().text();
        // showHelpInfo();
        showAnalysisResult();
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="pct_period"]').change(function () {
        // 页面默认加载上证指数日K（D)
        pctPeriod = this.value;
        showHelpInfo();
        showExpectedPctChart(tsCode, strategyCode, pctPeriod);
    });

    // 根据选择的周期，显示该周期中最大跌幅，最大涨幅
    $('input:radio[name="period"]').change(function () {
        // 页面默认加载上证指数日K（D)
        period = this.value;
        showHelpInfo();
        showHighPeriodChart(tsCode, strategyCode, period);
        showLowPeriodDistChart(tsCode, strategyCode, period);
    });

    // 根据选择的周期，显示该周期中最大跌幅，最大涨幅
    $('input:radio[name="candlestick-period"]').change(function () {
        // 页面默认加载上证指数日K（D)
        candlestickPeriod = this.value;
        drawStockChart();
    });


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
        stockCode = item.id;
        tsCode = item.ts_code;
        stockName = item.text;
        market = item.market;
        showAnalysisResult();
    });

    showAnalysisResult();
});  