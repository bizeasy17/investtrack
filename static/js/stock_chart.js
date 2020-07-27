// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

$(function () {
    var chart;

    var csrftoken = Cookies.get('csrftoken');
    var investorEndpoint = '/investors/';
    var txnvisEndpoint = '/txnvis/';
    var stockmarketEndpoint = '/stockmarket/';
    var dashboardEndpoint = '/dashboard/';


    var chartShowDays15 = 15
    var chartShowDays30 = 15
    var chartShowDays60 = 30
    var chartShowDays = 60
    var chartShowDaysW = 180
    var chartShowDaysM = 720

    var dt = new Date();
    var endDate = formatDate(dt, '-');
    var chartCanvas = document.getElementById('stockChart').getContext('2d');

    // render the stock charts
    // 更新当前所选股票信息
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


    var updateChartFor = function (showName, showCode, symbol, period) {
        var startDate = getStartDate(period, '-');
        var accountId;
        if ($("#hiddenAccount").val() != undefined) accountId = $("#hiddenAccount").val();
        else accountId = 0;
        $.ajax({
            // url: investBaseEndpoint + 'get-price/' + tsCode + '/' + startDate + '/' + endDate + '/' + period + '/',
            url: txnvisEndpoint + 'hist/' + accountId + "/" + symbol + '/' + startDate + '/' + endDate + '/' + period + '/',
            success: function (data) {
                chart.data.datasets.forEach(function (dataset) {
                    dataset.data = data;
                    dataset.label = showName + ' - ' + showCode;
                });
                update();
            }
        })
    }


    var refreshStockInfo2Realtime = function () {
        var showName = $("#hiddenName").val();
        var symbol = $("#hiddenCode").val();
        var showCode = $("#hiddenTscode").val();
        var period = "D";
        updateChartFor(showName, showCode, symbol, period);
        // refreshPositionBySymbol(symbol);
    };

    // var refreshInterval = setInterval(function () {
    //     var d = new Date();
    //     if (isOpenForTrade(d)) {
    //         refreshStockInfo2Realtime();
    //     }
    // }, 5 * 60 * 1000);


    $("#followStock").click(function () {
        var symbol = $("#hiddenCode").val();
        var name = $("#hiddenName").val();
        $.ajax(
            {
                url: investorEndpoint + 'follow-stock/' + symbol + "/",
                data: {
                    name: name
                },
                headers: { 'X-CSRFToken': csrftoken },
                method: 'POST',
                success: function (data) {
                    $("#messages").removeClass('d-none');
                    if (data.code == "ok") {
                        $("#messages").addClass('alert-success');
                        $("#tblStockRealtime tbody").append(
                            
                        );
                    } else {
                        $("#messages").addClass('alert-danger');
                    }
                    $("#messageText").html("<strong>" + data.message + "</strong>");
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


    $('#stockSearch').autoComplete({
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
                    stockmarketEndpoint + 'listed_companies/' + $('#stockSearch').val(),
                ).done(function (res) {
                    callback(res.results)
                });
            }
        }
    });

    $('#stockSearch').on('autocomplete.select', function (evt, item) {
        var code = item.id;
        var showCode = item.ts_code;
        var showName = item.text;
        var market = item.market;
        var period = "D";
        // 设置当前选定股票
        $('#hiddenCode').val(code);
        $('#hiddenName').val(showName);
        $('#hiddenTscode').val(showCode);
        $('#hiddenMarket').val(market);
        // location.replace("https://www.w3schools.com");
        updateChartFor(showName, showCode, code, period)
    });

    // 页面默认加载上证指数日K（D)
    var initStockChart = function (symbol, showCode, showName) {
        // var period = '$('input:radio[name="period"]:checked').val()';
        var period = "D";
        var startDate = getStartDate(period, '-');
        var accountId = $("#hiddenAccount").val();
        accountId = accountId == undefined ? 0 : accountId

        if (chartCanvas) {
            $.ajax({
                // url: investBaseEndpoint + 'get-price/' + code + '/' + startDate + '/' + endDate + '/' + period + '/',
                url: txnvisEndpoint + 'hist/' + accountId + "/" + symbol + '/' + startDate + '/' + endDate + '/' + period + '/',
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

                                        var percentage = ((parseFloat(c) - parseFloat(o)) / parseFloat(o) * 100).toFixed(2);

                                        if (label) {
                                            label += ':';
                                        }
                                        label = showName + ' - 收:' + c + ' 涨:' + percentage.toString() + "%";
                                        return label;
                                    }
                                }
                            }
                        }
                    });
                }
            });
        }
    }

    $("#tblStockRealtime tbody tr").click(function () {
        // alert($(this).find('th').text()); // firstElementChild.innerText);
        //get <td> element values here!!??
        var nameCode = $(this).find('th a');
        var showName = $(nameCode[0]).text();
        var code = $(nameCode[1]).text();
        var showCode = code;
        var period = "D";

        if (showCode.charAt(0) == '6') {
            market = 'SH';
            showCode = showCode + '.SH';
        } else {
            market = 'SZ';
            showCode = showCode + '.SZ';
        }
        $('#hiddenCode').val(code);
        $('#hiddenName').val(showName);
        $('#hiddenTscode').val(showCode);
        updateChartFor(showName, showCode, code, period);
    });

    $('input:radio[name="period"]').change(function () {
        // 设置当前选定股票
        var code = $('#hiddenCode').val()
        var showCode = $('#hiddenTscode').val();
        var showName = $('#hiddenName').val();
        var period = $(this).val();

        // 实时行情只能在开盘时候才可以9:30am - 15：00pm (CN time)
        if ($(this).val() == 'R') {
            var d = new Date();
            if (!isOpenForTrade(d)) {
                $("#messages").removeClass('d-none');
                // $("#messages").addClass('d-block');
                $("#messageText").html('<strong>非交易时间，实时行情不可用，请在交易时间查看.</strong>');
            }
        } else
            updateChartFor(showName, showCode, code, period);
    });

    $("#tblStockRealtime").on('click', '.btn-unfollow', function () {
        var symbol = $(this).attr("id");
        var tr = $(this).closest("tr");
        $.ajax(
            {
                url: investorEndpoint + 'unfollow-stock/' + symbol + "/",
                headers: { 'X-CSRFToken': csrftoken },
                method: 'DELETE',
                success: function (data) {
                    $("#messages").removeClass('d-none');
                    if (data.code == "ok") {
                        $("#messages").addClass('alert-success');
                        tr.remove();
                    } else {
                        $("#messages").addClass('alert-danger');
                    }
                    $("#messageText").html("<strong>" + data.message + "</strong>");
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

    // $('input:radio[name="unfollow"]').click(function () {
    //     var symbol = $(this).attr("id").val();
    //     // var symbol = $("#hiddenCode").val();

    // });

    $('input:radio[name="index"]').change(function () {
        // 页面默认加载上证指数日K（D)
        var code = this.value;
        var showCode = this.id;
        var showName = $(this).parent().text().trim();
        var period = $('input:radio[name="period"]:checked').val();

        $('#hiddenCode').val(code);
        $('#hiddenName').val(showName);
        $('#hiddenTscode').val(showCode);

        updateChartFor(showName, showCode, code, period);
    });


    $(".close").click(function () {
        $("#messages").addClass('d-none');
    });

    var update = function () {
        var dataset = chart.config.data.datasets[0];

        // // candlestick vs ohlc
        // var type = document.getElementById('type').value;
        // dataset.type = type;

        // // color
        // var colorScheme = document.getElementById('color-scheme').value;
        // if (colorScheme === 'neon') {
        //     dataset.color = {
        //         up: '#01ff01',
        //         down: '#fe0000',
        //         unchanged: '#999',
        //     };
        // } else {
        //     delete dataset.color;
        // }

        // // border
        // var border = document.getElementById('border').value;
        // var defaultOpts = Chart.defaults.global.elements[type];
        // if (border === 'true') {
        //     dataset.borderColor = defaultOpts.borderColor;
        // } else {
        //     dataset.borderColor = {
        //         up: defaultOpts.color.up,
        //         down: defaultOpts.color.down,
        //         unchanged: defaultOpts.color.up
        //     };
        // }

        chart.update();
    };

    initStockChart($('#hiddenCode').val(), $('#hiddenTscode').val(), $('#hiddenName').val());
});