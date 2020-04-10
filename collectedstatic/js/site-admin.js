$(function () {
    var saBaseEndpoint = '/siteadmin/';

    function formatDate(date, conn) {
        var dayNames = [
            "01", "02", "03",
            "04", "05", "06", "07",
            "08", "09", "10",
            "11", "12", "13", "14",
            "15", "16", "17", "18",
            "19", "20", "21", "22",
            "23", "24", "25", "26",
            "27", "28", "29", "30", "31"
        ];

        var monthNames = [
            "01", "02", "03",
            "04", "05", "06", "07",
            "08", "09", "10",
            "11", "12"
        ];

        var dayIndex = date.getDate();
        var monthIndex = date.getMonth();
        var year = date.getFullYear();

        return year + conn + monthNames[monthIndex] + conn + dayNames[dayIndex - 1];
    }

    var isTradeOfftime = function (inputDatetime) {
        // var dateAndTime = inputDatetime.split(" ");
        var date = formatDate(inputDatetime, "-");
        var openTime = new Date(date + " 9:30:00");
        var closeTime = new Date(date + " 15:05:00");
        if (inputDatetime >= closeTime) {
            return true;
        }
        return false;
    }

    var showDetailOfPosition = function(pId) {
        // var pId = $(this).attr("id");
        if($("#pId" + pId).hasClass("d-none")){
            $("#pId" + pId).removeClass("d-none");
        }else{
            $("#pId" + pId).addClass("d-none");
        }
    }

    var showOrHideTradeRecBreakdown = function(refer_number) {
        // var pId = $(this).attr("id");
        if($("#bd_" + refer_number).hasClass("d-none")){
            $("#bd_" + refer_number).removeClass("d-none");
        }else{
            $("#bd_" + refer_number).addClass("d-none");
        }
    }

    var showOrHideTradeRecBreakdown = function(refer_number) {
        // var pId = $(this).attr("id");
        if($("#bd_" + refer_number).hasClass("d-none")){
            $("#bd_" + refer_number).removeClass("d-none");
        }else{
            $("#bd_" + refer_number).addClass("d-none");
        }
    }

    var showOrHideTradeRecPicked = function(refer_number) {
        // var pId = $(this).attr("id");
        if($("#alloc_" + refer_number).hasClass("d-none")){
            $("#alloc_" + refer_number).removeClass("d-none");
        }else{
            $("#alloc_" + refer_number).addClass("d-none");
        }
    }

    var showPickedRecords4Sell = function(ref_id){
        if( $("#alloc_"+ref_id).children().length==0){
            $.ajax({
                url: saBaseEndpoint + "trans/detail/pkd/" + ref_id,
                method: "GET",
                dataType: "json",
                success: function (data) {
                    if (data.code == 'ok') {
                        // alert(refer_number + " Clicked");
                        $(data.content).each(function(id, obj){
                            var direction = obj.direction;
                            var shares = 0;
                            var badge = '<span class="badge badge-pill badge-danger">买入</span>'
                            $("#alloc_"+ref_id).append(
                                '<hr>'+
                                '<div class="d-flex align-items-center justify-content-between flex-wrap small">'+
                                '<div class="text-muted">'+
                                    '<div><span class="font-weight-bold">ID</span></div>'+
                                    '<div>'+obj.id+'</div>'+
                                '</div>'+    
                                '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">类型</span></div>'+
                                        '<div>'+badge+'<i class="fa fa-robot"></i></div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">时间</span></div>'+
                                        '<div>'+obj.trade_time+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">价格</span></div>'+
                                        '<div>'+obj.price+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">数量</span></div>'+
                                        '<div>'+obj.shares+'</div>'+
                                    '</div>'+
                                    // '<div class="text-muted">'+
                                    //     '<div><span class="font-weight-bold">现价</span></div>'+
                                    //     '<div>'+obj.curent_price+'</div>'+
                                    // '</div>'+
                                    // '<div class="text-muted"> '+
                                    //     '<div><span class="font-weight-bold">账户</span></div>'+
                                    //     '<div>'+obj.account+'</div>'+
                                    // '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">已卖出？</span></div>'+
                                        '<div>'+obj.is_sold+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">卖出ID</span></div>'+
                                        '<div>'+obj.sell_ref+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">剩余持仓</span></div>'+
                                        '<div>'+obj.lots_remain+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">交易金额</span></div>'+
                                        '<div>'+obj.amount+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">引用编号</span></div>'+
                                        '<div><input type="button" class="btn btn-sm btn-link" id="ref_'+obj.refer_number+'" value="'+obj.refer_number+'"/></div>'+
                                    '</div>'+
                                '</div>'+
                                '<hr>'
                            )
                        });
                        showOrHideTradeRecPicked(ref_id);
                    }
                }
            });
        }else{
            showOrHideTradeRecPicked(ref_id)
        }
    }

    var showTradeBreakdown = function(id, refer_number) {
        // alert(refer_number);
        if( $("#bd_"+refer_number).children().length==0){
            $.ajax({
                url: saBaseEndpoint + "trans/detail/breakdown/" + id + "/" + refer_number,
                method: "GET",
                dataType: "json",
                success: function (data) {
                    if (data.code == 'ok') {
                        // alert(refer_number + " Clicked");
                        $(data.content).each(function(id, obj){
                            var direction = obj.direction;
                            var shares = 0;
                            var badge = '<span class="badge badge-pill badge-danger">买入</span>'
                            $("#bd_"+refer_number).append(
                                '<hr>'+
                                '<div class="d-flex align-items-center justify-content-between flex-wrap small">'+
                                '<div class="text-muted">'+
                                    '<div><span class="font-weight-bold">ID</span></div>'+
                                    '<div>'+obj.id+'</div>'+
                                '</div>'+    
                                '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">类型</span></div>'+
                                        '<div>'+badge+'<i class="fa fa-robot"></i></div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">时间</span></div>'+
                                        '<div>'+obj.trade_time+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">价格</span></div>'+
                                        '<div>'+obj.price+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">数量</span></div>'+
                                        '<div>'+obj.shares+'</div>'+
                                    '</div>'+
                                    // '<div class="text-muted">'+
                                    //     '<div><span class="font-weight-bold">现价</span></div>'+
                                    //     '<div>'+obj.curent_price+'</div>'+
                                    // '</div>'+
                                    // '<div class="text-muted"> '+
                                    //     '<div><span class="font-weight-bold">账户</span></div>'+
                                    //     '<div>'+obj.account+'</div>'+
                                    // '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">已卖出？</span></div>'+
                                        '<div>'+obj.is_sold+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">卖出ID</span></div>'+
                                        '<div>'+obj.sell_ref+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">剩余持仓</span></div>'+
                                        '<div>'+obj.lots_remain+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">交易金额</span></div>'+
                                        '<div>'+obj.amount+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">引用编号</span></div>'+
                                        '<div><input type="button" class="btn btn-sm btn-link" id="ref_'+obj.refer_number+'" value="'+obj.refer_number+'"/></div>'+
                                    '</div>'+
                                '</div>'+
                                '<hr>'
                            )
                        });
                        showOrHideTradeRecBreakdown(refer_number);
                    }
                }
            });
        }else{
            showOrHideTradeRecBreakdown(refer_number);
        }
    }
    
    var bindDetailOfPosition = function() {
        var pId = $(this).attr("id");
        if($("#pId" + pId).children().length==0){
            $.ajax({
                url: saBaseEndpoint + "trans/detail/position/" + pId,
                method: "GET",
                dataType: "json",
                success: function (data) {
                    if (data.code == 'ok') {
                        $(data.content).each(function(id, obj){
                            var direction = obj.direction;
                            var badge = "";
                            var sold = "";
                            var shares = 0;
                            if(direction=='b'){
                                badge = '<span class="badge badge-pill badge-danger">买入</span>'
                                shares = parseInt(obj.shares);
                            }else{
                                badge = '<span class="badge badge-pill badge-success">卖出</span>'
                                shares = - parseInt(obj.shares);
                            }
                            if(obj.is_sold){
                                sold = '<i class="fa fa-battery-empty"></i>'
                            }else{
                                if(obj.lots_remain < obj.shares){
                                    sold = '<i class="fa fa-battery-half"></i>'
                                }else if(obj.lots_remain == obj.shares){
                                    sold = '<i class="fa fa-battery-full"></i>'
                                }
                            }
                            $("#pId" + pId).append(
                                '<div class="d-flex align-items-center justify-content-between flex-wrap small">'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">ID</span></div>'+
                                        '<div><input type="button" class="btn btn-sm btn-link" id="pkd_'+obj.id+'" value="'+obj.id+'"/></div>'+
                                    '</div>'+    
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">类型</span></div>'+
                                        '<div>'+badge+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">时间</span></div>'+
                                        '<div>'+obj.trade_time+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">价格</span></div>'+
                                        '<div>'+obj.price+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">数量</span></div>'+
                                        '<div>'+shares+'</div>'+
                                    '</div>'+
                                    // '<div class="text-muted">'+
                                    //     '<div><span class="font-weight-bold">现价</span></div>'+
                                    //     '<div>'+obj.curent_price+'</div>'+
                                    // '</div>'+
                                    // '<div class="text-muted"> '+
                                    //     '<div><span class="font-weight-bold">账户</span></div>'+
                                    //     '<div>'+obj.account+'</div>'+
                                    // '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">已卖出？</span></div>'+
                                        '<div>'+sold+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">剩余持仓</span></div>'+
                                        '<div>'+obj.lots_remain+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">交易金额</span></div>'+
                                        '<div>'+obj.amount+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">引用编号</span></div>'+
                                        '<div><input type="button" class="btn btn-sm btn-link" id="ref_'+obj.refer_number+'" value="'+obj.refer_number+'"/></div>'+
                                    '</div>'+
                                '</div>'+
                                '<hr>'+
                                '<div class="mb-2 mt-2 d-none" id="alloc_'+obj.id+'">'+
                                '</div>'+
                                '<div class="mb-2 mt-2 d-none" id="bd_'+obj.refer_number+'">'+
                                '</div>'
                            );
                            document.getElementById("ref_"+obj.refer_number).addEventListener("click", function(a){
                                showTradeBreakdown(obj.id, obj.refer_number);
                            });// , event,);

                            document.getElementById("pkd_"+obj.id).addEventListener("click", function(a){
                                showPickedRecords4Sell(obj.id);
                            });// , event,);
                        });
                        showDetailOfPosition(pId);
                    } else {
                    alert("<p>" + data.message + "</p>");
                    }
                },
                error: function () {
                    $("#snapshotStatus").html("<p>An error has occurred</p>");
                    $("#snapshotSpinner").addClass("d-none");
                    $("#executeStockSnapshot").removeAttr("disabled");
                },
                statusCode: {
                    403: function () {
                        $("#snapshotStatus").append("<span>403 forbidden</span>");
                        $("#snapshotSpinner").addClass("d-none");
                        $("#executeStockSnapshot").removeAttr("disabled");
                    },
                    404: function () {
                        $("#snapshotStatus").append("<span>404 page not found</span>");
                        $("#snapshotSpinner").addClass("d-none");
                        $("#executeStockSnapshot").removeAttr("disabled");
                    },
                    500: function () {
                        $("#snapshotStatus").append("<span>500 internal server error</span>");
                        $("#snapshotSpinner").addClass("d-none");
                        $("#executeStockSnapshot").removeAttr("disabled");
                    }
                }
            });
        }else{
            showDetailOfPosition(pId);
        }
    };

    $("#executeStockSnapshot").click(function () {
        if (!isTradeOfftime(new Date()))
            return;
        var appliedPeriod = "d";
        $('#snapshotSpinner').removeClass('d-none');
        $(this).prop("disabled", true);
        $.ajax({
            url: saBaseEndpoint + "snapshot/manual/",
            method: "GET",
            dataType: "json",
            success: function (data) {
                if (data.code == 'ok') {
                    $("#snapshotStatus").html(data.message);
                    $("#snapshotSpinner").addClass("d-none");
                    $("#executeStockSnapshot").removeAttr("disabled");
                } else {
                    $("#snapshotStatus").html("<p>" + data.message + "</p>");
                    $("#snapshotSpinner").addClass("d-none");
                    $("#executeStockSnapshot").removeAttr("disabled");
                }
            },
            error: function () {
                $("#snapshotStatus").html("<p>An error has occurred</p>");
                $("#snapshotSpinner").addClass("d-none");
                $("#executeStockSnapshot").removeAttr("disabled");
            },
            statusCode: {
                403: function () {
                    $("#snapshotStatus").append("<span>403 forbidden</span>");
                    $("#snapshotSpinner").addClass("d-none");
                    $("#executeStockSnapshot").removeAttr("disabled");
                },
                404: function () {
                    $("#snapshotStatus").append("<span>404 page not found</span>");
                    $("#snapshotSpinner").addClass("d-none");
                    $("#executeStockSnapshot").removeAttr("disabled");
                },
                500: function () {
                    $("#snapshotStatus").append("<span>500 internal server error</span>");
                    $("#snapshotSpinner").addClass("d-none");
                    $("#executeStockSnapshot").removeAttr("disabled");
                }
            }
        });
    });

    $("#syncCompanyInfo").click(function () {
        $('#syncSpinner').removeClass('d-none');
        $(this).prop("disabled", true);

        $.ajax({
            url: investBaseEndpoint + 'sync-company-list/',
            method: 'GET',
            dataType: 'json',
            success: function (data) {
                $('#syncStatus').html(data.success);
                $('#syncSpinner').addClass('d-none');
                $('#syncCompanyInfo').removeAttr('disabled');
            },
            error: function () {
                $('#syncStatus').html('<p>An error has occurred</p>');
                $('#syncSpinner').addClass('d-none');
                $('#syncCompanyInfo').removeAttr('disabled');
            },
            statusCode: {
                403: function () {
                    $("#syncStatus").append("<span>403 forbidden</span>");
                    $('#syncSpinner').addClass('d-none');
                    $('#syncCompanyInfo').removeAttr('disabled');

                },
                404: function () {
                    $("#syncStatus").append("<span>404 page not found</span>");
                    $('#syncSpinner').addClass('d-none');
                    $('#syncCompanyInfo').removeAttr('disabled');

                },
                500: function () {
                    $("#syncStatus").append(
                        "<span>500 internal server error</span>"
                    );
                    $('#syncSpinner').addClass('d-none');
                    $('#syncCompanyInfo').removeAttr('disabled');
                }
            }
        });
    });

    var btns = document.getElementsByName("show-trade-record");
    $(btns).each(function(id, obj){
       $(obj).on("click", bindDetailOfPosition);
    });

    // bindDetailOfPosition();
});

