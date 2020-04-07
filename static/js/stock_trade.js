// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

$(function () {
    var chart;

    var csrftoken = Cookies.get('csrftoken');
    var userBaseEndpoint = '/user/';
    var investBaseEndpoint = '/invest/stocks/';

    var chartShowDays15 = 15
    var chartShowDays30 = 15
    var chartShowDays60 = 30
    var chartShowDays = 60
    var chartShowDaysW = 180
    var chartShowDaysM = 720

    var dt = new Date();
    var endDate = formatDate(dt, '-');
    var chartCanvas = document.getElementById('stockChart').getContext('2d');

    var isOpenForTrade = function (inputDatetime) {
        // var dateAndTime = inputDatetime.split(" ");
        var date = formatDate(inputDatetime, "-");
        var openTime = new Date(date + " 9:30:00");
        var morningCloseTime = new Date(date + " 11:30:00");
        var afternoonOpenTime = new Date(date + " 13:00:00");
        var closeTime = new Date(date + " 15:00:00");
        var day = inputDatetime.getDay();
        var hour = inputDatetime.getHours();
        var min = inputDatetime.getMinutes();
        if (inputDatetime >= openTime && inputDatetime <= morningCloseTime) {
            return true;
        }
        if (inputDatetime >= afternoonOpenTime && inputDatetime <= closeTime) {
            return true;
        }
        if(inputDatetime > date) {
            return false;
        }
        return false;
    }

    // assign the selected strategy
    var updateTradeStockInfoFor = function (code) {
        var account = $('#pickedAccountID').val();
        if (code != '') {
            $.ajax({
                url: userBaseEndpoint + 'get-stock-for-trade/' + account + '/' + code + '/',
                // headers: { 'X-CSRFToken': csrftoken },
                method: 'GET',
                dataType: 'json',
                // data: {
                //     nameOrCode: nameOrCode
                // },
                success: function (data) {
                    $('#currentPrice').text(data.current_price);
                    $('#cashRemainToBuy').text(parseFloat(data.remain_to_buy).toLocaleString());
                    $('#sharesRemainToSell').text(data.remain_to_sell.toLocaleString());
                    $('#hiddenSharesRemainToSell').text(data.remain_to_sell);
                    $('#tradePrice').val(data.current_price);
                    var quantity = $('#quantity').val();
                    // $('#quantity').val($('#quantity').val().toLocaleString());
                    $('#refCashAmount').text(parseFloat(data.current_price * quantity).toLocaleString());
                    $('#targetPositionText').text(data.target_position.toLocaleString());
                    $('#targetPosition').val(data.target_position);
                    // $('#targetCashAmount').text(Math.round(data.target_cash_amount).toLocaleString());
                    if ($('#hiddenTradeType').val() == 'b') {
                        if (parseInt($('#targetPositionText').text()) == 0) {
                            $('#targetPosition').removeAttr('readonly');
                            $('#targetPosition').val(100);
                            $('#targetPositionText').text(100);
                            $('#targetCashAmount').text(Math.round(100 * data.current_price).toLocaleString());
                        } else {
                            $('#targetPosition').prop('readonly', true);
                            // $('#targetPosition').val(100);

                        }
                        if (parseInt($('#cashRemainToBuy').text()) <= 0) {
                            $('#btnSubmitTrade').prop('disabled', true);
                        } else {
                            $('#btnSubmitTrade').removeAttr('disabled');
                        }
                        $('#sharesRemainToSell').addClass('d-none');
                        $('#sharesRemainToSellLbl').addClass('d-none');

                    } else {
                        $('#targetPosition').prop('readonly', true);
                        if (parseInt($('#hiddenSharesRemainToSell').text()) <= 0) {
                            $('#btnSubmitTrade').prop('disabled', true);
                        } else {
                            $('#btnSubmitTrade').removeAttr('disabled');
                        }
                    }
                    $('#direction').val($('#hiddenTradeType').val());
                    refreshPositionBySymbol(code, data.current_price)
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

    // render the stock charts
    // 更新当前所选股票信息
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

    var getHistoricPrice = function (symbol, date, period) {
        var dateObj = date.toString().split("T");
        var startDate = dateObj[0];
        var endDate = dateObj[0];
        $.ajax({
            url: investBaseEndpoint + 'get-price/' + symbol + '/' + startDate + '/' + endDate + '/' + period + '/',
            success: function (data) {
                if(data.length>0){
                    $("#tradePrice").val(data[0].c)
                }
            }
        })
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

    var refreshPositionBySymbol = function (symbol, price) {
        // var symbol = $("#hiddenCode");
        var indexList = ["sh", "sz", "cyb"];
        if (indexList.indexOf(symbol)!=-1) return;
        var accountId = $("#pickedAccountID").val();
        $.ajax({
            url: userBaseEndpoint + 'position/account/' + accountId + '/' + symbol,
            success: function (data) {
                if (data.code == 'OK') {
                    $("#noPosition").addClass("d-none");
                    $("#stockPosition").removeClass("d-none");
                    var content = data.content;
                    $("#pStockName").text(content.stock_name); //股票名
                    $("#pStockSymbol").text(content.stock_symbol);//股票名
                    $("#pAccount").text(content.trade_account);//股票账户

                    if (content.profit > 0) {
                        if (!$("#pProfit").hasClass("badge-danger")) {
                            $("#pProfit").addClass("badge-danger");//利润
                            $("#pProfit").removeClass("badge-success");//利润
                            $("#pProfitRatio").addClass("badge-danger");//利润率
                            $("#pProfitRatio").removeClass("badge-success");//利润率
                        }
                        $("#pProfit").text("+" + content.profit.toLocaleString());//利润
                        $("#pProfitRatio").text("+" + content.profit_ratio);//利润率
                    } else {
                        if (!$("#pProfit").hasClass("badge-success")) {
                            $("#pProfit").addClass("badge-success");//利润
                            $("#pProfit").removeClass("badge-danger");//利润
                            $("#pProfitRatio").addClass("badge-success");//利润率
                            $("#pProfitRatio").removeClass("badge-danger");//利润率
                        }
                        $("#pProfit").text(content.profit);//利润
                        $("#pProfitRatio").text(content.profit_ratio);//利润率
                    }
                    $("#pCurrentPrice").text(content.current_price);//现价
                    $("#pPositionPrice").text(content.cost);//持仓成本
                    $("#pLots").text(content.lots.toLocaleString());//目标仓位
                    $("#pTargetPosition").text(content.target_position.toLocaleString());//目标仓位
                    $("#pCash").text(parseInt(content.capital).toLocaleString()); //市值
                } 
                else {
                    $("#pStockName").text($("#hiddenName").val()); //股票名
                    $("#pStockSymbol").text(symbol);//股票代码
                    $("#pProfit").text("-");//利润
                    $("#pProfitRatio").text("-");//利润率
                    $("#pCurrentPrice").text(price);//现价
                    $("#pPositionPrice").text("-");//持仓成本
                    $("#pLots").text("-");//目标仓位
                    $("#pTargetPosition").text("-");//目标仓位
                    $("#pCash").text("-"); //市值
                }
            }
        })
    }
    if ($("#tradeDatetime").length > 0){
        var date = formatDate(dt, "-");
        var hour = dt.getHours().toString().length == 2 ? dt.getHours() : "0" + dt.getHours();
        var min = dt.getMinutes().toString().length == 2 ? dt.getMinutes() : "0" + dt.getMinutes();
        var sec = dt.getSeconds().toString().length == 2 ? dt.getSeconds() : "0" + dt.getSeconds();
        $("#tradeDatetime").val(date+"T"+hour+":"+min+":"+sec);
    }
    refreshPositionBySymbol($("#hiddenCode").val(), null);

    var refreshRealtimeQuote = function () {
        $.ajax({
            url: userBaseEndpoint + 'positions/refresh/',
            success: function (data) {

            }
        })
    }

    var isOpenForTrade = function (inputDatetime) {
        // var dateAndTime = inputDatetime.split(" ");
        var date = formatDate(inputDatetime, "-");
        var openTime = new Date(date + " 9:15:00");
        var closeTime = new Date(date + " 15:05:00");
        var day = inputDatetime.getDay();
        var hour = inputDatetime.getHours();
        var min = inputDatetime.getMinutes();
        if (day == 6 || day == 0) return false;
        if (inputDatetime >= openTime && inputDatetime <= closeTime) {
            return true;
        }
        return false;
    }

    var refreshStockInfo2Realtime = function () {
        var showName = $("#hiddenName").val();
        var symbol = $("#hiddenCode").val();
        var showCode = $("#hiddenTscode").val();
        var period = $('input:radio[name="period"]:checked').val();
        updateChartFor(showName, showCode, symbol, period);
        updateTradeStockInfoFor(symbol);
        // refreshPositionBySymbol(symbol);
    };

    var refreshInterval = setInterval(function () {
        var d = new Date();
        if (isOpenForTrade(d)) {
            refreshStockInfo2Realtime();
        }
    }, 5 * 60 * 1000);

    function stopRefresh() {
        clearInterval(refreshInterval);
    }

    $("#tradeDatetime").change(function () {
        var symbol = $("#hiddenCode").val();
        getHistoricPrice(symbol, $(this).val(), "D");
    });

    $("#followStock").click(function(){
        var symbol = $("#hiddenCode").val();
        var name = $("#hiddenName").val();
        $.ajax(
            {
                url: userBaseEndpoint + 'stock/' + symbol + "/follow/",
                data:{
                    name: name
                },
                headers: { 'X-CSRFToken': csrftoken },
                method: 'POST',
                success: function (data) {
                    $("#messages").removeClass('d-none');
                    if(data.code=="ok"){
                        $("#messages").addClass('alert-success');
                    }else{
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

    // 页面加载时，更新请求的股票交易信息
    if ($('#hiddenCode').val() != "sh") {
        updateTradeStockInfoFor($('#hiddenCode').val())
    }

    if ($("#noAccount").length) {
        $("#btnSubmitTrade").addClass("disabled");
    }

    $('#searchNameOrCode').autoComplete({
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
        // location.replace("https://www.w3schools.com");
        updateChartFor(showName, showCode, code, period)
        updateTradeStockInfoFor(code);
        // refreshPositionBySymbol(code);
    });

    // 页面默认加载上证指数日K（D)
    var initStockChart = function (code, showCode, showName) {
        var period = $('input:radio[name="period"]:checked').val();
        var startDate = getStartDate(period, '-');
        // var code = $('input:radio[name="index"]:checked').val(); // e.g. sh
        // var showCode = $('input:radio[name="index"]:checked').attr('id')// e.g. 1A0001 上证
        // var showName = $('input:radio[name="index"]:checked').parent().text().trim();

        // $('#hiddenCode').val(code);
        // $('#hiddenName').val(showName);
        // $('#hiddenTscode').val(showCode);

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
                                    label = showName + ' - 开盘: ' + o + '  最高: ' + h + '  最低: ' + l + '  收盘: ' + c  + ' 涨幅: ' + percentage;
                                    return label;

                                    

                                    // if (!helpers$1.isNullOrUndef(point.y)) {
                                    //     return Chart.defaults.global.tooltips.callbacks.label(tooltipItem, data);
                                    // }

                                    

                                }
                            }
                        }
                    }
                });
            }
        });
    }

    // assign the selected strategy
    $('.strategy-item').click(function () {
        $('#pickedStrategy').val($(this).text());
        $('#pickedStrategyID').val($(this).data('id'));
    });

    // assign the selected strategy
    $('.account-item').click(function () {
        $('#pickedAccount').val($(this).text());
        $('#pickedAccountID').val($(this).data('id'));
        $('#hiddenAccountName').val($(this).text());
        $('#hiddenAccount').val($(this).data('id'));
    });

    $('input:radio[name="trade-type"]').change(function () {
        var trade_type = $(this).val();
        $('#direction').val($(this).val());
        if (trade_type == 'b') {
            $('#hiddenTradeType').val('b');
            $('#cashRemainToBuy').removeClass('d-none');
            $('#cashRemainToBuyLbl').removeClass('d-none');
            $('#sharesRemainToSell').addClass('d-none');
            $('#sharesRemainToSellLbl').addClass('d-none');
            if ($('#targetPositionText') == '0') {
                $('#targetPosition').prop('readonly', false);
            } else {
                $('#targetPosition').prop('readonly', true);
            }
        } else {
            $('#hiddenTradeType').val('s');
            $('#sharesRemainToSell').removeClass('d-none');
            $('#sharesRemainToSellLbl').removeClass('d-none');
            $('#cashRemainToBuy').addClass('d-none');
            $('#cashRemainToBuyLbl').addClass('d-none');
            $('#targetPosition').prop('readonly', true);
            // $('#btnSubmitTrade').prop('disabled', true);
        }

    });

    $("#tblMyPosition tbody tr").click(function () {
        // alert($(this).find('th').text()); // firstElementChild.innerText);
        //get <td> element values here!!??
        var rawNameCodeArray = $(this).find('th').text().split(' ');
        var code = rawNameCodeArray[0];
        var showName = rawNameCodeArray[1];
        var market = '', showCode = code;
        var period = $('input:radio[name="period"]:checked').val();

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
        $('#hiddenMarket').val(market);

        updateChartFor(showName, showCode, code, period);
        updateTradeStockInfoFor(code);
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
    $('#tradePrice').blur(function () {
        var price = $(this).val();
        var quantity = $('#quantity').val();
        // $('#quantity').val($('#quantity').val().toLocaleString());
        $('#refCashAmount').text(Math.round(price * quantity).toLocaleString());
    });

    // assign the selected strategy
    $('#quantity').blur(function () {
        var price = $('#tradePrice').val();
        var quantity = $(this).val();
        // $('#quantity').val($('#quantity').val().toLocaleString());
        $('#refCashAmount').text(Math.round(price * quantity).toLocaleString());
        if (quantity == '0') {
            $('#btnSubmitTrade').prop('disabled', true);
        } else {
            $('#btnSubmitTrade').removeAttr('disabled');
        }
    });

    $('#targetPosition').blur(function () {
        var price = $('#tradePrice').val();
        var quantity = $(this).val();
        $('#targetPositionText').text(quantity.toLocaleString());
        $('#targetCashAmount').text(Math.round(price * quantity).toLocaleString());
    });

    $('#traderecForm').submit(function (e) {
        var nameOrCode = $('#stockNameOrCode').val();
        var currentPrice = $('#currentPrice').val();
        var tradePrice = $('#tradePrice').val();
        var quantity = $('#quantity').val();
        var cash = $('#refCashAmount').text();

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

    $(".close").click(function(){
        $("#messages").addClass('d-none');
    });
    
    $('#btnSubmitTrade').click(function () {
        event.preventDefault();
        if ($('#btnSubmitTrade').hasClass("disabled")) return;
        var name = $('#hiddenName').val();
        var code = $('#hiddenCode').val();
        var tsCode = $('#hiddenTscode').val();
        var market = $('#hiddenMarket').val();
        var currentPrice = $('#currentPrice').text();
        var price = $('#tradePrice').val();
        var quantity = $('#quantity').val();
        var cash = $('#refCashAmount').text();
        var strategy = $('#pickedStrategyID').val();
        var targetPosition = $('#targetPosition').val();
        var direction = $('#direction').val();
        var tradeTime = $('#tradeDatetime').val();
        var tradeAcc = $('#pickedAccountID').val();

        if (strategy.length < 1) {
            $('#pickedStrategy').addClass("is-invalid");
            return;
        } else {
            $('#pickedStrategy').removeClass("is-invalid");
        }

        if (tradeTime.length < 1) {
            $('#tradeDatetime').addClass("is-invalid");
            return;
        } else {
            $('#tradeDatetime').removeClass("is-invalid");
        }

        if (price.length < 1) {
            $('#tradePrice').addClass("is-invalid");
            return;
        } else {
            $('#tradePrice').removeClass("is-invalid");
        }

        if (quantity.length < 1) {
            $('#quantity').addClass("is-invalid");
            return;
        } else {
            $('#quantity').removeClass("is-invalid");
        }

        if (direction == "s" && quantity > parseInt($("#hiddenSharesRemainToSell").text())) {
            $('#quantity').addClass("is-invalid");
            return;
        } else {
            $('#quantity').removeClass("is-invalid");
        }

        if (targetPosition.length < 1) {
            $('#targetPosition').addClass("is-invalid");
            return;
        } else {
            $('#targetPosition').removeClass("is-invalid");
        }

        if (!isOpenForTrade(new Date(tradeTime))) {
            $('#tradeDatetime').addClass("is-invalid");
            return;
        }

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
                currentPrice: price,//currentPrice,
                price: price,
                quantity: quantity,
                cash: cash,
                strategy: strategy,
                targetPosition: targetPosition,
                direction: direction,
                tradeTime: tradeTime,
                tradeAcc: tradeAcc
                // csrfmiddlewaretoken: '{{ csrf_token }}'
            },
            success: function (data) {
                $("#messages").removeClass('d-none');
                // $("#messages").addClass('d-block');
                $("#messageText").html('<strong>' + data.success + '</strong>.');
                // $("#messages").fadeOut(2000);
                // refreshPositionBySymbol(code);
                updateTradeStockInfoFor(code);
                // 更新k线图表
                var period = $('input:radio[name="period"]:checked').val();
                updateChartFor(name, tsCode, code, period);
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

    initStockChart($('#hiddenCode').val(), $('#hiddenTscode').val(), $('#hiddenName').val());

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