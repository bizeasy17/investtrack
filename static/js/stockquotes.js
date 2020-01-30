// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

/* Notifications JS basic client */
$(function () {
    var klineBaseEndpoint = 'stocks/kline/';
    var realtimeQuoteBaseEndpoint = 'stocks/realtime_quote/';
    var stockCodeBaseEndpoint = 'stocks/code/';
    var stockNameBaseEndpoint = 'stocks/name/';
    var chartCanvas = document.getElementById('myStockChart').getContext('2d');


    // when lost focus get the code auto filled
    $('#id_stock_name').blur(function(){
        // if(validateStockName()){
        // }
        // $('#id_stock_code').val('000001');
        // mock for now
        var chartShowDays = 60
        var dt = new Date();
        var priorDt = new Date(dt.getTime() - (chartShowDays * 24 * 60 * 60 * 1000));
        var stockNameOrCode = document.getElementById('id_stock_name').value;
        var startDate = formatDate(priorDt);
        var endDate = formatDate(dt);

        if(stockNameOrCode != null && $.isNumeric(stockNameOrCode)){
            // Input is code
            showStockKlineByCode(stockNameOrCode, startDate, endDate)
        }else{
            // Input is name
            showStockKlineByName(stockNameOrCode, startDate, endDate)
        }        
    });

    // when lost focus get the code auto filled
    $('#id_stock_code').blur(function(){
        // if(validateStockName()){
        // }
        // $('#id_stock_code').val('000001');
        // mock for now
        var stockCode = document.getElementById('id_stock_code').value;
        var startDate = '20191201';
        var endDate = '20191231'
        
        showStockKlineByCode(stockCode, startDate, endDate);
    });

    function formatDate(date) {
        var monthNames = [
          "01", "02", "03",
          "04", "05", "06", "07",
          "08", "09", "10",
          "11", "12"
        ];
      
        var day = date.getDate();
        var monthIndex = date.getMonth();
        var year = date.getFullYear();
      
        return year + '' + monthNames[monthIndex] + '' + day;
    }

    // var barCount = 60;
    // var initialDateStr = '20200110';
    function showStockKlineByName(stockName, startDate, endDate){
        // Bar Chart Example
        var stockCodeEndpoint = stockCodeBaseEndpoint + stockName;
        $.ajax({
            url: stockCodeEndpoint,
            success: function(data){
                var stockCode = data;
                var klineEndpoint = klineBaseEndpoint + 'code/' + stockCode + '/startdate/' + startDate + '/enddate/' + endDate;
                chartRender(klineEndpoint, stockName, stockCode);  
            }
        });
    }

    function showStockKlineByCode(stockCode, startDate, endDate){
        // Bar Chart Example
        marketCode = stockCode[0];
        if(marketCode=='6'){
            stockCode = stockCode + '.SH';
        }else{
            stockCode = stockCode + '.SZ';
        }

        stockNameBaseEndpoint = stockNameBaseEndpoint + stockCode;
        $.ajax({
            url: stockNameBaseEndpoint,
            success: function(data){
                var stockName = data;
                var klineEndpoint = klineBaseEndpoint + 'code/' + stockCode + '/startdate/' + startDate + '/enddate/' + endDate;
                chartRender(klineEndpoint, stockName, stockCode);  
            }
        });
    }

    function chartRender(klineEndpoint, stockName, stockCode){
        $.ajax({
            url: klineEndpoint,
            success: function(data){
                var chart = new Chart(chartCanvas, {
                    type: 'candlestick',
                    data: {
                        datasets: [{
                            label: stockCode + ' - ' + stockName,
                            data: data,
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
    }

    function showStockRealtimeQuote(stockCode, canvasId){
        var chartCanvas = document.getElementById(canvasId).getContext('2d');
        // Bar Chart Example
        
    }
    
});