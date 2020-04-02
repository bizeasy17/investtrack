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

    var showTradeBreakdown = function(refer_number) {
        // alert(refer_number);
         $.ajax({
            url: saBaseEndpoint + "trans/detail/breakdown/" + refer_number,
            method: "GET",
            dataType: "json",
            success: function (data) {
                if (data.code == 'ok') {
                    alert(refer_number + " Clicked");
                }
            }
        });
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
                            if(direction=='b'){
                                badge = '<span class="badge badge-pill badge-danger">买入</span>'
                            }else{
                                badge = '<span class="badge badge-pill badge-success">卖出</span>'
                            }
                            $("#pId" + pId).append(
                                '<div class="d-flex align-items-center justify-content-between flex-wrap small">'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">交易类型</span></div>'+
                                        '<div>'+badge+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">交易时间</span></div>'+
                                        '<div>'+obj.trade_time+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">交易价格</span></div>'+
                                        '<div>'+obj.price+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">现价</span></div>'+
                                        '<div>'+obj.curent_price+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted"> '+
                                        '<div><span class="font-weight-bold">账户</span></div>'+
                                        '<div>'+obj.account+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">是否已卖出</span></div>'+
                                        '<div>'+obj.is_sold+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">剩余持仓</span></div>'+
                                        '<div>'+obj.lots_remain+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">发生金额</span></div>'+
                                        '<div>'+obj.amount+'</div>'+
                                    '</div>'+
                                    '<div class="text-muted">'+
                                        '<div><span class="font-weight-bold">引用编号</span></div>'+
                                        '<div><input type="button" class="btn btn-sm btn-link" id="ref_'+obj.refer_number+'" value="'+obj.refer_number+'"/></div>'+
                                    '</div>'+
                                '</div>'+
                                '<hr>'+
                                '<div class="mb-2 mt-2 d-none" id="bd_'+obj.refer_number+'">'+
                                '</div>'
                            );
                            document.getElementById("ref_"+obj.refer_number).addEventListener("click", function(a){
                                showTradeBreakdown(obj.refer_number);
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

