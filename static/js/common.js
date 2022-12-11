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
    var chartFormat = { 'value': [] };
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

var jsonToFundaChartFormat = function (jsonData) {
    var chartFormat = { 'pe': [], 'pettm': [], 'pb': [], 'ps': [], 'psttm': [], 'vr': [], 'tr': [], 'label': [] };
    $(jsonData).each(function (idx, obj) {
        chartFormat.pe.push(obj["pe"]);
        chartFormat.pettm.push(obj["pe_ttm"]);
        chartFormat.pb.push(obj["pb"]);
        chartFormat.ps.push(obj["ps"]);
        chartFormat.psttm.push(obj["ps_ttm"]);
        chartFormat.tr.push(obj["turnover_rate"]);
        chartFormat.vr.push(obj["volume_ratio"]);
        chartFormat.label.push(obj["trade_date"]);
    });
    return chartFormat;
}

var jsonToChartOHLCFormat = function (jsonData) {
    var chartFormat = { 'ohlc': [], 'label': [], 'volume': [] };
    // var ohlc = [];
    $(jsonData).each(function (idx, obj) {
        // ohlc.push(obj['o']);
        // ohlc.push(obj['c']);
        // ohlc.push(obj['l']);
        // ohlc.push(obj['h']);
        chartFormat.ohlc.push([obj['o'], obj['c'], obj['l'], obj['h']]);
        chartFormat.label.push(obj['d']);
        chartFormat.volume.push(obj['v']);
    });
    return chartFormat;
}

var jsonToMixChartFormat = function (jsonData) {
    var chartFormat = { 'ohlc': [], 'label': [], 'volume': [], 'ma': [], 'ema': [], 'boll': [], 'bbi': [], 'macd': [], 'kdj': [], 'rsi': [], 'atr': [],'atr3': [],'atr6': [], 'equity': [] };
    var maFormat = { 'ma10': [], 'ma20': [], 'ma60': [], 'ma120': [], 'ma200': [] };
    var emaFormat = { 'ema10': [], 'ema20': [], 'ema60': [], 'ema120': [], 'ema200': [] };
    var bollFormat = { 'upper': [], 'mid': [], 'lower': [] };
    var macdFormat = { 'dif': [], 'dea': [], 'bar': [] };
    var kdjFormat = { 'k': [], 'd': [], 'j': [] };
    var rsiFormat = { 'rsi6': [], 'rsi12': [], 'rsi24': [] };

    chartFormat.ma.push(maFormat);
    chartFormat.ema.push(emaFormat);
    chartFormat.boll.push(bollFormat);
    chartFormat.macd.push(macdFormat);
    chartFormat.kdj.push(kdjFormat);
    chartFormat.rsi.push(rsiFormat);

    // var ohlc = [];
    $(jsonData).each(function (idx, obj) {
        // ohlc.push(obj['o']);
        // ohlc.push(obj['c']);
        // ohlc.push(obj['l']);
        // ohlc.push(obj['h']);
        chartFormat.ohlc.push([obj['o'], obj['c'], obj['l'], obj['h']]);
        chartFormat.label.push(obj['d']);
        chartFormat.volume.push(obj['v']);

        chartFormat.ma[0].ma10.push(obj['ma10']);
        chartFormat.ma[0].ma20.push(obj['ma20']);
        chartFormat.ma[0].ma60.push(obj['ma60']);
        chartFormat.ma[0].ma120.push(obj['ma120']);
        chartFormat.ma[0].ma200.push(obj['ma200']);

        chartFormat.ema[0].ema10.push(obj['ema10']);
        chartFormat.ema[0].ema20.push(obj['ema20']);
        chartFormat.ema[0].ema60.push(obj['ema60']);
        chartFormat.ema[0].ema120.push(obj['ema120']);
        chartFormat.ema[0].ema200.push(obj['ema200']);

        chartFormat.boll[0].upper.push(obj['bollupper']);
        chartFormat.boll[0].mid.push(obj['bollmid'])
        chartFormat.boll[0].lower.push(obj['bolllower']);

        chartFormat.bbi.push(obj['bbi']);
        // newly added for 止损
        chartFormat.atr.push(obj['atr']);
        // chartFormat.atr3.push(obj['3atr']);
        // chartFormat.atr6.push(obj['6atr']);


        chartFormat.kdj[0].k.push(obj['kdjk']);
        chartFormat.kdj[0].d.push(obj['kdjd']);
        chartFormat.kdj[0].j.push(obj['kdjj']);

        chartFormat.macd[0].dif.push(obj['macddif']);
        chartFormat.macd[0].dea.push(obj['macddea']);
        chartFormat.macd[0].bar.push(obj['macdbar']);

        chartFormat.rsi[0].rsi6.push(obj['rsi6']);
        chartFormat.rsi[0].rsi12.push(obj['rsi12']);
        chartFormat.rsi[0].rsi24.push(obj['rsi24']);

        chartFormat.equity.push(obj['eq']);
    });
    return chartFormat;
}

var jsonToBTResultFormat = function (jsonData) {
    var chartFormat = { 'equity': [], 'label': [], 'drawdownpct': [], 'drawdowndur': [], 'trades': [], 'entryprice': [], 'exitprice': [], 'duration': [], 'pnl': [] };

    // var ohlc = [];
    $(jsonData).each(function (idx, obj) {
        // ohlc.push(obj['o']);
        // ohlc.push(obj['c']);
        // ohlc.push(obj['l']);
        // ohlc.push(obj['h']);
        chartFormat.equity.push(obj['eq']);
        chartFormat.label.push(obj['dt']);
        chartFormat.drawdownpct.push(obj['ddp']);
        chartFormat.drawdowndur.push(obj['ddd']);
        chartFormat.trades.push([obj['bs'],obj['en_p'],obj['ex_p'],obj['dur'],obj['pnl'],obj['dt']]);
        // chartFormat.entryprice.push();
        // chartFormat.exitprice.push();
        // chartFormat.duration.push();
        // chartFormat.pnl.push();

    });
    return chartFormat;
}

var resampleEquity = function (equityData, xAxisOHLCLabel) {
    var equityDataOnly = equityData.equity;
    var equityLabel = equityData.label;
    return equityDataOnly.slice(-xAxisOHLCLabel.length);
}

var resampleTrades = function (equityData, xAxisOHLCLabel) {
    var trades = equityData.trades;
    return trades.slice(-xAxisOHLCLabel.length);
}

var resampleTradesFundamental = function (equityData, xAxisFundaLabel) {
    var equityDataOnly = equityData.equity;
    var equityLabel = equityData.label;
    var partEquity = [];
    // 先判断下xAxisFundaLabel的label最早的日期，只截取equityData大于最早日期的数据
    var earlistFundaLabel = xAxisFundaLabel[0];
    var earlistIndex = equityLabel.indexOf(earlistFundaLabel);
    if (earlistIndex != -1) {
        partEquity = equityDataOnly.splice(-(equityLabel.length - earlistIndex));
    } else {
        console.log("something goes wrong");
        return undefined;
    }
    var partEquityLength = equityLabel.length - earlistIndex;
    // 判断slice完以后的equity长度和aAxisFundaLabel的长度是否一致，如果一致就返回，如果不一致，需要插值
    if (partEquityLength != xAxisFundaLabel.length) {
        if (partEquityLength > xAxisFundaLabel.length) {
            
        }
        else {
            console.log("something goes wrong");
        }
    } else {
        return partEquity;
    }
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

var getQuantileOfArray = function (dataArray) {
    var quantileData = { 'qt10': [], 'qt50': [], 'qt90': [] };
    var quantileSeq = math.quantileSeq(dataArray, [0.1, 0.5, 0.9]);
    for (var i = 0; i < dataArray.length; i++) {
        quantileData.qt10.push(math.format(quantileSeq[0], 2));
        quantileData.qt50.push(math.format(quantileSeq[1], 2));
        quantileData.qt90.push(math.format(quantileSeq[2], 2));
    }
    return quantileData;
}
