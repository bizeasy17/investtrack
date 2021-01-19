$(function () {
    var stockmarketEndpoint = '/stockmarket/';
    var homeEndpoint = '/';
    var indexList = "sh,sz,cyb,hs300"
    var freq = "D";
    var histPeriod = 5;
    var histType = "close";
    var tsCode = "";
    var tsCodeNoSfx = "";
    var stockName = "";
    var market = "";

    var today = new Date();
    var startDate = "";
    var endDate = "";

    var strategy = "";
    var strategyName = "";
    var updownPctPeriod = 80;
    var expdPctPeriod = "pct20_period";

    var closeChart = echarts.init(document.getElementById('closeChart'));
    var peChart = echarts.init(document.getElementById('peChart'));
    var psChart = echarts.init(document.getElementById('psChart'));
    var pbChart = echarts.init(document.getElementById('pbChart'));
    var toChart = echarts.init(document.getElementById('toChart'));
    var vrChart = echarts.init(document.getElementById('vrChart'));
    var updownByPeriodChart = echarts.init(document.getElementById('updownByPeriodChart'));
    var periodByUpRangeChart = echarts.init(document.getElementById('periodByUpRangeChart'));


    var initParam = function(){
        tsCode = $("#currentTsCode").val();
        expdPctPeriod = $('input:radio[name="pct_period"]:checked').val();
        updownPctPeriod = $('input:radio[name="period"]:checked').val();
        strategy = $('input:radio[name="bstrategy"]:checked').val();;
        strategyName = $('input:radio[name="bstrategy"]:checked').next().text();

        startDate = formatDate(new Date(today.getTime() - (365 * 2 * 24 * 60 * 60 * 1000)), "");
        endDate = formatDate(today, "");
    }

    var initChart = function () {
        initParam();

        renderCloseChart(tsCode);
        renderCompanyBasicChart(tsCode, startDate, endDate);
        renderUpdownByPeriodChart();
        renderPeriodByUpRangeChart();
    }

    var renderCloseChart = function (tsCode) {
        $.ajax({
            url: stockmarketEndpoint + "stock-hist/" + tsCode + "/" + freq + "/" + histType + "/" + histPeriod + "/",
            success: function (data) {
                option = {
                    tooltip: {
                        trigger: 'axis',
                        position: function (pt) {
                            return [pt[0], '10%'];
                        }
                    },
                    legend: {
                        data: ['Close', 'MA25', 'MA60', 'MA200']
                    },
                    title: {
                        text: '收盘线',
                    },
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
                        data: data.label
                    },
                    yAxis: {
                        type: 'value',
                        boundaryGap: [0, '100%']
                    },
                    dataZoom: [{
                        type: 'inside',
                        start: 100,
                        end: 200
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
                            name: 'Close',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            itemStyle: {
                                color: 'rgb(25, 70, 131)'
                            },
                            data: data.close
                        },
                        {
                            name: 'MA25',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            itemStyle: {
                                color: 'rgb(0, 255, 0)'
                            },
                            data: data.ma25
                        },
                        {
                            name: 'MA60',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            itemStyle: {
                                color: 'rgb(0, 0, 255)'
                            },
                            data: data.ma60
                        },
                        {
                            name: 'MA200',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            itemStyle: {
                                color: 'rgb(25, 0, 31)'
                            },
                            data: data.ma200
                        }
                    ]
                };

                closeChart.setOption(option);
            }
        });
    }

    var renderCompanyBasicChart = function (tsCode, startDate, endDate) {
        $.ajax({
            url: stockmarketEndpoint + "daily-basic/company/" + tsCode + "/" + startDate + "/" + endDate + "/",
            success: function (data) {
                renderPEChart(data.date_label, data.pe, data.pe_ttm);
                renderPSChart(data.date_label, data.ps, data.ps_ttm);
                renderPBChart(data.date_label, data.pb);
                renderTOChart(data.date_label, data.turnover_rate);
                renderVRChart(data.date_label, data.volume_ratio);
            },
            statusCode: {
                403: function () {
                    alert(403);
                },
                404: function () {
                    alert(404);
                },
                500: function () {
                    alert(500);
                }
            }
        });
    }

    var renderPEChart = function (dateLabel, pe, peTTM) {
        option = {
            tooltip: {
                trigger: 'axis',
                position: function (pt) {
                    return [pt[0], '10%'];
                }
            },
            legend: {
                data: ['PE', 'PE-TTM']
            },
            title: {
                text: 'PE-市盈率',
            },
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
                data: dateLabel
            },
            yAxis: {
                type: 'value',
                boundaryGap: [0, '100%']
            },
            dataZoom: [{
                type: 'inside',
                start: 0,
                end: 1000
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
                    name: 'PE',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    sampling: 'average',
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },
                    data: pe
                },
                {
                    name: 'PE-TTM',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    sampling: 'average',
                    itemStyle: {
                        color: 'rgb(0, 255, 0)'
                    },
                    data: peTTM
                },
            ]
        };

        peChart.setOption(option);
    }

    var renderPSChart = function (dateLabel, ps, psTTM) {
        option = {
            tooltip: {
                trigger: 'axis',
                position: function (pt) {
                    return [pt[0], '10%'];
                }
            },
            legend: {
                data: ['PS', 'PS-TTM']
            },
            title: {
                text: '市销率',
            },
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
                data: dateLabel
            },
            yAxis: {
                type: 'value',
                boundaryGap: [0, '100%']
            },
            dataZoom: [{
                type: 'inside',
                start: 0,
                end: 10
            }, {
                start: 0,
                end: 10,
                handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
                handleSize: '80%',
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
                    name: 'PS',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    sampling: 'average',
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },

                    data: ps
                },
                {
                    name: 'PS-TTM',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    sampling: 'average',
                    itemStyle: {
                        color: 'rgb(55, 70, 131)'
                    },

                    data: psTTM
                }
            ]
        };

        psChart.setOption(option);
    }

    var renderPBChart = function (dateLabel, pb) {
        option = {
            tooltip: {
                trigger: 'axis',
                position: function (pt) {
                    return [pt[0], '10%'];
                }
            },
            legend: {
                data: ['PB']
            },
            title: {
                text: 'PB-市净率',
            },
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
                data: dateLabel
            },
            yAxis: {
                type: 'value',
                boundaryGap: [0, '100%']
            },
            dataZoom: [{
                type: 'inside',
                start: 0,
                end: 10
            }, {
                start: 0,
                end: 10,
                handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
                handleSize: '80%',
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
                    name: 'PB',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    sampling: 'average',
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },

                    data: pb
                }
            ]
        };

        pbChart.setOption(option);
    }

    var renderTOChart = function (dateLabel, turnoverRate) {
        option = {
            tooltip: {
                trigger: 'axis',
                position: function (pt) {
                    return [pt[0], '10%'];
                }
            },
            legend: {
                data: ['Turnover Rate']
            },
            title: {
                text: 'Turnover-换手率',
            },
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
                data: dateLabel
            },
            yAxis: {
                type: 'value',
                boundaryGap: [0, '100%']
            },
            dataZoom: [{
                type: 'inside',
                start: 0,
                end: 10
            }, {
                start: 0,
                end: 10,
                handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
                handleSize: '80%',
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
                    name: 'Turnover Rate',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    sampling: 'average',
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },

                    data: turnoverRate
                }
            ]
        };

        toChart.setOption(option);
    }

    var renderVRChart = function (dateLabel, volumeRatio) {
        option = {
            tooltip: {
                trigger: 'axis',
                position: function (pt) {
                    return [pt[0], '10%'];
                }
            },
            legend: {
                data: ['Volume Ratio']
            },
            title: {
                text: 'Volume Ratio-量比',
            },
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
                data: dateLabel
            },
            yAxis: {
                type: 'value',
                boundaryGap: [0, '100%']
            },
            dataZoom: [{
                type: 'inside',
                start: 0,
                end: 10
            }, {
                start: 0,
                end: 10,
                handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
                handleSize: '80%',
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
                    name: 'Volume Ratio',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    sampling: 'average',
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },

                    data: volumeRatio
                }
            ]
        };

        vrChart.setOption(option);
    }

    var renderUpdownByPeriodChart = function () {
        $.ajax({
            url: stockmarketEndpoint + "updown-pct/" + tsCode + "/" + strategy + "/" + updownPctPeriod + "/",
            success: function (data) {
                option = {
                    title: {
                        text: '固定天数内涨跌幅%',
                        // subtext: '数据来自西安兰特水电测控技术有限公司',
                        left: 10
                    },
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            animation: false
                        }
                    },
                    legend: {
                        data: ['涨幅%', '跌幅%'],
                        left: 'center'
                    },
                    toolbox: {
                        feature: {
                            dataZoom: {
                                yAxisIndex: 'none'
                            },
                            restore: {},
                            saveAsImage: {}
                        }
                    },
                    axisPointer: {
                        link: { xAxisIndex: 'all' }
                    },
                    dataZoom: [
                        {
                            show: true,
                            realtime: true,
                            start: 30,
                            end: 70,
                            xAxisIndex: [0, 1]
                        },
                        {
                            type: 'inside',
                            realtime: true,
                            start: 30,
                            end: 70,
                            xAxisIndex: [0, 1]
                        }
                    ],
                    grid: [{
                        left: 50,
                        right: 50,
                        height: '35%'
                    }, {
                        left: 50,
                        right: 50,
                        top: '55%',
                        height: '35%'
                    }],
                    xAxis: [
                        {
                            type: 'category',
                            boundaryGap: false,
                            axisLine: { onZero: true },
                            data: data.date_label
                        },
                        {
                            gridIndex: 1,
                            type: 'category',
                            boundaryGap: false,
                            axisLine: { onZero: true },
                            data: data.date_label,
                            position: 'top'
                        }
                    ],
                    yAxis: [
                        {
                            name: '涨幅%',
                            type: 'value',
                            max: 500,
                            axisLabel: {
                                formatter: '{value} %'
                            },
                        },
                        {
                            gridIndex: 1,
                            name: '跌幅%',
                            type: 'value',
                            inverse: false,
                            axisLabel: {
                                formatter: '{value} %'
                            },
                        },
                    ],
                    series: [
                        {
                            name: '涨幅%',
                            type: 'line',
                            symbolSize: 8,
                            hoverAnimation: false,
                            data: data.up_pct
                        },
                        {
                            name: '跌幅%',
                            type: 'line',
                            xAxisIndex: 1,
                            yAxisIndex: 1,
                            symbolSize: 8,
                            hoverAnimation: false,
                            data: data.down_pct
                        }
                    ]
                };
                updownByPeriodChart.setOption(option);
            },
            statusCode: {
                403: function () {

                },
                404: function () {

                },
                500: function () {

                }
            }
        });
    }

    var renderPeriodByUpRangeChart = function () {
        $.ajax({
            url: stockmarketEndpoint + "exp-pct/" + tsCode + "/" + strategy + "/" + expdPctPeriod + "/" + freq + "/",
            success: function (data) {
                option = {
                    title: {
                        text: '期望涨幅所需天数'
                        // subtext: 'Feature Sample: Gradient Color, Shadow, Click Zoom'
                    },
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'cross',
                            crossStyle: {
                                color: '#999'
                            }
                        }
                    },
                    toolbox: {
                        feature: {
                            dataView: { show: true, readOnly: false },
                            magicType: { show: true, type: ['line', 'bar'] },
                            restore: { show: true },
                            saveAsImage: { show: true }
                        }
                    },
                    legend: {
                        data: ['%涨幅天数']//, '降水量', '平均温度']
                    },
                    xAxis: [
                        {
                            type: 'category',
                            data: data.date_label,
                            axisPointer: {
                                type: 'shadow'
                            }
                        }
                    ],
                    yAxis: [
                        {
                            type: 'value',
                            name: '天数',
                            min: 0,
                            // max: 250,
                            interval: 50
                        }
                        // {
                        //     type: 'value',
                        //     name: '温度',
                        //     min: 0,
                        //     max: 25,
                        //     interval: 5,
                        //     axisLabel: {
                        //         formatter: '{value} °C'
                        //     }
                        // }
                    ],
                    series: [
                        {
                            name: '%涨幅天数',
                            type: 'bar',
                            data: data.exp_pct
                        }
                        // {
                        //     name: '降水量',
                        //     type: 'bar',
                        //     data: [2.6, 5.9, 9.0, 26.4, 28.7, 70.7, 175.6, 182.2, 48.7, 18.8, 6.0, 2.3]
                        // },
                        // {
                        //     name: '平均温度',
                        //     type: 'line',
                        //     yAxisIndex: 1,
                        //     data: [2.0, 2.2, 3.3, 4.5, 6.3, 10.2, 20.3, 23.4, 23.0, 16.5, 12.0, 6.2]
                        // }
                    ]
                };

                periodByUpRangeChart.setOption(option);
            },
            statusCode: {
                403: function () {

                },
                404: function () {

                },
                500: function () {

                }
            }
        });

    }

    var refreshCompanyClose = function (tsCode, startDate, endDate) {
        $.ajax({
            url: stockmarketEndpoint + "company-daily-basic/" + tsCode + "/" + startDate + "/" + endDate + "/",
            success: function (data) {
                closeChart.setOption({
                    xAxis: {
                        data: data.categories
                    },
                    series: [{
                        // 根据名字对应到相应的系列
                        name: '销量',
                        data: data.data
                    }]
                });
            }
        });
    }

    var refreshCompanyDailyBasic = function (tsCode, startDate, endDate) {
        $.ajax({
            url: stockmarketEndpoint + "company-daily-basic/" + tsCode + "/" + startDate + "/" + endDate + "/",
            success: function (data) {
                $(data).each(function (idx, obj) {
                });
            }
        });
    }

    var refreshCompanyBasic = function (tsCode) {
        $.ajax({
            url: stockmarketEndpoint + "company-basic/" + tsCode + "/",
            success: function (data) {
                $(data).each(function (idx, obj) {
                });
            }
        });
    }
    // 初始化图表
    initChart();

    $('#searchText').autoComplete({
        resolver: 'custom',
        // preventEnter: true,
        formatResult: function (item) {
            return {
                value: item.id,
                text: item.id + " - " + item.text,
                html: [
                    item.id + " - " + item.text + "[" + item.market + "], " + item.area + ", " + item.industry + ", " + item.list_date + "上市",
                ]
            };
        },
        events: {
            search: function (qry, callback) {
                // let's do a custom ajax call
                $.ajax(
                    stockmarketEndpoint + 'listed_companies/' + $('#searchText').val(),
                ).done(function (res) {
                    callback(res.results)
                });
            }
        }
    });

    $('#searchText').on('autocomplete.select', function (evt, item) {
        console.log('select');
        tsCodeNoSfx = item.id;
        tsCode = item.ts_code;
        stockName = item.text;
        market = item.market;
        $("#searchText").val(tsCode);
        window.history.pushState("", stockName + "基本信息一览", homeEndpoint + "?q=" + tsCode);
    });
});