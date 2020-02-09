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

    var dt = new Date();
    var endDate = formatDate(dt, '-');   
    var chartCanvas = document.getElementById('stockChart').getContext('2d');

    // render the stock charts
    // 更新当前所选股票信息
    var getStartDate = function (period, format){
        var priorDate;
        if(period=='15')
            priorDate = new Date(dt.getTime() - (chartShowDays15 * 24 * 60 * 60 * 1000));
        else if(period=='30')
            priorDate = new Date(dt.getTime() - (chartShowDays30 * 24 * 60 * 60 * 1000));
        else if(period=='60')
            priorDate = new Date(dt.getTime() - (chartShowDays60 * 24 * 60 * 60 * 1000));
        else if(period=='D')
            priorDate = new Date(dt.getTime() - (chartShowDays * 24 * 60 * 60 * 1000));
        else if(period=='W')
            priorDate = new Date(dt.getTime() - (chartShowDaysW * 24 * 60 * 60 * 1000));
        else if(period=='M')
            priorDate = new Date(dt.getTime() - (chartShowDaysM * 24 * 60 * 60 * 1000));

        return formatDate(priorDate, format);
    }

    var updateChartFor = function (showName, showCode, tsCode, period) {
        var startDate = getStartDate(period, '-');

        $.ajax({
            url: investBaseEndpoint + 'get-price/' + tsCode + '/' + startDate + '/' + endDate + '/' + period + '/',
            success: function (data) {
                chart.data.datasets.forEach(function (dataset) {
                    dataset.data = data;
                    dataset.label = showName + ' - ' + showCode;
                });
                update();
            }
        })
    }

    $('#searchNameOrCode').autoComplete({
        resolver: 'custom',
        formatResult: function (item) {
            return {
                value: item.id,
                text:  item.id + " - " + item.text ,
                html: [
                    item.id + ' - ' + item.text,// +  '[' + item.market + ']',
                ]
            };
        },
        events: {
            search: function (qry, callback) {
                // let's do a custom ajax call
                $.ajax(
                    investBaseEndpoint + 'search-autocomplete/' + $('#searchNameOrCode').val(),
                ).done(function (res) {
                    callback(res.results)
                });
            }
        }
    });

    $('#searchNameOrCode').on('autocomplete.select', function (evt, item) {
        var code = item.id;
        var showCode = item.ts_code;
        var showName = item.text;
        var market = item.market;
        var period = $('input:radio[name="period"]:checked').val();
        // 设置当前选定股票
        $('#hiddenCode').val(code);
        $('#hiddenName').val(showName);
        $('#hiddenTscode').val(showCode);
        $('#hiddenMarket').val(market);

        updateChartFor(showName, showCode, code, period)

        updateRealtimePriceFor(code);
    });

    // assign the selected strategy
    var updateRealtimePriceFor = function (code) {
        if (code != '') {
            $.ajax({
                url: investBaseEndpoint + 'get-realtime-price/' + code,
                // headers: { 'X-CSRFToken': csrftoken },
                method: 'GET',
                dataType: 'json',
                // data: {
                //     nameOrCode: nameOrCode
                // },
                success: function (data) {
                    $('#currentPrice').val(data.price);
                    $('#tradePrice').val(data.price);
                    var quantity = $('#quantity').val();

                    // $('#quantity').val($('#quantity').val().toLocaleString());
                    $('#cash').val(parseFloat(data.price * quantity).toLocaleString());
                    // $('input[type=number').digits();
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
            });
        }
    };

    // 页面默认加载上证指数日K（D)
    var initStockChart = function () {
        var period = $('input:radio[name="period"]:checked').val();
        var startDate = getStartDate(period, '-');
        var code = $('input:radio[name="index"]:checked').val(); // e.g. sh
        var showCode = $('input:radio[name="index"]:checked').attr('id')// e.g. 1A0001 上证
        var showName = $('input:radio[name="index"]:checked').parent().text().trim();

        $('#hiddenCode').val(code);
        $('#hiddenName').val(showName);
        $('#hiddenTscode').val(showCode);

        $.ajax({
            url: investBaseEndpoint + 'get-price/' + code + '/' + startDate + '/' + endDate + '/' + period + '/',
            success: function (data) {
                // ctx1.canvas.width = 1000;
                // ctx1.canvas.height = 250;
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

    // assign the selected strategy
    $('.strategy-item').click(function(){
        $('#pickedStrategy').val($(this).text());
        $('#pickedStrategyID').val($(this).data('id'));
    });

    $('#btnBuy').click(function(){
        $('#direction').val('b');
        $('#directionIndicate').text(' - 买入');
        $('#directionIndicate').addClass('text-danger');
        $('#directionIndicate').addClass('text-danger');
        // $('#collapseCreate').removeClass('collapse')

        // if ($('#collapseCreate').hasClass('collapse')){

        // }
    });

    $('#btnSell').click(function(){
        $('#direction').val('s');
        $('#directionIndicate').text(' - 卖出');
        $('#directionIndicate').removeClass('text-danger');
        $('#directionIndicate').addClass('text-success');
        // if ($('#collapseCreate').hasClass('collapse')) {

        // }

        // $('#collapseCreate').removeClass('collapse')

    });

    $("#tblMyPosition tbody tr").click(function () {
        // alert($(this).find('th').text()); // firstElementChild.innerText);
        //get <td> element values here!!??
        var rawNameCodeArray = $(this).find('th').text().split(' ');
        var code = rawNameCodeArray[0];
        var showName = rawNameCodeArray[1];
        var market = '', showCode = code;
        var period = $('input:radio[name="period"]:checked').val();

        if (showCode.charAt(0)=='6'){
            market = 'SH';
            showCode = showCode + '.SH';
        }else{
            market = 'SZ';
            showCode = showCode + '.SZ';
        }
        $('#hiddenCode').val(code);
        $('#hiddenName').val(showName);
        $('#hiddenTscode').val(showCode);
        $('#hiddenMarket').val(market);

        updateChartFor(showName, showCode, code, period);
        updateRealtimePriceFor(code);
    });

    $('input:radio[name="period"]').change(function(){
        // 设置当前选定股票
        var code = $('#hiddenCode').val()
        var showCode = $('#hiddenTscode').val();
        var showName = $('#hiddenName').val();
        var period = $(this).val();
        
        updateChartFor(showName, showCode, code, period);
    });

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
    
    // document.getElementById('stockNameOrCode').addEventListener('blur', getRealtimePrice, $(this).val());

    // assign the selected strategy
    $('#quantity').blur(function () {
        var price = $('#tradePrice').val();
        var quantity = $('#quantity').val();
        // $('#quantity').val($('#quantity').val().toLocaleString());
        $('#cash').val(parseFloat(price * quantity).toLocaleString());
    });

    $('#traderecForm').submit(function (e) {
        var nameOrCode = $('#stockNameOrCode').val();
        var currentPrice = $('#currentPrice').val();
        var tradePrice = $('#tradePrice').val();
        var quantity = $('#quantity').val();
        var cash = $('#cash').val();

        $(".error").remove();

        if (nameOrCode.length < 1) {
            $('#stockNameOrCode').after('<span class="error">股票名称/代码不能为空</span>');
        }
        if (currentPrice.length < 1) {
            $('#currentPrice').after('<span class="error">股票当前价格不能为空</span>');
        }
        if (tradePrice == '0') {
            $('#tradePrice').after('<span class="error">交易价格不能为空</span>');
        }
        if (quantity.length < 1) {
            $('#quantity').after('<span class="error">交易股数不能为空</span>');
        }
        if (cash.length < 1) {
            $('#cash').after('<span class="error">交易金额不能为空</span>');
        }
    });
    
    // $('#traderecForm').validate({
    //     rules: {
    //         nameOrCode: 'required',
    //         currentPrice: 'required',
    //         tradePrice: 'required',
    //         quantity: 'required',
    //         cash: 'required'
    //     },
    //     messages: {
    //         nameOrCode: '股票名称/代码不能为空',
    //         currentPrice: '股票当前价格不能为空',
    //         tradePrice: '交易价格不能为空',
    //         quantity: '交易股数不能为空',
    //         cash: '交易金额不能为空'
    //     }
    // });

    // $(".close").click(function(){
    //     $("#messages").addClass('d-none');
    // });

    $('.close').click(function () {
        // e.preventDefault();
        $('#messages').addClass('d-none');
    });
    
    $('#btnSubmitTrade').click(function(){
        event.preventDefault();

        var name = $('#hiddenName').val();
        var code = $('#hiddenCode').val();
        var tsCode = $('#hiddenTscode').val();
        var market = $('#hiddenMarket').val();
        var currentPrice = $('#currentPrice').val();
        var price = $('#tradePrice').val();
        var quantity = $('#quantity').val();
        var cash = $('#cash').val();
        var strategy = $('#pickedStrategyID').val();
        var targetPosition = $('#targetPosition').val();
        var direction = $('#direction').val();
        var tradeTime = $('#tradeDatetime').val();

        $.ajax({
            url: userBaseEndpoint + 'create-trade',
            headers: { 'X-CSRFToken': csrftoken },
            method: 'POST',
            dataType: 'json',
            data: {
                name: name, 
                code: code,
                tsCode: tsCode,
                market: market,
                currentPrice: currentPrice,
                price: price,
                quantity: quantity,
                cash: cash,
                strategy: strategy,
                targetPosition: targetPosition,
                direction: direction,
                tradeTime: tradeTime,
                // csrfmiddlewaretoken: '{{ csrf_token }}'
            },
            success: function (data) {
                $("#messages").removeClass('d-none');
                // $("#messages").addClass('d-block');
                $("#messageText").html('<strong>' + data.success + '</strong>.');
                // $("#messages").fadeOut(2000);
            },
            statusCode: {
                403: function () {
                    $("#messages").removeClass('hidden');
                    // $("#messages").addClass('d-block');
                    $("#messageText").html('<strong>403 forbidden</strong>.');
                },
                404: function () {
                    $("#messages").removeClass('hidden');
                    // $("#messages").addClass('d-block');
                    $("#messageText").html('<strong>404 page not found</strong>.');
                },
                500: function() {
                    $("#messages").removeClass('hidden');
                    // $("#messages").addClass('d-block');
                    $("#messageText").html('<strong>500 internal server error</strong>.');
                }
            }
        });
    });

    function formatDate(date, conn) {
        var dayNames = [
            "01", "02", "03",
            "04", "05", "06", "07",
            "08", "09", "10",
            "11", "12", "13", "14",
            "15", "16", "17", "18",
            "19", "20", "21", "22",
            "23", "24", "25", "26",
            "27", "28", "29", "30", "31"
        ];

        var monthNames = [
            "01", "02", "03",
            "04", "05", "06", "07",
            "08", "09", "10",
            "11", "12"
        ];

        var dayIndex = date.getDate();
        var monthIndex = date.getMonth();
        var year = date.getFullYear();

        return year + conn + monthNames[monthIndex] + conn + dayNames[dayIndex-1];
    }

    var update = function () {
        var dataset = chart.config.data.datasets[0];

        // candlestick vs ohlc
        var type = document.getElementById('type').value;
        dataset.type = type;

        // color
        var colorScheme = document.getElementById('color-scheme').value;
        if (colorScheme === 'neon') {
            dataset.color = {
                up: '#01ff01',
                down: '#fe0000',
                unchanged: '#999',
            };
        } else {
            delete dataset.color;
        }

        // border
        var border = document.getElementById('border').value;
        var defaultOpts = Chart.defaults.global.elements[type];
        if (border === 'true') {
            dataset.borderColor = defaultOpts.borderColor;
        } else {
            dataset.borderColor = {
                up: defaultOpts.color.up,
                down: defaultOpts.color.down,
                unchanged: defaultOpts.color.up
            };
        }

        chart.update();
    };

    initStockChart();
    
    // document.getElementById('update').addEventListener('click', update);

    // document.getElementById('stockSearch').addEventListener('click', function() {
    //     if ($('#hiddenTscode').val() != ''){
    //         var ts_code = $('#hiddenTscode').val();
    //         $.ajax({
    //             url: investBaseEndpoint + 'get-stock-price/' + ts_code + '/' + startDate + '/' + endDate + '/D/',
    //             success: function (data) {
    //                 chart.data.datasets.forEach(function (dataset) {
    //                     dataset.data = data;
    //                     dataset.label = ts_code;
    //                 });
    //                 update();
    //             }
    //         })
    //     }
    // });
    // var test = function () {
    //     alert('document.getElementbyID');
    // };
    // document.getElementById('stockSearch').addEventListener('click', test);
});
    