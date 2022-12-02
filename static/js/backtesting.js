$(function () {
    // <strategy_category>/<ta_indicator_dict>/<buy_cond_dict>/<sell_cond_dict>/<stoploss>/<cash>/<commission>/<leverage>/<freq>/
    const upColor = '#ec0000';
    const downColor = '#00da3c';

    let ohlcMixChartData = "";

    let taBIndicatorSet = new Set();
    let taSIndicatorSet = new Set();
    const bStrategyTextSet = new Set();
    const sStrategyTextSet = new Set();

    var strategyCategory = "system";
    var taIndicator = "";
    var bSystem = "";
    var sSystem = "";
    var stoploss = .97;
    var capital = 10000;
    var commission = .001;
    var leverage = 1;
    var tradeOnClose = 0;
    var restoration = "bfq";
    var freq = "D";
    // <tech_indicator>/<indicator_param>/<strategy_category>/<cash>/<commission>/<leverage>/<freq>/</freq>
    var tsCode;
    var stockName;

    var INDIC_CROSSOVER = "0";
    var INDIC_PAIR_COMP = "1";
    var INDIC_THRESHOLD = "2";

    var today = new Date();
    var startDate = "";
    var endDate = "";
    var stockHistPeriod = "3";

    var btMixChart;
    var btFundamentalChart;
    var indicChart;
    var fundaChart;
    var mixChartOption;
    var bStrategyCount = 0;
    var sStrategyCount = 0;
    // let strategyCount = [0, 0];

    var equityJsonData = undefined;
    var ohlcChartData;
    // var ohlcCount = 0;

    var stockmarketEndpoint = "/stockmarket/";
    var curIndicator = ["SMA", "0", "1", "3"];
    var curBStrategyCategory = "0";
    var curSStrategyCategory = "0";

    var condParamCrossover = ["向上穿越,crossover", "向下穿越,crossover"];
    var condParamValueCompare = ["大于,>", "小于,<"];
    var indicatorParamOHLC = ["收盘价,Close"];
    var smaParam = ["10", "20", "60", "120", "200"];
    var emaParam = ["10", "20", "60", "120", "200"];
    var bbiParam = ["BBI"];
    var bollParam = ["MID", "UPPER", "LOWER"];

    var kdjParam = ["K", "D", "J"];
    var macdParam = ["MACD", "DIFF", "DEA"];
    var rsiParam = ["6", "12", "24"];

    var typeAParam = ["SMA","EMA","RSI","BBI"];
    var typeBParam = ["KDJ","MACD","BOLL"];

    var indicaMap = new Map();
    var maChartData;
    var emaChartData;
    var bbiChartData;
    var bollChartData;
    // var basicCharts

    var initParam = function () {
        // global param
        tsCode = $("#hiddenTsCode").val();
        stockName = $("#hiddenTsCode").attr("name");

        capital = $("#capital").val();
        stoploss = (100 - parseInt($("#stoploss").val()))/100;

        stockHistPeriod = $('input:radio[name="period"]:checked').val();
        tradeOnClose = $('input:radio[name="trade-on-close"]:checked').val();
        restoration = $('input:radio[name="restoration"]:checked').val();
        freq = $('input:radio[name="freq"]:checked').val();

        startDate = formatDate(new Date(today.getTime() - (365 * stockHistPeriod * 24 * 60 * 60 * 1000)), "");
        endDate = formatDate(today, "");

        fundaChart = ["pe:6","pe_ttm:7","pb:8","ps:9","ps_ttm:10","turnover_rate:11","volume_ratio:12"];
        btMixChart = echarts.init(document.getElementById('btMixChart'));
        btFundamentalChart = echarts.init(document.getElementById('btFundamentalChart'));

        // ohlcChart = echarts.init(document.getElementById('ohlcChart'));
        // indicChart = echarts.init(document.getElementById('indicChart'));
        // fundaChart = echarts.init(document.getElementById('top10HoldersChart'));
        indicaMap.set("SMA", smaParam);
        indicaMap.set("EMA", emaParam);
        indicaMap.set("BOLL", bollParam);
        indicaMap.set("KDJ", kdjParam);
        indicaMap.set("MACD", macdParam);
        indicaMap.set("RSI", rsiParam);
        indicaMap.set("BBI", bbiParam);

        // local
        var unit = $('input:radio[name="commission-unit"]:checked').val();
        var commissionOpt = $('input:radio[name="commission"]:checked').val();

        if (unit == "tth") {
            commission = parseInt(commissionOpt) / 10000;
        } else {
            commission = parseInt(commissionOpt) / 1000;
        }

        setupStrategyCategories("#bStrategyCategory");
        setupStrategyCategories("#sStrategyCategory");

        // stockname display global
        $(".stock_name").text($("#hiddenTsCode").attr("name")  + " [" + $("#hiddenTsCode").val() + "]");
    }

    // 此处会有新的chart数据更新
    var updateBTMixChart = function (tsCode) {
        // 初始化OHLC，MA，VOL，Equity，MACD，KDJ，RSI，Fundamental Chart Data
        var zoomMin = 0;
        var zoomMax = 100;
        $.ajax({
            url: stockmarketEndpoint + "ohlc-indic/" + tsCode + "/" + freq + "/" + stockHistPeriod + "/",
            success: function (data) {
                ohlcChartData = jsonToMixChartFormat(data);
                // global OHLC数据
                ohlcMixChartData = data;
                // ohlcCount = chartData.label.length;

                option = initMixChartOption(ohlcChartData);
                btMixChart.setOption(option);

                updateOHLCChart(ohlcChartData);
                updateTechIndicatorChart();
                updateVolumeChart(ohlcChartData);
                updateRSIChart(ohlcChartData);
                updateMACDChart(ohlcChartData);
                updateKDJChart(ohlcChartData);

                if(equityJsonData == undefined){
                    updateEquityChart(ohlcChartData.equity);
                    updateTradesChart([]);
                }
                else{
                    var resampledEquityData = resampleEquity(equityJsonData, ohlcChartData.label);
                    var resampledTradesData = resampleTrades(equityJsonData, ohlcChartData.label);
                    // resampledTradesData = resampleTrades(equityJsonData, fundaChartData.label);
                    updateEquityChart(resampledEquityData);
                    updateTradesChart(resampledTradesData);
                }
            }
            ,
            complete: function (request, status) {
                // renderCompanyFundaChart(tsCode, startDate, endDate);
                // renderRSIChart(tsCode);
                // renderKDJChart(tsCode);
                // renderMACDChart(tsCode);
                // alert('do smthing');
                updateFundaChart(tsCode, startDate, endDate);
            }
        });
    }

    var initMixChartOption = function(ohlcChartData) {
        var mixChartOption = {
            animation: true,
            // legend: {
            //     top: 5,
            //     data: ['MA10','MA20','MA60','MA120','MA200']
            // },
            // tooltip: {
            //     trigger: 'axis',
            //     axisPointer: {
            //         type: 'cross'
            //     },
            //     borderWidth: 1,
            //     borderColor: '#ccc',
            //     padding: 10,
            //     textStyle: {
            //         color: '#000'
            //     },
            //     position: function (pos, params, el, elRect, size) {
            //         const obj = {
            //             top: 10
            //         };
            //         obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 30;
            //         return obj;
            //     }
            //     // extraCssText: 'width: 170px'
            // },
            axisPointer: {
                link: [
                    {
                        xAxisIndex: 'all'
                    }
                ],
                label: {
                    backgroundColor: '#777'
                }
            },
            // toolbox: {
            //     feature: {
            //         dataZoom: {
            //             yAxisIndex: false
            //         },
            //         brush: {
            //             type: ['lineX', 'clear']
            //         }
            //     }
            // },
            brush: {
                xAxisIndex: 'all',
                brushLink: 'all',
                outOfBrush: {
                    colorAlpha: 0.1
                }
            },
            // visualMap: {
            //     show: false,
            //     seriesIndex: 5,
            //     dimension: 2,
            //     pieces: [
            //         {
            //             value: 1,
            //             color: downColor
            //         },
            //         {
            //             value: -1,
            //             color: upColor
            //         }
            //     ]
            // },
            grid: [
                //OHLC grid index 0
                {left: '4%',right: '3%',top: "2%",height: '24%'},
                // reserved for equity grid index 1
                // {left: '4%',right: '1%',top: "2%",height: '13%'},+8
                {left: '4%',right: '3%',top: "34%",height: '8%'},

                //OHLC grid index 2, volume成交量 +4
                {left: '4%',right: '3%',top: '46%',height: '8%'},
                
                //OHLC grid index 3, RSI +4
                {left: '4%',right: '3%',top: '58%',height: '8%'},
                //OHLC grid index 4, MACD +7
                {left: '4%',right: '3%',top: '73%',height: '8%'},
                //OHLC grid index 5, KDJ +7
                {left: '4%',right: '3%',top: '88%',height: '8%'},

                //Fundamental grid index 5, PE
                // {left: '4%', top: '52%',height:'7%',width: '42%'},
                //Fundamental grid index 6, PE TTM
                // {right: '3%',top: '52%',height:'7%',width: '42%'},

                //Fundamental grid index 7, PB
                // {left: '4%', right: '3%',top: '63%',height: '7%'},

                //Fundamental grid index 8, PS
                // {left: '4%',top: '76%',height:'7%',width: '42%'},
                //Fundamental grid index 9, PS TTM
                // {right: '3%',top: '76%',height:'7%',width: '42%'},
                
                //Fundamental grid index 10, Turnover ratio
                // {left: '4%',top: '89%',height: '7%', width: '42%'},
                //Fundamental grid index 11, Vol ratio
                // {right: '3%',top: '89%',height: '7%', width: '42%'}
            ],
            xAxis: [
                {gridIndex: 0, data: ohlcChartData.label, min: 'dataMin', max: 'dataMax',axisLine: { onZero: false }, id:"ohlcxAxis"}, // OHLC
                {gridIndex: 1, data: ohlcChartData.label, min: 'dataMin', max: 'dataMax', id: 'equityxAxis'}, // Equity资产净值
                {gridIndex: 2, data: ohlcChartData.label, min: 'dataMin', max: 'dataMax',axisLine: { onZero: false },axisTick: { show: false },splitLine: { show: false },axisLabel: { show: false }, id:'volxAxis'}, // VOL
                
                {gridIndex: 3, data: ohlcChartData.label, min: 'dataMin', max: 'dataMax', id:"rsixAxis"}, // RSI
                {gridIndex: 4, data: ohlcChartData.label, min: 'dataMin', max: 'dataMax', id:"macdxAxis"}, // MACD
                {gridIndex: 5, data: ohlcChartData.label, min: 'dataMin', max: 'dataMax', id:"kdjxAxis"}, // KDJ

                // {gridIndex: 6, min: 'dataMin', max: 'dataMax', id:"pexAxis"}, // PE
                // {gridIndex: 7, min: 'dataMin', max: 'dataMax', id:"pettmxAxis"}, // PE TTM
                // {gridIndex: 8, min: 'dataMin', max: 'dataMax', id:"pbxAxis"}, // PB
                // {gridIndex: 9, min: 'dataMin', max: 'dataMax', id:"psxAxis"}, // PS
                // {gridIndex: 10, min: 'dataMin', max: 'dataMax', id:"psttmxAxis"}, // PS TTM
                // {gridIndex: 11, min: 'dataMin', max: 'dataMax', id:"turnoverxAxis"}, // TO 换手率 
                // {gridIndex: 12, min: 'dataMin', max: 'dataMax', id:"volratioxAxis"} // VO 量比 

                // {
                //     type: 'category',
                //     gridIndex: 1,
                //     data: chartData.label,
                //     boundaryGap: false,
                //     axisLine: { onZero: false },
                //     axisTick: { show: false },                                                                                
                //     splitLine: { show: false },
                //     axisLabel: { show: false },
                //     min: 'dataMin',
                //     max: 'dataMax'
                // }
            ],
            yAxis: [
                {gridIndex: 0, scale: true, min: 'dataMin', max: 'dataMax'}, // OHLC
                {gridIndex: 1, scale: true, min: 0, name: '资产净值', nameLocation: 'end',}, // OHLC
                {gridIndex: 2, scale: true, min: 'dataMin', max: 'dataMax', name: '成交量', nameLocation: 'middle', axisLine: { show: false, onZero: false },axisTick: { show: false },splitLine: { show: false },axisLabel: { show: false }}, // VOL
                
                {gridIndex: 3, scale: true, min: 'dataMin', max: 'dataMax', name: 'RSI(6,12,24)', nameLocation: 'end'}, // RSI
                {gridIndex: 4, scale: true, min: 'dataMin', max: 'dataMax', name: 'MACD(12,26,9)', nameLocation: 'end'}, // MACD
                {gridIndex: 5, scale: true, min: 'dataMin', max: 'dataMax', name: 'KDJ(3,9,0)', nameLocation: 'end'}, // KDJ

                // {gridIndex: 6, scale: true, min: 'dataMin', max: 'dataMax', name: '市盈', nameLocation: 'end'}, // PE
                // {gridIndex: 7, scale: true, min: 'dataMin', max: 'dataMax', name: '动态市盈率', nameLocation: 'end'}, // PE TTM
                // {gridIndex: 8, scale: true, min: 'dataMin', max: 'dataMax', name: '市净率', nameLocation: 'end'}, // PB
                // {gridIndex: 9, scale: true, min: 'dataMin', max: 'dataMax', name: '市销率', nameLocation: 'end'}, // PS
                // {gridIndex: 10, scale: true, min: 'dataMin', max: 'dataMax', name: '动态市销率', nameLocation: 'end'}, // PS TTM
                // {gridIndex: 11, scale: true, min: 'dataMin', max: 'dataMax', name: '换手率', nameLocation: 'end'}, // TO 换手率 
                // {gridIndex: 12, scale: true, min: 'dataMin', max: 'dataMax', name: '量比', nameLocation: 'end'} // VO 量比 

                // { scale: true,
                //     splitArea: {
                //         show: true
                //     }
                // },
                // {
                //     scale: true,
                //     gridIndex: 1,
                //     splitNumber: 2,
                //     axisLabel: { show: false },
                //     axisLine: { show: false },
                //     axisTick: { show: false },
                //     splitLine: { show: false }
                // }
            ],
            dataZoom: [
                {
                    type: 'inside',
                    xAxisIndex: [0,1,2,3,4,5],
                    start: 0,
                    end: 100
                }
                // ,
                // {
                //     show: true,
                //     xAxisIndex: [0, 1],
                //     type: 'slider',
                //     top: '85%',
                //     start: 0,
                //     end: 100
                // }
            ],
            series: [
                {
                    id: "ohlc",
                    name: 'k线',
                    type: 'candlestick',
                    // data: chartData.value,
                    itemStyle: {
                        color: upColor,
                        color0: downColor,
                        borderColor: undefined,
                        borderColor0: undefined
                    },
                    markPoint: {
                        symbol: "triangle", 
                    }
                },
                {
                    id: "indic1",
                    // name: 'MA10',
                    type: 'line',
                    // data: calculateMA(10, chartData),
                    showSymbol: false,
                    smooth: true,
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "indic2",
                    // name: 'MA20',
                    type: 'line',
                    // data: calculateMA(20, chartData),
                    smooth: true,
                    showSymbol: false,
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "indic3",
                    // name: 'MA60',
                    type: 'line',
                    // data: calculateMA(60, chartData),
                    smooth: true,
                    showSymbol: false,
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "indic4",
                    // name: 'MA120',
                    type: 'line',
                    // data: calculateMA(120, chartData),
                    smooth: true,
                    showSymbol: false,
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "indic5",
                    // name: 'MA200',
                    type: 'line',
                    // data: calculateMA(200, chartData),
                    smooth: true,
                    showSymbol: false,
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                // {
                //     id: "ohlctrades",
                //     // name: 'MA200',
                //     type: 'line',
                //     showSymbol: false,
                //     lineStyle: {
                //         opacity: 0.5
                //     }
                // },
                {
                    id: 'equity',
                    name: '净值',
                    type: 'line',
                    smooth: true,
                    showSymbol: false,
                    xAxisIndex: 1,
                    yAxisIndex: 1,
                    // data: chartData.equity
                },
                {
                    id: "vol",
                    name: 'Volume',
                    type: 'bar',
                    xAxisIndex: 2,
                    yAxisIndex: 2,
                    // data: chartData.volume
                },
                {
                    id: "rsi6",
                    name: "RSI(6)",
                    type: 'line',
                    xAxisIndex: 3,
                    yAxisIndex: 3,
                    smooth: true,
                    showSymbol: false
                },
                {
                    id: "rsi12",
                    name: "RSI(12)",
                    xAxisIndex: 3,
                    yAxisIndex: 3,
                    type: 'line',
                    smooth: true,
                    showSymbol: false
                },
                {
                    id: "rsi24",
                    name: "RSI(24)",
                    type: 'line',
                    xAxisIndex: 3,
                    yAxisIndex: 3,
                    smooth: true,
                    showSymbol: false
                },
                {
                    id: "macddif",
                    name: "MACD_DIF",
                    type: 'line',
                    xAxisIndex: 4,
                    yAxisIndex: 4,
                    smooth: true,
                    showSymbol: false
                },
                {
                    id: "macddea",
                    name: "MACD_DEA",
                    xAxisIndex: 4,
                    yAxisIndex: 4,
                    type: 'line',
                    smooth: true,
                    showSymbol: false
                },
                {
                    id: "macdbar",
                    name: "MACD_BAR",
                    type: 'bar',
                    xAxisIndex: 4,
                    yAxisIndex: 4,
                    smooth: true,
                    showSymbol: false
                },
                {
                    id: "kdjk",
                    name: "KDJ_K",
                    type: 'line',
                    xAxisIndex: 5,
                    yAxisIndex: 5,
                    smooth: true,
                    showSymbol: false
                },
                {
                    id: "kdjd",
                    name: "KDJ_D",
                    xAxisIndex: 5,
                    yAxisIndex: 5,
                    type: 'line',
                    smooth: true,
                    showSymbol: false
                },
                {
                    id: "kdjj",
                    name: "KDJ_J",
                    type: 'line',
                    xAxisIndex: 5,
                    yAxisIndex: 5,
                    smooth: true,
                    showSymbol: false
                }
            ]
        };
        return mixChartOption;
    }

    var updateOHLCChart = function(ohlcChartData){
        var ohlcChartOption = {
            // xAxis:[ 
            //     {id: "ohlcxAxis", data: ohlcChartData.label} // OHLC
            // ],
            series:[
                {
                    id: "ohlc",
                    data: ohlcChartData.ohlc,
                }
            ]};

        //动态添加 legend.data
        btMixChart.setOption(ohlcChartOption);
    }

    var updateVolumeChart = function(volChartData){
        var volChartOption = {
            // xAxis: 
            //     {id: "volxAxis", data: volChartData.label} // OHLC
            // ,
            series:[
                {
                    id: "vol",
                    data: volChartData.volume,
                }
            ]};

        //动态添加 legend.data
        btMixChart.setOption(volChartOption);
    }

    var updateMAChart = function (maChartData) {
        //动态添加series
        var maChartOption = {
            series:[
            {
                id: "indic1",
                data: maChartData.ma[0].ma10
            },
            {
                id: "indic2",
                // name: 'MA20',
                data: maChartData.ma[0].ma20,
            },
            {
                id: "indic3",
                // name: 'MA60',
                data: maChartData.ma[0].ma60,
            },
            {
                id: "indic4",
                // name: 'MA120',
                data: maChartData.ma[0].ma120,
            },
            {
                id: "indic5",
                // name: 'MA200',
                data: maChartData.ma[0].ma200,
            }]};

        //动态添加 legend.data
        // mixChartOption.legend.data.push('其他');
        btMixChart.setOption(maChartOption);
    }

    var updateEMAChart = function (chartData) {
        //动态添加series
        var emaChartOption = {
            series:[
            {
                id: "indic1",
                name: 'EMA10',
                data: chartData.ema[0].ema10
            },
            {
                id: "indic2",
                name: 'EMA20',
                data: chartData.ema[0].ema20
            },
            {
                id: "indic3",
                name: 'EMA60',
                data: chartData.ema[0].ema60
            },
            {
                id: "indic4",
                name: 'EMA120',
                data: chartData.ema[0].ema120
            },
            {
                id: "indic5",
                name: 'EMA200',
                data: chartData.ema[0].ema200
            }]};

        //动态添加 legend.data
        // mixChartOption.legend.data.push('其他');
        btMixChart.setOption(emaChartOption);
    }

    var updateBOLLChart = function (chartData) {
        //动态添加series
        var bollChartOption = {
            series:[
            {
                id: "indic1",
                name: 'BOLL_UPPER',
                data: chartData.boll[0].upper,
            },
            {
                id: "indic2",
                name: 'BOLL_MID',
                data: chartData.boll[0].mid,
            },
            {
                id: "indic3",
                name: 'BOLL_LOW',
                data: chartData.boll[0].lower,
            },
            {
                id: "indic4",
                data: undefined,
            },
            {
                id: "indic5",
                data: undefined,
            }]};

        //动态添加 legend.data
        // mixChartOption.legend.data.push('其他');
        btMixChart.setOption(bollChartOption);
    }

    var updateBBIChart = function (chartData) {
        //动态添加series
        var bbiChartOption = {
            series:[
            {
                id: "indic1",
                name: 'BBI',
                data: chartData.bbi,
            },
            {
                id: "indic2",
                data: undefined,
            },
            {
                id: "indic3",
                data: undefined,
            },
            {
                id: "indic4",
                data: undefined,
            },
            {
                id: "indic5",
                data: undefined,
            }]};

        //动态添加 legend.data
        // mixChartOption.legend.data.push('其他');
        btMixChart.setOption(bbiChartOption);
    }

    var updateRSIChart = function (chartData) {

        //动态添加series
        var mixChartOption = {
            series: [
            {
                id: "rsi6",
                data: chartData.rsi[0].rsi6,
            },
            {
                id: "rsi12",
                data: chartData.rsi[0].rsi12
            },
            {
                id: "rsi24",
                data: chartData.rsi[0].rsi24
            }
        ]};

        //动态添加 legend.data
        // mixChartOption.legend.data.push('其他');
        btMixChart.setOption(mixChartOption);
    }

    var updateMACDChart = function (chartData) {
        // var chartData = jsonToChartMACDFormat(jsonData);
        //动态添加series
        var macdChartOption = {
            series: [
                {
                    id: "macddif",
                    data: chartData.macd[0].dif
                },
                {
                    id: "macddea",
                    data: chartData.macd[0].dea
                },
                {
                    id: "macdbar",
                    data: chartData.macd[0].bar
                }]};

        //动态添加 legend.data
        // mixChartOption.legend.data.push('其他');
        btMixChart.setOption(macdChartOption);
    }

    var updateKDJChart = function (chartData) {
        // var chartData = jsonToChartKDJFormat(jsonData);

        //动态添加series
        var kdjChartOption = {
            series:[
                {
                    id: "kdjk",
                    data: chartData.kdj[0].k
                },
                {
                    id: "kdjd",
                    data: chartData.kdj[0].d
                },
                {
                    id: "kdjj",
                    data: chartData.kdj[0].j
                }]};

        //动态添加 legend.data
        // mixChartOption.legend.data.push('其他');
        btMixChart.setOption(kdjChartOption);
    }

    var initFundaChartOption = function(fundaChartData) {
        var fundaChartOption = {
            animation: true,
            // legend: {
            //     top: 5,
            //     data: ['MA10','MA20','MA60','MA120','MA200']
            // },
            // tooltip: {
            //     trigger: 'axis',
            //     axisPointer: {
            //         type: 'cross'
            //     },
            //     borderWidth: 1,
            //     borderColor: '#ccc',
            //     padding: 10,
            //     textStyle: {
            //         color: '#000'
            //     },
            //     position: function (pos, params, el, elRect, size) {
            //         const obj = {
            //             top: 10
            //         };
            //         obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 30;
            //         return obj;
            //     }
            //     // extraCssText: 'width: 170px'
            // },
            axisPointer: {
                link: [
                    {
                        xAxisIndex: 'all'
                    }
                ],
                label: {
                    backgroundColor: '#777'
                }
            },
            // toolbox: {
            //     feature: {
            //         dataZoom: {
            //             yAxisIndex: false
            //         },
            //         brush: {
            //             type: ['lineX', 'clear']
            //         }
            //     }
            // },
            brush: {
                xAxisIndex: 'all',
                brushLink: 'all',
                outOfBrush: {
                    colorAlpha: 0.1
                }
            },
            // visualMap: {
            //     show: false,
            //     seriesIndex: 5,
            //     dimension: 2,
            //     pieces: [
            //         {
            //             value: 1,
            //             color: downColor
            //         },
            //         {
            //             value: -1,
            //             color: upColor
            //         }
            //     ]
            // },
            grid: [
                //Fundamental grid index 5, PE
                {left: '4%', top: '5%',height:'15%',width: '42%'},
                //Fundamental grid index 6, PE TTM
                {right: '3%',top: '5%',height:'15%',width: '42%'},

                //Fundamental grid index 7, PB
                {left: '4%', right: '3%',top: '30%',height: '15%'},

                //Fundamental grid index 8, PS
                {left: '4%',top: '55%',height:'15%',width: '42%'},
                //Fundamental grid index 9, PS TTM
                {right: '3%',top: '55%',height:'15%',width: '42%'},
                
                //Fundamental grid index 10, Turnover ratio
                {left: '4%',top: '80%',height: '15%', width: '42%'},
                //Fundamental grid index 11, Vol ratio
                {right: '3%',top: '80%',height: '15%', width: '42%'}
            ],
            xAxis: [
                {gridIndex: 0, data: fundaChartData.label, min: 'dataMin', max: 'dataMax', id:"pexAxis"}, // PE
                {gridIndex: 1, data: fundaChartData.label, min: 'dataMin', max: 'dataMax', id:"pettmxAxis"}, // PE TTM
                {gridIndex: 2, data: fundaChartData.label, min: 'dataMin', max: 'dataMax', id:"pbxAxis"}, // PB
                {gridIndex: 3, data: fundaChartData.label, min: 'dataMin', max: 'dataMax', id:"psxAxis"}, // PS
                {gridIndex: 4, data: fundaChartData.label, min: 'dataMin', max: 'dataMax', id:"psttmxAxis"}, // PS TTM
                {gridIndex: 5, data: fundaChartData.label, min: 'dataMin', max: 'dataMax', id:"turnoverxAxis"}, // TO 换手率 
                {gridIndex: 6, data: fundaChartData.label, min: 'dataMin', max: 'dataMax', id:"volratioxAxis"} // VO 量比 
            ],
            yAxis: [
                {gridIndex: 0, scale: true, min: 'dataMin', max: 'dataMax', name: '市盈率', nameLocation: 'end'}, // PE
                {gridIndex: 1, scale: true, min: 'dataMin', max: 'dataMax', name: '动态市盈率', nameLocation: 'end'}, // PE TTM
                {gridIndex: 2, scale: true, min: 'dataMin', max: 'dataMax', name: '市净率', nameLocation: 'end'}, // PB
                {gridIndex: 3, scale: true, min: 'dataMin', max: 'dataMax', name: '市销率', nameLocation: 'end'}, // PS
                {gridIndex: 4, scale: true, min: 'dataMin', max: 'dataMax', name: '动态市销率', nameLocation: 'end'}, // PS TTM
                {gridIndex: 5, scale: true, min: 'dataMin', max: 'dataMax', name: '换手率', nameLocation: 'end'}, // TO 换手率 
                {gridIndex: 6, scale: true, min: 'dataMin', max: 'dataMax', name: '量比', nameLocation: 'end'} // VO 量比 

                // { scale: true,
                //     splitArea: {
                //         show: true
                //     }
                // },
                // {
                //     scale: true,
                //     gridIndex: 1,
                //     splitNumber: 2,
                //     axisLabel: { show: false },
                //     axisLine: { show: false },
                //     axisTick: { show: false },
                //     splitLine: { show: false }
                // }
            ],
            dataZoom: [
                {
                    type: 'inside',
                    xAxisIndex: [0,1,2,3,4,5,6],
                    start: 0,
                    end: 100
                }
                // ,
                // {
                //     show: true,
                //     xAxisIndex: [0, 1],
                //     type: 'slider',
                //     top: '85%',
                //     start: 0,
                //     end: 100
                // }
            ],
            series: [
                {
                    id: "pe",
                    type: 'line',
                    xAxisIndex: 0,
                    yAxisIndex: 0,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "peL",
                    type: 'line',
                    xAxisIndex: 0,
                    yAxisIndex: 0,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(0, 255, 0)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "peM",
                    type: 'line',
                    xAxisIndex: 0,
                    yAxisIndex: 0,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "peH",
                    type: 'line',
                    xAxisIndex: 0,
                    yAxisIndex: 0,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(255, 0, 0)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "pettm",
                    type: 'line',
                    xAxisIndex: 1,
                    yAxisIndex: 1,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "pettmL",
                    type: 'line',
                    xAxisIndex: 1,
                    yAxisIndex: 1,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(0, 255, 0)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "pettmM",
                    type: 'line',
                    xAxisIndex: 1,
                    yAxisIndex: 1,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "pettmH",
                    type: 'line',
                    xAxisIndex: 1,
                    yAxisIndex: 1,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(255, 0, 0)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "pb",
                    type: 'line',
                    xAxisIndex: 2,
                    yAxisIndex: 2,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "pbL",
                    type: 'line',
                    xAxisIndex: 2,
                    yAxisIndex: 2,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(0, 255, 0)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "pbM",
                    type: 'line',
                    xAxisIndex: 2,
                    yAxisIndex: 2,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "pbH",
                    type: 'line',
                    xAxisIndex: 2,
                    yAxisIndex: 2,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(255, 0, 0)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "ps",
                    type: 'line',
                    xAxisIndex: 3,
                    yAxisIndex: 3,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "psL",
                    type: 'line',
                    xAxisIndex: 3,
                    yAxisIndex: 3,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(0, 255, 0)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "psM",
                    type: 'line',
                    xAxisIndex: 3,
                    yAxisIndex: 3,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "psH",
                    type: 'line',
                    xAxisIndex: 3,
                    yAxisIndex: 3,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(255, 0, 0)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "psttm",
                    type: 'line',
                    xAxisIndex: 4,
                    yAxisIndex: 4,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "psttmL",
                    type: 'line',
                    xAxisIndex: 4,
                    yAxisIndex: 4,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(0, 255, 0)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "psttmM",
                    type: 'line',
                    xAxisIndex: 4,
                    yAxisIndex: 4,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "psttmH",
                    type: 'line',
                    xAxisIndex: 4,
                    yAxisIndex: 4,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(255, 0, 0)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "tr",
                    type: 'line',
                    xAxisIndex: 5,
                    yAxisIndex: 5,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "trL",
                    type: 'line',
                    xAxisIndex: 5,
                    yAxisIndex: 5,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(0, 255, 0)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "trM",
                    type: 'line',
                    xAxisIndex: 5,
                    yAxisIndex: 5,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "trH",
                    type: 'line',
                    xAxisIndex: 5,
                    yAxisIndex: 5,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(255, 0, 0)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "vr",
                    type: 'line',
                    xAxisIndex: 6,
                    yAxisIndex: 6,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "vrL",
                    type: 'line',
                    xAxisIndex: 6,
                    yAxisIndex: 6,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(0, 255, 0)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "vrM",
                    type: 'line',
                    xAxisIndex: 6,
                    yAxisIndex: 6,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                },
                {
                    id: "vrH",
                    type: 'line',
                    xAxisIndex: 6,
                    yAxisIndex: 6,
                    showSymbol: false,
                    smooth: true,
                    itemStyle: {
                        color: 'rgb(255, 0, 0)'
                    },
                    lineStyle: {
                        opacity: 0.5
                    }
                }
            ]
        };
        return fundaChartOption;
    }

    //  http://127.0.0.1:8000/stockmarket/bt-system/000001.SZ/system/
    //    %7B'SMA_10':%2010,'SMA_20':20,'RSI_20':20%7D/%7B'attr':%7B'sma_level':'10','rsi_level':'20'%7D,
    //  'condition':%7B'threshold':%7B'RSI_20':'RSI_20%3E30'%7D,
    //  'crossover':%7B'a10':'cross(a(10),%20a(20))'%7D,'pair_comp':%20%7B'a10':'a(10)%20%3E%20a(20)'%7D%7D%7D/%
    //   7B'attr':%7B'sma_level':'10','rsi_level':'90'%7D,'condition':%7B'threshold':%7B'RSI_20':'RSI_20%3E90'%7D,
    //  'crossover':%7B'a20':'cross(a(20),%20a(10))'%7D,'pair_comp':%20%7B'a10':'a(20)%20%3E%20a(10)'%7D%7D%7D/.95/10000/.001/1/D/

    var updateEquityChart = function (equityChartData) {
        //添加series
        // mixChartOption.series.slice(7,1);
        var equityOption = 
        {
            series: [
                {
                    id: 'equity',
                    data: equityChartData,
                }
            ]
        }

        btMixChart.setOption(equityOption);
    }

    var updateTradesChart = function (tradeChartData) {
        //添加series
        // mixChartOption.series.slice(7,1);
        var ohlcDateLabel = ohlcChartData.label;
        var ohlc = ohlcChartData.ohlc;
        var markData = [];
        var tooltipsData = [];

        $(tradeChartData).each(function(idx, tradeObj){
            if(tradeObj[0]!=null){
                var indexTradeDate = ohlcDateLabel.indexOf(tradeObj[5]);
                if(tradeObj[0]=="b"){
                    markData.push(
                        {
                            coord: [tradeObj[5], ohlc[indexTradeDate][2]],
                            value: "b",
                            symbol: "pin",
                            symbolSize: 25,
                            symbolRotate: 180,
                            itemStyle: {
                              //设置标记点的样式
                              normal: { color: "red" },
                            },
                        }
                    );
                }
                if(tradeObj[0]=="s"){
                    markData.push(
                        {
                            coord: [tradeObj[5], ohlc[indexTradeDate][3]],
                            value: "s",
                            symbol: "pin",
                            symbolSize: 25,
                            // symbolRotate: 180,
                            itemStyle: {
                              //设置标记点的样式
                              normal: { color: "green" },
                            },
                        }
                    );
                }
                if(tradeObj[0]=="b&s"){
                    markData.push(
                        [{
                            coord: [tradeObj[5], ohlc[indexTradeDate][2]],
                            value: "b",
                            symbol: "pin",
                            symbolRotate: 180,
                            symbolSize: 25,
                            itemStyle: {
                              //设置标记点的样式
                              normal: { color: "red" },
                            },
                        },
                        {
                            coord: [tradeObj[5], ohlc[indexTradeDate][3]],
                            value: "s",
                            symbol: "pin",
                            symbolSize: 25,
                            itemStyle: {
                              //设置标记点的样式
                              normal: { color: "green" },
                            },
                        }]
                    );
                }
            }
        });

        // $(ohlcChartData).each(function(id, ohlcObj){
        //     $(tradeChartData).each(function(idx, tradeObj){
        //         $(ohlcObj.label).each(function(idd, ohlcObjLabel){
        //             if(ohlcObjLabel == tradeObj[5]){
        //                 if(tradeObj[0]!=null){
        //                     if(tradeObj[0]=="b"){
        //                         markData.push(
        //                             {
        //                                 coord: [ohlcObjLabel, ohlcObj.ohlc[2]],
        //                                 value: "b",
        //                                 symbol: "triangle",
        //                                 // symbolSize: 20,
        //                                 symbolRotate: 180,
        //                                 itemStyle: {
        //                                   //设置标记点的样式
        //                                   normal: { color: "red" },
        //                                 },
        //                             }
        //                         );
        //                     }
        //                     if(tradeObj[0]=="s"){
        //                         markData.push(
        //                             {
        //                                 coord: [ohlcObjLabel, ohlcObj.ohlc[3]],
        //                                 value: "s",
        //                                 symbol: "triangle",
        //                                 symbolSize: 20,
        //                                 symbolRotate: 180,
        //                                 itemStyle: {
        //                                   //设置标记点的样式
        //                                   normal: { color: "green" },
        //                                 },
        //                             }
        //                         );
        //                     }
        //                     if(tradeObj[0]=="b&s"){
        //                         markData.push(
        //                             [{
        //                                 coord: [ohlcObjLabel, ohlcObj.ohlc[2]],
        //                                 value: "b",
        //                                 symbol: "triangle",
        //                                 symbolRotate: 180,
        //                                 // symbolSize: 20,
        //                                 itemStyle: {
        //                                   //设置标记点的样式
        //                                   normal: { color: "red" },
        //                                 },
        //                             },
        //                             {
        //                                 coord: [ohlcObjLabel, ohlcObj.ohlc[3]],
        //                                 value: "s",
        //                                 symbol: "triangle",
        //                                 // symbolSize: 20,
        //                                 itemStyle: {
        //                                   //设置标记点的样式
        //                                   normal: { color: "green" },
        //                                 },
        //                             }]
        //                         );
        //                     }
        //                 }
        //             } 
        //         });
                
        //     });
        // });
        

        var tradeOption = 
        {
            series: [
                {
                    id: 'ohlc',
                    // tooltip:{

                    // } ,
                    markPoint:{
                        data: markData,
                    }
                }
            ]
        }

        btMixChart.setOption(tradeOption);
    }

    const fundaList = [ 'pe','pettm','pb','ps','psttm','vr','tr' ];

    var updateFundaChart = function (tsCode, startDate, endDate) {
        $.ajax({
            url: stockmarketEndpoint + "daily-basic-history/" + tsCode + "/" + startDate + "/" + endDate + "/?format=json",
            success: function (data) {
                var chartData = jsonToFundaChartFormat(data);
                
                var option = initFundaChartOption(chartData);
                btFundamentalChart.setOption(option);

                $(fundaList).each(function (idx, obj) {
                    addFundaSeriesData(obj, chartData[obj]);
                });
            },
            statusCode: {
                403: function () {
                    console.info(403);
                },
                404: function () {
                    console.info(404);
                },
                500: function () {
                    console.info(500);
                }
            }
        });
    }

    var addFundaSeriesData = function (fundaId, fundaData) {
        var fundaQuantile = getQuantileOfArray(fundaData);
        // var chartCanvas = echarts.init(canvas);

        //动态添加series
        var mixChartOption = 
            {
                series:[
                {
                    id: fundaId,
                    data: fundaData
                },
                {
                    id: fundaId + "L",
                    data: fundaQuantile.qt10
                },
                {
                    id: fundaId + "M",
                    data: fundaQuantile.qt50
                },
                {
                    id: fundaId + 'H',
                    data: fundaQuantile.qt90
                }]
            };

        btFundamentalChart.setOption(mixChartOption);
    }

    $('#searchText').autoComplete({
        resolver: 'custom',
        // preventEnter: true,
        formatResult: function (item) {
            return {
                value: item.stock_code,
                text: item.stock_code + " - " + item.stock_name,
                html: [
                    item.stock_code + " - " + item.stock_name + "[" + item.market + "], " + item.area + ", " + item.industry + ", " + item.list_date + "上市",
                ]
            };
        },
        events: {
            search: function (qry, callback) {
                // let's do a custom ajax call
                $.ajax(
                    stockmarketEndpoint + 'companies/' + $('#searchText').val() + "/?format=json",
                ).done(function (companies) {
                    callback(companies)
                });
            }
        }
    });

    $('#searchText').on('autocomplete.select', function (evt, item) {
        console.log('select');
        tsCodeNoSfx = item.stock_code;
        tsCode = item.ts_code;
        stockName = item.stock_name;
        market = item.market;
        $("#searchText").val(item.ts_code);
        $("#hiddenTscode").val(item.ts_code);
        // $("#ind").text(item.industry);
        $(".stock_name").each(function (idx, obj) {
            $(obj).text(item.stock_name + " [" + tsCode + "]");
        });

        equityJsonData = undefined;
        ohlcChartData = undefined;

        updateBTMixChart(tsCode);
        // updateTechIndicatorChart();
    });

    var setupStrategyCategories = function (strategyCategory) {
        var strategyCategories = $(strategyCategory + " div");
        // curIndicator e.g. ["SMA","0","1","2"]
        $.each(strategyCategories.children(), function (index, value) {
            $(value).removeClass("disabled");
            if ($.inArray(index.toString(), curIndicator) == -1) {
                $(value).addClass("disabled");
            }
        });

    }

    var onIndicatorChange = function () {
        // alert($(this).val());
        curIndicator = $(this).val().split(",");

        setupStrategyCategories("#bStrategyCategory");
        setupStrategyCategories("#sStrategyCategory");

        // showIndicatorChart(indic);
        updateTechIndicatorChart();
    }

    // 无服务器端数据更新情况下，只是更改技术指标
    var updateTechIndicatorChart = function(){
        if(curIndicator[0]=="EMA"){
            updateEMAChart(ohlcChartData);
        }
        if(curIndicator[0]=="SMA"){
            updateMAChart(ohlcChartData);
        }
        if(curIndicator[0]=="BOLL"){
            updateBOLLChart(ohlcChartData);
        }
        if(curIndicator[0]=="BBI"){
            updateBBIChart(ohlcChartData);
        }
    }

    var updateBTStatsPanel = function(btStatData){
        $(btStatData[0].stats).each(function(idx, obj){
            for(var k in obj){
                $("#"+k).after("<span class='ml-1 tex-muted font-weight-bold'>"+obj[k]+"</span>");
            }
        });
    }

    var onPresetOptChange = function (event) {
        $(event.data.target).val($(this).val());
        if (event.data.type == "capital") {
            capital = $(this).val();
        } else if (event.data.type == "stoploss") {
            stoploss = $(this).val();
        }
    }

    $('input:radio[name="indicator"]').change(onIndicatorChange);

    $('input:radio[name="capital-option"]').change({ target: "#capital", type: "capital" }, onPresetOptChange);

    $('input:radio[name="sl-option"]').change({ target: "#stoploss", type: "stoploss" }, onPresetOptChange);

    $('input:radio[name="commission-unit"]').change(function () {
        var unit = $(this).val();
        var commissionOpt = $('input:radio[name="commission"]:checked').val();

        if (unit == "tth") {
            commission = parseInt(commissionOpt) / 10000;
        } else {
            commission = parseInt(commissionOpt) / 1000;
        }
    });

    $('input:radio[name="commission"]').change(function () {
        var unit = $('input:radio[name="commission-unit"]:checked').val();
        var commissionOpt = $(this).val();

        if (unit == "tth") {
            commission = parseInt(commissionOpt) / 10000;
        } else {
            commission = parseInt(commissionOpt) / 1000;
        }
    });

    $('input:radio[name="trade-on-close"]').change(function () {
        tradeOnClose = $(this).val();
    });

    $('input:radio[name="restoration"]').change(function () {
        restoration = $(this).val();
    });

    $('input:radio[name="freq"]').change(function () {
        freq = $(this).val();
        // initializeBTMixChart(tsCode);
        updateBTMixChart(tsCode);
        updateFundaChart(tsCode, startDate, endDate);
    });

    $('input:radio[name="period"]').change(function () {
        stockHistPeriod = $(this).val();
        startDate = formatDate(new Date(today.getTime() - (365 * stockHistPeriod * 24 * 60 * 60 * 1000)), "");
        // initializeBTMixChart(tsCode);
        updateBTMixChart(tsCode);
        updateFundaChart(tsCode, startDate, endDate);

        // if(equityJsonData != undefined){
        //     var resampledEquityData = resampleEquity(equityJsonData, ohlcChartData.label);
        //     var resampledTradesData = resampleTrades(equityJsonData, ohlcChartData.label);
        //     // resampledTradesData = resampleTrades(equityJsonData, fundaChartData.label);
        //     updateEquityChart(resampledEquityData);
        //     updateTradesChart(resampledTradesData);
        // }
    });

    /**** 
    var pushBCondition = function () {
        taIndicatorType = $("#bStrategyCategory").val();
        // buy_condition: map
        // "{
        //     'attr':{'sma_level':'10','rsi_level':'20'},
        //     'condition':
        //     {
        //         'threshold':{'RSI_20':'self.RSI_20[-1]>30'},
        //         'crossover':{'a10':'crossover(self.SMA_10, self.SMA_20)'},
        //         'pair_comp': {'a10':'self.SMA_10[-1] > self.SMA_20[-1]'}
        //     }
        // }"
        // alert("hello");
        // type 0
        if (taIndicatorType == INDIC_CROSSOVER) {
            if ($("#bCondition").tex() == "上穿") {
                // let condition = new Map();
                bCrossoverSet.add("crossover(self." + $("#bTechIndicator1").val() + ",self." + $("#bTechIndicator2").val() + ")");
                // let crossover = new Map();
                // conditionItem.set("crossover", condition)
            }

            if ($("#bCondition").tex() == "下穿") {
                // let condition = new Map();
                bCrossoverSet.add("crossover(self." + $("#bTechIndicator2").val() + ",self." + $("#bTechIndicator1").val() + ")");
                // let crossover = new Map();
                // conditionItem.set("crossover", condition)
            }

            taIndicatorSet.add($("#bTechIndicator1").val());
            taIndicatorSet.add($("#bTechIndicator2").val());
        }

        if (taIndicatorType == INDIC_PAIR_COMP) {
            // let condition = new Map();
            bPairCompareSet.add("self." + $("#bTechIndicator1").val() + $("#bCondition").val() + "self." + $("#bTechIndicator2").val());
            // let pairComp = new Map();
            // conditionItem.set("pair_comp", condition)
            taIndicatorSet.add($("#bTechIndicator1").val());
            taIndicatorSet.add($("#bTechIndicator2").val());
        }

        if (taIndicatorType == INDIC_THRESHOLD) {
            // let condition = new Map();
            bThresholdSet.add("self." + $("#bTechIndicator1").val() + $("#bCondition").val() + "self." + $("#bTechIndicator2").val());
            taIndicatorSet.add($("#bTechIndicator1").val());
            // taIndicators.add($("#bTechIndicator1").val() + "_" + $("#bTechIndicator2").val());
            // let pairComp = new Map();
            // conditionItem.set("threshhold", condition)
        }

        // buyConditionDict.set("condition", conditionItem);   // a string key
        // buyConditionDict.set("attr", 'str1');   // a string key
    }

    var pushSellCondition = function () {
        // sell_condition
        // "{
        //     'attr':{'sma_level':'10','rsi_level':'90'},
        //     'condition':{
        //         'threshold':{'RSI_20':'self.RSI_20[-1]>90'}, type - 0
        //         'crossover':{'a20':'crossover(self.SMA_20, self.SMA_10)'}, type - 1
        //         'pair_comp': {'a10':'self.SMA_20[-1] > self.SMA_10[-1]'}, type - 2
        //     }
        // }"
    }

    var buildBuyCondition = function () {
        // ta_indicator:
        // "{'SMA_10': 10,'SMA_20':20,'RSI_20':20}"
        var count = 0;
        taIndicator += "{";
        for (let value of taIndicatorSet) {
            var techIndic = value.split("_")[0];
            var techIndicParam = value.split("_")[1];
            taIndicator += techIndic + ":" + techIndicParam;
            count++;
            if (count < taIndicator.size) {
                taIndicator += ",";
            } else {
                taIndicator += "}";
            }
        }
        // buy_condition: map
        // "{
        //     'attr':{'sma_level':'10','rsi_level':'20'},
        //     'condition':
        //     {
        //         'threshold':{'RSI_20':'self.RSI_20[-1]>30'},
        //         'crossover':{'a10':'crossover(self.SMA_10, self.SMA_20)'},
        //         'pair_comp': {'a10':'self.SMA_10[-1] > self.SMA_20[-1]'}
        //     }
        // }"
        var thresholdKey = "threshold:{";
        var crossoverKey = "crossover:{";
        var pairCompKey = "pair_comp:{";

        buyCondition += "{";

        count = 0;
        for (let value of bCrossoverSet) {
            crossoverKey += count.toString() + ":" + value;
            count++;
            if (count < bCrossoverSet.size) {
                crossoverKey += ",";
            } else {
                crossoverKey += "}";
            }
        }

        count = 0;
        for (let value of bThresholdSet) {
            thresholdKey += count.toString() + ":" + value;
            count++;
            if (count < bThresholdSet.size) {
                thresholdKey += ",";
            } else {
                thresholdKey += "}";
            }
        }

        count = 0;
        for (let value of bPairCompareSet) {
            pairCompKey += count.toString() + ":" + value;
            count++;
            if (count < bPairCompareSet.size) {
                pairCompKey += ",";
            } else {
                pairCompKey += "}";
            }
        }

        buyCondition += crossoverKey + ",";
        buyCondition += thresholdKey + ",";
        buyCondition += pairCompKey;
        buyCondition += "}";
    }
    *******/

    var buildTAIndicator = function () {
        var count = 0;
        var taIndicatorSet = new Set();
        for(let b of taBIndicatorSet){
            taIndicatorSet.add(b);
        }
        for(let s of taSIndicatorSet){
            taIndicatorSet.add(s);
        }

        taIndicator = "";
        taIndicator += "{";
        for (let indic of taIndicatorSet) {
            // var techIndic = indic.split("_")[0];
            var techIndicParam = indic.split("_")[1];
            if(techIndicParam == undefined || techIndicParam == "BBI") techIndicParam = -1;
            taIndicator += "'" + indic + "':" + techIndicParam;
            count++;
            if (count < taIndicatorSet.size) {
                taIndicator += ",";
            } else {
                taIndicator += "}";
            }
        }
    }

    var buildBStrategy = function () {
        // buy_condition: map
        // "{
        //     'attr':{'sma_level':'10','rsi_level':'20'},
        //     'condition':
        //     {
        //         'threshold':{'RSI_20':'self.RSI_20[-1]>30'},
        //         'crossover':{'a10':'crossover(self.SMA_10, self.SMA_20)'},
        //         'pair_comp': {'a10':'self.SMA_10[-1] > self.SMA_20[-1]'}
        //     }
        // }"
        // generted value
        // {
        //     'attr':{'level':0},
        //     'condition':{
        //         'crossver':{'0':'crossover(self.SMA_10,self.SMA_20)'},
        //         'pair_comp':{},
        //         'threshold':{}
        //     }
        // }
        var bCrossover = "'crossver':{";
        var bPairComp = "'pair_comp':{";
        var bThreshold = "'threshold':{";
        var bClose = "'close':{";

        bSystem = "";
        bSystem += "{'attr':{'level':0},'condition':{";

        $.each($("#bStrategyList").children(), function (index, value) {
            var bStrategy = $(value).children()[2].value;
            if (bStrategy.split(":")[0] == "0") {
                bCrossover += "'" + index.toString() + "':'" + bStrategy.split(":")[1] + "',";
            } else if (bStrategy.split(":")[0] == "1") {
                bPairComp += "'" + index.toString() + "':'" + bStrategy.split(":")[1] + "',";
            } else if (bStrategy.split(":")[0] == "2") {
                bThreshold += "'" + index.toString() + "':'" + bStrategy.split(":")[1] + "',";
            } else if (bStrategy.split(":")[0] == "3") {
                bClose += "'" + index.toString() + "':'" + bStrategy.split(":")[1] + "',";
            }

            if (index == $("#bStrategyList").children().length - 1) {
                bCrossover += "},";
                bPairComp += "},";
                bThreshold += "},";
                bClose += "}";
                bSystem += bCrossover + bPairComp + bThreshold + bClose + "}}";
            }
        });


        // executeBT();
    }

    var buildSStrategy = function () {
        // buy_condition: map
        // generted value
        // {
        //     'attr':{'level':0},
        //     'condition':{
        //         'crossver':{'0':'crossover(self.SMA_10,self.SMA_20)'},
        //         'pair_comp':{},
        //         'threshold':{}
        //     }
        // }
        // var sSystem = "";
        var sCrossover = "'crossver':{";
        var sPairComp = "'pair_comp':{";
        var sThreshold = "'threshold':{";
        var sClose = "'close':{";

        sSystem = "";
        sSystem += "{'attr':{'level':0},'condition':{";

        $.each($("#sStrategyList").children(), function (index, value) {
            var sStrategy = $(value).children()[2].value;
            if (sStrategy.split(":")[0] == "0") {
                sCrossover += "'" + index.toString() + "':'" + sStrategy.split(":")[1] + "',";
            } else if (sStrategy.split(":")[0] == "1") {
                sPairComp += "'" + index.toString() + "':'" + sStrategy.split(":")[1] + "',";
            } else if (sStrategy.split(":")[0] == "2") {
                sThreshold += "'" + index.toString() + "':'" + sStrategy.split(":")[1] + "',";
            } else if (sStrategy.split(":")[0] == "3") {
                sClose += "'" + index.toString() + "':'" + sStrategy.split(":")[1] + "',";
            }

            if (index == $("#sStrategyList").children().length - 1) {
                sCrossover += "},";
                sPairComp += "},";
                sThreshold += "},";
                sClose += "}";

                sSystem += sCrossover + sPairComp + sThreshold + sClose + "}}";
            }
        });


        // executeBT();
    }

    var isEmptyStrategySet = function() {
        if(taBIndicatorSet.size==0 || taSIndicatorSet.size==0) return true;
        return false; 
    }

    var executeBT = function () {
        if(isEmptyStrategySet()) return;

        capital = $("#capital").val();
        stoploss = (100 - parseInt($("#stoploss").val()))/100;

        $.ajax({
            url: stockmarketEndpoint + "bt-system/" + tsCode + "/" + strategyCategory + "/" + taIndicator +
                "/" + bSystem + "/" + sSystem + "/" + stoploss.toString() + "/" + capital.toString() + "/" + commission.toString() +
                "/" + leverage.toString() + "/" + tradeOnClose.toString() + "/" + freq + "/",
            success: function (data) {
                // console.log(data)
                // 全局equity json
                equityJsonData = jsonToBTResultFormat(data);
                var resampledEquityData = resampleEquity(equityJsonData, ohlcChartData.label);
                var resampledTradesData = resampleTrades(equityJsonData, ohlcChartData.label);
                // resampledTradesData = resampleTrades(equityJsonData, fundaChartData.label);
                updateEquityChart(resampledEquityData);
                updateTradesChart(resampledTradesData);
                updateBTStatsPanel(data.slice(-1));
            }
        });
    }

    var getIndicatorFrom = function(param){
        var indic = "";
        var prefix = param.split("_");

        if(typeAParam.includes(prefix[0])){
            indic = param;
        } else if(typeBParam.includes(prefix[0])){
            indic = prefix[0]
        }
        return indic;
    }

    $("#addBStrategy").click(function () {
        var newItem = "";
        var bStrategyText = ""; //$("#bTIPicked1").text() + " " + $("#bCondPicked").text() + " " + $("#bTIPicked2").text();
        var bStrategyValue = "";

        if ($("#hiddenStrategyCategory").val() == "") return;

        if ($("#hiddenStrategyCategory").val() == "0") { //crossover，KDJ, MACD (Not Bar), RSI, crossover(self.KDJ_K, self.KDJ_D), crossover(self.MACD.DEA, MACD_DIFF)
            bStrategyText = $("#bTIPicked1").text() + " " + $("#bCondPicked").text() + " " + $("#bTIPicked2").text();
            bStrategyValue = "0:" + $("#hiddenBCond").val() + "(self." + $("#hiddenBTI1").val() + "," + "self." + $("#hiddenBTI2").val() + ")";

            taBIndicatorSet.add(getIndicatorFrom($("#hiddenBTI1").val()));
            taBIndicatorSet.add(getIndicatorFrom($("#hiddenBTI2").val()));
        } else if ($("#hiddenStrategyCategory").val() == "1") {//tech indicator pair compare, SMA, EMA, KDJ, MACD, RSI, 
            bStrategyText = $("#bTIPicked1").text() + " " + $("#bCondPicked").text() + " " + $("#bTIPicked2").text();
            bStrategyValue = "1:self." + $("#hiddenBTI1").val() + "[-1]" + $("#hiddenBCond").val() + "self." + $("#hiddenBTI2").val() + "[-1]";

            taBIndicatorSet.add(getIndicatorFrom($("#hiddenBTI1").val()));
            taBIndicatorSet.add(getIndicatorFrom($("#hiddenBTI2").val()));
        } else if ($("#hiddenStrategyCategory").val() == "2") {//tech indicator value threshold, KDJ, MACD, RSI, 
            bStrategyText = $("#bTIPicked1").text() + " " + $("#bCondPicked").text() + " " + $("#bTIPicked2").text();
            bStrategyValue = "2:self." + $("#hiddenBTI1").val() + "[-1]" + $("#hiddenBCond").val() + $("#hiddenBTI2").val();

            taBIndicatorSet.add(getIndicatorFrom($("#hiddenBTI1").val()));
        } else if ($("#hiddenStrategyCategory").val() == "3") {//OHLC - close ta compare,  SMA, EMA, BOLL, BBI 
            bStrategyText = $("#bTIPicked1").text() + " " + $("#bCondPicked").text() + " " + $("#bTIPicked2").text();
            bStrategyValue = "3:self.data." + $("#hiddenBTI1").val() + "[-1]" + $("#hiddenBCond").val() + "self." + $("#hiddenBTI2").val() + "[-1]";

            // 收盘价不需要加到TA set
            taBIndicatorSet.add(getIndicatorFrom($("#hiddenBTI2").val()));
        }

        if (!bStrategyTextSet.has(bStrategyText)) {
            bStrategyCount++;
            newItem += "<div class='col-lg-8 d-flex justify-content-between align-items-center'>" +
                "<span class='text-primary small'>" + bStrategyText + "</span>" +
                "<a class='badge rounded-pill' href='javascript:void(0)' id='bRM" + bStrategyCount + "'>x</a>" +
                "<input type='hidden' value='" + bStrategyValue + "'>" +
                "</div>";

            $("#bStrategyList").append(newItem);
            $("#bRM" + bStrategyCount).on("click", { strategyText: bStrategyText, holder: $("#bStrategyCount"), indic1: $("#hiddenBTI1").val(), indic2: $("#hiddenBTI2").val()}, function (event) {
                bStrategyCount--;
                bStrategyTextSet.delete(bStrategyText);
                
                if(event.data.indic1!=""){
                    if(typeAParam.includes(event.data.indic1.split("_")[0])){
                        taBIndicatorSet.delete(event.data.indic1);
                    }else if(typeBParam.includes(event.data.indic1.split("_")[0])){
                        taBIndicatorSet.delete(event.data.indic1.split("_")[0]);
                    }
                }
                if(event.data.indic2!=""){
                    if(typeAParam.includes(event.data.indic2.split("_")[0])){
                        taBIndicatorSet.delete(event.data.indic2);
                    }else if(typeBParam.includes(event.data.indic2.split("_")[0])){
                        taBIndicatorSet.delete(event.data.indic2.split("_")[0]);
                    }
                }
                event.data.holder.text(bStrategyCount.toString());
                $(this).parent().remove();
            });
            $("#bStrategyCount").text(bStrategyCount.toString());
            bStrategyTextSet.add(bStrategyText);
            $("#bMsg").text("");
        } else {
            $("#bMsg").text("勿重复添加");
            $("#bMsg").addClass("text-warning");
        }
    });

    $("#addSStrategy").click(function () {
        var newItem = "";
        var sStrategyText = ""; //$("#bTIPicked1").text() + " " + $("#bCondPicked").text() + " " + $("#bTIPicked2").text();
        var sStrategyValue = "";

        if ($("#hiddenSStrategyCategory").val() == "") return;

        if ($("#hiddenSStrategyCategory").val() == "0") { //crossover
            sStrategyText = $("#sTIPicked1").text() + " " + $("#sCondPicked").text() + " " + $("#sTIPicked2").text();
            sStrategyValue = "0:" + $("#hiddenSCond").val() + "(self." + $("#hiddenSTI2").val() + "," + "self." + $("#hiddenSTI1").val() + ")";

            taSIndicatorSet.add(getIndicatorFrom($("#hiddenSTI1").val()));
            taSIndicatorSet.add(getIndicatorFrom($("#hiddenSTI2").val()));
        } else if ($("#hiddenSStrategyCategory").val() == "1") {//tech indicator pair compare
            sStrategyText = $("#sTIPicked1").text() + " " + $("#sCondPicked").text() + " " + $("#sTIPicked2").text();
            sStrategyValue = "1:self." + $("#hiddenSTI1").val() + "[-1]" + $("#hiddenSCond").val() + "self." + $("#hiddenSTI2").val() + "[-1]";

            taSIndicatorSet.add(getIndicatorFrom($("#hiddenSTI1").val()));
            taSIndicatorSet.add(getIndicatorFrom($("#hiddenSTI2").val()));
        } else if ($("#hiddenSStrategyCategory").val() == "2") {//tech indicator value threshold
            sStrategyText = $("#sTIPicked1").text() + " " + $("#sCondPicked").text() + " " + $("#sTIPicked2").text();
            sStrategyValue = "2:self." + $("#hiddenSTI1").val() + "[-1]" + $("#hiddenSCond").val() + $("#hiddenSTI2").val();

            taSIndicatorSet.add(getIndicatorFrom($("#hiddenSTI1").val()));
        } else if ($("#hiddenSStrategyCategory").val() == "3") {//Close indicator value threshold
            sStrategyText = $("#sTIPicked1").text() + " " + $("#sCondPicked").text() + " " + $("#sTIPicked2").text();
            sStrategyValue = "3:self.data." + $("#hiddenSTI1").val() + "[-1]" + $("#hiddenSCond").val() + "self." + $("#hiddenSTI2").val() + "[-1]";

            taSIndicatorSet.add(getIndicatorFrom($("#hiddenSTI2").val()));
        }

        if (!sStrategyTextSet.has(sStrategyText)) {
            sStrategyCount++;
            // strategyCount[1]++;
            newItem += "<div class='col-lg-8 d-flex justify-content-between align-items-center'>" +
                "<span class='text-primary small'>" + sStrategyText + "</span>" +
                "<a href='javascript:void(0)' id='sRM" + sStrategyCount + "'>x</a>" +
                "<input type='hidden' value='" + sStrategyValue + "'>" +
                "</div>";
            $("#sStrategyList").append(newItem);
            // $("#sStrategyList div a").on("click", {count: sStrategyCount, holder: $("#sStrategyCount")}, removeElement)
            $("#sRM" + sStrategyCount).on("click", { strategyText: sStrategyText, holder: $("#sStrategyCount"), indic1: $("#hiddenSTI1").val(), indic2: $("#hiddenSTI2").val() }, function (event) {
                sStrategyCount--;
                sStrategyTextSet.delete(sStrategyText);
                if(event.data.indic1!=""){
                    if(typeAParam.includes(event.data.indic1.split("_")[0])){
                        taSIndicatorSet.delete(event.data.indic1);
                    }else if(typeBParam.includes(event.data.indic1.split("_")[0])){
                        taSIndicatorSet.delete(event.data.indic1.split("_")[0]);
                    }
                }
                if(event.data.indic2!=""){
                    if(typeAParam.includes(event.data.indic2.split("_")[0])){
                        taSIndicatorSet.delete(event.data.indic2);
                    }else if(typeBParam.includes(event.data.indic2.split("_")[0])){
                        taSIndicatorSet.delete(event.data.indic2.split("_")[0]);
                    }
                }
                event.data.holder.text(sStrategyCount.toString());
                $(this).parent().remove();
            });
            // $("#sStrategyCount").text(strategyCount[1].toString());
            $("#sStrategyCount").text(sStrategyCount.toString());
            sStrategyTextSet.add(sStrategyText);
            $("#sMsg").text("");
        } else {
            $("#sMsg").text("勿重复添加");
            $("#sMsg").addClass("text-warning");
        }
    });

    var setupStrategyParam = function (strategyCategory, indicHolderArry, indicPickedHolderArray) {
        var indic = curIndicator[0];
        $(indicHolderArry[0] + " div")[0].innerHTML = ""; // 指标1
        $(indicHolderArry[1] + " div")[0].innerHTML = ""; // 指标2
        $(indicHolderArry[2] + " div")[0].innerHTML = ""; // 判断条件
        $(indicPickedHolderArray[0][0]).text("参数1");
        $(indicPickedHolderArray[0][1]).val("");
        $(indicPickedHolderArray[1][0]).text("参数2");
        $(indicPickedHolderArray[1][1]).val("");
        $(indicPickedHolderArray[2][0]).text("判断条件");
        $(indicPickedHolderArray[2][1]).text("");

        switch (strategyCategory) {
            case "0": // crossover
                $.each(condParamCrossover, function (idx, value) {
                    $(indicHolderArry[2] + " div").append("<a class='dropdown-item' href='javascript:void(0)' value='" + value.split(",")[1] + "'>" + value.split(",")[0] + "</a>")
                });
                break;
            case "1": // two indicator
            case "2": // indicator & value
            case "3": // close & value
                $.each(condParamValueCompare, function (idx, value) {
                    $(indicHolderArry[2] + " div").append("<a class='dropdown-item' href='javascript:void(0)' value='" + value.split(",")[1] + "'>" + value.split(",")[0] + "</a>")
                });
                break;
        }
        $.each($(indicHolderArry[2] + " div a"), function (idx, value) {
            $(value).on("click", { txtHolder: indicPickedHolderArray[2][0], vHolder: indicPickedHolderArray[2][1] }, strategyMenuItemClick);
        });

        switch (strategyCategory) {
            case "0": // crossover
            case "1": // two indicator
                $.each(indicaMap.get(indic), function (idx, value) {
                    $(indicHolderArry[0] + " div").append("<a class='dropdown-item' href='javascript:void(0)' value='" + indic + "_" + value + "'>" + indic + "(" + value + ")</a>");
                    $(indicHolderArry[1] + " div").append("<a class='dropdown-item' href='javascript:void(0)' value='" + indic + "_" + value + "'>" + indic + "(" + value + ")</a>");
                });
                $(indicHolderArry[0] + " div").append("<div class='dropdown-divider'</div>");
                $(indicHolderArry[1] + " div").append("<div class='dropdown-divider'</div>");
                $(indicHolderArry[0] + " div").append("<input type='number' step='5' class='dropdown-item form-control form-control-sm border-danger' placeholder='自定义周期' autocomplete='off' name='indicator_value'/>");
                $(indicHolderArry[1] + " div").append("<input type='number' step='5' class='dropdown-item form-control form-control-sm border-danger' placeholder='自定义周期' autocomplete='off' name='indicator_value'/>");

                $.each($(indicHolderArry[0] + " div input"), function (idx, value) {
                    $(value).on("blur", { type: 0, txtHolder: indicPickedHolderArray[0][0], vHolder: indicPickedHolderArray[0][1] }, strategyValueInputOnchange);
                });

                $.each($(indicHolderArry[1] + " div input"), function (idx, value) {
                    $(value).on("blur", { type: 0, txtHolder: indicPickedHolderArray[1][0], vHolder: indicPickedHolderArray[1][1] }, strategyValueInputOnchange);
                });
                break;
            case "2": // indicator & value
                $.each(indicaMap.get(indic), function (idx, value) {
                    $(indicHolderArry[0] + " div").append("<a class='dropdown-item' href='javascript:void(0)' value='" + indic + "_" + value + "'>" + indic + "(" + value + ")</a>")
                    // $(indicHolder2 + " div").append("<a class='dropdown-item' value='"+indic+"_"+value+"'>"+indic+"("+value+")</a>")
                });
                $(indicHolderArry[0] + " div").append("<div class='dropdown-divider'</div>");
                $(indicHolderArry[0] + " div").append("<input type='number' step='5' class='dropdown-item form-control form-control-sm border-danger' placeholder='自定义周期' autocomplete='off' name='indicator_value'/>");
                $(indicHolderArry[1] + " div").append("<input type='number' step='5' class='dropdown-item form-control form-control-sm border-danger' placeholder='自定义值' autocomplete='off' name='indicator_value'/>");
                // $(indicHolder2 + " div").append("<div class='dropdown-divider' value='" + indic + "_" + value + "'>" + indic + "(" + value + ")</div>");

                // type 0 - 指标(周期), type 1 - 值
                $.each($(indicHolderArry[0] + " div input"), function (idx, value) {
                    $(value).on("blur", { type: 0, txtHolder: indicPickedHolderArray[0][0], vHolder: indicPickedHolderArray[0][1] }, strategyValueInputOnchange);
                });

                $.each($(indicHolderArry[1] + " div input"), function (idx, value) {
                    $(value).on("blur", { type: 1, txtHolder: indicPickedHolderArray[1][0], vHolder: indicPickedHolderArray[1][1] }, strategyValueInputOnchange);
                });
                break;
            case "3": // close & value
                $.each(indicatorParamOHLC, function (idx, value) {
                    $(indicHolderArry[0] + " div").append("<a class='dropdown-item' href='javascript:void(0)' value='" + value.split(",")[1] + "'>" + value.split(",")[0] + "</a>");
                });

                $.each(indicaMap.get(indic), function (idx, value) {
                    // $(indicHolderArry[0] + " div").append("<a class='dropdown-item' href='javascript:void(0)' value='" + indic + "_" + value + "'>" + indic + "(" + value + ")</a>");
                    $(indicHolderArry[1] + " div").append("<a class='dropdown-item' href='javascript:void(0)' value='" + indic + "_" + value + "'>" + indic + "(" + value + ")</a>");
                });
                // $(indicHolder1 + " div").append("<div class='dropdown-divider' value='" + indic + "_" + value + "'>" + indic + "(" + value + ")</div>");
                // $(indicHolder1 + " div").append("<input class='dropdown-item form-control form-control-sm border-danger' placeholder='自定义' autocomplete='off' name='indicator_value'/>");
                // $(indicHolder2 + " div").append("<div class='dropdown-divider' value='" + indic + "_" + value + "'>" + indic + "(" + value + ")</div>");
                $(indicHolderArry[1] + " div").append("<div class='dropdown-divider'</div>");
                $(indicHolderArry[1] + " div").append("<input type='number' step='5' class='dropdown-item form-control form-control-sm border-danger' placeholder='自定义值' autocomplete='off' name='indicator_value'/>");
                $.each($(indicHolderArry[1] + " div input"), function (idx, value) {
                    $(value).on("blur", { type: 1, txtHolder: indicPickedHolderArray[1][0], vHolder: indicPickedHolderArray[1][1] }, strategyValueInputOnchange);
                });
                break;
        }
        $.each($(indicHolderArry[0] + " div a"), function (idx, value) {
            $(value).on("click", { txtHolder: indicPickedHolderArray[0][0], vHolder: indicPickedHolderArray[0][1] }, strategyMenuItemClick);
        });

        $.each($(indicHolderArry[1] + " div a"), function (idx, value) {
            $(value).on("click", { txtHolder: indicPickedHolderArray[1][0], vHolder: indicPickedHolderArray[1][1] }, strategyMenuItemClick);
        });
    }

    // Buy Event Handling
    $("#bStrategyCategory div a").click(function () {
        // alert("i am clicked " + $(this).attr("href"));
        curBStrategyCategory = $(this).attr("value");
        $("#bSCPicked").text($(this).text());
        $("#hiddenStrategyCategory").val($(this).attr("value"));

        setupStrategyParam(curBStrategyCategory, ["#bMenuTI1", "#bMenuTI2", "#bMenuCond"], [["#bTIPicked1", "#hiddenBTI1"], ["#bTIPicked2", "#hiddenBTI2"], ["#bCondPicked", "#hiddenBCond"]]);
    });

    var strategyMenuItemClick = function (event) {
        // alert("i am clicked " + $(this).attr("href"));
        // alert(event.data.a);
        $(event.data.txtHolder).text($(this).text());
        $(event.data.vHolder).val($(this).attr("value"));
    }

    var strategyValueInputOnchange = function (event) {
        if ($(this).val() != "") {
            if (event.data.type == 0) { // 指标
                $(event.data.txtHolder).text(curIndicator[0] + "(" + $(this).val() + ")");
                $(event.data.vHolder).val(curIndicator[0] + "_" + $(this).val());
            } else {// 数值
                $(event.data.txtHolder).text($(this).val());
                $(event.data.vHolder).val($(this).val());
            }
        }
    }

    $("#bMenuTI1 div a").click({ txtHolder: "#bTIPicked1", vHolder: "#hiddenBTI1" }, strategyMenuItemClick);
    $("#bMenuTI2 div a").click({ txtHolder: "#bTIPicked2", vHolder: "#hiddenBTI2" }, strategyMenuItemClick);
    $("#bMenuCond div a").click({ txtHolder: "#bCondPicked", vHolder: "#hiddenBCond" }, strategyMenuItemClick);

    // Sell Strategy Event
    $("#sStrategyCategory div a").click(function () {
        // alert("i am clicked " + $(this).attr("href"));
        curSStrategyCategory = $(this).attr("value");
        $("#sSCPicked").text($(this).text());
        $("#hiddenSStrategyCategory").val($(this).attr("value"));

        setupStrategyParam(curSStrategyCategory, ["#sMenuTI1", "#sMenuTI2", "#sMenuCond"], [["#sTIPicked1", "#hiddenSTI1"], ["#sTIPicked2", "#hiddenSTI2"], ["#sCondPicked", "#hiddenSCond"]]);

    });

    $("#sMenuTI1 div a").click({ txtHolder: "#sTIPicked1", vHolder: "#hiddenSTI1" }, strategyMenuItemClick);
    $("#sMenuTI2 div a").click({ txtHolder: "#sTIPicked2", vHolder: "#hiddenSTI2" }, strategyMenuItemClick);
    $("#sMenuCond div a").click({ txtHolder: "#sCondPicked", vHolder: "#hiddenSCond" }, strategyMenuItemClick);

    $("#executeBT").click(function () {
        buildTAIndicator();
        buildBStrategy();
        buildSStrategy();
        executeBT();
    });

    initParam();
    updateBTMixChart(tsCode);
    updateFundaChart(tsCode, startDate, endDate);
});