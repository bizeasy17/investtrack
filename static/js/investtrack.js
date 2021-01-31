/* Project specific Javascript goes here. */

/*
Formatting hack to get around crispy-forms unfortunate hardcoding
in helpers.FormHelper:

    if template_pack == 'bootstrap4':
        grid_colum_matcher = re.compile('\w*col-(xs|sm|md|lg|xl)-\d+\w*')
        using_grid_layout = (grid_colum_matcher.match(self.label_class) or
                             grid_colum_matcher.match(self.field_class))
        if using_grid_layout:
            items['using_grid_layout'] = True

Issues with the above approach:

1. Fragile: Assumes Bootstrap 4's API doesn't change (it does)
2. Unforgiving: Doesn't allow for any variation in template design
3. Really Unforgiving: No way to override this behavior
4. Undocumented: No mention in the documentation, or it's too hard for me to find
*/
$('.form-group').removeClass('row');
var refreshInterval = 1;

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

var isOpenForTrade = function (inputDatetime) {
    // var dateAndTime = inputDatetime.split(" ");
    var date = formatDate(inputDatetime, "-");
    var openTime = new Date(date + " 9:30:00");
    var morningCloseTime = new Date(date + " 11:30:00");
    var afternoonOpenTime = new Date(date + " 13:00:00");
    var closeTime = new Date(date + " 15:00:00");
    var day = inputDatetime.getDay();
    var hour = inputDatetime.getHours();
    var min = inputDatetime.getMinutes();
    if (day == 0 || day == 6) return false; //周六周日不需要刷新
    if (inputDatetime >= openTime && inputDatetime <= morningCloseTime) {
        return true;
    }
    if (inputDatetime >= afternoonOpenTime && inputDatetime <= closeTime) {
        return true;
    }
    if (inputDatetime > date) {
        return false;
    }
    return false;
}

/* Notifications JS basic client */
$(function () {
    var saBaseEndpoint = '/siteadmin/';
    let emptyMessage = '你有新的通知';
    // function checkNotifications() {
    //     $.ajax({
    //         url: '/notifications/latest-notifications/',
    //         cache: false,
    //         success: function (data) {
    //             if (!data.includes(emptyMessage)) {
    //                 $("#notifications").addClass("btn-danger");
    //             }
    //         },
    //     });
    // };

    // function update_social_activity(id_value) {
    //     let newsToUpdate = $("[news-id=" + id_value + "]");
    //     payload = {
    //         'id_value': id_value,
    //     };
    //     $.ajax({
    //         url: '/news/update-interactions/',
    //         data: payload,
    //         type: 'POST',
    //         cache: false,
    //         success: function (data) {
    //             $(".like-count", newsToUpdate).text(data.likes);
    //             $(".comment-count", newsToUpdate).text(data.comments);
    //         },
    //     });
    // };

    // checkNotifications();

    // $('#notifications').popover({
    //     html: true,
    //     trigger: 'manual',
    //     container: "body",
    //     placement: "bottom",
    // });

    // $("#notifications").click(function () {
    //     if ($(".popover").is(":visible")) {
    //         $("#notifications").popover('hide');
    //         checkNotifications();
    //     }
    //     else {
    //         $("#notifications").popover('dispose');
    //         $.ajax({
    //             url: '/notifications/latest-notifications/',
    //             cache: false,
    //             success: function (data) {
    //                 $("#notifications").popover({
    //                     html: true,
    //                     trigger: 'focus',
    //                     container: "body",
    //                     placement: "bottom",
    //                     content: data,
    //                 });
    //                 $("#notifications").popover('show');
    //                 $("#notifications").removeClass("btn-danger")
    //             },
    //         });
    //     }
    //     return false;
    // });

    // Code block to manage WebSocket connections
    // Try to correctly decide between ws:// and wss://
    // let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    // let ws_path = ws_scheme + '://' + window.location.host + "/notifications/";
    // let webSocket = new channels.WebSocketBridge();
    // webSocket.connect(ws_path);

    // Helpful debugging
    // webSocket.socket.onopen = function () {
    //     console.log("Connected to " + ws_path);
    // };

    // webSocket.socket.onclose = function () {
    //     console.error("Disconnected from " + ws_path);
    // };

    // Listen the WebSocket bridge created throug django-channels library.
    // webSocket.listen(function (event) {
    //     switch (event.key) {
    //         case "notification":
    //             $("#notifications").addClass("btn-danger");
    //             break;

    //         case "social_update":
    //             $("#notifications").addClass("btn-danger");
    //             update_social_activity(event.id_value);
    //             break;

    //         case "additional_news":
    //             if (event.actor_name !== currentUser) {
    //                 $(".stream-update").show();
    //             }
    //             break;

    //         default:
    //             console.log('error: ', event);
    //             break;
    //     };
    // });

    var showDetailOfPosition = function (pId) {
        // var pId = $(this).attr("id");
        if ($("#pId" + pId).hasClass("d-none")) {
            $("#pId" + pId).removeClass("d-none");
        } else {
            $("#pId" + pId).addClass("d-none");
        }
    }

    var bindDetailOfPosition = function () {
        var pId = $(this).attr("id");
        if ($("#pId" + pId).children().length == 0) {
            $.ajax({
                url: saBaseEndpoint + "trans/detail/position/" + pId,
                method: "GET",
                dataType: "json",
                success: function (data) {
                    if (data.code == 'ok') {
                        $(data.content).each(function (id, obj) {
                            var direction = obj.direction;
                            var badge = "";
                            var sold = "";
                            var shares = 0;
                            if (direction == 'b') {
                                badge = '<span class="badge badge-pill badge-danger">买入</span>'
                                shares = parseInt(obj.shares);
                            } else {
                                badge = '<span class="badge badge-pill badge-success">卖出</span>'
                                shares = - parseInt(obj.shares);
                            }
                            if (obj.is_sold) {
                                sold = '<i class="fa fa-battery-empty"></i>'
                            } else {
                                if (obj.lots_remain < obj.shares) {
                                    sold = '<i class="fa fa-battery-half"></i>'
                                } else if (obj.lots_remain == obj.shares) {
                                    sold = '<i class="fa fa-battery-full"></i>'
                                }
                            }
                            $("#pId" + pId).append(
                                '<div class="d-flex align-items-center justify-content-between flex-wrap small">' +
                                '<div class="text-muted">' +
                                '<div><span class="font-weight-bold">类型</span></div>' +
                                '<div>' + badge + '</div>' +
                                '</div>' +
                                '<div class="text-muted">' +
                                '<div><span class="font-weight-bold">时间</span></div>' +
                                '<div>' + obj.trade_time + '</div>' +
                                '</div>' +
                                '<div class="text-muted">' +
                                '<div><span class="font-weight-bold">价格</span></div>' +
                                '<div>' + obj.price + '</div>' +
                                '</div>' +
                                '<div class="text-muted">' +
                                '<div><span class="font-weight-bold">数量</span></div>' +
                                '<div>' + shares + '</div>' +
                                '</div>' +
                                // '<div class="text-muted">'+
                                //     '<div><span class="font-weight-bold">现价</span></div>'+
                                //     '<div>'+obj.curent_price+'</div>'+
                                // '</div>'+
                                // '<div class="text-muted"> '+
                                //     '<div><span class="font-weight-bold">账户</span></div>'+
                                //     '<div>'+obj.account+'</div>'+
                                // '</div>'+
                                '<div class="text-muted">' +
                                '<div><span class="font-weight-bold">已卖出？</span></div>' +
                                '<div>' + sold + '</div>' +
                                '</div>' +
                                '<div class="text-muted">' +
                                '<div><span class="font-weight-bold">剩余持仓</span></div>' +
                                '<div>' + obj.lots_remain + '</div>' +
                                '</div>' +
                                '<div class="text-muted">' +
                                '<div><span class="font-weight-bold">交易金额</span></div>' +
                                '<div>' + obj.amount + '</div>' +
                                '</div>' +
                                '</div>' +
                                '<hr>'
                            );
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
        } else {
            showDetailOfPosition(pId);
        }
    };

    var btns = document.getElementsByName("show-trade-record");
    if (btns) {
        $(btns).each(function (id, obj) {
            $(obj).on("click", bindDetailOfPosition);
        });
    }

    var showDetailBtns = document.getElementsByName("show-transaction-detail");
    if(showDetailBtns.length>0){
        showDetailBtns[0].addEventListener("click", bindDetailOfPosition)
    }

    $('.close').click(function () {
        // e.preventDefault();
        $('#messages').addClass('d-none');
    });
});
