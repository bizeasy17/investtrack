$(function () {
    var recordCount = 50;
    // ranking/<strategy_code>/<test_type>/<qt_pct>/<input_param>/<int:start_idx>/<int:end_idx>/
    var pickStrategy;
    // var sStrategy;
    var pickYear;
    var pickMon;
    var pickDay;
    var inputParam;
    var startIdx = 0;
    var rowCount = 25;
    var currentIdx = 0;
    var prevStockPickTr = undefined;
    var analysisEndpoint = '/analysis/';

    var selStockName;
    var selStockCode;
    var showStockCode;

    var initParam = function () {
        pickStrategy = $('input:radio[name="bstrategy"]:checked').val();
        // sStrategy = $('input:radio[name="sstrategy"]:checked').val();
        pickYear = $('input:radio[name="pick-yr"]:checked').val();
        pickMon = $('input:radio[name="pick-mon"]:checked').val();
        pickDay = $('input:radio[name="pick-day"]:checked').val();
    }

    var updateStockPicking = function (strategyCode, pickYear, pickMon, pickDay) {
        bandPickingTable(strategyCode, pickYear, pickMon, pickDay);
    }

    var showStockDetailRanking = function () {
        var nameCode = $(this).find('th a');
        selStockName = $(nameCode[0]).text();
        selStockCode = $(nameCode[1]).text();
        showStockCode = selStockCode;
        if (prevStockPickTr) {
            if ($(prevStockPickTr).hasClass("bg-light")) {
                $(prevStockPickTr).removeClass("bg-light");
            }
        }
        prevStockPickTr = this;
        $(this).addClass("bg-light");
        $(".cur-stock").text(selStockName + ' - ' + showStockCode);
        updateStockPicking(selStockCode, testPeriod, targetPct);
    }

    var bandPickingTable = function (strategyCode, pickYear, pickMon, pickDay, startIdx, endIdx) {
        var tbd = $("#tblPickedStocks > tbody");
        $.ajax({
            url: analysisEndpoint + 'xuangu/' + pickYear + "/" + pickMon + "/" + pickDay + "/" + strategyCode + "/" + startIdx + "/" + endIdx + "/",
            success: function (data) {
                tbd.empty();
                $(data.value).each(function (idx, pkStocks) {
                    // var me = this;//save `this` reference
                    // $(pkStocks.qt_uppct).each(function (idx, upPct) {
                    // });

                    // $(pkStocks.qt_downpct).each(function (idx, downPct) {
                    // });
                    
                    // $(pkStocks.qt_targetpct).each(function (idx, targetPct) {
                    // });
                    var content = "";
                    content += 
                        '<tr>'+
                            '<th scope="row">'+
                                '<div class="">'+
                                    '<div class="card-title small"><a href="#" class="text-dark">'+pkStocks.ts_code+'</a><span class="small text-muted" id=""></span></div>'+
                                    '<div class="card-subtitle small text-muted"><a href="#" class="text-dark">'+pkStocks.ts_code+'</a></div>'+
                                '</div>'+
                            '</th>'+
                            '<td>'+
                                '<span class="small">'+pkStocks.price+'</span>'+
                            '</td>'+
                            '<td>'+
                                '<span class="small">'+pkStocks.chg_pct+'</span>'+
                            '</td>';
                    content += 
                            '<td>'+
                                '<div class="content-wrapper small">'+
                                    '<div class="row">'+
                                        '<div class="col-lg-2">持仓天数</div>'+
                                        '<div class="col-lg-2">25ile</div>'+
                                        '<div class="col-lg-2">50ile</div>'+
                                        '<div class="col-lg-2">75ile</div>'+
                                        '<div class="col-lg-2">Max</div>' +
                                        '<div class="col-lg-2">Mean</div>' +
                                    '</div>';
                    
                    for(var i=0;i<pkStocks.qt_uppct.length;i++){  
                        var obj = pkStocks.qt_uppct[i];
                        content +=              
                                    '<div class="row">'+
                                        '<div class="col-lg-2">'+
                                            obj.period +
                                        '</div>'+
                                        '<div class="col-lg-2">'+
                                            obj.qt25ile +
                                        '</div>'+
                                        '<div class="col-lg-2">'+
                                            obj.qt50ile +
                                        '</div>'+
                                        '<div class="col-lg-2">'+
                                            obj.qt75ile +
                                        '</div>'+
                                        '<div class="col-lg-2">' +
                                            obj.max +
                                        '</div>'+
                                        '<div class="col-lg-2">' +
                                            obj.mean +
                                        '</div>'+
                                    '</div>';
                    }
                    content +=
                                '</div>'+
                            '</td>';
                    
                    content += 
                            '<td>'+
                                '<div class="content-wrapper small">'+
                                    '<div class="row">'+
                                        '<div class="col-lg-2">持仓天数</div>'+
                                        '<div class="col-lg-2">25ile</div>'+
                                        '<div class="col-lg-2">50ile</div>'+
                                        '<div class="col-lg-2">75ile</div>'+
                                        '<div class="col-lg-2">Max</div>'+
                                        '<div class="col-lg-2">Mean</div>'+
                                    '</div>';
                    
                    for(var i=0;i<pkStocks.qt_downpct.length;i++){  
                        var obj = pkStocks.qt_downpct[i];
                        content +=              
                                    '<div class="row">'+
                                        '<div class="col-lg-2">'+
                                            obj.period +
                                        '</div>'+
                                        '<div class="col-lg-2">'+
                                            obj.qt25ile +
                                        '</div>'+
                                        '<div class="col-lg-2">'+
                                            obj.qt50ile +
                                        '</div>'+
                                        '<div class="col-lg-2">'+
                                            obj.qt75ile +
                                        '</div>'+
                                        '<div class="col-lg-2">' +
                                            obj.max +
                                        '</div>'+
                                        '<div class="col-lg-2">' +
                                            obj.mean +
                                        '</div>'+
                                    '</div>';
                    }
                    content +=
                                '</div>'+
                            '</td>';
                    
                    content += 
                            '<td>'+
                                '<div class="content-wrapper small">'+
                                    '<div class="row">'+
                                        '<div class="col-lg-2">涨幅</div>'+
                                        '<div class="col-lg-2">25ile</div>'+
                                        '<div class="col-lg-2">50ile</div>'+
                                        '<div class="col-lg-2">75ile</div>'+
                                        '<div class="col-lg-2">Max</div>'+
                                        '<div class="col-lg-2">Mean</div>'+
                                    '</div>';
                    
                    for(var i=0;i<pkStocks.qt_targetpct.length;i++){  
                        var obj = pkStocks.qt_targetpct[i];
                        content +=              
                                    '<div class="row">'+
                                        '<div class="col-lg-2">'+
                                            obj.period +
                                        '</div>'+
                                        '<div class="col-lg-2">'+
                                            obj.qt25ile +
                                        '</div>'+
                                        '<div class="col-lg-2">'+
                                            obj.qt50ile +
                                        '</div>'+
                                        '<div class="col-lg-2">'+
                                            obj.qt75ile +
                                        '</div>'+
                                        '<div class="col-lg-2">' +
                                            obj.min +
                                        '</div>'+
                                        '<div class="col-lg-2">' +
                                            obj.mean +
                                        '</div>'+
                                    '</div>';
                    }
                    content +=
                                '</div>'+
                            '</td>'+
                        '</tr>';
                    tbd.append(content);
                    // tbd.append(
                    //     '<tr>'+
                    //         '<th scope="row">'+
                    //             '<div class="">'+
                    //                 '<div class="card-title small"><a href="#" class="text-dark">'+pkStocks.ts_code+'</a><span class="small text-muted" id=""></span></div>'+
                    //                 '<div class="card-subtitle small text-muted"><a href="#" class="text-dark">'+pkStocks.ts_code+'</a></div>'+
                    //             '</div>'+
                    //         '</th>'+
                    //         '<td>'+
                    //             '<span class="small">'+pkStocks.price+'</span>'+
                    //         '</td>'+
                    //         '<td>'+
                    //             '<span class="small">'+pkStocks.chg_pct+'</span>'+
                    //         '</td>'+
                    //         '<td>'+
                    //             '<div class="content-wrapper small">'+
                    //                 '<div class="row">'+
                    //                     '<div class="col-lg-2">持仓天数</div>'+
                    //                     '<div class="col-lg-2">25ile</div>'+
                    //                     '<div class="col-lg-2">50ile</div>'+
                    //                     '<div class="col-lg-2">75ile</div>'+
                    //                     '<div class="col-lg-2">Max</div>' +
                    //                     '<div class="col-lg-2">Mean</div>' +
                    //                 '</div>'+
                    //                 '<div class="row">'+
                    //                     '<div class="col-lg-2">'+
                    //                         10
                    //                     '</div>'+
                    //                     '<div class="col-lg-2">'+
                    //                         2%
                    //                     '</div>'+
                    //                     '<div class="col-lg-2">'+
                    //                         3.5%
                    //                     '</div>'+
                    //                     '<div class="col-lg-2">'+
                    //                         8%
                    //                     '</div>'+
                    //                     '<div class="col-lg-2">' +
                    //                         8 %
                    //                     '</div>'+
                    //                 '</div>'+
                    //             '</div>'+
                    //         '</td>'+
                    //         '<td>'+
                    //             '<div class="content-wrapper small">'+
                    //                 '<div class="row">'+
                    //                     '<div class="col-lg-2">持仓</div>'+
                    //                     '<div class="col-lg-2">25ile</div>'+
                    //                     '<div class="col-lg-2">50ile</div>'+
                    //                     '<div class="col-lg-2">75ile</div>'+
                    //                     '<div class="col-lg-2">Max</div>'+
                    //                     '<div class="col-lg-2">Mean</div>'+
                    //                 '</div>'+
                    //                 '<div class="row">'+
                    //                     '<div class="col-lg-2">'+
                    //                         10天
                    //                     '</div>'+
                    //                     '<div class="col-lg-2">'+
                    //                         -2%
                    //                     '</div>'+
                    //                     '<div class="col-lg-2">'+
                    //                         -3.5%
                    //                     '</div>'+
                    //                     '<div class="col-lg-2">'+
                    //                         -8%
                    //                     '</div>'+
                    //                     '<div class="col-lg-2">'+
                    //                         -3.5%
                    //                     '</div>'+
                    //                     '<div class="col-lg-2">'+
                    //                         -28%
                    //                     '</div>'+
                    //                 '</div>'+
                    //             '</div>'+
                    //         '</td>'+
                    //         '<td>'+
                    //             '<div class="content-wrapper small">'+
                    //                 '<div class="row">'+
                    //                     '<div class="col-lg-2">涨幅</div>'+
                    //                     '<div class="col-lg-2">25ile</div>'+
                    //                     '<div class="col-lg-2">50ile</div>'+
                    //                     '<div class="col-lg-2">75ile</div>'+
                    //                     '<div class="col-lg-2">Max</div>'+
                    //                     '<div class="col-lg-2">Mean</div>'+
                    //                 '</div>'+
                    //                 '<div class="row">'+
                    //                     '<div class="col-lg-2">'+
                    //                         10%
                    //                     '</div>'+
                    //                     '<div class="col-lg-2">'+
                    //                         15
                    //                     '</div>'+
                    //                     '<div class="col-lg-2">'+
                    //                         35
                    //                     '</div>'+
                    //                     '<div class="col-lg-2">'+
                    //                         80
                    //                     '</div>'+
                    //                     '<div class="col-lg-2">'+
                    //                         35
                    //                     '</div>'+
                    //                     '<div class="col-lg-2">'+
                    //                         80
                    //                     '</div>‘+
                    //                 '</div>’+
                    //             '</div>‘+
                    //         '</td>’+
                    //     '</tr>‘
                    // )
                    // tbd.append(
                    //     '<tr id="rankingRow' + pkStocks.ts_code + '">' +
                    //     '<th scope="row">' +
                    //     '<div class="">' +
                    //     '<div class="card-title small"><a href="#" class="text-dark">' + pkStocks.stock_name + '</a><span class="small text-muted" id="xxx"></span></div>' +
                    //     '<div class="card-subtitle small text-muted"><a href="#" class="text-dark">' + pkStocks.ts_code + '</a></div>' +
                    //     '</div>' +
                    //     '</th>' +
                    //     '<td><span id="" class="small">-</span></td>' +
                    //     '<td><span id="" class="small">' + pkStocks.qt_pct_val + '</span></td>' +
                    //     '<td><span id="" class="small">' + (pkStocks.rank + 1) + '</span></td>' +
                    //     '</tr>'
                    // );
                    // var showStockRanking = document.getElementById("rankingRow" + pkStocks.ts_code);
                    // showStockRanking.addEventListener("click", showStockDetailRanking);
                });
            },
            statusCode: {
                403: function () {
                },
                404: function () {
                    $(tbd).append(
                        '<th scope="row">' +
                        '<div class="">' +
                        '<div class="card-title small"><a href="#" class="text-dark">无选股记录</a><span class="small text-muted" id="xxx"></span></div>' +
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

    // 初始化ranking表
    initParam();
    bandPickingTable(pickStrategy, pickYear, pickMon, pickDay, startIdx, rowCount);

    $('input:radio[name="pick-yr"]').change(function () {
        // 页面默认加载上证指数日K（D)
        pickYear = this.value;
        bandPickingTable(pickStrategy, pickYear, pickMon, pickDay, startIdx, rowCount);
    });

    $('input:radio[name="pick-mon"]').change(function () {
        // 页面默认加载上证指数日K（D)
        pickMon = this.value;
        bandPickingTable(pickStrategy, pickYear, pickMon, pickDay, startIdx, rowCount);
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="pick-day"]').change(function () {
        // 页面默认加载上证指数日K（D)
        pickDay = this.value;
        bandPickingTable(pickStrategy, pickYear, pickMon, pickDay, startIdx, rowCount);
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="bstrategy"]').change(function () {
        // 页面默认加载上证指数日K（D)
        pickStrategy = this.value;
        bandPickingTable(pickStrategy, pickYear, pickMon, pickDay, startIdx, rowCount);
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="sstrategy"]').change(function () {
        // 页面默认加载上证指数日K（D)
        pickStrategy = this.value;
        bandPickingTable(pickStrategy, pickYear, pickMon, pickDay, startIdx, rowCount);
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
        bandPickingTable(pickStrategy, pickYear, pickMon, pickDay, currentIdx, currentIdx + rowCount);
    });
});