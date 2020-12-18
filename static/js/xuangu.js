$(function () {
    var recordCount = 50;
    var csrftoken = Cookies.get('csrftoken');
    // ranking/<strategy_code>/<test_type>/<qt_pct>/<input_param>/<int:start_idx>/<int:end_idx>/
    var pickStrategy;
    // var sStrategy;
    var pickYear;
    var pickMon;
    var pickDay;
    var period;
    var expPct;
    var inputParam;
    var startIdx = 0;
    var rowCount = 5;
    var currentIdx = 0;
    var prevStockPickTr = undefined;
    var analysisEndpoint = '/analysis/';
    var investorEndpoint = "/investors/";
    var totalRowCount = 0
    var prevPagination;
    var bstr;
    var sstr;

    var selStockName;
    var selStockCode;
    var showStockCode;

    var initParam = function () {
        pickStrategy = $('input:radio[name="bstrategy"]:checked').val();
        // sStrategy = $('input:radio[name="sstrategy"]:checked').val();
        pickYear = $('input:radio[name="pick-yr"]:checked').val();
        pickMon = $('input:radio[name="pick-mon"]:checked').val();
        pickDay = $('input:radio[name="pick-day"]:checked').val();
        period = $('input:radio[name="stk-period"]:checked').val();
        expPct = $('input:radio[name="stk-pct_period"]:checked').val();
        bstr = $('input:radio[name="bstrategy"]');
    }

    var followStock = function (symbol, name) {
        $.ajax(
            {
                url: investorEndpoint + 'follow-stock/' + symbol + "/",
                data: {
                    name: name
                },
                headers: { 'X-CSRFToken': csrftoken },
                method: 'POST',
                success: function (data) {
                    $("#messages").removeClass('d-none');
                    if (data.code == "ok") {
                        $("#messages").addClass('alert-success');
                    } else {
                        $("#messages").addClass('alert-danger');
                    }
                    $("#messageText").html("<strong>" + data.message + "</strong>");
                },
                statusCode: {
                    403: function () {
                        alert("403 forbidden");
                    },
                    404: function () {
                        alert("404 page not found");
                    },
                    500: function () {
                        alert("500 internal server error");
                    }
                }
            }
        );
    }


    var updateStockPicking = function (strategyCode, pickYear, pickMon, pickDay, period, expPct) {
        bandPickingTable(strategyCode, pickYear, pickMon, pickDay, period, expPct);
    }

    var bandPickingTable = function (strategyCode, pickYear, pickMon, pickDay, period, expPct, startIdx, endIdx) {
        var container = $("#pkResults");
        $.ajax({
            url: analysisEndpoint + 'xuangu/' + pickYear + "/" + pickMon + "/" + pickDay + "/" + strategyCode + "/" + period + "/" + expPct + "/" + startIdx + "/" + endIdx + "/",
            success: function (data) {
                // return;
                container.empty();
                $(data.value).each(function (idx, pkStocks) {
                    var content = "";
                    var pctInd = ""
                    if (parseFloat(pkStocks.chg_pct) < 0) {
                        pctInd = "text-success";
                    } else {
                        pctInd = "text-danger";
                    }
                    content +=
                        '<div class="row">' +
                        '<div class="col-lg-2">' +
                        '<div class="small">' +
                        '<a href="#" class="text-dark">' + pkStocks.stockname + '</a><span class="small text-muted" id=""> ' + pkStocks.ts_code + '</span>' +
                        // '<div class="card-subtitle small text-muted"><a href="#" class="text-dark">'+pkStocks.ts_code+'</a></div>'+
                        '</div>' +
                        '<div class="small">' +
                        '<span class="small text-muted" id="xxx">价:' + pkStocks.price + '</span>' +
                        '<span class="small ' + pctInd + '" id="xxx"> 涨跌: ' + pkStocks.chg_pct + '%</span>' +
                        '</div>' +
                        '<div class="small">' +
                        '<span class="small text-light btn btn-sm btn-info follow" id="' + pkStocks.ts_code + ',' + pkStocks.stockname + '">加自选</span>' +
                        '</div>' +
                        '</div>';

                    content +=
                        '<div class="col-lg-3">' +
                        '<div class="content-wrapper small">' +
                        '<div class="row">' +
                        '<div class="col-lg-2">(天)</div>' +
                        '<div class="col-lg-2">25ile</div>' +
                        '<div class="col-lg-2">50ile</div>' +
                        '<div class="col-lg-2">75ile</div>' +
                        '<div class="col-lg-2">Mean</div>' +
                        '<div class="col-lg-2">Best</div>' +
                        '</div>';

                    for (var i = 0; i < pkStocks.qt_uppct.length; i++) {
                        var obj = pkStocks.qt_uppct[i];
                        content +=
                            '<div class="row">' +
                            '<div class="col-lg-2">' +
                            obj.period +
                            '</div>' +
                            '<div class="col-lg-2">' +
                            obj.qt25ile +
                            '</div>' +
                            '<div class="col-lg-2">' +
                            obj.qt50ile +
                            '</div>' +
                            '<div class="col-lg-2">' +
                            obj.qt75ile +
                            '</div>' +
                            '<div class="col-lg-2">' +
                            obj.mean +
                            '</div>' +
                            '<div class="col-lg-2">' +
                            obj.max +
                            '</div>' +
                            '</div>';
                    }
                    content +=
                        '</div>' +
                        '</div>';

                    content +=
                        '<div class="col-lg-3">' +
                        '<div class="content-wrapper small">' +
                        '<div class="row">' +
                        '<div class="col-lg-2">(天)</div>' +
                        '<div class="col-lg-2">25ile</div>' +
                        '<div class="col-lg-2">50ile</div>' +
                        '<div class="col-lg-2">75ile</div>' +
                        '<div class="col-lg-2">Mean</div>' +
                        '<div class="col-lg-2">Worst</div>' +
                        '</div>';

                    for (var i = 0; i < pkStocks.qt_downpct.length; i++) {
                        var obj = pkStocks.qt_downpct[i];
                        content +=
                            '<div class="row">' +
                            '<div class="col-lg-2">' +
                            obj.period +
                            '</div>' +
                            '<div class="col-lg-2">' +
                            obj.qt25ile +
                            '</div>' +
                            '<div class="col-lg-2">' +
                            obj.qt50ile +
                            '</div>' +
                            '<div class="col-lg-2">' +
                            obj.qt75ile +
                            '</div>' +
                            '<div class="col-lg-2">' +
                            obj.mean +
                            '</div>' +
                            '<div class="col-lg-2">' +
                            obj.min +
                            '</div>' +
                            '</div>';
                    }
                    content +=
                        '</div>' +
                        '</div>';

                    content +=
                        '<div class="col-lg-4">' +
                        '<div class="content-wrapper small">' +
                        '<div class="row">' +
                        '<div class="col-lg-2">涨幅</div>' +
                        '<div class="col-lg-2">25ile</div>' +
                        '<div class="col-lg-2">50ile</div>' +
                        '<div class="col-lg-2">75ile</div>' +
                        '<div class="col-lg-2">Mean</div>' +
                        '<div class="col-lg-2">Best</div>' +
                        '</div>';

                    for (var i = 0; i < pkStocks.qt_targetpct.length; i++) {
                        var obj = pkStocks.qt_targetpct[i];
                        content +=
                            '<div class="row">' +
                            '<div class="col-lg-2">' +
                            obj.pct +
                            '</div>' +
                            '<div class="col-lg-2">' +
                            obj.qt25ile +
                            '</div>' +
                            '<div class="col-lg-2">' +
                            obj.qt50ile +
                            '</div>' +
                            '<div class="col-lg-2">' +
                            obj.qt75ile +
                            '</div>' +
                            '<div class="col-lg-2">' +
                            obj.mean +
                            '</div>' +
                            '<div class="col-lg-2">' +
                            obj.min +
                            '</div>' +
                            '</div>';
                    }
                    content +=
                        '</div>' +
                        '</div>' +
                        '</div>' +
                        '<hr/>';
                    container.append(content);
                });

                $(".follow").click(function () {
                    followStock($(this).attr("id").split(",")[0], $(this).attr("id").split(",")[1]);
                });

                $(container).append(
                    '<div class="row">' +
                    '<div class="col-lg-12">' +
                    '<div class="card-title small"><a href="#" class="text-dark">选股结果共: ' + data.row_count + ' 条</a><span class="small text-muted" id="xxx"></span></div>' +
                    '<div class="card-subtitle small text-muted">当前: ' + (currentIdx + 1) + ' - ' + (currentIdx + rowCount) + ' 条<a href="#" class="text-dark"></a></div>' +
                    '</div>' +
                    '</div>'
                );
                totalRowCount = data.row_count;
            },
            statusCode: {
                403: function () {
                },
                404: function () {
                    $(container).empty();
                    $(container).append(
                        '<th scope="row">' +
                        '<div class="">' +
                        '<div class="card-title small"><a href="#" class="text-dark">无选股记录</a><span class="small text-muted" id="xxx"></span></div>' +
                        '<div class="card-subtitle small text-muted"><a href="#" class="text-dark"></a></div>' +
                        '</div>' +
                        '</th>'
                    );
                },
                500: function () {
                    $(container).empty();
                    $(container).append(
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
    bandPickingTable(pickStrategy, pickYear, pickMon, pickDay, period, expPct, startIdx, rowCount);

    $('input:radio[name="pick-yr"]').change(function () {
        // 页面默认加载上证指数日K（D)
        pickYear = this.value;
        bandPickingTable(pickStrategy, pickYear, pickMon, pickDay, period, expPct, startIdx, rowCount);
    });

    $('input:radio[name="pick-mon"]').change(function () {
        // 页面默认加载上证指数日K（D)
        pickMon = this.value;
        bandPickingTable(pickStrategy, pickYear, pickMon, pickDay, period, expPct, startIdx, rowCount);
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="pick-day"]').change(function () {
        // 页面默认加载上证指数日K（D)
        pickDay = this.value;
        bandPickingTable(pickStrategy, pickYear, pickMon, pickDay, period, expPct, startIdx, rowCount);
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="bstrategy"]').change(function () {
        // 页面默认加载上证指数日K（D)
        bstr = $(this)
        if (sstr != undefined) {
            $(sstr).removeAttr("checked")
            $(sstr).parent("label").removeClass("active");
        } 

        pickStrategy = this.value;
        bandPickingTable(pickStrategy, pickYear, pickMon, pickDay, period, expPct, startIdx, rowCount);
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="sstrategy"]').change(function () {
        // 页面默认加载上证指数日K（D)
        sstr = $(this);
        if (bstr != undefined) {
            $(bstr).removeAttr("checked")
            $(bstr).parent("label").removeClass("active");
        } 
        pickStrategy = this.value;
        bandPickingTable(pickStrategy, pickYear, pickMon, pickDay, period, expPct, startIdx, rowCount);
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="stk-period"]').change(function () {
        // 页面默认加载上证指数日K（D)
        period = this.value;
        bandPickingTable(pickStrategy, pickYear, pickMon, pickDay, period, expPct, startIdx, rowCount);
    });

    // 根据选择的期望收益，显示达到期望收益的天数
    $('input:radio[name="stk-pct_period"]').change(function () {
        // 页面默认加载上证指数日K（D)
        expPct = this.value;
        bandPickingTable(pickStrategy, pickYear, pickMon, pickDay, period, expPct, startIdx, rowCount);
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
});