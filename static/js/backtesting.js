$(function () {
    // <strategy_category>/<ta_indicator_dict>/<buy_cond_dict>/<sell_cond_dict>/<stoploss>/<cash>/<commission>/<leverage>/<freq>/
    var strategyCategory = "system";
    var taIndicatorType = "";
    var taIndicator = "";
    var bSystem = "";
    var sSystem = "";
    let buyAttr = new Map();
    var buyCondition = "";
    let sellConditionDict = new Map();
    var stoploss = ".95";
    var cash = "10000";
    var commission = ".001";
    var leverage = "1";
    var freq = "D";
    // <tech_indicator>/<indicator_param>/<strategy_category>/<cash>/<commission>/<leverage>/<freq>/</freq>
    var indicatorParam = "";
    var tsCode = $("#hiddenTscode").val();

    var INDIC_CROSSOVER = "0";
    var INDIC_PAIR_COMP = "1";
    var INDIC_THRESHOLD = "2";

    var stockmarketEndpoint = "/stockmarket/";
    var equityChart = echarts.init(document.getElementById('equityChart'));
    var ohlcChart = echarts.init(document.getElementById('ohlcChart'));

    //  http://127.0.0.1:8000/stockmarket/bt-system/000001.SZ/system/
    //    %7B'SMA_10':%2010,'SMA_20':20,'RSI_20':20%7D/%7B'attr':%7B'sma_level':'10','rsi_level':'20'%7D,
    //  'condition':%7B'threshold':%7B'RSI_20':'RSI_20%3E30'%7D,
    //  'crossover':%7B'a10':'cross(a(10),%20a(20))'%7D,'pair_comp':%20%7B'a10':'a(10)%20%3E%20a(20)'%7D%7D%7D/%
    //   7B'attr':%7B'sma_level':'10','rsi_level':'90'%7D,'condition':%7B'threshold':%7B'RSI_20':'RSI_20%3E90'%7D,
    //  'crossover':%7B'a20':'cross(a(20),%20a(10))'%7D,'pair_comp':%20%7B'a10':'a(20)%20%3E%20a(10)'%7D%7D%7D/.95/10000/.001/1/D/
    var renderEquityChart = function (tsCode) {
        var zoomMin = 0;
        var zoomMax = 100;
        $.ajax({
            url: stockmarketEndpoint + "stock-close-history/bt-system/" + tsCode + "/" + freq + "/" + closePeriod + "/?format=json",
            success: function (data) {
                var chartData = jsonToChartFormat(data, "equity");
                option = {
                    tooltip: {
                        trigger: 'axis',
                        position: function (pt) {
                            return [pt[0], '10%'];
                        }
                    },
                    legend: {
                        data: ['资产净值']
                    },
                    xAxis: {
                        type: 'category',
                        boundaryGap: false,
                        data: chartData.label//data.label
                    },
                    yAxis: {
                        type: 'value',
                        boundaryGap: [0, '100%']
                    },
                    dataZoom: [{
                        type: 'inside',
                        start: zoomMin,
                        end: zoomMax
                    }, {
                        start: 0,
                        end: 10,
                        handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
                        handleSize: '100%',
                        handleStyle: {
                            color: '#fff',
                            shadowBlur: 3,
                            shadowColor: 'rgba(0, 0, 0, 0.6)',
                            shadowOffsetX: 2,
                            shadowOffsetY: 2
                        }
                    }],
                    series: [
                        {
                            name: '收盘价',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            itemStyle: {
                                color: 'rgb(25, 70, 131)'
                            },
                            data: chartData.value, //data.close,
                            markPoint: {
                                data: [
                                    { type: 'max', name: '最大值' },
                                    { type: 'min', name: '最小值' }
                                ]
                            }
                        }
                    ]
                };

                equityChart.setOption(option);
            }
        });
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
        $("#currentTsCode").val(item.ts_code);
        $("#ind").text(item.industry)
        $(".stock_name").each(function (idx, obj) {
            $(obj).text(item.stock_name);
        });
        $("#industryUrl").attr("href", "/industry/" + item.industry);

        // window.history.pushState("", stockName + "基本信息一览", homeEndpoint + "?q=" + tsCode);
        // renderChart();
        // showIndBasic(item.industry);
        // showStockBasic(item.ts_code);
    });

    // var buildTaCondition = function(){
    //     // ta_indicator:
    //     // "{'SMA_10': 10,'SMA_20':20,'RSI_20':20}"


    // }

    // var 
    let taIndicatorSet = new Set();

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
            taIndicator += "'"+ indic + "':" + techIndicParam;
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

        $.each($("#bStrategyList ul li"), function (index, value) {
            var bCond = $(value).children()[2].value;
            if (bCond.split(":")[0] == "0") {
                bCrossover += "'" + index.toString() + "':'" + bCond.split(":")[1] + "',";
            } else if (bCond.split(":")[0] == "1") {
                bPairComp += "'" + index.toString() + "':'" + bCond.split(":")[1] + "',";
            } else if (bCond.split(":")[0] == "2") {
                bThreshold += "'" + index.toString() + "':'" + bCond.split(":")[1] + "',";
            }

            if (index == $("#bStrategyList ul li").length - 1) {
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
        $.ajax({
            url: stockmarketEndpoint + "bt-system/" + tsCode + "/" + strategyCategory + "/" + taIndicator + 
                "/" + bSystem + "/" + sSystem + "/" + stoploss + "/" + cash + "/" + commission + "/" + leverage + "/" + freq + "/",
            success: function (data) {
                console.log(data)
            }
        });
    }

    $("#addBStrategy").click(function () {
        var newItem = "";
        var bCondText = ""; //$("#bTIPicked1").text() + " " + $("#bCondPicked").text() + " " + $("#bTIPicked2").text();
        var bCondValue = "";

        if ($("#hiddenStrategyCategory").val() == "") return;

        if ($("#hiddenStrategyCategory").val() == "0") { //crossover
            bCondText = $("#bTIPicked1").text() + " " + $("#bCondPicked").text() + " " + $("#bTIPicked2").text();
            bCondValue = "0:" + $("#hiddenBCond").val() + "(self." + $("#hiddenBTI1").val() + "," + "self." + $("#hiddenBTI2").val() + ")";

            taIndicatorSet.add($("#hiddenBTI1").val())
            taIndicatorSet.add($("#hiddenBTI2").val())
        } else if ($("#hiddenStrategyCategory").val() == "1") {//tech indicator pair compare
            bCondText = $("#bTIPicked1").text() + " " + $("#bCondPicked").text() + " " + $("#bTIPicked2").text();
            bCondValue = "1:self." + $("#hiddenBTI1").val() + "[-1]" + $("#hiddenBCond").val() + "self." + $("#hiddenBTI2").val() + "[-1]";

            taIndicatorSet.add($("#hiddenBTI1").val())
            taIndicatorSet.add($("#hiddenBTI2").val())
        } else if ($("#hiddenStrategyCategory").val() == "2") {//tech indicator value threshold
            bCondText = $("#bTIPicked1").text() + " " + $("#bCondPicked").text() + " " + $("#bTIValue").val();
            bCondValue = "2:self." + $("#hiddenBTI1").val() + "[-1]" + $("#hiddenBCond").val() + $("#bTIValue").val();

            taIndicatorSet.add($("#hiddenBTI1").val())
        }

        newItem += "<li class='list-group-item d-flex justify-content-between align-items-center list-group-item-action'>" +
            "<span class='text-primary small'>" + bCondText + "</span>" +
            "<a class='badge rounded-pill' href='javascript:void(0)'>x</a>" +
            "<input type='hidden' value='" + bCondValue + "'>" +
            "</li>";
        $("#bStrategyList ul").append(newItem);
    });

    $("#addSStrategy").click(function () {
        var newItem = "";
        var sCondText = ""; //$("#bTIPicked1").text() + " " + $("#bCondPicked").text() + " " + $("#bTIPicked2").text();
        var sCondValue = "";

        if ($("#hiddenSStrategyCategory").val() == "") return;

        if ($("#hiddenSStrategyCategory").val() == "0") { //crossover
            sCondText = $("#sTIPicked1").text() + " " + $("#sCondPicked").text() + " " + $("#sTIPicked2").text();
            sCondValue = "0:" + $("#hiddenSCond").val() + "(self." + $("#hiddenSTI2").val() + "," + "self." + $("#hiddenSTI1").val() + ")";

            taIndicatorSet.add($("#hiddenSTI1").val())
            taIndicatorSet.add($("#hiddenSTI2").val())
        } else if ($("#hiddenSStrategyCategory").val() == "1") {//tech indicator pair compare
            sCondText = $("#sTIPicked1").text() + " " + $("#sCondPicked").text() + " " + $("#sTIPicked2").text();
            sCondValue = "1:self." + $("#hiddenSTI1").val() + "[-1]" + $("#hiddenSCond").val() + "self." + $("#hiddenSTI2").val() + "[-1]";

            taIndicatorSet.add($("#hiddenSTI1").val())
            taIndicatorSet.add($("#hiddenSTI2").val())
        } else if ($("#hiddenSStrategyCategory").val() == "2") {//tech indicator value threshold
            sCondText = $("#sTIPicked1").text() + " " + $("#sCondPicked").text() + " " + $("#sTIValue").val();
            sCondValue = "2:self." + $("#hiddenSTI1").val() + "[-1]" + $("#hiddenSCond").val() + $("#sTIValue").val();

            taIndicatorSet.add($("#hiddenSTI1").val())
        }

        newItem += "<li class='list-group-item d-flex justify-content-between align-items-center list-group-item-action'>" +
            "<span class='text-primary small'>" + sCondText + "</span>" +
            "<a class='badge rounded-pill' href='javascript:void(0)'>x</a>" +
            "<input type='hidden' value='" + sCondValue + "'>" +
            "</li>";
        $("#sStrategyList ul").append(newItem);
    });


    // Buy Event Handling
    $("#bStrategyCategory div a").click(function () {
        // alert("i am clicked " + $(this).attr("href"));
        $("#bSCPicked").text($(this).text());
        $("#hiddenStrategyCategory").val($(this).attr("value"));
    });

    $("#bMenuTI1 div a").click(function () {
        // alert("i am clicked " + $(this).attr("href"));
        $("#bTIPicked1").text($(this).text());
        $("#hiddenBTI1").val($(this).attr("value"));
    });

    $("#bMenuTI2 div a").click(function () {
        // alert("i am clicked " + $(this).attr("href"));
        $("#bTIPicked2").text($(this).text());
        $("#hiddenBTI2").val($(this).attr("value"));
    });

    $("#bMenuCond div a").click(function () {
        // alert("i am clicked " + $(this).attr("href"));
        $("#bCondPicked").text($(this).text());
        $("#hiddenBCond").val($(this).attr("value"));
    });

    // Sell Strategy Event
    $("#sStrategyCategory div a").click(function () {
        // alert("i am clicked " + $(this).attr("href"));
        $("#sSCPicked").text($(this).text());
        $("#hiddenSStrategyCategory").val($(this).attr("value"));
    });

    $("#sMenuTI1 div a").click(function () {
        // alert("i am clicked " + $(this).attr("href"));
        $("#sTIPicked1").text($(this).text());
        $("#hiddenSTI1").val($(this).attr("value"));
    });

    $("#sMenuTI2 div a").click(function () {
        // alert("i am clicked " + $(this).attr("href"));
        $("#sTIPicked2").text($(this).text());
        $("#hiddenSTI2").val($(this).attr("value"));
    });

    $("#sMenuCond div a").click(function () {
        // alert("i am clicked " + $(this).attr("href"));
        $("#sCondPicked").text($(this).text());
        $("#hiddenSCond").val($(this).attr("value"));
    });

    $("#executeBT").click(function () {
        buildTAIndicator();
        buildBStrategy();
        buildSStrategy();
        executeBT();
    });

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