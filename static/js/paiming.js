$(function () {
    var paimingEndpoint = '/paiming/';
    var stockmarketEndpoint = '/stockmarket/';
    var analysisEndpoint = '/analysis/';
    var homeEndpoint = '/';
    var indexList = "sh,sz,cyb,hs300"
    var freq = "D";
    var histPeriod = 3;
    var histType = "close";
    var tsCode = "";
    var tsCodeNoSfx = "";
    var stockName = "";
    var market = "";

    // 傳給btest ranking url的參數
    // var btestTypeCtg = "up_pct";
    var startIdx = 0;
    var endIdx = 50;
    var btestType;
    var btestVal;
    var sortedBy;
    var filters;
    var strategy;
    var strategyName;
    var area;
    var industry;
    var degree;
    var marketVal;
    var province;
    var board;
    var container;
    // var updownPctPeriod = 80;
    // var expdPctPeriod = "pct20_period";
    // end

    var pctOnPeriodDates = "";
    var periodOnPctDates = "";

    var bstr;
    var sstr;

    var today = new Date();
    // var startQ = "199001";
    // var endQ = "202101";
    // var startDate = "";
    // var endDate = "";
    // var countYear = 3;


    // var closeChart = echarts.init(document.getElementById('closeChart'));

    var initParam = function () {
        btestType = $('input:radio[name="btestType"]:checked').val();
        btestVal = $('input:radio[name="btestVal"]:checked').val();
        strategy = $('input:radio[name="strategy"]:checked').val();
        strategyName = $('input:radio[name="strategy"]:checked').parent('label').text();
        sortedBy = $('input:radio[name="sortedBy"]:checked').val();
        container = $("#rankedResults");
        // startDate = formatDate(new Date(today.getTime() - (365 * histPeriod * 24 * 60 * 60 * 1000)), "");
        // endDate = formatDate(today, "");

        // initBTestDates();
    }


    var renderChart = function () {
        renderCloseChart();
    }

    var renderCloseChart = function () {
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
                    xAxis: {
                        type: 'category',
                        boundaryGap: false,
                        data: data.label
                    },
                    yAxis: {
                        type: 'value',
                        boundaryGap: [0, '100%']
                    },
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
                            data: data.close
                        }
                    ]
                };

                closeChart.setOption(option);
            }
        });
    }

    var buildFilter = function () {
        // ["company__area=='深圳'"]
        var filter = "";

        filter += "[";
        if (board){
            filter += "'company__market == \"" + board + "\"',";
        }
        if (area) {
            filter += "'company__area == \"" + area + "\"',";
        }
        if (industry) {
            filter += "'company__industry == \"" + industry + "\"',";
        }
        if (province) {
            filter += "'company_basic__province == \"" + industry + "\"',";
        }
        // if (marketVal) {
        //     filter += "companydailybasic__market_val=='" + market + "',";
        // }
        // if (degree) {
        //     filter += "companymanagers__edu=='" + degree + "',";
        // }
        filter += "]";

        return filter;
    }

    var bindCompanyBasic = function() {
        $.ajax({
            url: stockmarketEndpoint + "daily-basic-latest/companies/" + tsCode + "/",
            success: function (data) {
                $(data.results).each(function(id,obj){
                    var close = document.getElementById("close_"+obj.ts_code);
                    var pe = document.getElementById("pe_"+obj.ts_code);
                    var mv = document.getElementById("mv_"+obj.ts_code);
                    $(close).text(obj.close);
                    $(pe).text("PE - " + obj.pe);
                    $(mv).text("市值 - " + (parseInt(obj.mv) / 10000).toLocaleString() + "亿");
                    // $("peTTM."+obj.ts_code).text(obj.pe_ttm);
                    // $("pb."+obj.ts_code).text(obj.pb);
                    // $("ps."+obj.ts_code).text(obj.ps);
                    // $("psTTM."+obj.ts_code).text(obj.ps_ttm);
                });
            }
        });
    }

    var showRankedStocks = function () {
        var filters = buildFilter();
        var rankedNodes = "";
        $.ajax({
            url: stockmarketEndpoint + "btest-ranking/" + btestType + "/" + btestVal + "/" + strategy + "/" + sortedBy + "/" + filters + "/" + freq + "/" + startIdx + "/" + endIdx + "/",
            success: function (data) {
                $(container).html("");
                rankedNodes = "";
                $(data.value).each(function(id, obj){
                    tsCode += obj.ts_code + ",";
                    rankedNodes +=
                        '<div class="row">'+
                            '<div class="col-lg-12">'+
                                '<hr />'+
                            '</div>'+
                        '</div>'+
                        '<div class="row" id="">'+
                            '<div class="col-lg-1">'+
                                '<span class="badge badge-pill badge-primary mt-3">'+obj.stock_name.substring(0,2)+'<br>'+obj.stock_name.substring(2)+'</span>'+
                            '</div>'+
                            '<div class="col-lg-2">'+
                                '<span class="text-primary small">'+obj.ts_code+'</span><br>'+
                                // '<span class="font-weight-bold text-primary">华夏银行</span><br>'+
                                '<span class="font-weight-bold market-value small" id="mv_'+obj.ts_code+'"></span><br>'+
                                '<span class="font-weight-bold pe small" id="pe_'+obj.ts_code+'"></span>'+
                            '</div>'+
                            '<div class="col-lg-2">'+
                                '<span class="text-muted small">基本</span><br>'+
                                '<span class="font-weight-bold small">地区 - '+obj.area+'</span><br>'+
                                '<span class="font-weight-bold small">行业 - '+obj.industry+'</span><br>'+
                                '<span class="font-weight-bold small">板块 - '+obj.market+'</span><br>'+
                                '<a class="small" href="https://'+obj.website.trim()+'" target="_blank">公司网站</a>'+

                            '</div>'+
                            '<div class="col-lg-2">'+
                                '<span class="text-muted small">排名</span><br>'+
                                '<span class="font-weight-bold small text-danger">'+obj.ranking+'</span><br>'+
                                '<span class="font-weight-bold small">中位 - '+parseFloat(obj.median).toFixed(2)+'</span><br>'+
                                '<span class="font-weight-bold small">平均 - '+parseFloat(obj.mean).toFixed(2)+'</span>'+
                            '</div>'+
                            '<div class="col-lg-2">'+
                                '<span class="text-muted small">策略</span><br>'+
                                '<span class="font-weight-bold small">'+strategyName+'</span>'+
                            '</div>'+
                            '<div class="col-lg-1">'+
                                '<span class="text-muted small">收</span><br>'+
                                '<span class="font-weight-bold text-danger price small" id="close_'+obj.ts_code+'"></span><br>'+
                            '</div>'+
                            '<div class="col-lg-2">'+
                                '<span class="text-muted small">收盘线</span><br>'+
                                '<div id="closeChart.'+obj.ts_code+'"" style="width: 100%; height: 100%"></div>'+
                            '</div>'+
                        '</div>';
                }); 
                $(container).append(rankedNodes);
            },
            complete: function () {
                // var codes = tsCode.split(",");
                // $(codes).each(function(id, obj){
                //     var close = document.getElementById("close_"+obj);
                //     if(close){
                //         $(close).text(obj);
                //     } 
                //     // if($("#pe1_"+obj)) $("#pe_"+obj).text(obj);
                //     // if($("#mv1_"+obj)) $("#mv_"+obj).text(obj);
                // });
                
                bindCompanyBasic();
            }
        });
    }

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="btestType"]').change(function () {
        // 页面默认加载上证指数日K（D)
        // 页面默认加载上证指数日K（D)
        btestType = $(this).val()
        showRankedStocks();
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="btestVal"]').change(function () {
        // 页面默认加载上证指数日K（D)
        // 页面默认加载上证指数日K（D)
        btestVal = $(this).val()
        showRankedStocks();
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="sortedBy"]').change(function () {
        // 页面默认加载上证指数日K（D)
        // 页面默认加载上证指数日K（D)
        sortedBy = $(this).val()
        showRankedStocks();
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="strategy"]').change(function () {
        // 页面默认加载上证指数日K（D)
        // 页面默认加载上证指数日K（D)
        strategy = $(this).val()
        strategyName = $(this).parent('label').text();
        showRankedStocks();
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="board"]').change(function () {
        // 页面默认加载上证指数日K（D)
        // 页面默认加载上证指数日K（D)
        board = $(this).val()
        showRankedStocks();
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="industry"]').change(function () {
        // 页面默认加载上证指数日K（D)
        // 页面默认加载上证指数日K（D)
        industry = $(this).val()
        showRankedStocks();
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="province"]').change(function () {
        // 页面默认加载上证指数日K（D)
        // 页面默认加载上证指数日K（D)
        province = $(this).val()
        showRankedStocks();
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="area"]').change(function () {
        // 页面默认加载上证指数日K（D)
        // 页面默认加载上证指数日K（D)
        area = $(this).val()
        showRankedStocks();
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="degree"]').change(function () {
        // 页面默认加载上证指数日K（D)
        // 页面默认加载上证指数日K（D)
        degree = $(this).val()
        showRankedStocks();
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="marketVal"]').change(function () {
        // 页面默认加载上证指数日K（D)
        // 页面默认加载上证指数日K（D)
        marketVal = $(this).val()
        showRankedStocks();
    });

    $(".pagination").on("click", ".page-item", function (event) {
        // if (currentIdx + rowCount * 2 > totalRowCount) {
        //     $(this).prop("disabled", true)
        //     return;
        // } else {
        //     $(this).removeAttr("disabled")
        // }
        if ($(this).index() == 0) {
            // prev
            if (currentIdx == 0) return;
            else {
                currentIdx -= rowCount;
            }
            console.log(currentIdx);
        } else {
            // next
            if (currentIdx + rowCount + 1 > totalRowCount) {
                return;
            }
            // if (totalRowCount - currentIdx > 1 && totalRowCount - currentIdx - rowCount < rowCount) {
            //     rowCount = totalRowCount - currentIdx - rowCount;
            // } 
            currentIdx += rowCount;
            console.log(currentIdx);
        }

        prevPagination = $(this);
        bandPickingTable(pickStrategy, pickYear, pickMon, pickDay, period, expPct, currentIdx, currentIdx + rowCount);
    });

    // 初始化图表 
    initParam();
    // renderChart();
    showRankedStocks();
});