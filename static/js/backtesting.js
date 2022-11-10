$(function () {
    // <strategy_category>/<ta_indicator_dict>/<buy_cond_dict>/<sell_cond_dict>/<stoploss>/<cash>/<commission>/<leverage>/<freq>/
    const upColor = '#ec0000';
    const downColor = '#00da3c';

    let taIndicatorSet = new Set();
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

    var INDIC_CROSSOVER = "0";
    var INDIC_PAIR_COMP = "1";
    var INDIC_THRESHOLD = "2";

    var today = new Date();
    var startDate = "";
    var endDate = "";
    var stockHistPeriod = "3";

    var btMixChart;
    // var ohlcChart;
    var indicChart;
    var fundaChart;
    var mixChartOption;
    var bStrategyCount = 0;
    var sStrategyCount = 0;
    // let strategyCount = [0, 0];

    var equityJsonData;
    var ohlcCount = 0;

    var stockmarketEndpoint = "/stockmarket/";
    var curIndicator = ["SMA", "0", "1", "3"];
    var curBStrategyCategory = "0";
    var curSStrategyCategory = "0";

    var condParamCrossover = ["向上穿越,crossover", "向下穿越,crossover"];
    var condParamValueCompare = ["大于,>", "小于,<"];
    var indicatorParamOHLC = ["收盘价,Close"];
    var smaParam = ["10", "20", "60", "120", "200"];
    var emaParam = ["10", "20", "60", "120", "200"];
    var bollParam = ["MID", "UPPER", "LOWER"];
    var kdjParam = ["K", "D", "J"];
    var macdParam = ["MACD", "DIFF", "DEA"];
    var rsiParam = ["6", "12", "24"];
    var bbiParam = ["BBI多空指标"];
    var indicaMap = new Map();


    // var basicCharts

    var initParam = function () {
        tsCode = $("#hiddenTsCode").val();
        stockHistPeriod = $('input:radio[name="stockHistPeriod"]:checked').val();
        capital = $("#capital").val();
        stoploss = (100 - parseInt($("#stoploss").val()))/100;

        var unit = $('input:radio[name="commission-unit"]:checked').val();
        var commissionOpt = $('input:radio[name="commission"]:checked').val();
        if (unit == "tth") {
            commission = parseInt(commissionOpt) / 10000;
        } else {
            commission = parseInt(commissionOpt) / 1000;
        }
        tradeOnClose = $('input:radio[name="trade-on-close"]:checked').val();
        restoration = $('input:radio[name="restoration"]:checked').val();
        freq = $('input:radio[name="freq"]:checked').val();

        startDate = formatDate(new Date(today.getTime() - (365 * stockHistPeriod * 24 * 60 * 60 * 1000)), "");
        endDate = formatDate(today, "");

        fundaChart = $(".funda-chart");
        btMixChart = echarts.init(document.getElementById('btMixChart'));
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

        setupStrategyCategories("#bStrategyCategory");
        setupStrategyCategories("#sStrategyCategory");
    }

    //  http://127.0.0.1:8000/stockmarket/bt-system/000001.SZ/system/
    //    %7B'SMA_10':%2010,'SMA_20':20,'RSI_20':20%7D/%7B'attr':%7B'sma_level':'10','rsi_level':'20'%7D,
    //  'condition':%7B'threshold':%7B'RSI_20':'RSI_20%3E30'%7D,
    //  'crossover':%7B'a10':'cross(a(10),%20a(20))'%7D,'pair_comp':%20%7B'a10':'a(10)%20%3E%20a(20)'%7D%7D%7D/%
    //   7B'attr':%7B'sma_level':'10','rsi_level':'90'%7D,'condition':%7B'threshold':%7B'RSI_20':'RSI_20%3E90'%7D,
    //  'crossover':%7B'a20':'cross(a(20),%20a(10))'%7D,'pair_comp':%20%7B'a10':'a(20)%20%3E%20a(10)'%7D%7D%7D/.95/10000/.001/1/D/

    function calculateMA(dayCount, data) {
        var result = [];
        for (var i = 0, len = data.value.length; i < len; i++) {
            if (i < dayCount) {
                result.push('-');
                continue;
            }
            var sum = 0;
            for (var j = 0; j < dayCount; j++) {
                sum += data.value[i - j][1];
            }
            result.push(+(sum / dayCount).toFixed(3));
        }
        return result;
    }

    var renderBTMixChart = function (tsCode) {
        var zoomMin = 0;
        var zoomMax = 100;
        $.ajax({
            url: stockmarketEndpoint + "ohlc/" + tsCode + "/" + freq + "/" + stockHistPeriod + "/?format=json",
            success: function (data) {
                var chartData = jsonToChartOHLCFormat(data);
                ohlcCount = chartData.label.length;
                mixChartOption = {
                    animation: true,
                    legend: {
                        top: 5,
                        data: ['MA10','MA20','MA60','MA120','MA200']
                    },
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
                        {left: '4%',right: '3%',top: "2%",height: '20%'},
                        // reserved for equity + OHLC grid index 0
                        // {left: '4%',right: '1%',top: "2%",height: '13%'},
                        // {left: '4%',right: '1%',top: "16%",height: '7%'},

                        //OHLC grid index 1, volume成交量
                        {left: '4%',right: '3%',top: '24%',height: '4%'},
                        
                        //OHLC grid index 2, RSI
                        {left: '4%',right: '3%',top: '29%',height: '5%'},
                        //OHLC grid index 3, MACD
                        {left: '4%',right: '3%',top: '35%',height: '5%'},
                        //OHLC grid index 4, KDJ
                        {left: '4%',right: '3%',top: '41%',height: '5%'},

                        //Fundamental grid index 5, PE
                        {left: '4%', top: '48%',height:'10%',width: '38%'},
                        //Fundamental grid index 6, PE TTM
                        {right: '3%',top: '48%',height:'10%',width: '38%'},

                        //Fundamental grid index 7, PB
                        {left: '4%', right: '3%',top: '59%',height: '10%'},

                        //Fundamental grid index 8, PS
                        {left: '4%',top: '70%',height:'10%',width: '38%'},
                        //Fundamental grid index 9, PS TTM
                        {right: '3%',top: '70%',height:'10%',width: '38%'},
                        
                        //Fundamental grid index 10, Turnover ratio
                        {left: '4%',top: '81%',height: '10%', width: '38%'},
                        //Fundamental grid index 11, Vol ratio
                        {right: '3%',top: '81%',height: '10%', width: '38%'}
                    ],
                    xAxis: [
                        {gridIndex: 0, data: chartData.label, min: 'dataMin', max: 'dataMax',axisLine: { onZero: false }}, // OHLC
                        {gridIndex: 1, data: chartData.label, min: 'dataMin', max: 'dataMax',axisLine: { onZero: false },axisTick: { show: false },splitLine: { show: false },axisLabel: { show: false }}, // VOL
                        
                        {gridIndex: 2, data: chartData.label, min: 'dataMin', max: 'dataMax'}, // RSI
                        {gridIndex: 3, data: chartData.label, min: 'dataMin', max: 'dataMax'}, // MACD
                        {gridIndex: 4, data: chartData.label, min: 'dataMin', max: 'dataMax'}, // KDJ

                        {gridIndex: 5, data: chartData.label, min: 'dataMin', max: 'dataMax'}, // PE
                        {gridIndex: 6, data: chartData.label, min: 'dataMin', max: 'dataMax'}, // PE TTM
                        {gridIndex: 7, data: chartData.label, min: 'dataMin', max: 'dataMax'}, // PB
                        {gridIndex: 8, data: chartData.label, min: 'dataMin', max: 'dataMax'}, // PS
                        {gridIndex: 9, data: chartData.label, min: 'dataMin', max: 'dataMax'}, // PS TTM
                        {gridIndex: 10, data: chartData.label, min: 'dataMin', max: 'dataMax'}, // TO 换手率 
                        {gridIndex: 11, data: chartData.label, min: 'dataMin', max: 'dataMax'} // VO 量比 

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
                        {gridIndex: 1, scale: true, min: 'dataMin', max: 'dataMax',axisLine: { show: false, onZero: false },axisTick: { show: false },splitLine: { show: false },axisLabel: { show: false }}, // VOL
                        
                        {gridIndex: 2, scale: true, min: 'dataMin', max: 'dataMax'}, // RSI
                        {gridIndex: 3, scale: true, min: 'dataMin', max: 'dataMax'}, // MACD
                        {gridIndex: 4, scale: true, min: 'dataMin', max: 'dataMax'}, // KDJ

                        {gridIndex: 5, scale: true, min: 'dataMin', max: 'dataMax'}, // PE
                        {gridIndex: 6, scale: true, min: 'dataMin', max: 'dataMax'}, // PE TTM
                        {gridIndex: 7, scale: true, min: 'dataMin', max: 'dataMax'}, // PB
                        {gridIndex: 8, scale: true, min: 'dataMin', max: 'dataMax'}, // PS
                        {gridIndex: 9, scale: true, min: 'dataMin', max: 'dataMax'}, // PS TTM
                        {gridIndex: 10, scale: true, min: 'dataMin', max: 'dataMax'}, // TO 换手率 
                        {gridIndex: 11, scale: true, min: 'dataMin', max: 'dataMax'} // VO 量比 

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
                            xAxisIndex: [0, 1],
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
                            name: 'k线',
                            type: 'candlestick',
                            data: chartData.value,
                            itemStyle: {
                                color: upColor,
                                color0: downColor,
                                borderColor: undefined,
                                borderColor0: undefined
                            }
                        },
                        {
                            name: 'MA10',
                            type: 'line',
                            data: calculateMA(10, chartData),
                            showSymbol: false,
                            smooth: true,
                            lineStyle: {
                                opacity: 0.5
                            }
                        },
                        {
                            name: 'MA20',
                            type: 'line',
                            data: calculateMA(20, chartData),
                            smooth: true,
                            showSymbol: false,
                            lineStyle: {
                                opacity: 0.5
                            }
                        },
                        {
                            name: 'MA60',
                            type: 'line',
                            data: calculateMA(60, chartData),
                            smooth: true,
                            showSymbol: false,
                            lineStyle: {
                                opacity: 0.5
                            }
                        },
                        {
                            name: 'MA120',
                            type: 'line',
                            data: calculateMA(120, chartData),
                            smooth: true,
                            showSymbol: false,
                            lineStyle: {
                                opacity: 0.5
                            }
                        },
                        {
                            name: 'MA200',
                            type: 'line',
                            data: calculateMA(200, chartData),
                            smooth: true,
                            showSymbol: false,
                            lineStyle: {
                                opacity: 0.5
                            }
                        },
                        {
                            name: 'Volume',
                            type: 'bar',
                            xAxisIndex: 1,
                            yAxisIndex: 1,
                            data: chartData.volume
                        }
                        // ,{
                        //     name: '净值',
                        //     type: 'line',
                        //     yAxisIndex: 2
                        //     // data: chartData.volume
                        // }
                    ]
                };
                btMixChart.setOption(mixChartOption);
            }
        });
    }

    var pushEquityData = function (data, legend, yAxisIdx, type) {
        //添加series
        var equity = jsonToArray(data, "eq");
        mixChartOption.series.push({
            name: legend,
            color: upColor,
            type: type,
            yAxisIndex: yAxisIdx,
            data: equity.value.slice(-ohlcCount)
        });

        //添加 legend
        mixChartOption.legend.data.push(legend)
        btMixChart.setOption(mixChartOption);
    }

    var renderCompanyFundaChart = function (tsCode, startDate, endDate) {
        $.ajax({
            url: stockmarketEndpoint + "daily-basic-history/" + tsCode + "/" + startDate + "/" + endDate + "/?format=json",
            success: function (data) {
                $(fundaChart).each(function (idx, obj) {
                    if (tsCode == "000001.SH" || tsCode == "399001.SZ" || tsCode == "399006.SZ") {
                        if ($(obj).attr("name") == "pe" || $(obj).attr("name") == "pe_ttm" || $(obj).attr("name") == "trade_date" || $(obj).attr("name") == "pb" || $(obj).attr("name") == "turnover_rate") {
                            pushFunda2MixChart(data, obj, $(obj).attr("name"));
                        }
                    } else {
                        pushFunda2MixChart(data, obj, $(obj).attr("name"));
                    }
                });
                // renderPETTMChart(data.pe_ttm);
                // renderPSChart(data.ps);
                // renderPSTTMChart(data.ps_ttm);
                // renderPBChart(data.pb);
                // renderTOChart(data.turnover_rate);
                // renderVRChart(data.volume_ratio);
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

    var pushFunda2MixChart = function (jsonData, fundaType) {
        var chartData = jsonToChartFormat(jsonData, fundaType);
        var peQuantile = getQuantile(chartData);
        // var chartCanvas = echarts.init(canvas);

        //动态添加series
        mixChartOption.series.push({
            name: fundaType,
            type: 'line',
            smooth: true,
            showSymbol: false,
            data: chartData.value,
            markPoint: {
                data: [
                    { type: 'max', name: '最大值' },
                    { type: 'min', name: '最小值' }
                ]
            }
        },
        {
            name: fundaType + '低位',
            type: 'line',
            // smooth: true,
            showSymbol: false,
            itemStyle: {
                color: 'rgb(0, 255, 0)'
            },
            data: peQuantile.qt10
        },
        {
            name: fundaType + '中位',
            type: 'line',
            smooth: true,
            showSymbol: false,
            itemStyle: {
                color: 'rgb(25, 70, 131)'
            },
            data: peQuantile.qt50
        },
        {
            name: fundaType + '高位',
            type: 'line',
            smooth: true,
            showSymbol: false,
            itemStyle: {
                color: 'rgb(255, 0, 0)'
            },
            data: peQuantile.qt90
        });

        //动态添加 legend.data
        // mixChartOption.legend.data.push('其他');
        btMixChart.setOption(mixChartOption);

        mixChartOption = {
            tooltip: {
                trigger: 'axis',
                position: function (pt) {
                    return [pt[0], '10%'];
                }
            },
            legend: {
                data: [fundaType, fundaType + "中位"]
            },
            // title: {
            //     text: '市盈',
            //     left: '5%',
            // },
            toolbox: {
                feature: {
                    // dataZoom: {
                    //     yAxisIndex: 'none'
                    // },
                    // restore: {},
                    saveAsImage: {}
                }
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: chartData.label
            },
            yAxis: {
                type: 'value',
                boundaryGap: [0, '100%']
            },
            dataZoom: [{
                type: 'inside',
                start: 0,
                end: 100
            }
                // , {
                //     start: 0,
                //     end: 10,
                //     handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
                //     handleSize: '100%',
                //     handleStyle: {
                //         color: '#fff',
                //         shadowBlur: 3,
                //         shadowColor: 'rgba(0, 0, 0, 0.6)',
                //         shadowOffsetX: 2,
                //         shadowOffsetY: 2
                //     }
                // }
            ],
            series: [
                {
                    name: fundaType,
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    sampling: 'average',
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },
                    data: chartData.value,
                    markPoint: {
                        data: [
                            { type: 'max', name: '最大值' },
                            { type: 'min', name: '最小值' }
                        ]
                    },
                    markLine: {
                        data: [
                            { type: 'average', name: '平均值' }
                        ]
                    }
                },
                {
                    name: fundaType + '低位',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    itemStyle: {
                        color: 'rgb(0, 255, 0)'
                    },
                    data: peQuantile.qt10
                },
                {
                    name: fundaType + '中位',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    sampling: 'average',
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },
                    data: peQuantile.qt50
                },
                {
                    name: fundaType + '高位',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    itemStyle: {
                        color: 'rgb(255, 0, 0)'
                    },
                    data: peQuantile.qt90
                }
            ]
        };

        // chartCanvas.setOption(mixChartOption);
    }

    var renderChart = function () {
        renderBTMixChart(tsCode);
        // renderIndicChart(tsCode);
        renderCompanyFundaChart(tsCode, startDate, endDate);
        // if (tsCode == "000001.SH" || tsCode == "399001.SZ" || tsCode == "399006.SZ") {
        //     $("#psChart").addClass("d-none");
        //     $("#psTTMChart").addClass("d-none");
        //     $("#vrChart").addClass("d-none");
        // } else {
        //     // showCompanyBasic(tsCode);
        //     $("#psChart").removeClass("d-none");
        //     $("#psTTMChart").removeClass("d-none");
        //     $("#vrChart").removeClass("d-none");
        // }
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
        // $("#industryUrl").attr("href", "/industry/" + item.industry);

        // window.history.pushState("", stockName + "基本信息一览", homeEndpoint + "?q=" + tsCode);
        renderChart();
        // showIndBasic(item.industry);
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
        taIndicator = "";
        taIndicator += "{";
        for (let indic of taIndicatorSet) {
            var techIndic = indic.split("_")[0];
            var techIndicParam = indic.split("_")[1];
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
            }

            if (index == $("#bStrategyList").children().length - 1) {
                bCrossover += "},";
                bPairComp += "},";
                bThreshold += "}";
                bSystem += bCrossover + bPairComp + bThreshold + "}}";
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
        sSystem = "";
        sSystem += "{'attr':{'level':0},'condition':{";

        $.each($("#sStrategyList ul li"), function (index, value) {
            var sCond = $(value).children()[2].value;
            if (sCond.split(":")[0] == "0") {
                sCrossover += "'" + index.toString() + "':'" + sCond.split(":")[1] + "',";
            } else if (sCond.split(":")[0] == "1") {
                sPairComp += "'" + index.toString() + "':'" + sCond.split(":")[1] + "',";
            } else if (sCond.split(":")[0] == "2") {
                sThreshold += "'" + index.toString() + "':'" + sCond.split(":")[1] + "',";
            }

            if (index == $("#sStrategyList ul li").length - 1) {
                sCrossover += "},";
                sPairComp += "},";
                sThreshold += "}";
                sSystem += sCrossover + sPairComp + sThreshold + "}}";
            }
        });


        // executeBT();
    }

    var executeBT = function () {
        capital = $("#capital").val();
        stoploss = (100 - parseInt($("#stoploss").val()))/100;

        $.ajax({
            url: stockmarketEndpoint + "bt-system/" + tsCode + "/" + strategyCategory + "/" + taIndicator +
                "/" + bSystem + "/" + sSystem + "/" + stoploss.toString() + "/" + capital.toString() + "/" + commission.toString() +
                "/" + leverage.toString() + "/" + tradeOnClose.toString() + "/" + freq + "/",
            success: function (data) {
                // console.log(data)
                // equityJsonData = data;
                // pushEquityData(equityJsonData, "净值", 2, "line");
            }
        });
    }

    $("#addBStrategy").click(function () {
        var newItem = "";
        var bStrategyText = ""; //$("#bTIPicked1").text() + " " + $("#bCondPicked").text() + " " + $("#bTIPicked2").text();
        var bStrategyValue = "";

        if ($("#hiddenStrategyCategory").val() == "") return;

        if ($("#hiddenStrategyCategory").val() == "0") { //crossover
            bStrategyText = $("#bTIPicked1").text() + " " + $("#bCondPicked").text() + " " + $("#bTIPicked2").text();
            bStrategyValue = "0:" + $("#hiddenBCond").val() + "(self." + $("#hiddenBTI1").val() + "," + "self." + $("#hiddenBTI2").val() + ")";

            taIndicatorSet.add($("#hiddenBTI1").val())
            taIndicatorSet.add($("#hiddenBTI2").val())
        } else if ($("#hiddenStrategyCategory").val() == "1") {//tech indicator pair compare
            bStrategyText = $("#bTIPicked1").text() + " " + $("#bCondPicked").text() + " " + $("#bTIPicked2").text();
            bStrategyValue = "1:self." + $("#hiddenBTI1").val() + "[-1]" + $("#hiddenBCond").val() + "self." + $("#hiddenBTI2").val() + "[-1]";

            taIndicatorSet.add($("#hiddenBTI1").val())
            taIndicatorSet.add($("#hiddenBTI2").val())
        } else if ($("#hiddenStrategyCategory").val() == "2") {//tech indicator value threshold
            bStrategyText = $("#bTIPicked1").text() + " " + $("#bCondPicked").text() + " " + $("#bTIPicked2").text();
            bStrategyValue = "2:self." + $("#hiddenBTI1").val() + "[-1]" + $("#hiddenBCond").val() + $("#hiddenBTI2").val();

            taIndicatorSet.add($("#hiddenBTI1").val())
        } else if ($("#hiddenStrategyCategory").val() == "3") {//OHLC - close ta compare
            bStrategyText = $("#bTIPicked1").text() + " " + $("#bCondPicked").text() + " " + $("#bTIPicked2").text();
            bStrategyValue = "3:self.data." + $("#hiddenBTI1").val() + "[-1]" + $("#hiddenBCond").val() + "self." + $("#hiddenBTI2").val() + "[-1]";

            taIndicatorSet.add($("#hiddenBTI1").val())
        }

        if (!bStrategyTextSet.has(bStrategyText)) {
            bStrategyCount++;
            newItem += "<div class='col-lg-8 d-flex justify-content-between align-items-center'>" +
                "<span class='text-primary small'>" + bStrategyText + "</span>" +
                "<a class='badge rounded-pill' href='javascript:void(0)' id='bRM" + bStrategyCount + "'>x</a>" +
                "<input type='hidden' value='" + bStrategyValue + "'>" +
                "</div>";

            $("#bStrategyList").append(newItem);
            $("#bRM" + bStrategyCount).on("click", { strategyText: bStrategyText, holder: $("#bStrategyCount") }, function (event) {
                bStrategyCount--;
                bStrategyTextSet.delete(bStrategyText);
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

            taIndicatorSet.add($("#hiddenSTI1").val())
            taIndicatorSet.add($("#hiddenSTI2").val())
        } else if ($("#hiddenSStrategyCategory").val() == "1") {//tech indicator pair compare
            sStrategyText = $("#sTIPicked1").text() + " " + $("#sCondPicked").text() + " " + $("#sTIPicked2").text();
            sStrategyValue = "1:self." + $("#hiddenSTI1").val() + "[-1]" + $("#hiddenSCond").val() + "self." + $("#hiddenSTI2").val() + "[-1]";

            taIndicatorSet.add($("#hiddenSTI1").val())
            taIndicatorSet.add($("#hiddenSTI2").val())
        } else if ($("#hiddenSStrategyCategory").val() == "2") {//tech indicator value threshold
            sStrategyText = $("#sTIPicked1").text() + " " + $("#sCondPicked").text() + " " + $("#sTIPicked2").text();
            sStrategyValue = "2:self." + $("#hiddenSTI1").val() + "[-1]" + $("#hiddenSCond").val() + $("#hiddenSTI2").val();

            taIndicatorSet.add($("#hiddenSTI1").val())
        } else if ($("#hiddenSStrategyCategory").val() == "3") {//tech indicator value threshold
            sStrategyText = $("#sTIPicked1").text() + " " + $("#sCondPicked").text() + " " + $("#sTIPicked2").text();
            sStrategyValue = "2:self." + $("#hiddenSTI1").val() + "[-1]" + $("#hiddenSCond").val() + "self." + $("#hiddenSTI2").val() + "[-1]";

            taIndicatorSet.add($("#hiddenSTI1").val())
        }

        if (!sStrategyTextSet.has(sStrategyText)) {
            sStrategyCount++;
            // strategyCount[1]++;
            newItem += "<div class='col-lg-8 d-flex justify-content-between align-items-center'>" +
                "<span class='text-primary small'>" + sStrategyText + "</span>" +
                "<a class='badge rounded-pill' href='javascript:void(0)' id='sRM" + sStrategyCount + "'>x</a>" +
                "<input type='hidden' value='" + sStrategyValue + "'>" +
                "</div>";
            $("#sStrategyList").append(newItem);
            // $("#sStrategyList div a").on("click", {count: sStrategyCount, holder: $("#sStrategyCount")}, removeElement)
            $("#sRM" + sStrategyCount).on("click", { strategyText: sStrategyText, holder: $("#sStrategyCount") }, function (event) {
                sStrategyCount--;
                sStrategyTextSet.delete(sStrategyText);
                event.data.holder.text(sStrategyCount.toString());
                $(this).parent().remove();
            });
            // $("#sStrategyCount").text(strategyCount[1].toString());
            $("#sStrategyCount").text(sStrategyCount.toString());
            sStrategyTextSet.add(sStrategyText);
            $("#sMsg").text("");
        } else {
            $("#sMsg").text("勿重复添加");
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

    var removeElement = function (event) {
        event.data.count--;
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
    renderChart();

    // $('input:radio[name="strategyCategory"]').change(function () {
    //     strategyCategory = $(this).val();
    // });

    // $('input:radio[name="taIndicator"]').change(function () {
    //     taIndicator = $(this).val();
    // });

    // $('input:radio[name="taIndicator"]').change(function () {
    //     taIndicator = $(this).val();
    // });

});