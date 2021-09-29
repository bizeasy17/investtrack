$(function () {
    var stockmarketEndpoint = '/stockmarket/';
    var investorEndpoint = "/investors/";
    var homeEndpoint = '/';
    var indexList = "sh,sz,cyb,hs300"
    var freq = "D";
    var closePeriod = 5;
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
    var startDate = "";
    var endDate = "";
    // var countYear = 3;

    var strategyCode = "";
    var strategyName = "";
    var updownPctPeriod = 80;
    var expdPctPeriod = "pct20_period";

    var closeChart = echarts.init(document.getElementById('closeChart'));
    var peChart = echarts.init(document.getElementById('peChart'));
    var peTTMChart = echarts.init(document.getElementById('peTTMChart'));
    var psChart = echarts.init(document.getElementById('psChart'));
    var psTTMChart = echarts.init(document.getElementById('psTTMChart'));
    var pbChart = echarts.init(document.getElementById('pbChart'));
    var toChart = echarts.init(document.getElementById('toChart'));
    var vrChart = echarts.init(document.getElementById('vrChart'));
    // var updownByPeriodChart = echarts.init(document.getElementById('updownByPeriodChart'));
    // var periodByUpRangeChart = echarts.init(document.getElementById('periodByUpRangeChart'));


    var initParam = function () {
        tsCode = $("#currentTsCode").val();
        // expdPctPeriod = $('input:radio[name="pct_period"]:checked').val();
        // updownPctPeriod = $('input:radio[name="period"]:checked').val();
        // strategyCode = $('input:radio[name="bstrategy"]:checked').val();
        // strategyName = $('input:radio[name="bstrategy"]:checked').next().text();
        // bstr = $('input:radio[name="bstrategy"]:checked');

        closePeriod = $('input:radio[name="closePeriod"]:checked').val();

        startDate = formatDate(new Date(today.getTime() - (365 * closePeriod * 24 * 60 * 60 * 1000)), "");
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
        showCompanyBasic(tsCode);
        renderCloseChart(tsCode);
        renderCompanyBasicChart(tsCode, startDate, endDate);
        // renderUpdownByPeriodChart();
        // renderPeriodByUpRangeChart();
    }

    var showCompanyBasic = function (tsCode) {
        $.ajax({
            url: stockmarketEndpoint + "company-basic/" + tsCode + "/",
            success: function (data) {
                if ($("#companyName").parent().children().length > 1) {
                    $("#companyName").parent().children().last().remove();
                }
                if ($("#setupDate").parent().children().length > 1) {
                    $("#setupDate").parent().children().last().remove();
                }
                if ($("#capital").parent().children().length > 1) {
                    $("#capital").parent().children().last().remove();
                }
                if ($("#website").parent().children().length > 1) {
                    $("#website").parent().children().last().remove();
                }
                if ($("#province").parent().children().length > 1) {
                    $("#province").parent().children().last().remove();
                }
                if ($("#city").parent().children().length > 1) {
                    $("#city").parent().children().last().remove();
                }
                if ($("#industry").parent().children().length > 1) {
                    $("#industry").parent().children().last().remove();
                }
                if ($("#chairman").parent().children().length > 1) {
                    $("#chairman").parent().children().last().remove();
                }
                if ($("#manager").parent().children().length > 1) {
                    $("#manager").parent().children().last().remove();
                }
                if ($("#employees").parent().children().length > 1) {
                    $("#employees").parent().children().last().remove();
                }
                $("#companyName").parent().append("<span>" + data[0].company_name + "</span>");
                $("#setupDate").parent().append("<span>" + data[0].setup_date + "</span>");
                $("#capital").parent().append("<span>" + data[0].reg_capital + "万</span>");
                $("#website").parent().append('<a href="http://' + data[0].website + '"><span>http://' + data[0].website + "</span></a>");
                $("#province").parent().append("<span>" + data[0].province + "</span>");
                $("#city").parent().append("<span>" + data[0].city + "</span>");
                $("#industry").parent().append("<span>" + data[0].main_business + "</span>");
                $("#chairman").parent().append("<span>" + data[0].chairman + "</span>");
                $("#manager").parent().append("<span>" + data[0].manager + "</span>");
                $("#employees").parent().append("<span>" + data[0].employees + "</span>");
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

    var renderCloseChart = function (tsCode) {
        var zoomMin = 75;
        var zoomMax = 100;
        $.ajax({
            url: stockmarketEndpoint + "close/" + tsCode + "/" + freq + "/" + closePeriod + "/",
            success: function (data) {
                option = {
                    tooltip: {
                        trigger: 'axis',
                        position: function (pt) {
                            return [pt[0], '10%'];
                        }
                    },
                    legend: {
                        data: ['收', '25', '60', '200']
                    },
                    // title: {
                    //     text: '收盘线',
                    //     left: '5%',
                    // },
                    // toolbox: {
                    //     feature: {
                    //         dataZoom: {
                    //             yAxisIndex: 'none'
                    //         },
                    //         restore: {},
                    //         saveAsImage: {}
                    //     }
                    // },
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
                            name: '收',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            itemStyle: {
                                color: 'rgb(25, 70, 131)'
                            },
                            data: data.close,
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
                            name: '25',
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
                            name: '60',
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
                            name: '200',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            sampling: 'average',
                            itemStyle: {
                                color: 'rgb(25, 0, 31)'
                            },
                            data: data.ma200
                        },
                        {
                            name: '低位',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            itemStyle: {
                                color: 'rgb(0, 255, 0)'
                            },
                            data: data.close10
                        },
                        {
                            name: '高位',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            itemStyle: {
                                color: 'rgb(255, 0, 0)'
                            },
                            data: data.close90
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
                renderPEChart(data.date_label, data.pe, data.pe_10qt, data.pe_50qt, data.pe_90qt, data.pe_range[0], data.pe_range[1]);
                renderPETTMChart(data.date_label, data.pe_ttm, data.pe_ttm_10qt, data.pe_ttm_50qt, data.pe_ttm_90qt, data.pe_range[0], data.pe_range[1]);
                renderPSChart(data.date_label, data.ps, data.ps_10qt, data.ps_50qt, data.ps_90qt, data.ps_range[0], data.ps_range[1]);
                renderPSTTMChart(data.date_label, data.ps_ttm, data.ps_ttm_10qt, data.ps_ttm_50qt, data.ps_ttm_90qt, data.ps_range[0], data.ps_range[1]);
                renderPBChart(data.date_label, data.pb, data.pb_10qt, data.pb_50qt, data.pb_90qt, data.pb_range[0], data.pb_range[1]);
                renderTOChart(data.date_label, data.turnover_rate, data.to_50qt, data.to_range[0], data.to_range[1]);
                renderVRChart(data.date_label, data.volume_ratio, data.vr_50qt, data.vr_range[0], data.vr_range[1]);
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

    var renderPEChart = function (dateLabel, pe, pe10qt, pe50qt, pe90qt, zoomMin, zoomMax) {
        option = {
            tooltip: {
                trigger: 'axis',
                position: function (pt) {
                    return [pt[0], '10%'];
                }
            },
            legend: {
                data: ['PE', 'PE中位']
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
                data: dateLabel
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
                    name: 'PE',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    sampling: 'average',
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },
                    data: pe,
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
                    data: pe10qt
                },
                {
                    name: 'PE中位',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    sampling: 'average',
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },
                    data: pe50qt
                },
                {
                    name: '高位',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    itemStyle: {
                        color: 'rgb(255, 0, 0)'
                    },
                    data: pe90qt
                }
            ]
        };

        peChart.setOption(option);
    }

    var renderPETTMChart = function (dateLabel, peTTM, peTTM10qt, peTTM50qt, peTTM90qt, zoomMin, zoomMax) {
        option = {
            tooltip: {
                trigger: 'axis',
                position: function (pt) {
                    return [pt[0], '10%'];
                }
            },
            legend: {
                data: ['PE(动)', 'PE(动)中位']
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
                data: dateLabel
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
                    name: 'PE(动)',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    sampling: 'average',
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },
                    data: peTTM,
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
                    data: peTTM10qt
                },
                {
                    name: 'PE(动)中位',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },
                    data: peTTM50qt
                },
                {
                    name: '高位',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    itemStyle: {
                        color: 'rgb(255, 0, 0)'
                    },
                    data: peTTM90qt
                }
            ]
        };

        peTTMChart.setOption(option);
    }

    var renderPSChart = function (dateLabel, ps, ps10qt, ps50qt, ps90qt, zoomMin, zoomMax) {
        option = {
            tooltip: {
                trigger: 'axis',
                position: function (pt) {
                    return [pt[0], '10%'];
                }
            },
            legend: {
                data: ['PS', 'PS中位']
            },
            // title: {
            //     text: '市销',
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
                data: dateLabel
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

                    data: ps,
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

                    data: ps10qt
                },
                {
                    name: 'PS中位',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },

                    data: ps50qt
                },
                {
                    name: '高位',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    itemStyle: {
                        color: 'rgb(255, 0, 0)'
                    },

                    data: ps90qt
                }
            ]
        };

        psChart.setOption(option);
    }

    var renderPSTTMChart = function (dateLabel, psTTM, psTTM10qt, psTTM50qt, psTTM90qt, zoomMin, zoomMax) {
        option = {
            tooltip: {
                trigger: 'axis',
                position: function (pt) {
                    return [pt[0], '10%'];
                }
            },
            legend: {
                data: ['PS(动)', 'PS(动)中位']
            },
            // title: {
            //     text: '市销',
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
                data: dateLabel
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
                    name: 'PS(动)',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    sampling: 'average',
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },

                    data: psTTM,
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

                    data: psTTM10qt
                },
                {
                    name: 'PS中位',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    sampling: 'average',
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },

                    data: psTTM50qt
                },
                {
                    name: '高位',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    itemStyle: {
                        color: 'rgb(255, 0, 0)'
                    },

                    data: psTTM90qt
                }
            ]
        };

        psTTMChart.setOption(option);
    }

    var renderPBChart = function (dateLabel, pb, pb10qt, pb50qt, pb90qt, zoomMin, zoomMax) {
        option = {
            tooltip: {
                trigger: 'axis',
                position: function (pt) {
                    return [pt[0], '10%'];
                }
            },
            legend: {
                data: ['PB', 'PB中位']
            },
            // title: {
            //     text: '市净',
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
                data: dateLabel
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

                    data: pb,
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
                    name: 'PB中位',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    // sampling: 'average',
                    itemStyle: {
                        color: 'rgb(25, 70, 131)'
                    },

                    data: pb50qt
                },
                {
                    name: '低位',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    // sampling: 'average',
                    itemStyle: {
                        color: 'rgb(0, 255, 0)'
                    },

                    data: pb10qt
                },
                {
                    name: '高位',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    // sampling: 'average',
                    itemStyle: {
                        color: 'rgb(255, 0, 0)'
                    },

                    data: pb90qt
                }
            ]
        };

        pbChart.setOption(option);
    }

    var renderTOChart = function (dateLabel, turnoverRate, tr50qt, zoomMin, zoomMax) {
        option = {
            tooltip: {
                trigger: 'axis',
                position: function (pt) {
                    return [pt[0], '10%'];
                }
            },
            legend: {
                data: ['换手', '换手中位']
            },
            // title: {
            //     text: '换手率',
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
                data: dateLabel
            },
            yAxis: {
                type: 'value',
                boundaryGap: [0, '100%'],
                // max: Math.round(data.up_qt[6])+100,
                axisLabel: {
                    formatter: '{value} %'
                },
            },
            dataZoom: [{
                type: 'inside',
                start: zoomMin,
                end: zoomMax
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
                    name: '换手',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    sampling: 'average',
                    // itemStyle: {
                    //     color: 'rgb(25, 70, 131)'
                    // },

                    data: turnoverRate,
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
                    name: '换手中位',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    sampling: 'average',
                    // itemStyle: {
                    //     color: 'rgb(255, 0, 0)'
                    // },

                    data: tr50qt
                }
            ]
        };

        toChart.setOption(option);
    }

    var renderVRChart = function (dateLabel, volumeRatio, vr50qt, zoomMin, zoomMax) {
        option = {
            tooltip: {
                trigger: 'axis',
                position: function (pt) {
                    return [pt[0], '10%'];
                }
            },
            legend: {
                data: ['量比', '量比中位']
            },
            // title: {
            //     text: '量比',
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
                data: dateLabel
            },
            yAxis: {
                type: 'value',
                boundaryGap: [0, '100%'],
                axisLabel: {
                    formatter: '{value} %'
                },
            },
            dataZoom: [{
                type: 'inside',
                start: zoomMin,
                end: zoomMax
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
                    name: '量比',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    sampling: 'average',
                    // itemStyle: {
                    //     color: 'rgb(25, 70, 131)'
                    // },

                    data: volumeRatio,
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
                    name: '量比中位',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    sampling: 'average',
                    // itemStyle: {
                    //     color: 'rgb(255, 0, 0)'
                    // },

                    data: vr50qt
                }
            ]
        };

        vrChart.setOption(option);
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


    $('input:radio[name="closePeriod"]').change(function () {
        // alert($(this).val());
        closePeriod = $(this).val();
        // closeChart.clear();
        closeChart.showLoading();
        renderCloseChart(tsCode);
        closeChart.hideLoading();
        // closeChart.resize();
    });

    $('input:radio[name="pePeriod"]').change(function () {
        // alert($(this).val());
        var basicInfoPeriod = parseInt($(this).val());
        // peChart.clear();
        // peChart.showLoading();
        if (basicInfoPeriod == 0) {
            basicInfoPeriod = 30;
        }
        startDate = formatDate(new Date(today.getTime() - (365 * basicInfoPeriod * 24 * 60 * 60 * 1000)), "");
        renderCompanyBasicChart(tsCode, startDate, endDate);
        // peChart.hideLoading();
        // closeChart.resize();
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
                    stockmarketEndpoint + 'companies/' + $('#searchText').val(),
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

    var showIndBasic = function (industry) {
        var basicType = "pe,pb,ps";
        // var indContainer = $(".industry");
        $.ajax({
            url: stockmarketEndpoint + "industry-latest-daily-basic/" + industry+ "/" + basicType + "/",
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
            url: stockmarketEndpoint + "latest-daily-basic/" + tsCode + "/" ,
            success: function (data) {
                var content = data.latest_basic;
                $(content).each(function(idx, obj){
                    for(var k in obj){
                        $("#" + k).text(" " + obj[k]);
                    }
                });
            }
        });
    }

    showIndBasic($("#ind").text());
    showStockBasic($("#currentTsCode").val());

    // 初始化图表
    initParam();
    renderChart();
});