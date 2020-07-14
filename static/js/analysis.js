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
	grey: 'rgb(201, 203, 207)'
};

$(function () {
    var chart;
    var analysisEndpoint = '/analysis/';
    var stockmarketEndpoint = '/stockmarket/';
    var selCategory = $('input:radio[name="strategy-ctg"]:checked').val();

    var showAnalysisHist = function () {
        // var strategy = "jz_b";
        console.log($('#hiddenStrategyBtnId').val());
        $(this).removeClass("btn-info");
        $(this).addClass("btn-danger");
        if ($('#hiddenStrategyBtnId').val()) {
            $("#" + $('#hiddenStrategyBtnId').val()).removeClass("btn-danger");
            $("#" + $('#hiddenStrategyBtnId').val()).addClass("btn-info");
        }

        // var strategyAnalyzeBtns = document.getElementsByName("show-analysis-hist");
        var tsCode = $('#hiddenTsCode').val();
        var stockName = $('#hiddenStockName').val();
        var pctPeriod = $('input:radio[name="pct_period"]:checked').val();
        var period = $('input:radio[name="period"]:checked').val();
        var strategyCode = $(this).val().split(",")[0];
        var strategyName = $(this).val().split(",")[1];
        $('#hiddenStrategyCode').val(strategyCode);
        $('#hiddenStrategyName').val(strategyName);
        $('#hiddenStrategyBtnId').val($(this).attr("id"))
        $(".cur-strategy").text(strategyName);
        $(".cur-stock").text(stockName + ' - ' + tsCode);
        // var freq = "D";
        showExpectedPctChart(tsCode, strategyCode, pctPeriod);
        showHighPeriodChart(tsCode, strategyCode, period);
        showLowPeriodDistChart(tsCode, strategyCode, period);
    }

    var fetchStrategyByCtg = function (categoryName) {
        var strategyDiv = $("#strategyList");
        $.ajax(
            {
                url: analysisEndpoint + 'strategies/by-category/' + categoryName + "/",
                method: 'GET',
                success: function (data) {
                    var strategiesTag = "";
                    strategyDiv.html("");
                    $(data).each(function (idx, obj) {
                        strategiesTag +=
                            '<div class="row">' +
                            '<div class="col">' +
                            '<img src="' + imgRoot + obj.code + '.png" height="75" width="75" style="border-radius: 10%">' +
                            '</div>' +
                            '<div class="col">' +
                            '<div><span class="small text-primary">' + obj.strategy_name + '</span></div>'
                        // '<div class="small text-muted">成功率-' + obj.success_rate + '%</div>';<span class="small"> 成功率-' + obj.success_rate + '%</span>
                        // '<div class="container">'+
                        //     '<div class="row">'+
                        //         '<div class="col-4 text-primary">总数</div>'+
                        //         '<div class="col-4 text-primary">成功</div>'+00000
                        //         '<div class="col-4 text-primary">失败</div>'+
                        //         '<div class="w-100"></div>'+
                        //         '<div class="col-4 text-primary">'+
                        //             obj.count+
                        //         '</div>'+
                        //         '<div class="col-4 text-primary">'+
                        //             obj.success_count+
                        //         '</div>'+
                        //         '<div class="col-4 text-primary">'+
                        //             obj.fail_count+
                        //         '</div>'+
                        //     '</div>'+
                        // '</div>';
                        // if(obj.analyzed){
                        //     strategiesTag += '<button class="btn btn-sm btn-info" name="show-analysis-hist" id="showHistBtn'+obj.id+'" value="'+obj.code+'"><i class="fa fa-eye">历史分析</i></button>';
                        // }else{
                        //     strategiesTag += '<button class="btn btn-sm btn-outline-info" name="show-analysis-hist" id="showHistBtn'+obj.id+'" value="'+obj.code+'" disabled><i class="fa fa-eye"></i>未分析</button>';
                        // }
                        strategiesTag += '<button class="btn btn-sm btn-info" name="show-analysis-hist" id="showHistBtn' + obj.id + '" value="' + obj.code + ',' + obj.strategy_name + '"><small>分析</small></button>';
                        strategiesTag += '</div></div><hr/>';
                        strategyDiv.append(strategiesTag);
                        strategiesTag = "";
                        var showAnalysisBtn = document.getElementById("showHistBtn" + obj.id);
                        showAnalysisBtn.addEventListener("click", showAnalysisHist);
                    });
                    // strategiesTag += '</div>';

                    // if (btns) {
                    //     $(btns).each(function (id, obj) {
                    //         $(obj).on("click", bindDetailOfPosition);
                    //     });
                    // }
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
    fetchStrategyByCtg(selCategory);

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
        var freq = 'D'
        var pctPeriod = $('input:radio[name="pct_period"]:checked').val();
        var period = $('input:radio[name="period"]:checked').val();
        var chartType = $('input:radio[name="chart-type"]:checked').val();
        var strategyCode = $('#hiddenStrategyCode').val();
        var strategyName = $('#hiddenStrategyName').val();
        $('#hiddenTsCode').val(tsCode);
        $('#hiddenStockName').val(showName);
        $(".cur-strategy").text(strategyName);
        $(".cur-stock").text(tsCode);
        showExpectedPctChart(tsCode, strategyCode, pctPeriod);
        showHighPeriodChart(tsCode, strategyCode, period);
        showLowPeriodDistChart(tsCode, strategyCode, period);
        drawStockChart(tsCode, code, showName, strategyCode, chartType, freq);
    });

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
    var stockHistChart;
    var stockHistChartCanvas = $("#stockHistCanv")
                .get(0)
                .getContext("2d");
    var drawStockChart = function(symbol, showCode, showName, strategyCode, type, freq) {
        if(type == 'k'){
            drawStockKChart(symbol, showCode, showName, strategyCode, freq);
        }else if(type == 'c'){
            drawStockHistCloseChart(symbol, strategyCode, freq)
        }
    }

    var drawStockKChart = function (tsCode, showCode, showName, strategyCode, freq) {
        var startDate = getStartDate(freq, '-');
        // var accountId = $("#hiddenAccount").val();
        $.ajax({
            // url: investBaseEndpoint + 'get-price/' + code + '/' + startDate + '/' + endDate + '/' + period + '/',
            url: analysisEndpoint + "stock-hist/strategy/" + strategyCode + "/" + tsCode + "/" + freq + '/ticks/',
            success: function (data) {
                if (stockHistChart) {
                    // update chart
                    stockHistChart.data.labels = data.label;
                    stockHistChart.data.datasets[0].data = data.ticks;
                    stockHistChart.data.datasets[1].data = data.ma25;
                    stockHistChart.data.datasets[2].data = data.ma60;
                    stockHistChart.data.datasets[3].data = data.ma200;
                    stockHistChart.update();
                } else {
                    stockHistChart = new Chart(stockHistChartCanvas, {
                        type: 'candlestick',
                        data: {
                            datasets: [{
                                label: showName + '-' + showCode,
                                data: data.ticks
                            }
                            // , {
                            //     label: 'MA25',
                            //     backgroundColor: window.chartColors.red,
                            //     borderColor: window.chartColors.red,
                            //     data: data.ma25,
                            //     fill: false,
                            // }, {
                            //     label: 'MA60',
                            //     backgroundColor: window.chartColors.red,
                            //     borderColor: window.chartColors.blue,
                            //     data: data.ma60,
                            //     fill: false,
                            // },{
                            //     label: 'MA200',
                            //     backgroundColor: window.chartColors.red,
                            //     borderColor: window.chartColors.green,
                            //     data: data.ma200,
                            //     fill: false,
                            // }
                        ]
                        },
                        options: {
                            scales: {
                                xAxes: [{
                                    afterBuildTicks: function (scale, ticks) {
                                        var majorUnit = scale._majorUnit;
                                        var firstTick = ticks[0];
                                        var i, ilen, val, tick, currMajor, lastMajor;

                                        val = luxon.DateTime.fromMillis(ticks[0].value);
                                        if ((majorUnit === 'minute' && val.second === 0)
                                            || (majorUnit === 'hour' && val.minute === 0)
                                            || (majorUnit === 'day' && val.hour === 9)
                                            || (majorUnit === 'month' && val.day <= 3 && val.weekday === 1)
                                            || (majorUnit === 'year' && val.month === 0)) {
                                            firstTick.major = true;
                                        } else {
                                            firstTick.major = false;
                                        }
                                        lastMajor = val.get(majorUnit);

                                        for (i = 1, ilen = ticks.length; i < ilen; i++) {
                                            tick = ticks[i];
                                            val = luxon.DateTime.fromMillis(tick.value);
                                            currMajor = val.get(majorUnit);
                                            tick.major = currMajor !== lastMajor;
                                            lastMajor = currMajor;
                                        }
                                        return ticks;
                                    }
                                }]
                            },
                            tooltips: {
                                callbacks: {
                                    label: function (tooltipItem, data) {
                                        var dataset = data.datasets[tooltipItem.datasetIndex];
                                        var point = dataset.data[tooltipItem.index];
                                        var label = data.datasets[tooltipItem.datasetIndex].label || '';

                                        var o = point.o;
                                        var h = point.h;
                                        var l = point.l;
                                        var c = point.c;

                                        var percentage = Math.floor((parseFloat(c) - parseFloat(o)) / parseFloat(o) * 100) + "%";

                                        if (label) {
                                            label += ': ';
                                        }
                                        label = showName + ' - 开盘: ' + o + '  最高: ' + h + '  最低: ' + l + '  收盘: ' + c + ' 涨幅: ' + percentage;
                                        return label;
                                    }
                                }
                            }
                        }
                    });
                }
            }
        });
    }

    
    var drawStockHistCloseChart = function (tsCode, strategyCode, freq) {
        var period = 1;
        if ($("#stockHistCanv").length) {
            // var strategy = "9";
            // var stock_symbol = "600626.SH"
            // var period = $('input:radio[name="period"]:checked').val();
            $.ajax({
                url: analysisEndpoint + "stock-hist/strategy/" + strategyCode + "/" + tsCode + "/" + freq + '/close/',
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
                    if (stockHistChart) {
                        // update chart
                        stockHistChart.data.labels = data.label;
                        stockHistChart.data.datasets[0].data = data.ma25;
                        stockHistChart.data.datasets[1].data = data.close;
                        stockHistChart.update();
                    } else {
                        stockHistChart = new Chart(stockHistChartCanvas, {
                            type: "line",
                            data: {
                                labels: data.label,
                                datasets: [{
                                    label: 'MA25',
                                    backgroundColor: window.chartColors.red,
                                    borderColor: window.chartColors.red,
                                    data: data.ma25,
                                    fill: false,
                                }, {
                                    label: 'MA60',
                                    backgroundColor: window.chartColors.red,
                                    borderColor: window.chartColors.blue,
                                    data: data.ma60,
                                    fill: false,
                                },{
                                    label: 'MA200',
                                    backgroundColor: window.chartColors.red,
                                    borderColor: window.chartColors.green,
                                    data: data.ma200,
                                    fill: false,
                                },{
                                    label: '收盘价',
                                    fill: false,
                                    backgroundColor: window.chartColors.blue,
                                    borderColor: window.chartColors.grey,
                                    data: data.close,
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
                                        radius: 3,
                                        backgroundColor: "#ff4c5b"
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
                                        radius: 3,
                                        backgroundColor: "#ff4c5b"
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
                                        radius: 3,
                                        backgroundColor: "#ff4c5b"
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