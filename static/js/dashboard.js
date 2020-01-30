$(function () {
    var csrftoken = Cookies.get('csrftoken');
    var stockBaseEndpoint = '/users/invest/';
    var investBaseEndpoint = '/invest/stocks/';

    // function definition start
    
    // end

    // search auto-complete
    $('.advancedAutoComplete').autoComplete({
        resolver: 'custom',
        events: {
            search: function (qry, callback) {
                // let's do a custom ajax call
                $.ajax(
                    './testdata/test-dict.json',
                    {
                        data: { 'qry': qry }
                    }
                ).done(function (res) {
                    callback(res.results)
                });
            }
        }
    });

    // assign the selected strategy
    $('.dropdown-item').click(function(){
        $('#pickedStrategy').val($(this).text());
        $('#pickedStrategyID').val($(this).data('id'));
    });

    $('#btnBuy').click(function(){
        $('#direction').val('b');
    });

    $('btnSell').click(function(){
        $('#direction').val('s');
    });

    // assign the selected strategy
    $('#stockNameOrCode').blur(function () {
        var nameOrCode = $('#stockNameOrCode').val();
        if (nameOrCode != '') {
            $.ajax({
                url: investBaseEndpoint + '/get-realtime-price/' + encodeURIComponent(nameOrCode),
                // headers: { 'X-CSRFToken': csrftoken },
                method: 'GET',
                dataType: 'json',
                data: {
                    nameOrCode: nameOrCode
                },
                success: function (data) {
                    $('#currentPrice').val(data.price);
                    $('#tradePrice').val(data.price);
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
    });

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

    $('#btnSubmitTrade').click(function(){
        event.preventDefault();

        var stockNameOrCode = $('#stockNameOrCode').val();
        var currentPrice = $('#currentPrice').val();
        var price = $('#tradePrice').val();
        var quantity = $('#quantity').val();
        var cash = $('#cash').val();
        var strategy = $('#pickedStrategyID').val();
        var targetPosition = $('#targetPosition').val();
        var direction = $('#direction').val();

        $.ajax({
            url: stockBaseEndpoint + 'create',
            headers: { 'X-CSRFToken': csrftoken },
            method: 'POST',
            dataType: 'json',
            data: {
                stockName: stockNameOrCode, 
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
                $(".error").remove();
            },
            statusCode: {
                403: function () {
                    alert("403 forbidden");
                },
                404: function () {
                    alert("404 page not found");
                },
                500: function() {
                    alert("500 internal server error");
                }
            }
        });
    });

    // render the stock charts
    var chartCanvas = document.getElementById('stockChart').getContext('2d');

    $.ajax({
        url: klineEndpoint,
        success: function(data){
            // ctx1.canvas.width = 1000;
            // ctx1.canvas.height = 250;
            var chart = new Chart(chartCanvas, {
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

    $('stockSearch').addEventListener('click', function() {
        chart.data.datasets.forEach(function(dataset) {

            dataset.data = getRandomData(initialDateStr, barCount + getRandomInt(10));
        });
        update();
    });
});