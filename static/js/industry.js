$(function () {
    var stockmarketEndpoint = '/stockmarket/';
    var investorEndpoint = "/investors/";
    // var homeEndpoint = '/';
    // var indexList = "sh,sz,cyb,hs300"
    var freq = "D";
    var period = 5;
    var basicType = "close";
    var curInd = "";
    var quantile = "";
    var today = new Date();
    var startDate = "";
    var endDate = "";

    var peChart = document.getElementById("peChart");//$("#peChart");
    var pbChart = document.getElementById("pbChart");//$("#peChart");
    var psChart = document.getElementById("psChart");//$("#peChart");
    var stkQtyChart = document.getElementById("stockQtyChart");//$("#peChart");



    var initParam = function () {
        curInd = $("#curInd").val();
        period = $('input:radio[name="period"]:checked').val();
        quantile = $('input:radio[name="quantilePe"]:checked').val();
        startDate = formatDate(new Date(today.getTime() - (365 * period * 24 * 60 * 60 * 1000)), "");
        endDate = formatDate(today, "");
    }

    var renderChart = function () {
        // showCompanyBasic(tsCode);
        renderIndustryBasicChart(peChart, curInd, "pe", parseFloat(quantile), startDate, endDate);
        renderIndustryBasicChart(pbChart, curInd, "pb", parseFloat(quantile), startDate, endDate);
        renderIndustryBasicChart(psChart, curInd, "ps", parseFloat(quantile), startDate, endDate);
    }


    var renderIndustryBasicChart = function (chart, industry, basicType, quantile, startDate, endDate) {
        var zoomMin = 75;
        var zoomMax = 100;
        $.ajax({
            // industry-basic/<industry>/<basic_type>/<quantile>/<start_date>/<end_date>/
            url: stockmarketEndpoint + "industry-basic/" + industry + "/" + basicType + "/" + quantile + "/" + startDate + "/" + endDate + "/?format=json",
            success: function (data) {
                var chartCanvas = echarts.init(chart);

                if ($(".error-msg").hasClass("d-none")==false){
                    $(".error-msg").addClass("d-none");
                }
                if ($(".dashboard").hasClass("d-none")) {
                    $(".dashboard").removeClass("d-none");
                }
                var chartData = jsonToChartFormat(data, "quantile_val"); //18156636216
                var basicQuantile = getQuantile(chartData);
                option = {
                    tooltip: {
                        trigger: 'axis',
                        position: function (pt) {
                            return [pt[0], '10%'];
                        }
                    },
                    legend: {
                        data: [basicType]
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
                            name: basicType,
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
                            },
                            markLine: {
                                data: [
                                    { type: 'average', name: '平均值' }
                                ]
                            }
                        },
                        {
                            name: '低位',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            itemStyle: {
                                color: 'rgb(0, 255, 0)'
                            },
                            data: basicQuantile.qt10
                        },
                        {
                            name: '中位',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            itemStyle: {
                                color: 'rgb(25, 70, 131)'
                            },
                            data: basicQuantile.qt50
                        },
                        {
                            name: '高位',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            itemStyle: {
                                color: 'rgb(255, 0, 0)'
                            },
                            data: basicQuantile.qt90
                        }
                    ]
                };
                chartCanvas.setOption(option);

                showIndustryStock(stkQtyChart, data);
            }
        });
    }

    var renderCompanyBasicChart = function (tsCode, startDate, endDate) {
        $.ajax({
            url: stockmarketEndpoint + "daily-basic-history/" + tsCode + "/" + startDate + "/" + endDate + "/?format=json",
            success: function (data) {
                $(basicCharts).each(function (idx, obj) {
                    renderBasicChart(data, obj, $(obj).attr("name"));
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

    var showIndustryStock = function (chart, data) {
        var chartData = jsonToChartFormat(data, "stock_count");
        var peQuantile = getQuantile(chartData);
        var chartCanvas = echarts.init(chart);

        option = {
            tooltip: {
                trigger: 'axis',
                position: function (pt) {
                    return [pt[0], '10%'];
                }
            },
            legend: {
                data: ["股票数"]
            },
            // title: {
            //     text: '市盈',
            //     left: '5%',
            // },
            toolbox: {
                feature: {
                    dataZoom: {
                        yAxisIndex: 'none'
                    },
                    restore: {},
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
                    name: "股票数",
                    type: 'bar',
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
            ]
        };

        chartCanvas.setOption(option);
    }

    var followStock = function (tsCode, btn) {
        if (currentUser == "") {
            window.location.href = loginEndpoint + "?next=/?q=" + $("#currentTsCode").val();
        }
        var methodUrl = "";
        var method = "POST";
        if ($.trim($(btn).text()) == "+") {
            methodUrl = "follow-stock/";
            mehod = "POST";
        } else {
            methodUrl = "unfollow-stock/";
            method = "DELETE";
        }
        $.ajax(
            {
                url: investorEndpoint + methodUrl + tsCode + "/",
                headers: { 'X-CSRFToken': csrftoken },
                method: method,
                success: function (data) {
                    if (data.code == "aok") {
                        $(btn).text("-");
                    } else {
                        $(btn).text("+");
                    }
                },
                statusCode: {
                    403: function () {
                        console.info("403 forbidden");
                    },
                    404: function () {
                        console.info("404 page not found");
                    },
                    500: function () {
                        console.info("500 internal server error");
                    }
                }
            }
        );
    }

    $("#followStock").click(function () {
        followStock($("#currentTsCode").val(), this);
    });

    $("#unfollowStock").click(function () {
        followStock($("#currentTsCode").val(), "delete", this);
    });


    $('input:radio[name="quantilePe"]').change(function () {
        // alert($(this).val());
        quantile = $(this).val();
        renderIndustryBasicChart(peChart, curInd, "pe", parseFloat(quantile), startDate, endDate);
    });

    $('input:radio[name="quantilePb"]').change(function () {
        // alert($(this).val());
        quantile = $(this).val();
        renderIndustryBasicChart(pbChart, curInd, "pb", parseFloat(quantile), startDate, endDate);
    });

    $('input:radio[name="quantilePs"]').change(function () {
        // alert($(this).val());
        quantile = $(this).val();
        renderIndustryBasicChart(psChart, curInd, "ps", parseFloat(quantile), startDate, endDate);
    });

    $('input:radio[name="period"]').change(function () {
        // alert($(this).val());
        var basicInfoPeriod = parseInt($(this).val());
        // peChart.clear();
        // peChart.showLoading();
        if (basicInfoPeriod == 0) {
            basicInfoPeriod = 30;
        }
        startDate = formatDate(new Date(today.getTime() - (365 * basicInfoPeriod * 24 * 60 * 60 * 1000)), "");
        renderIndustryBasicChart(peChart, curInd, "pe", parseFloat(quantile), startDate, endDate);
        renderIndustryBasicChart(pbChart, curInd, "pb", parseFloat(quantile), startDate, endDate);
        renderIndustryBasicChart(psChart, curInd, "ps", parseFloat(quantile), startDate, endDate);

    });

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
        curInd = item.ts_code;
        stockName = item.stock_name;
        market = item.market;
        $("#searchText").val(item.ts_code);
        $("#currentTsCode").val(item.ts_code);
        $("#ind").text(item.industry)
        $(".stock_name").each(function (idx, obj) {
            $(obj).text(item.stock_name);
        });
        // window.history.pushState("", stockName + "基本信息一览", homeEndpoint + "?q=" + tsCode);
        renderChart();
        showIndBasic(item.industry);
        showStockBasic(item.ts_code);
    });

    var showIndBasic = function (industry) {
        var basicType = "pe,pb,ps";
        // var indContainer = $(".industry");
        $.ajax({
            url: stockmarketEndpoint + "industry-latest-daily-basic/" + industry + "/" + basicType + "/",
            success: function (data) {
                var content = data.content;
                for (var key in content) {
                    // $("[id='pct" + key + "'").append("<span class='badge badge-pill badge-danger'>9</span>");
                    $(content[key]).each(function (id, ob) {
                        if (ob.qt == "0.1") {
                            $("[id='iqt.1" + ob.type + "']").text(" " + ob.val);
                        }

                        if (ob.qt == "0.5") {
                            $("[id='iqt.5" + ob.type + "']").text(" " + ob.val);
                        }

                        if (ob.qt == "0.9") {
                            $("[id='iqt.9" + ob.type + "']").text(" " + ob.val);
                        }
                    });
                    // if (content[key] != undefined && content[key].hasOwnProperty("qt")) {

                    // }
                }
            }
        });
    }

    var showStockBasic = function (tsCode) {
        $.ajax({
            url: stockmarketEndpoint + "latest-daily-basic/" + tsCode + "/",
            success: function (data) {
                var content = data.latest_basic;
                $(content).each(function (idx, obj) {
                    for (var k in obj) {
                        $("#" + k).text(" " + obj[k]);
                    }
                });
            }
        });
    }

    // var jsonToChartFormat = function (jsonData, dataType) {
    //     var chartFormat = { 'value': [], 'label': [] };
    //     $(jsonData).each(function (idx, obj) {
    //         chartFormat.value.push(obj[dataType]);
    //         chartFormat.label.push(obj.trade_date);
    //     });
    //     return chartFormat;
    // }

    // var getQuantile = function (chartData) {
    //     var quantileData = { 'qt10': [], 'qt50': [], 'qt90': [] };
    //     var quantileSeq = math.quantileSeq(chartData.value, [0.1, 0.5, 0.9]);
    //     for (var i = 0; i < chartData.value.length; i++) {
    //         quantileData.qt10.push(math.format(quantileSeq[0],2));
    //         quantileData.qt50.push(math.format(quantileSeq[1], 2));
    //         quantileData.qt90.push(math.format(quantileSeq[2], 2));
    //     }
    //     return quantileData;
    // }

    showIndBasic($("#curInd").val());
    // showStockBasic($("#currentTsCode").val());

    // 初始化图表
    initParam();
    renderChart();
});