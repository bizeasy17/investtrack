// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

$(function () {
    var csrftoken = Cookies.get('csrftoken');
    var userBaseEndpoint = '/user/';
    var investBaseEndpoint = '/invest/stocks/';

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
        var ts_code = item.ts_code
        var code = item.id;
        var ts_name = item.text;
        $.ajax({
            url: investBaseEndpoint + 'get-stock-price/' + ts_code + '/' + startDate + '/' + endDate + '/D/',
            success: function (data) {
                chart.data.datasets.forEach(function (dataset) {
                    dataset.data = data;
                    dataset.label = ts_name + ' - ' + code;
                });
                update();
            }
        })
        getRealtimePrice(item.id, item.text, item.ts_code, item.market);
    });

    // $('#stockNameOrCode').autoComplete({
    //     resolver: 'custom',
    //     formatResult: function (item) {
    //         return {
    //             value: item.id,
    //             text: item.id + " - " + item.text,
    //             html: [
    //                 item.id + ' - ' + item.text,// +  '[' + item.market + ']',
    //             ]
    //         };
    //     },
    //     events: {
    //         search: function (qry, callback) {
    //             // let's do a custom ajax call
    //             $.ajax(
    //                 investBaseEndpoint + 'search-autocomplete/' + $('#stockNameOrCode').val(),
    //             ).done(function (res) {
    //                 callback(res.results)
    //             });
    //         }
    //     }
    // });

    // $('#stockNameOrCode').on('autocomplete.select', function (evt, item) {
    //     var ts_code = item.ts_code
    //     var code = item.id;
    //     var ts_name = item.text;
    //     $.ajax({
    //         url: investBaseEndpoint + 'get-stock-price/' + ts_code + '/' + startDate + '/' + endDate + '/D/',
    //         success: function (data) {
    //             chart.data.datasets.forEach(function (dataset) {
    //                 dataset.data = data;
    //                 dataset.label = ts_name + ' - ' + code;
    //             });
    //             update();
    //         }
    //     })
    //     getRealtimePrice(item.id, item.text);
    // });

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

    // assign the selected strategy
    var getRealtimePrice = function (code, name, ts_code, market) {
        // $('#stockNameOrCode').val(code + ' - ' + name);
        $('#hiddenName').val(name);
        $('#hiddenCode').val(code);
        $('#hiddenTscode').val(ts_code);
        $('#hiddenMarket').val(market);

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

    // render the stock charts
    function formatDate(date) {
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

        return year + '' + monthNames[monthIndex] + '' + dayNames[dayIndex-1];
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

    var chartShowDays = 60
    var dt = new Date();
    var priorDt = new Date(dt.getTime() - (chartShowDays * 24 * 60 * 60 * 1000));
    var startDate = formatDate(priorDt);
    var endDate = formatDate(dt);
    var chartCanvas = document.getElementById('stockChart').getContext('2d');

    // 页面默认加载上证指数日K（D)
    var chart;
    $.ajax({
        url: investBaseEndpoint + 'get-index-price/sh/' + startDate + '/' + endDate + '/D/',
        success: function(data){
            // ctx1.canvas.width = 1000;
            // ctx1.canvas.height = 250;
            chart = new Chart(chartCanvas, {
                type: 'candlestick',
                data: {
                    datasets: [{
                        label: '上证指数',
                        data: data
                    }]
                },
                options: {
                    scales: {
                        xAxes: [{
                            afterBuildTicks: function(scale, ticks) {
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
    
    document.getElementById('update').addEventListener('click', update);

    // $('#searchNameOrCode').blur(function(){
    //     var code = $('#searchNameOrCode').val();
    //     $.ajax({
    //         url: investBaseEndpoint + 'get-tscode/' + code,
    //         success: function (data) {
    //             if(data!='err'){
    //                 if(data.charAt(0)=='6'){
    //                     $('#hiddenTscode').val(data+'.SH');
    //                 }else{
    //                     $('#hiddenTscode').val(data+'.SZ');
    //                 }
    //                 $('#stockNameOrCode').val(data);
    //                 getRealtimePrice();
    //                 // chart.label = data;
    //             }else{
    //                 $('#hiddenTscode').val('');
    //             }
    //         }
    //     });
    // });

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
    