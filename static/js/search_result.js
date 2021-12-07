$(function () {
    var stockmarketEndpoint = '/stockmarket/';
    var investorEndpoint = "/investors/";
    // var homeEndpoint = '/';
    // var indexList = "sh,sz,cyb,hs300"
    var freq = "D";
    var closePeriod = 5;
    // var histType = "close";
    var tsCode = "";
    var period = 18;
    // var tsCodeNoSfx = "";
    // var stockName = "";
    // var market = "";
    // var pctOnPeriodDates = "";
    // var periodOnPctDates = "";

    // var bstr;
    // var sstr;

    var today = new Date();
    var startDate = "";
    var endDate = "";

    var closeChart = echarts.init(document.getElementById('closeChart'));
    var top10HoldersChart = echarts.init(document.getElementById('top10HoldersChart'));
    var top10HoldersPetChart = echarts.init(document.getElementById('top10HoldersPETChart'));
    var top10HoldersPbChart = echarts.init(document.getElementById('top10HoldersPBChart'));
    var top10HoldersPsChart = echarts.init(document.getElementById('top10HoldersPSChart'));

    var basicCharts = $(".basic-chart");


    var initParam = function () {
        tsCode = $("#currentTsCode").val();
        closePeriod = $('input:radio[name="closePeriod"]:checked').val();
        startDate = formatDate(new Date(today.getTime() - (365 * closePeriod * 24 * 60 * 60 * 1000)), "");
        endDate = formatDate(today, "");
    }

    var renderChart = function () {
        showCompanyBasic(tsCode);
        renderCloseChart(tsCode);
        renderCompanyBasicChart(tsCode, startDate, endDate);
        renderTop10HolderStatChart(tsCode, period);
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
                $("#website").parent().append('<a href="http://' + data[0].website + '" target="_blank"><span>http://' + data[0].website + '</span><i class="fa fa-external-link-alt ml-1" aria-hidden="true"></i></a>');
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
            url: stockmarketEndpoint + "stock-close-history/" + tsCode + "/" + freq + "/" + closePeriod + "/?format=json",
            success: function (data) {
                if ($(".error-msg").hasClass("d-none") == false) {
                    $(".error-msg").addClass("d-none");
                }
                if ($(".dashboard").hasClass("d-none")) {
                    $(".dashboard").removeClass("d-none");
                }
                var chartData = jsonToChartFormat(data, "close");
                var closeQuantile = getQuantile(chartData);
                option = {
                    tooltip: {
                        trigger: 'axis',
                        position: function (pt) {
                            return [pt[0], '10%'];
                        }
                    },
                    legend: {
                        data: ['收盘价']
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
                            },
                            markLine: {
                                data: [
                                    { type: 'average', name: '平均值' }
                                ]
                            }
                        },
                        // {
                        //     name: 'MA25',
                        //     type: 'line',
                        //     smooth: true,
                        //     symbol: 'none',
                        //     sampling: 'average',
                        //     itemStyle: {
                        //         color: 'rgb(0, 255, 0)'
                        //     },
                        //     data: data.ma25
                        // },
                        // {
                        //     name: '60',
                        //     type: 'line',
                        //     smooth: true,
                        //     symbol: 'none',
                        //     sampling: 'average',
                        //     itemStyle: {
                        //         color: 'rgb(0, 0, 255)'
                        //     },
                        //     data: data.ma60
                        // },
                        // {
                        //     name: '200',
                        //     type: 'line',
                        //     smooth: true,
                        //     symbol: 'none',
                        //     sampling: 'average',
                        //     itemStyle: {
                        //         color: 'rgb(25, 0, 31)'
                        //     },
                        //     data: data.ma200
                        // },
                        {
                            name: '低位',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            itemStyle: {
                                color: 'rgb(0, 255, 0)'
                            },
                            data: closeQuantile.qt10
                        },
                        {
                            name: '中位',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            itemStyle: {
                                color: 'rgb(25, 70, 131)'
                            },
                            data: closeQuantile.qt50
                        },
                        {
                            name: '高位',
                            type: 'line',
                            smooth: true,
                            symbol: 'none',
                            itemStyle: {
                                color: 'rgb(255, 0, 0)'
                            },
                            data: closeQuantile.qt90
                        }
                    ]
                };

                closeChart.setOption(option);
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

    var renderBasicChart = function (jsonData, canvas, basicType) {
        var chartData = jsonToChartFormat(jsonData, basicType);
        var peQuantile = getQuantile(chartData);
        var chartCanvas = echarts.init(canvas);

        option = {
            tooltip: {
                trigger: 'axis',
                position: function (pt) {
                    return [pt[0], '10%'];
                }
            },
            legend: {
                data: [basicType, basicType + "中位"]
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
                start: 75,
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
                    name: basicType,
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
                    name: basicType + '低位',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    itemStyle: {
                        color: 'rgb(0, 255, 0)'
                    },
                    data: peQuantile.qt10
                },
                {
                    name: basicType + '中位',
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
                    name: basicType + '高位',
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

        chartCanvas.setOption(option);
    }

    var renderTop10HolderStatChart = function (tsCode, period) {
        $.ajax({
            url: stockmarketEndpoint + "top10-holders-stat/" + tsCode + "/" + period + "/?format=json",
            success: function (data) {
                // if ($(".error-msg").hasClass("d-none") == false) {
                //     $(".error-msg").addClass("d-none");
                // }
                // if ($(".dashboard").hasClass("d-none")) {
                //     $(".dashboard").removeClass("d-none");
                // }
                var closeData = jsonToChartFormat(data, "close");
                var petData = jsonToChartFormat(data, "pe_ttm");
                var pbData = jsonToChartFormat(data, "pb");
                var psData = jsonToChartFormat(data, "ps");

                var pctData = jsonToChartFormat(data, "hold_pct");

                const colors = ['#5470C6', '#EE6666'];
                option = {
                    color: colors,
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'cross'
                        }
                    },
                    grid: {
                        right: '20%'
                    },
                    toolbox: {
                        feature: {
                            dataView: { show: true, readOnly: false },
                            restore: { show: true },
                            saveAsImage: { show: true }
                        }
                    },
                    legend: {
                        data: ['收', '持仓']
                    },
                    xAxis: [
                        {
                            type: 'category',
                            axisTick: {
                                alignWithLabel: true
                            },
                            // prettier-ignore
                            data: closeData.label
                        }
                    ],
                    yAxis: [
                        {
                            type: 'value',
                            name: '持仓',
                            min: 0,
                            max: 100,
                            position: 'right',
                            axisLine: {
                                show: true,
                                lineStyle: {
                                    color: colors[0]
                                }
                            },
                            axisLabel: {
                                formatter: '{value} %'
                            }
                        },
                        {
                            type: 'value',
                            name: '收盘',
                            // min: 0,
                            // max: 25,
                            position: 'left',
                            axisLine: {
                                show: true,
                                lineStyle: {
                                    color: colors[1]
                                }
                            },
                            axisLabel: {
                                formatter: '{value}元'
                            }
                        }
                    ],
                    series: [
                        {
                            name: '持仓',
                            type: 'bar',
                            data: pctData.value
                        },
                        // {
                        //     name: 'Precipitation',
                        //     type: 'bar',
                        //     yAxisIndex: 1,
                        //     data: [
                        //         2.6, 5.9, 9.0, 26.4, 28.7, 70.7, 175.6, 182.2, 48.7, 18.8, 6.0, 2.3
                        //     ]
                        // },
                        {
                            name: '收',
                            type: 'line',
                            yAxisIndex: 1,
                            data: closeData.value
                        }
                    ]
                };

                petOption = {
                    color: colors,
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'cross'
                        }
                    },
                    grid: {
                        right: '20%'
                    },
                    toolbox: {
                        feature: {
                            dataView: { show: true, readOnly: false },
                            restore: { show: true },
                            saveAsImage: { show: true }
                        }
                    },
                    legend: {
                        data: ['PET', '持仓']
                    },
                    xAxis: [
                        {
                            type: 'category',
                            axisTick: {
                                alignWithLabel: true
                            },
                            // prettier-ignore
                            data: closeData.label
                        }
                    ],
                    yAxis: [
                        {
                            type: 'value',
                            name: '持仓',
                            min: 0,
                            max: 100,
                            position: 'right',
                            axisLine: {
                                show: true,
                                lineStyle: {
                                    color: colors[0]
                                }
                            },
                            axisLabel: {
                                formatter: '{value} %'
                            }
                        },
                        {
                            type: 'value',
                            name: 'PET',
                            // min: 0,
                            // max: 25,
                            position: 'left',
                            axisLine: {
                                show: true,
                                lineStyle: {
                                    color: colors[1]
                                }
                            },
                            axisLabel: {
                                formatter: '{value}'
                            }
                        }
                    ],
                    series: [
                        {
                            name: '持仓',
                            type: 'bar',
                            data: pctData.value
                        },
                        // {
                        //     name: 'Precipitation',
                        //     type: 'bar',
                        //     yAxisIndex: 1,
                        //     data: [
                        //         2.6, 5.9, 9.0, 26.4, 28.7, 70.7, 175.6, 182.2, 48.7, 18.8, 6.0, 2.3
                        //     ]
                        // },
                        {
                            name: 'PET',
                            type: 'line',
                            yAxisIndex: 1,
                            data: petData.value
                        }
                    ]
                };

                pbOption = {
                    color: colors,
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'cross'
                        }
                    },
                    grid: {
                        right: '20%'
                    },
                    toolbox: {
                        feature: {
                            dataView: { show: true, readOnly: false },
                            restore: { show: true },
                            saveAsImage: { show: true }
                        }
                    },
                    legend: {
                        data: ['PB', '持仓']
                    },
                    xAxis: [
                        {
                            type: 'category',
                            axisTick: {
                                alignWithLabel: true
                            },
                            // prettier-ignore
                            data: closeData.label
                        }
                    ],
                    yAxis: [
                        {
                            type: 'value',
                            name: '持仓',
                            min: 0,
                            max: 100,
                            position: 'right',
                            axisLine: {
                                show: true,
                                lineStyle: {
                                    color: colors[0]
                                }
                            },
                            axisLabel: {
                                formatter: '{value} %'
                            }
                        },
                        {
                            type: 'value',
                            name: 'PB',
                            // min: 0,
                            // max: 25,
                            position: 'left',
                            axisLine: {
                                show: true,
                                lineStyle: {
                                    color: colors[1]
                                }
                            },
                            axisLabel: {
                                formatter: '{value}'
                            }
                        }
                    ],
                    series: [
                        {
                            name: '持仓',
                            type: 'bar',
                            data: pctData.value
                        },
                        // {
                        //     name: 'Precipitation',
                        //     type: 'bar',
                        //     yAxisIndex: 1,
                        //     data: [
                        //         2.6, 5.9, 9.0, 26.4, 28.7, 70.7, 175.6, 182.2, 48.7, 18.8, 6.0, 2.3
                        //     ]
                        // },
                        {
                            name: 'PB',
                            type: 'line',
                            yAxisIndex: 1,
                            data: pbData.value
                        }
                    ]
                };

                psOption = {
                    color: colors,
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'cross'
                        }
                    },
                    grid: {
                        right: '20%'
                    },
                    toolbox: {
                        feature: {
                            dataView: { show: true, readOnly: false },
                            restore: { show: true },
                            saveAsImage: { show: true }
                        }
                    },
                    legend: {
                        data: ['PS', '持仓']
                    },
                    xAxis: [
                        {
                            type: 'category',
                            axisTick: {
                                alignWithLabel: true
                            },
                            // prettier-ignore
                            data: closeData.label
                        }
                    ],
                    yAxis: [
                        {
                            type: 'value',
                            name: '持仓',
                            min: 0,
                            max: 100,
                            position: 'right',
                            axisLine: {
                                show: true,
                                lineStyle: {
                                    color: colors[0]
                                }
                            },
                            axisLabel: {
                                formatter: '{value} %'
                            }
                        },
                        {
                            type: 'value',
                            name: 'PS',
                            // min: 0,
                            // max: 25,
                            position: 'left',
                            axisLine: {
                                show: true,
                                lineStyle: {
                                    color: colors[1]
                                }
                            },
                            axisLabel: {
                                formatter: '{value}'
                            }
                        }
                    ],
                    series: [
                        {
                            name: '持仓',
                            type: 'bar',
                            data: pctData.value
                        },
                        // {
                        //     name: 'Precipitation',
                        //     type: 'bar',
                        //     yAxisIndex: 1,
                        //     data: [
                        //         2.6, 5.9, 9.0, 26.4, 28.7, 70.7, 175.6, 182.2, 48.7, 18.8, 6.0, 2.3
                        //     ]
                        // },
                        {
                            name: 'PS',
                            type: 'line',
                            yAxisIndex: 1,
                            data: psData.value
                        }
                    ]
                };

                top10HoldersChart.setOption(option);
                top10HoldersPetChart.setOption(petOption);
                top10HoldersPbChart.setOption(pbOption);
                top10HoldersPsChart.setOption(psOption);
            }
        });
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
                        if (parseFloat(obj[k]) == 0) {
                            obj[k] = "亏"
                        }
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

    showIndBasic($("#ind").text());
    showStockBasic($("#currentTsCode").val());

    // 初始化图表
    initParam();
    renderChart();
});