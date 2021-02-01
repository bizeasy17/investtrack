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
    var psChart = echarts.init(document.getElementById('psChart'));
    var pbChart = echarts.init(document.getElementById('pbChart'));
    var toChart = echarts.init(document.getElementById('toChart'));
    var vrChart = echarts.init(document.getElementById('vrChart'));
    var updownByPeriodChart = echarts.init(document.getElementById('updownByPeriodChart'));
    var periodByUpRangeChart = echarts.init(document.getElementById('periodByUpRangeChart'));


    var initParam = function () {
        tsCode = $("#currentTsCode").val();
        expdPctPeriod = $('input:radio[name="pct_period"]:checked').val();
        updownPctPeriod = $('input:radio[name="period"]:checked').val();
        strategyCode = $('input:radio[name="bstrategy"]:checked').val();
        strategyName = $('input:radio[name="bstrategy"]:checked').next().text();
        bstr =  $('input:radio[name="bstrategy"]:checked');

        startDate = formatDate(new Date(today.getTime() - (365 * histPeriod * 24 * 60 * 60 * 1000)), "");
        endDate = formatDate(today, "");
    }

    var renderChart = function () {
        showCompanyBasic(tsCode);
        renderCloseChart(tsCode);
        renderCompanyBasicChart(tsCode, startDate, endDate);
        renderUpdownByPeriodChart();
        renderPeriodByUpRangeChart();
    }

    var showCompanyBasic = function (tsCode) {
        $.ajax({
            url: stockmarketEndpoint + "company-basic/" + tsCode + "/",
            success: function (data) {
                if($("#companyName").parent().children().length>1){
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
                        data: ['收', '25', '60', '200']
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
                                    { type: 'max', name: '最大值' }
                                    // { type: 'min', name: '最小值' }
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
                renderPEChart(data.date_label, data.pe, data.pe_ttm, data.pe_50qt, data.pe_ttm_50qt, data.pe_range[0], data.pe_range[1]);
                renderPSChart(data.date_label, data.ps, data.ps_ttm, data.ps_50qt, data.ps_ttm_50qt, data.ps_range[0], data.ps_range[1]);
                renderPBChart(data.date_label, data.pb, data.pb_50qt, data.pb_range[0], data.pb_range[1]);
                renderTOChart(data.date_label, data.turnover_rate, data.to_50qt, data.to_range[0], data.to_range[1]);
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

    var renderPEChart = function (dateLabel, pe, peTTM, pe50qt, peTTM50qt, zoomMin, zoomMax) {
        option = {
            tooltip: {
                trigger: 'axis',
                position: function (pt) {
                    return [pt[0], '10%'];
                }
            },
            legend: {
                data: ['PE', 'PE(动)', 'PE中位', 'PE(动)中位']
            },
            title: {
                text: '市盈',
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
                    name: 'PE(动)',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    sampling: 'average',
                    itemStyle: {
                        color: 'rgb(255, 0, 0)'
                    },
                    data: peTTM
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
                    data: peTTM50qt
                },
                {
                    name: 'PE(动)中位',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    sampling: 'average',
                    itemStyle: {
                        color: 'rgb(255, 0, 0)'
                    },
                    data: pe50qt
                }
            ]
        };

        peChart.setOption(option);
    }

    var renderPSChart = function (dateLabel, ps, psTTM, ps50qt, psTTM50qt, zoomMin, zoomMax) {
        option = {
            tooltip: {
                trigger: 'axis',
                position: function (pt) {
                    return [pt[0], '10%'];
                }
            },
            legend: {
                data: ['PS', 'PS(动)', 'PS中位', 'PS(动)中位']
            },
            title: {
                text: '市销',
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
                    name: 'PS(动)',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    sampling: 'average',
                    itemStyle: {
                        color: 'rgb(255, 0, 0)'
                    },

                    data: psTTM
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

                    data: ps50qt
                },
                {
                    name: 'PS(动)中位',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    sampling: 'average',
                    itemStyle: {
                        color: 'rgb(255, 0, 0)'
                    },

                    data: psTTM50qt
                }
            ]
        };

        psChart.setOption(option);
    }

    var renderPBChart = function (dateLabel, pb, pb50qt, zoomMin, zoomMax) {
        option = {
            tooltip: {
                trigger: 'axis',
                position: function (pt) {
                    return [pt[0], '10%'];
                }
            },
            legend: {
                data: ['PB','PB中位']
            },
            title: {
                text: '市净',
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
                    // itemStyle: {
                    //     color: 'rgb(25, 70, 131)'
                    // },

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
                    sampling: 'average',
                    // itemStyle: {
                    //     color: 'rgb(255, 0, 0)'
                    // },

                    data: pb50qt
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
                data: ['换手','换手中位']
            },
            title: {
                text: '换手率',
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
                data: ['量比','量比中位']
            },
            title: {
                text: '量比',
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

    var renderUpdownByPeriodChart = function () {
        $.ajax({
            url: stockmarketEndpoint + "updown-pct/" + tsCode + "/" + strategyCode + "/" + updownPctPeriod + "/",
            success: function (data) {
                option = {
                    title: {
                        text: '固定天数涨跌%',
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
                        data: ['涨%', '涨中位%', '跌%', '跌中位%'],
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
                        boundaryGap: false,
                        data: data.date_label
                    },
                    yAxis: {
                        type: 'value',
                        max: data.up_max,
                        axisLabel: {
                            formatter: '{value} %'
                        },
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
                            name: '涨%',
                            type: 'line',
                            symbolSize: 8,
                            hoverAnimation: false,
                            data: data.up_pct,
                            markPoint: {
                                data: [
                                    { type: 'max', name: '最大值' }
                                    // { type: 'min', name: '最小值' }
                                ]
                            },
                            markLine: {
                                data: [
                                    { type: 'average', name: '平均值' }
                                ]
                            }
                        },
                        {
                            name: '涨中位%',
                            type: 'line',
                            symbolSize: 8,
                            hoverAnimation: false,
                            data: data.up_50qt
                        },
                        {
                            name: '跌%',
                            type: 'line',
                            symbolSize: 8,
                            hoverAnimation: false,
                            data: data.down_pct,
                            markPoint: {
                                data: [
                                    // { type: 'max', name: '最大值' }
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
                            name: '跌中位%',
                            type: 'line',
                            symbolSize: 8,
                            hoverAnimation: false,
                            data: data.down_50qt
                        },
                    ]

                };


                updownByPeriodChart.setOption(option);
            },
            statusCode: {
                403: function () {

                },
                404: function () {
                    $("#updownPctSubtitle").text("上市时间小于3年，暂无回测记录！");
                },
                500: function () {

                }
            }
        });
    }

    var renderPeriodByUpRangeChart = function () {
        $.ajax({
            url: stockmarketEndpoint + "exp-pct/" + tsCode + "/" + strategyCode + "/" + expdPctPeriod + "/" + freq + "/",
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
                        data: ['%天数', '%中位天数']//, '降水量', '平均温度']
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
                            name: '%天数',
                            type: 'bar',
                            data: data.exp_pct
                        },
                        {
                            name: '%中位天数',
                            type: 'line',
                            data: data.qt_50
                        }
                    ]
                };

                periodByUpRangeChart.setOption(option);
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
        renderUpdownByPeriodChart();
        renderPeriodByUpRangeChart();
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
        renderUpdownByPeriodChart();
        renderPeriodByUpRangeChart();
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="pct_period"]').change(function () {
        // 页面默认加载上证指数日K（D)
        expdPctPeriod = this.value;
        // showHelpInfo();
        renderPeriodByUpRangeChart();
    });

    // 根据选择的周期，显示该周期中最大跌幅，最大涨幅
    $('input:radio[name="period"]').change(function () {
        // 页面默认加载上证指数日K（D)
        updownPctPeriod = this.value;
        // showHelpInfo();
        renderUpdownByPeriodChart();
    });

    // 初始化图表
    initParam();
    renderChart();
});