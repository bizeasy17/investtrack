var chartShowDays60 = 60;
var chartShowDays = 60;
var chartShowDaysW = 180;
var chartShowDaysM = 720;

var closeChartShowDays = 365 * 2;

var formatDate = function (date, connector) {
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

    return year + connector + monthNames[monthIndex] + connector + dayNames[dayIndex - 1];
}

var isOpenForTrade = function (inputDatetime) {
    // var dateAndTime = inputDatetime.split(" ");
    var date = formatDate(inputDatetime, "-");
    var openTime = new Date(date + " 9:30:00");
    var morningCloseTime = new Date(date + " 11:30:00");
    var afternoonOpenTime = new Date(date + " 13:00:00");
    var closeTime = new Date(date + " 15:05:00");
    var day = inputDatetime.getDay();
    var hour = inputDatetime.getHours();
    var min = inputDatetime.getMinutes();
    if (day == 0 || day == 6) return false; //周六周日不需要刷新
    if (inputDatetime >= openTime && inputDatetime <= morningCloseTime) {
        return true;
    }
    if (inputDatetime >= afternoonOpenTime && inputDatetime <= closeTime) {
        return true;
    }
    if (inputDatetime > date) {
        return false;
    }
    return false;
}

var getStartDate = function (period, format) {
    var dt = new Date();
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

var jsonToArray = function (jsonData, dataType) {
    var chartFormat = { 'value': []};
    $(jsonData).each(function (idx, obj) {
        chartFormat.value.push(obj[dataType]);
    });
    return chartFormat;
}

var jsonToChartFormat = function (jsonData, dataType) {
    var chartFormat = { 'value': [], 'label': [] };
    $(jsonData).each(function (idx, obj) {
        chartFormat.value.push(obj[dataType]);
        chartFormat.label.push(obj.trade_date);
    });
    return chartFormat;
}

var jsonToChartOHLCFormat = function (jsonData) {
    var chartFormat = { 'value': [], 'label': [], 'volume': [], 'equity': [] };
    // var ohlc = [];
    $(jsonData).each(function (idx, obj) {
        // ohlc.push(obj['o']);
        // ohlc.push(obj['c']);
        // ohlc.push(obj['l']);
        // ohlc.push(obj['h']);
        chartFormat.value.push([obj['o'],obj['c'],obj['l'],obj['h']]);
        chartFormat.label.push(obj['d']);
        chartFormat.volume.push(obj['v']);
        chartFormat.equity.push(obj['e']);

        // ohlc.splice(0);
    });
    return chartFormat;
}

var jsonToChartEMAFormat = function (jsonData) {
    var chartFormat = { 'ema_10': [], 'label': [], 'ema_20': [], 'ema_60': [] , 'ema_120': [] , 'ema_200': [] };
    // var ohlc = []
    $(jsonData).each(function (idx, obj) {
        $(obj.ema_10).each(function(idx, o){
            $.each(o, function(k){
                chartFormat.ema_10.push(o[k]);
            });
        });
    
        $(obj.ema_20).each(function(idx, o){
            $.each(o, function(k){
                chartFormat.ema_20.push(o[k]);
            });
        });
    
        $(obj.ema_60).each(function(idx, o){
            $.each(o, function(k){
                chartFormat.ema_60.push(o[k]);
            });
        });

        $(obj.ema_120).each(function(idx, o){
            $.each(o, function(k){
                chartFormat.ema_120.push(o[k]);
            });
        });

        $(obj.ema_200).each(function(idx, o){
            $.each(o, function(k){
                chartFormat.ema_200.push(o[k]);
            });
        });
    });
    return chartFormat;
}

var jsonToChartBOLLFormat = function (jsonData) {
    var chartFormat = { 'boll_high': [], 'label': [], 'boll_mid': [], 'boll_low': []};
    // var ohlc = []
    $(jsonData).each(function (idx, obj) {
        $($.parseJSON(obj.high)).each(function(idx, o){
            $.each(o, function(k){
                chartFormat.boll_high.push(o[k]);
            });
        });
    
        $($.parseJSON(obj.mid)).each(function(idx, o){
            $.each(o, function(k){
                chartFormat.boll_mid.push(o[k]);
            });
        });
    
        $($.parseJSON(obj.low)).each(function(idx, o){
            $.each(o, function(k){
                chartFormat.boll_low.push(o[k]);
            });
        });
    });
    return chartFormat;
}

var jsonToChartBBIFormat = function (jsonData) {
    var chartFormat = { 'bbi': [], 'label': []};
    // var ohlc = []
    $($.parseJSON(jsonData).bbi).each(function (idx, obj) {
        // $(obj).each(function(id, o){
        $.each(obj, function(k){
            chartFormat.bbi.push(obj[k]);
        });
        // });
    });
    return chartFormat;
}

var jsonToChartRSIFormat = function (jsonData) {
    var chartFormat = { 'rsi_6': [], 'label': [], 'rsi_12': [], 'rsi_24': [] };
    // var ohlc = []
    $(jsonData).each(function (idx, obj) {
        $(obj.rsi_6).each(function(idx, o){
            // for(var key in o) {
            //     chartFormat.rsi_6.push(o[key]);
            //  }
            $.each(o, function(k){
                chartFormat.rsi_6.push(o[k]);
            });
        });
    
        $(obj.rsi_12).each(function(idx, o){
            $.each(o, function(k){
                chartFormat.rsi_12.push(o[k]);
            });
        });
    
        $(obj.rsi_24).each(function(idx, o){
            $.each(o, function(k){
                chartFormat.rsi_24.push(o[k]);
            });
        });
    });
    return chartFormat;
}

var jsonToChartKDJFormat = function (jsonData) {
    var chartFormat = { 'k': [], 'label': [], 'd': [], 'j': [] };
    // var ohlc = []
    $(jsonData).each(function (idx, obj) {
        $(obj.k).each(function(idx, o){
            $.each(o, function(k){
                chartFormat.k.push(o[k]);
            });
        });
    
        $(obj.d).each(function(idx, o){
            $.each(o, function(k){
                chartFormat.d.push(o[k]);
            });
        });
    
        $(obj.j).each(function(idx, o){
            $.each(o, function(k){
                chartFormat.j.push(o[k]);
            });
        });
    });
    return chartFormat;
}

var jsonToChartMACDFormat = function (jsonData) {
    var chartFormat = { 'dif': [], 'label': [], 'dea': [], 'bar': [] };
    // var ohlc = []
    $(jsonData).each(function (idx, obj) {
        $(obj.dif).each(function(idx, o){
            $.each(o, function(k){
                chartFormat.dif.push(o[k]);
            });
        });
    
        $(obj.dea).each(function(idx, o){
            $.each(o, function(k){
                chartFormat.dea.push(o[k]);
            });
        });
    
        $(obj.bar).each(function(idx, o){
            $.each(o, function(k){
                chartFormat.bar.push(o[k]);
            });
        });
    });
    return chartFormat;
}

var getQuantile = function (chartData) {
    var quantileData = { 'qt10': [], 'qt50': [], 'qt90': [] };
    var quantileSeq = math.quantileSeq(chartData.value, [0.1, 0.5, 0.9]);
    for (var i = 0; i < chartData.value.length; i++) {
        quantileData.qt10.push(math.format(quantileSeq[0], 2));
        quantileData.qt50.push(math.format(quantileSeq[1], 2));
        quantileData.qt90.push(math.format(quantileSeq[2], 2));
    }
    return quantileData;
}
