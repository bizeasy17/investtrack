$(function () {
    var recordCount = 50;
    // ranking/<strategy_code>/<test_type>/<qt_pct>/<input_param>/<int:start_idx>/<int:end_idx>/
    var strategyCtg;
    var strategyCode;
    var strategyName;
    var testType;
    var qtPct;
    var inputParam;
    var startIdx = 0;
    var rowCount = 25;
    var currentIdx = 0;
    var prevStockRankingTr = undefined;
    var analysisEndpoint = '/analysis/';

    var targetPctChart;
    var upPctChart;
    var downPctChart;

    var selStockName;
    var selStockCode;
    var showStockCode;
    var testPeriod;
    var targetPct;
    // var stockUpDownTestType;

    var initParam = function () {
        strategyCtg = $('input:radio[name="strategy-ctg"]:checked').val();
        strategyCode = $("#hiddenStrategyCode").val();
        strategyName = $("#hiddenStrategyName").val();
        testType = $('input:radio[name="test_type"]:checked').val();
        qtPct = $('input:radio[name="qt_pct"]:checked').val();
        inputParam = $('input:radio[name="period"]:checked').val();
        testPeriod = $('input:radio[name="stk-period"]:checked').val();
        targetPct = $('input:radio[name="stk-pct_period"]:checked').val();
        // stockUpDownTestType = $('input:radio[name="stk-pct_period"]:checked').val();
        $("#pctPeriodBtnGroup").addClass("d-none");
    }

    var updateUpPctRankingChart = function (stockCode, testPeriod, strategyCtg) {
        var upPctRankingChartData = {};
        // var newDataset = {};
        var upPctChartCanvas = $("#upPctChart").get(0).getContext("2d");
        var sType;
        if (strategyCtg == "买策略") {
            sType = "b";
        } else {
            sType = "s"
        }
        $.ajax({
            url: analysisEndpoint + "updown-pct-ranking-by-stock/" + stockCode + "/" + testPeriod + "/" + sType + "/up_pct/",
            // headers: { 'X-CSRFToken': csrftoken },
            method: 'GET',
            dataType: 'json',
            success: function (data) {
                if (data.code == "empty") {
                    $("#noUpPct").append("<span class='text-muted'>无预期涨幅分析</span>");
                } else {
                    // $("#pTotalAvailPerTarget").text(data.total_percentage);
                    upPctRankingChartData = {
                        labels: data.label,
                        datasets: [{
                            label: '平均涨幅%',
                            data: data.mean
                        }]
                    };

                    if (!upPctChart) {
                        upPctChart = new Chart(upPctChartCanvas, {
                            type: 'bar',
                            data: upPctRankingChartData,
                            options: {
                                responsive: true,
                                legend: {
                                    display: true,
                                    position: 'right'
                                }
                            },
                        });
                    } else {
                        upPctChart.data = upPctRankingChartData;
                    }

                    $(data.rankings).each(function (idx, ranking) {
                        var newDataset = {
                            label: data.strategy_label[idx],
                            data: ranking
                        };
                        upPctRankingChartData.datasets.push(newDataset);
                    });
                }
            },
            complete: function () {
                console.log("in complete function");
                upPctChart.update();
            }
        });

    }

    var updateDownPctRankingChart = function (stockCode, testPeriod, strategyCtg) {
        var downPctRankingChartData = {};
        // var newDataset = {};
        var downPctChartCanvas = $("#downPctChart").get(0).getContext("2d");
        var sType;
        if (strategyCtg == "买策略") {
            sType = "b";
        } else {
            sType = "s"
        }
        $.ajax({
            url: analysisEndpoint + "updown-pct-ranking-by-stock/" + stockCode + "/" + testPeriod + "/" + sType + "/down_pct/",
            // headers: { 'X-CSRFToken': csrftoken },
            method: 'GET',
            dataType: 'json',
            success: function (data) {
                if (data.code == "empty") {
                    $("#noDownPct").append("<span class='text-muted'>无预期涨幅分析</span>");
                } else {
                    // $("#pTotalAvailPerTarget").text(data.total_percentage);
                    downPctRankingChartData = {
                        labels: data.label,
                        datasets: [{
                            label: '平均涨幅%',
                            data: data.mean
                        }]
                    };

                    if (!downPctChart) {
                        downPctChart = new Chart(downPctChartCanvas, {
                            type: 'bar',
                            data: downPctRankingChartData,
                            options: {
                                responsive: true,
                                legend: {
                                    display: true,
                                    position: 'right'
                                }
                            },
                        });
                    } else {
                        downPctChart.data = downPctRankingChartData;
                    }

                    $(data.rankings).each(function (idx, ranking) {
                        var newDataset = {
                            label: data.strategy_label[idx],
                            data: ranking
                        };
                        downPctRankingChartData.datasets.push(newDataset);
                    });
                }
            },
            complete: function () {
                console.log("in complete function");
                downPctChart.update();
            }
        });

    }

    var updateUpPctRanking = function (stockCode, testPeriod) {
        updateUpPctRankingChart(stockCode, testPeriod, strategyCtg);
    }

    var updateDownPctRanking = function (stockCode, testPeriod) {
        updateDownPctRankingChart(stockCode, testPeriod, strategyCtg);
    }

    var updateTargetPctRankingChart = function (stockCode, targetPct) {
        if ($("#targetPctChart").length) {
            var targetPctRankingChartData = {};
            // var newDataset = {};
            var targetPctChartCanvas = $("#targetPctChart").get(0).getContext("2d");
            $.ajax({
                url: analysisEndpoint + 'target-pct-ranking-by-stock/' + stockCode + '/' + targetPct + "/",
                // headers: { 'X-CSRFToken': csrftoken },
                method: 'GET',
                dataType: 'json',
                success: function (data) {
                    if (data.code == "empty") {
                        $("#noTargetPct").append("<span class='text-muted'>无预期涨幅分析</span>");
                    } else {
                        // $("#pTotalAvailPerTarget").text(data.total_percentage);
                        targetPctRankingChartData = {
                            labels: data.label,
                            datasets: [{
                                label: '平均天数',
                                data: data.mean
                            }]
                        };

                        if (!targetPctChart) {
                            targetPctChart = new Chart(targetPctChartCanvas, {
                                type: 'bar',
                                data: targetPctRankingChartData,
                                options: {
                                    responsive: true,
                                    legend: {
                                        display: true,
                                        position: 'right'
                                    }
                                },
                            });
                        } else {
                            targetPctChart.data = targetPctRankingChartData;
                        }

                        $(data.rankings).each(function (idx, ranking) {
                            var newDataset = {
                                label: data.strategy_label[idx],
                                data: ranking
                            };
                            targetPctRankingChartData.datasets.push(newDataset);
                        });
                    }
                },
                complete: function () {
                    console.log("in complete function");
                    targetPctChart.update();
                }
            });
        }
    }

    var updateSingleStockRanking = function (stockCode, testPeriod, targetPct) {
        if ($("#upPctChart").length) {
            updateUpPctRanking(stockCode, testPeriod);
        }
        if ($("#downPctChart").length) {
            updateDownPctRanking(stockCode, testPeriod);
        }
        updateTargetPctRankingChart(stockCode, targetPct);
    }

    var showStockDetailRanking = function () {
        var nameCode = $(this).find('th a');
        selStockName = $(nameCode[0]).text();
        selStockCode = $(nameCode[1]).text();
        showStockCode = selStockCode;
        if (prevStockRankingTr) {
            if ($(prevStockRankingTr).hasClass("bg-light")) {
                $(prevStockRankingTr).removeClass("bg-light");
            }
        }
        prevStockRankingTr = this;
        $(this).addClass("bg-light");
        $(".cur-stock").text(selStockName + ' - ' + showStockCode);
        updateSingleStockRanking(selStockCode, testPeriod, targetPct);
    }

    var bandRankingTable = function (strategy_code, strategyName, test_type, qt_pct, input_param, start_idx, end_idx) {
        var tbd = $("#tblStrategyRanking > tbody");
        var label = $("#curAnalysisCond");
        label.empty();
        label.append("当前策略 - <b>" + strategyName + "</b>，分析类型 - <b>" + test_type + "</b>，概率 - <b>" + qt_pct + "</b>，输入值 - <b>" + input_param + "</b>");
        $.ajax({
            url: analysisEndpoint + 'ranking/' + strategy_code + '/' + test_type + '/' + qt_pct + '/' + input_param + '/' + start_idx + '/' + end_idx + '/',
            success: function (data) {
                tbd.empty();
                $(data).each(function (idx, ranking) {
                    tbd.append(
                        '<tr id="rankingRow' + ranking.ts_code + '">' +
                        '<th scope="row">' +
                        '<div class="">' +
                        '<div class="card-title small"><a href="#" class="text-dark">' + ranking.stock_name + '</a><span class="small text-muted" id="xxx"></span></div>' +
                        '<div class="card-subtitle small text-muted"><a href="#" class="text-dark">' + ranking.ts_code + '</a></div>' +
                        '</div>' +
                        '</th>' +
                        '<td><span id="" class="small">-</span></td>' +
                        '<td><span id="" class="small">' + ranking.qt_pct_val + '</span></td>' +
                        '<td><span id="" class="small">' + (ranking.rank + 1) + '</span></td>' +
                        '</tr>'
                    );
                    var showStockRanking = document.getElementById("rankingRow" + ranking.ts_code);
                    showStockRanking.addEventListener("click", showStockDetailRanking);
                });
            },
            statusCode: {
                403: function () {
                },
                404: function () {
                    $(tbd).append(
                        '<th scope="row">' +
                        '<div class="">' +
                        '<div class="card-title small"><a href="#" class="text-dark">无排名记录</a><span class="small text-muted" id="xxx"></span></div>' +
                        '<div class="card-subtitle small text-muted"><a href="#" class="text-dark"></a></div>' +
                        '</div>' +
                        '</th>'
                    );
                },
                500: function () {
                    $(tbd).append(
                        '<th scope="row">' +
                        '<div class="">' +
                        '<div class="card-title small"><a href="#" class="text-dark">系统错误</a><span class="small text-muted" id="xxx"></span></div>' +
                        '<div class="card-subtitle small text-muted"><a href="#" class="text-dark"></a></div>' +
                        '</div>' +
                        '</th>'
                    );
                }
            }
        });
    }

    var showStrategyChgResult = function () {
        // if ($(this).hasClass("btn-info")) {
        //     $(this).removeClass("btn-info");
        //     $(this).addClass("btn-danger");
        // }

        // if (strategyCode) {
        //     if ($("#btnStrategy" + strategyCode).hasClass("btn-danger")) {
        //         $("#btnStrategy" + strategyCode).removeClass("btn-danger");
        //         $("#btnStrategy" + strategyCode).addClass("btn-info");
        //     }
        // }

        strategyCode = this.value.split(",")[0];
        strategyName = this.value.split(",")[1];
        bandRankingTable(strategyCode, strategyName, testType, qtPct, inputParam, startIdx, rowCount);
    }

    var bindStrategyByCtg = function (categoryName) {
        var strategyDiv = $("#strategyListRanking");
        $.ajax(
            {
                url: analysisEndpoint + 'strategies/by-category/' + categoryName + "/",
                method: 'GET',
                success: function (data) {
                    var strategiesTag = "";
                    strategyDiv.empty();
                    $(data).each(function (idx, obj) {
                        strategiesTag +=
                            '<div class="row">' +
                            '<div class="col-lg-6">' +
                            '<img src="' + imgRoot + obj.code + '.png" height="50" width="50">' +
                            '</div>' +
                            '<div class="col-lg-6">' +
                            '<div><span class="small text-primary">' + obj.strategy_name + '</span></div>'
                        strategiesTag += '<button class="btn btn-sm btn-info" name="strategy-code" id="btnStrategy' + obj.id + '" value="' + obj.code + ',' + obj.strategy_name + '"><small>分析</small></button>';
                        strategiesTag += '</div></div><hr/>';
                        strategyDiv.append(strategiesTag);
                        strategiesTag = "";
                        var showStrategyResultBtn = document.getElementById("btnStrategy" + obj.id);
                        showStrategyResultBtn.addEventListener("click", showStrategyChgResult);
                    });
                },
                statusCode: {
                    403: function () {
                        strategyDiv.html("403 forbidden");
                    },
                    404: function () {
                        strategyDiv.html("系统无法找到相关策略");
                    },
                    500: function () {
                        strategyDiv.html("系统错误，请稍后再试");
                    }
                }
            }
        );
    }

    var updateIndividuleStat = function () {

    }

    // 初始化ranking表
    initParam();
    bindStrategyByCtg(strategyCtg);
    bandRankingTable(strategyCode, strategyName, testType, qtPct, inputParam, startIdx, rowCount);

    $('input:radio[name="test_type"]').change(function () {
        // 页面默认加载上证指数日K（D)
        testType = this.value;
        if (testType == "up_pct" || testType == "down_pct") {
            if ($("#periodBtnGroup").hasClass("d-none")) {
                $("#periodBtnGroup").removeClass("d-none");
            }
            if (!$("#pctPeriodBtnGroup").hasClass("d-none")) {
                $("#pctPeriodBtnGroup").addClass("d-none");
            }
            inputParam = $('input:radio[name="period"]:checked').val();
        } else if (testType == "target_pct") {
            if ($("#pctPeriodBtnGroup").hasClass("d-none")) {
                $("#pctPeriodBtnGroup").removeClass("d-none");
            }
            if (!$("#periodBtnGroup").hasClass("d-none")) {
                $("#periodBtnGroup").addClass("d-none");
            }
            inputParam = $('input:radio[name="pct_period"]:checked').val();
        }
        bandRankingTable(strategyCode, strategyName, testType, qtPct, inputParam, startIdx, rowCount);
    });

    $('input:radio[name="qt_pct"]').change(function () {
        // 页面默认加载上证指数日K（D)
        qtPct = this.value;
        bandRankingTable(strategyCode, strategyName, testType, qtPct, inputParam, startIdx, rowCount);
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="period"]').change(function () {
        // 页面默认加载上证指数日K（D)
        inputParam = this.value;
        bandRankingTable(strategyCode, strategyName, testType, qtPct, inputParam, startIdx, rowCount);
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="pct_period"]').change(function () {
        // 页面默认加载上证指数日K（D)
        inputParam = this.value;
        bandRankingTable(strategyCode, strategyName, testType, qtPct, inputParam, startIdx, rowCount);
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="stk-period"]').change(function () {
        // 页面默认加载上证指数日K（D)
        testPeriod = this.value;
        updateUpPctRankingChart(selStockCode, testPeriod, strategyCtg);
        updateDownPctRankingChart(selStockCode, testPeriod, strategyCtg);
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="stk-pct_period"]').change(function () {
        // 页面默认加载上证指数日K（D)
        targetPct = this.value;
        updateTargetPctRankingChart(selStockCode, targetPct);
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="strategy-ctg"]').change(function () {
        // 页面默认加载上证指数日K（D)
        strategyCtg = this.value;
        bindStrategyByCtg(strategyCtg);
        updateSingleStockRanking(selStockCode, testPeriod, targetPct);
    });

    $(".pagination").on("click", ".page-item", function (event) {
        if ($(this).index() == 0) {
            if (currentIdx == 0) return;
            else {
                currentIdx -= rowCount;
            }
            console.log(currentIdx);
        } else {
            currentIdx += rowCount;
            console.log(currentIdx);
        }
        bandRankingTable(strategyCode, strategyName, testType, qtPct, inputParam, currentIdx, currentIdx+rowCount);
    });
});