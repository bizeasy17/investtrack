$(function () {
    var hongguanEndpoint = '/hongguan/';
    var homeEndpoint = '/';
    var indexList = "sh,sz,cyb,hs300"
    var freq = "D";
    var histPeriod = 3;
    var histType = "close";
    var tsCode = "";
    var tsCodeNoSfx = "";
    var stockName = "";
    var market = "";
    var pctOnPeriodDates = "";
    var periodOnPctDates = "";

    var bstr;
    var sstr;

    var today = new Date();
    var startQ = "199001";
    var endQ = "202101";
    var startDate = "";
    var endDate = "";
    // var countYear = 3;

    var strategyCode = "";
    var strategyName = "";
    var updownPctPeriod = 80;
    var expdPctPeriod = "pct20_period";

    var m0m1m2Chart = echarts.init(document.getElementById('moneySupplyChart'));
    // var m0m1m2YoyChart = echarts.init(document.getElementById('moneySuppyYoyChart'));
    // var m0m1m2MomChart = echarts.init(document.getElementById('moneySupplyMomChart'));
    var gdpChart = echarts.init(document.getElementById('gdpChart'));
    var gdpIndChart = echarts.init(document.getElementById('gdpIndChart'));

    var cpiChart = echarts.init(document.getElementById('cpiChart'));
    var ppiChart = echarts.init(document.getElementById('ppiChart'));

    var shiborChart = echarts.init(document.getElementById('shiborChart'));
    var liborChart = echarts.init(document.getElementById('liborChart'));
    var hiborChart = echarts.init(document.getElementById('hiborChart'));
    var shiborLprChart = echarts.init(document.getElementById('lprChart'));

    var initParam = function () {
        tsCode = $("#currentTsCode").val();
        expdPctPeriod = $('input:radio[name="pct_period"]:checked').val();
        updownPctPeriod = $('input:radio[name="period"]:checked').val();
        strategyCode = $('input:radio[name="bstrategy"]:checked').val();
        strategyName = $('input:radio[name="bstrategy"]:checked').next().text();

        idxMa25Filter = $('input:radio[name="radioIndexMA25"]:checked').val();
        idxMa60Filter = $('input:radio[name="radioIndexMA60"]:checked').val();
        idxMa200Filter = $('input:radio[name="radioIndexMA200"]:checked').val();
        // idxVolFilter = $('#rangeIndexVolume').val();

        stkMa25Filter = $('input:radio[name="radioStockMA25"]:checked').val();
        stkMa60Filter = $('input:radio[name="radioStockMA60"]:checked').val();
        stkMa200Filter = $('input:radio[name="radioStockMA200"]:checked').val();
        // stkVolFilter = $('#rangeStockVolume').val();

        startDate = formatDate(new Date(today.getTime() - (365 * histPeriod * 24 * 60 * 60 * 1000)), "");
        endDate = formatDate(today, "");

        // initBTestDates();
    }

    // var initVolRange = function() {
    //     $.ajax({
    //         url: stockmarketEndpoint + "updown-pct-dates/" + tsCode + "/" + strategyCode + "/" + updownPctPeriod + "/" + freq + "/",
    //         success: function (data) {
    //             pctOnPeriodDates = data;
    //         }
    //     });

    //     $.ajax({
    //         url: stockmarketEndpoint + "exp-pct-dates/" + tsCode + "/" + strategyCode + "/" + expdPctPeriod + "/" + freq + "/",
    //         success: function (data) {
    //             periodOnPctDates = data;
    //         }
    //     });
    // }

    var renderChart = function () {
        renderGDPChart();
        renderGDPByIndChart();
        renderM0M1M2Chart();
        renderShiborChart();
        renderLiborChart();
        renderHiborChart();
        renderShiborLPRChart();
        renderPPIChart();
        renderCPIChart();
        // renderCompanyBasicChart(tsCode, startDate, endDate);
        // renderUpdownByPeriodChart();
        // renderPeriodByUpRangeChart();
    }

    var renderM0M1M2Chart = function () {
        $.ajax({
            url: hongguanEndpoint + "money-supply/" + startDate + "/" + endDate + "/",
            success: function (data) {
                option = {
                    tooltip: {
                        trigger: 'axis',
                        position: function (pt) {
                            return [pt[0], '10%'];
                        }
                    },
                    legend: {
                        data: ['M0', 'M1', 'M2','M0同比', 'M1同比', 'M2同比']
                    },
                    title: {
                        text: '货币供应量',
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
                        axisTick: {
                            alignWithLabel: true
                        },
                        data: data.date_label
                    },
                    yAxis: [{
                        type: 'value',
                        boundaryGap: [0, '100%']
                    },
                    {
                        type: 'value',
                        name: '增幅%',
                        axisLabel: {
                            formatter: '{value} %'
                        }
                    }
                    ],
                    dataZoom: [{
                        type: 'inside',
                        start: data.m_range[0],
                        end: data.m_range[1]
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
                            name: 'M0',
                            type: 'bar',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            // itemStyle: {
                            //     color: 'rgb(25, 70, 131)'
                            // },
                            data: data.m0,
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
                            name: 'M1',
                            type: 'bar',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            // itemStyle: {
                            //     color: 'rgb(0, 255, 0)'
                            // },
                            data: data.m1,
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
                            name: 'M2',
                            type: 'bar',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            // itemStyle: {
                            //     color: 'rgb(0, 0, 255)'
                            // },
                            data: data.m2,
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
                            name: 'M0同比',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            // itemStyle: {
                            //     color: 'rgb(25, 70, 131)'
                            // },
                            yAxisIndex: 1,
                            data: data.m0_yoy
                        },
                        {
                            name: 'M1同比',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            // itemStyle: {
                            //     color: 'rgb(0, 255, 0)'
                            // },
                            yAxisIndex: 1,
                            data: data.m1_yoy
                        },
                        {
                            name: 'M2同比',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            // itemStyle: {
                            //     color: 'rgb(0, 0, 255)'
                            // },
                            yAxisIndex: 1,
                            data: data.m2_yoy
                        },
                    ]
                };

                m0m1m2Chart.setOption(option);
            }
        });
    }

    var renderGDPChart = function () {
        $.ajax({
            url: hongguanEndpoint + "gdp/" + startQ + "/" + endQ + "/",
            success: function (data) {
                option = {
                    tooltip: {
                        trigger: 'axis',
                        position: function (pt) {
                            return [pt[0], '10%'];
                        }
                    },
                    legend: {
                        data: ['国内生产总值GDP','同比']
                    },
                    title: {
                        text: '国内生产总值GDP',
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
                        axisTick: {
                            alignWithLabel: true
                        },
                        data: data.date_label
                    },
                    yAxis: [{
                        type: 'value',
                        boundaryGap: [0, '100%']
                    },
                    {
                        type: 'value',
                        name: '增幅%',
                        axisLabel: {
                            formatter: '{value} %'
                        }
                    }
                    ],
                    dataZoom: [{
                        type: 'inside',
                        start: data.m_range[0],
                        end: data.m_range[1]
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
                            name: '国内生产总值GDP',
                            type: 'bar',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            // itemStyle: {
                            //     color: 'rgb(25, 70, 131)'
                            // },
                            data: data.gdp,
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
                            name: '同比',
                            type: 'line',
                            smooth: true,
                            yAxisIndex: 1,
                            // itemStyle: {
                            //     color: 'rgb(25, 70, 131)'
                            // },
                            data: data.gdp_yoy,
                        }
                    ]
                };

                gdpChart.setOption(option);
            }
        });
    }

    var renderGDPByIndChart = function () {
        $.ajax({
            url: hongguanEndpoint + "gdp/" + startQ + "/" + endQ + "/",
            success: function (data) {
                option = {
                    tooltip: {
                        trigger: 'axis',
                        position: function (pt) {
                            return [pt[0], '10%'];
                        }
                    },
                    legend: {
                        data: ['第一产业', '第二产业', '第三产业']
                    },
                    title: {
                        text: '产业GDP',
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
                        axisTick: {
                            alignWithLabel: true
                        },
                        data: data.date_label
                    },
                    yAxis: {
                        type: 'value',
                        boundaryGap: [0, '100%']
                    },
                    dataZoom: [{
                        type: 'inside',
                        start: data.m_range[0],
                        end: data.m_range[1]
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
                            name: '第一产业',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            // itemStyle: {
                            //     color: 'rgb(25, 70, 131)'
                            // },
                            data: data.pi,
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
                            name: '第二产业',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            // itemStyle: {
                            //     color: 'rgb(0, 255, 0)'
                            // },
                            data: data.si,
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
                            name: '第三产业',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            // itemStyle: {
                            //     color: 'rgb(0, 0, 255)'
                            // },
                            data: data.ti,
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

                gdpIndChart.setOption(option);
            }
        });
    }

    var renderCompanyBasicChart = function (tsCode, startDate, endDate) {
        $.ajax({
            url: hongguanEndpoint + "daily-basic/company/" + tsCode + "/" + startDate + "/" + endDate + "/",
            success: function (data) {
                renderShiborChart(data.date_label, data.pe, data.pe_ttm, data.pe_50qt, data.pe_ttm_50qt, data.pe_range[0], data.pe_range[1]);
                renderLiborChart(data.date_label, data.ps, data.ps_ttm, data.ps_50qt, data.ps_ttm_50qt, data.ps_range[0], data.ps_range[1]);
                renderHiborChart(data.date_label, data.pb, data.pb_50qt, data.pb_range[0], data.pb_range[1]);
                renderShiborLPRChart(data.date_label, data.turnover_rate, data.to_50qt, data.to_range[0], data.to_range[1]);
                renderVRChart(data.date_label, data.volume_ratio, data.vr_50qt, data.vr_range[0], data.vr_range[1]);
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

    var renderShiborChart = function () {
        $.ajax({
            url: hongguanEndpoint + "shibor/" + startDate + "/" + endDate + "/",
            success: function (data) {
                option = {
                    tooltip: {
                        trigger: 'axis',
                        position: function (pt) {
                            return [pt[0], '10%'];
                        }
                    },
                    legend: {
                        data: ['隔夜', '1y']
                    },
                    title: {
                        text: 'Shibor',
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
                        axisTick: {
                            alignWithLabel: true
                        },
                        data: data.date_label
                    },
                    yAxis: {
                        type: 'value',
                        boundaryGap: [0, '100%']
                    },
                    dataZoom: [{
                        type: 'inside',
                        start: data.m_range[0],
                        end: data.m_range[1]
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
                            name: '隔夜',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            // itemStyle: {
                            //     color: 'rgb(25, 70, 131)'
                            // },
                            data: data.shibor_on,
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
                            name: '1y',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            // itemStyle: {
                            //     color: 'rgb(255, 0, 0)'
                            // },
                            data: data.shibor_1y,
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
                        }
                    ]
                }

                shiborChart.setOption(option);

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

    var renderLiborChart = function () {
        $.ajax({
            url: hongguanEndpoint + "libor/" + startDate + "/" + endDate + "/",
            success: function (data) {
                option = {
                    tooltip: {
                        trigger: 'axis',
                        position: function (pt) {
                            return [pt[0], '10%'];
                        }
                    },
                    legend: {
                        data: ['隔夜', '1y']
                    },
                    title: {
                        text: 'Libor',
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
                        data: data.date_label
                    },
                    yAxis: {
                        type: 'value',
                        boundaryGap: [0, '100%']
                    },
                    dataZoom: [{
                        type: 'inside',
                        start: data.m_range[0],
                        end: data.m_range[1]
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
                            name: '隔夜',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            // itemStyle: {
                            //     color: 'rgb(25, 70, 131)'
                            // },
                            data: data.libor_on,
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
                            name: '1y',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            // itemStyle: {
                            //     color: 'rgb(255, 0, 0)'
                            // },
                            data: data.libor_12m,
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
                        }
                    ]
                }

                liborChart.setOption(option);

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

    var renderHiborChart = function () {
        $.ajax({
            url: hongguanEndpoint + "hibor/" + startDate + "/" + endDate + "/",
            success: function (data) {
                option = {
                    tooltip: {
                        trigger: 'axis',
                        position: function (pt) {
                            return [pt[0], '10%'];
                        }
                    },
                    legend: {
                        data: ['隔夜', '1y']
                    },
                    title: {
                        text: 'Hibor',
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
                        data: data.date_label
                    },
                    yAxis: {
                        type: 'value',
                        boundaryGap: [0, '100%']
                    },
                    dataZoom: [{
                        type: 'inside',
                        start: data.m_range[0],
                        end: data.m_range[1]
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
                            name: '隔夜',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            // itemStyle: {
                            //     color: 'rgb(25, 70, 131)'
                            // },
                            data: data.hibor_on,
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
                            name: '1y',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            // itemStyle: {
                            //     color: 'rgb(255, 0, 0)'
                            // },
                            data: data.hibor_12m,
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
                        }
                    ]
                }

                hiborChart.setOption(option);
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

    var renderShiborLPRChart = function () {
        $.ajax({
            url: hongguanEndpoint + "shibor-lpr/" + startDate + "/" + endDate + "/",
            success: function (data) {
                option = {
                    tooltip: {
                        trigger: 'axis',
                        position: function (pt) {
                            return [pt[0], '10%'];
                        }
                    },
                    legend: {
                        data: ['LPR']
                    },
                    title: {
                        text: 'LPR',
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
                        data: data.date_label
                    },
                    yAxis: {
                        type: 'value',
                        boundaryGap: [0, '100%']
                    },
                    dataZoom: [{
                        type: 'inside',
                        start: data.m_range[0],
                        end: data.m_range[1]
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
                            name: 'LPR',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            // itemStyle: {
                            //     color: 'rgb(25, 70, 131)'
                            // },
                            data: data.shibor_lpr,
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
                        }
                    ]
                }

                shiborLprChart.setOption(option);
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

    var renderCPIChart = function () {
        // var filters = buildBTestFilter();
        $.ajax({
            url: hongguanEndpoint + "cpi/" + startDate + "/" + endDate + "/",
            success: function (data) {
                option = {
                    title: {
                        text: 'CPI',
                        // subtext: '数据来自西安兰特水电测控技术有限公司',
                        // left: 10
                    },
                    tooltip: {
                        trigger: 'axis',
                        position: function (pt) {
                            return [pt[0], '10%'];
                        }
                    },
                    legend: {
                        data: ['全国', '城镇', '农村','全国同比', '城镇同比', '农村同比'],
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
                    xAxis: {
                        type: 'category',
                        axisTick: {
                            alignWithLabel: true
                        },
                        data: data.date_label
                    },
                    yAxis:[ {
                        type: 'value',
                        name: '指数',
                        boundaryGap: [0, '100%']
                    },
                    {
                        type: 'value',
                        name: '增幅%',
                        axisLabel: {
                            formatter: '{value} %'
                        }
                    }
                    ],
                    dataZoom: [{
                        type: 'inside',
                        start: data.m_range[0],
                        end: data.m_range[1]
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
                            name: '全国',
                            type: 'bar',
                            hoverAnimation: false,
                            data: data.nt,
                        },
                        {
                            name: '城镇',
                            type: 'bar',
                            hoverAnimation: false,
                            data: data.town
                        },
                        {
                            name: '农村',
                            type: 'bar',
                            hoverAnimation: false,
                            data: data.cnt,
                        },
                        {
                            name: '全国同比',
                            type: 'line',
                            hoverAnimation: false,
                            data: data.nt_yoy,
                            yAxisIndex: 1
                        },
                        {
                            name: '城镇同比',
                            type: 'line',
                            hoverAnimation: false,
                            data: data.town_yoy,
                            yAxisIndex: 1
                        },
                        {
                            name: '农村同比',
                            type: 'line',
                            hoverAnimation: false,
                            data: data.cnt_yoy,
                            yAxisIndex: 1
                        }
                    ]

                };

                cpiChart.setOption(option);
            },
            statusCode: {
                403: function () {

                },
                404: function () {
                    $("#cpiSubtitle").text("暂无记录！");
                },
                500: function () {

                }
            }
        });
    }

    var renderPPIChart = function () {
        $.ajax({
            url: hongguanEndpoint + "ppi/" + startDate + "/" + endDate + "/",
            success: function (data) {
                option = {
                    title: {
                        text: 'PPI'
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
                        data: ['全部工业品同比', '全部工业品环比','全部工业品累计同比']//, '降水量', '平均温度']
                    },
                    xAxis: [
                        {
                            type: 'category',
                            data: data.date_label,
                            axisTick: {
                                alignWithLabel: true
                            },
                        }
                    ],
                    yAxis: [
                        {
                            type: 'value',
                            name: '%',
                            interval: 5,
                            axisLabel: {
                                formatter: '{value} %'
                            }
                        }
                    ],dataZoom: [{
                        type: 'inside',
                        start: data.m_range[0],
                        end: data.m_range[1]
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
                            name: '全部工业品同比',
                            type: 'line',
                            data: data.ppi_mp_yoy
                        },
                        {
                            name: '全部工业品环比',
                            type: 'line',
                            data: data.ppi_mp_mom
                        },
                        {
                            name: '全部工业品累计同比',
                            type: 'line',
                            data: data.ppi_accu
                        }
                    ]
                };

                ppiChart.setOption(option);
            },
            statusCode: {
                403: function () {

                },
                404: function () {
                    $("#targetPctSubtitle").text("上市时间小于3年，暂无回测记录！");
                },
                500: function () {

                }
            }
        });

    }

    var refreshCompanyClose = function (tsCode, startDate, endDate) {
        $.ajax({
            url: hongguanEndpoint + "company-daily-basic/" + tsCode + "/" + startDate + "/" + endDate + "/",
            success: function (data) {
                m0m1m2Chart.setOption({
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
            url: hongguanEndpoint + "company-daily-basic/" + tsCode + "/" + startDate + "/" + endDate + "/",
            success: function (data) {
                $(data).each(function (idx, obj) {
                });
            }
        });
    }

    var refreshCompanyBasic = function (tsCode) {
        $.ajax({
            url: hongguanEndpoint + "company-basic/" + tsCode + "/",
            success: function (data) {
                $(data).each(function (idx, obj) {
                });
            }
        });
    }

    var idxMa25FilterOn = false, idxMa60FilterOn = false, idxMa200FilterOn = false, idxVolFilterOn = false;
    var idxMa25Filter = "", idxMa60Filter = "", idxMa200Filter = "", idxVolFilter = "";
    var stkMa25FilterOn = false, stkMa60FilterOn = false, stkMa200FilterOn = false, stkVolFilterOn = false;
    var stkMa25Filter = "", stkMa60Filter = "", stkMa200Filter = "", stkVolFilter = "";
    var idxKey = "I", stkKey = "E";

    var buildBTestFilter = function () {
        var filter = "";
        filter += "{'" + idxKey + "':[";
        if (idxMa25FilterOn) {
            filter += "'" + idxMa25Filter + "',";
        }
        if (idxMa60FilterOn) {
            filter += "'" + idxMa60Filter + "',";
        }
        if (idxMa200FilterOn) {
            filter += "'" + idxMa200Filter + "',";
        }
        if (idxVolFilterOn) {
            filter += "'vol > " + idxVolFilter + "',";
        }
        filter += "]";

        filter += ",'" + stkKey + "':[";
        if (stkMa25FilterOn) {
            filter += "'" + stkMa25Filter + "',";
        }
        if (stkMa60FilterOn) {
            filter += "'" + stkMa60Filter + "',";
        }
        if (stkMa200FilterOn) {
            filter += "'" + stkMa200Filter + "',";
        }
        if (stkVolFilterOn) {
            filter += "'vol > " + stkVolFilter + "',";
        }
        filter += "]}";

        return filter;
    }

    $('#switchIndexMA25').change(function () {
        // alert($(this).is(":checked"));
        idxMa25FilterOn = $(this).is(":checked");
        renderCPIChart();
        renderPPIChart();
    });

    $('#switchIndexMA60').change(function () {
        idxMa60FilterOn = $(this).is(":checked");
        renderCPIChart();
        renderPPIChart();
    });

    $('#switchIndexMA200').change(function () {
        idxMa200FilterOn = $(this).is(":checked");
        renderCPIChart();
        renderPPIChart();
    });

    $('#switchIndexVol').change(function () {
        idxVolFilterOn = $(this).is(":checked");
        renderCPIChart();
        renderPPIChart();
    });

    $('#switchStockMA25').change(function () {
        stkMa25FilterOn = $(this).is(":checked");
        renderCPIChart();
        renderPPIChart();
    });

    $('#switchStockMA60').change(function () {
        stkMa60FilterOn = $(this).is(":checked");
        renderCPIChart();
        renderPPIChart();
    });

    $('#switchStockMA200').change(function () {
        stkMa200FilterOn = $(this).is(":checked");
        renderCPIChart();
        renderPPIChart();
    });

    $('#switchStockVol').change(function () {
        stkVolFilterOn = $(this).is(":checked");
        renderCPIChart();
        renderPPIChart();
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="radioIndexMA25"]').change(function () {
        // alert($(this).val());
        if (idxMa25FilterOn) {
            idxMa25Filter = $(this).val();
            renderCPIChart();
            renderPPIChart();
        }
    });

    $('input:radio[name="radioIndexMA60"]').change(function () {
        // alert($(this).val());
        if (idxMa60FilterOn) {
            idxMa60Filter = $(this).val();
            renderCPIChart();
            renderPPIChart();
        }
    });

    $('input:radio[name="radioIndexMA200"]').change(function () {
        // alert($(this).val());
        if (idxMa200FilterOn) {
            idxMa200Filter = $(this).val();
            renderCPIChart();
            renderPPIChart();
        }
    });

    $("#rangeIndexVolume").change(function () {
        // alert($(this).val());
        idxVolFilter = $(this).val();

        if (idxVolFilterOn) {
            renderCPIChart();
            renderPPIChart();
        }
    });

    $('input:radio[name="radioStockMA25"]').change(function () {
        // alert($(this).val());
        if (stkMa25FilterOn) {
            stkMa25Filter = $(this).val();
            renderCPIChart();
            renderPPIChart();
        }
    });

    $('input:radio[name="radioStockMA60"]').change(function () {
        // alert($(this).val());
        if (stkMa60FilterOn) {
            stkMa25Filter = $(this).val();
            renderCPIChart();
            renderPPIChart();
        }
    });

    $('input:radio[name="radioStockMA200"]').change(function () {
        // alert($(this).val());
        if (stkMa200FilterOn) {
            stkMa200Filter = $(this).val();
            renderCPIChart();
            renderPPIChart();
        }
    });

    $("#rangeStockVolume").change(function () {
        // alert($(this).val());
        stkVolFilter = $(this).val();

        if (stkVolFilterOn) {
            renderCPIChart();
            renderPPIChart();
        }
    });

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
                    hongguanEndpoint + 'listed_companies/' + $('#searchText').val(),
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
        // window.history.pushState("", stockName + "基本信息一览", homeEndpoint + "?q=" + tsCode);
        renderChart();
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="bstrategy"]').change(function () {
        // 页面默认加载上证指数日K（D)
        // 页面默认加载上证指数日K（D)
        bstr = $(this)
        if (sstr != undefined) {
            $(sstr).removeAttr("checked")
            $(sstr).parent("label").removeClass("active");
        }

        strategyCode = this.value;
        strategyName = $(this).next().text();
        // showHelpInfo();
        renderCPIChart();
        renderPPIChart();
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="sstrategy"]').change(function () {
        // 页面默认加载上证指数日K（D)
        sstr = $(this);
        if (bstr != undefined) {
            $(bstr).removeAttr("checked")
            $(bstr).parent("label").removeClass("active");
        }

        strategyCode = this.value;
        strategyName = $(this).next().text();
        // showHelpInfo();
        renderCPIChart();
        renderPPIChart();
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="pct_period"]').change(function () {
        // 页面默认加载上证指数日K（D)
        expdPctPeriod = this.value;
        // showHelpInfo();
        renderPPIChart();
    });

    // 根据选择的周期，显示该周期中最大跌幅，最大涨幅
    $('input:radio[name="period"]').change(function () {
        // 页面默认加载上证指数日K（D)
        updownPctPeriod = this.value;
        // showHelpInfo();
        renderCPIChart();
    });

    // 初始化图表
    initParam();
    renderChart();
});