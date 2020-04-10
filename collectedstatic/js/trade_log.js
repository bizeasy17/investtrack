$(function(){
    // 业务相关代码
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

    var dt = new Date();
    var endDate = formatDate(dt, '-');
    var chartCanvas = document.getElementById('bsChart').getContext('2d');

    // 更新当前所选股票信息
    var updateChart = function () {
        var dataset = chart.config.data.datasets[0];
        chart.update();
    };

    var getStartDate = function (period, format) {
        var priorDate;
        if (period == '15')
            priorDate = new Date(dt.getTime() - (chartShowDays15 * 24 * 60 * 60 * 1000));
        else if (period == '30')
            priorDate = new Date(dt.getTime() - (chartShowDays30 * 24 * 60 * 60 * 1000));
        else if (period == '60')
            priorDate = new Date(dt.getTime() - (chartShowDays60 * 24 * 60 * 60 * 1000));
        else if (period == 'D')
            priorDate = new Date(dt.getTime() - (chartShowDays * 24 * 60 * 60 * 1000));
        else if (period == 'W')
            priorDate = new Date(dt.getTime() - (chartShowDaysW * 24 * 60 * 60 * 1000));
        else if (period == 'M')
            priorDate = new Date(dt.getTime() - (chartShowDaysM * 24 * 60 * 60 * 1000));

        return formatDate(priorDate, format);
    }

    var updateChartFor = function (showName, showCode, tsCode, period) {
        var startDate = getStartDate(period, '-');

        $.ajax({
            url: investBaseEndpoint + 'get-price/' + tsCode + '/' + startDate + '/' + endDate + '/' + period + '/',
            success: function (data) {
                $("#spBsChart").addClass("d-none");//隐藏spinner
                chart.data.datasets.forEach(function (dataset) {
                    dataset.data = data;
                    dataset.label = showName + ' - ' + showCode;
                });
                updateChart();
            }
        })
    }

    // 页面默认加载上证指数日K（D)
    var initStockChart = function (code, showCode, showName) {
        var period = $('input:radio[name="period"]:checked').val();
        var startDate = getStartDate(period, '-');
        // var code = $('input:radio[name="index"]:checked').val(); // e.g. sh
        // var showCode = $('input:radio[name="index"]:checked').attr('id')// e.g. 1A0001 上证
        // var showName = $('input:radio[name="index"]:checked').parent().text().trim();

        $.ajax({
            url: investBaseEndpoint + 'get-price/' + code + '/' + startDate + '/' + endDate + '/' + period + '/',
            success: function (data) {
                // ctx1.canvas.width = 1000;
                // ctx1.canvas.height = 250;
                $("#spBsChart").addClass("d-none");//隐藏spinner
                chart = new Chart(chartCanvas, {
                    type: 'candlestick',
                    data: {
                        datasets: [{
                            label: showName + '-' + showCode,
                            data: data
                        }]
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
                        }
                    }
                });
            }
        });
    }

    initStockChart($('#hiddenCode').val(), $('#hiddenTscode').val(), $('#hiddenName').val());


    $('input:radio[name="period"]').change(function () {
        // 设置当前选定股票
        var code = $('#hiddenCode').val()
        var showCode = $('#hiddenTscode').val();
        var showName = $('#hiddenName').val();
        var period = $(this).val();
        updateChartFor(showName, showCode, code, period);
    });

    $("#collapseChart").click(function () {
        if ($("#chartContainer").hasClass("collapse")) {
            $("#chartContainer").removeClass("collapse");
            $(this).val("收起k线图");
        } else {
            $("#chartContainer").addClass("collapse");
            $(this).val("展开k线图");

        }
    });

    // 显示s相关操作
    $('input[name = sRelatedTrade]').click(function () {
        //get the file name
        var id = $(this).attr("id");
        //replace the "Choose a file" label
        alert(id);
    });

    // 显示b相关操作
    $('input[name = bRelatedTrade]').click(function () {
        //get the file name
        var id = $(this).attr("id");
        //replace the "Choose a file" label
        alert(id);
    });
});